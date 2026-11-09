# the real web interface, replacing the terminal play loop.
# Runs with Flask

import datetime
import os

from flask import Flask, redirect, render_template, request, send_from_directory, session, url_for

import ai_clue_generator
import answer_store
import hints
import image_generator
import message_colors
import score_summary

app = Flask(__name__)
app.secret_key = os.urandom(24)  # new random key every time the server starts, so old sessions reset automatically

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")

MAX_TRIES = 3
MAX_HINTS = 2

def get_puzzle_of_the_day():
    """
    Pick one puzzle to feature today. Deterministic and based on the actual
    calendar date, so every player sees the SAME puzzle on a given day, and
    it automatically changes to a different one at midnight -- cycling back
    around to the start once every puzzle has had a turn. No admin work
    needed to "schedule" it.
    """
    all_puzzles = answer_store.load_puzzles()
    if not all_puzzles:
        return []
    index = datetime.date.today().toordinal() % len(all_puzzles)
    return [all_puzzles[index]]

def get_puzzles():
    # "all" mode (reached via "Play More Puzzles" after finishing today's
    # puzzle) plays through every puzzle in order, like the game used to --
    # except if the player already solved today's featured puzzle, it's
    # temporarily left out of this set so they don't see it again right
    # after solving it (just for this session; it's back in rotation
    # tomorrow, or anytime a fresh session starts).
    if session.get("mode") == "all":
        puzzles = answer_store.load_puzzles()
        excluded_answer = session.get("excluded_answer")
        if excluded_answer:
            puzzles = [
                p for p in puzzles
                if p["answer"].strip().lower() != excluded_answer.strip().lower()
            ]
        return puzzles
    return get_puzzle_of_the_day()

def reset_game(mode="daily"):
    session["mode"] = mode
    session["puzzle_index"] = 0
    session["attempt"] = 1
    session["hint_count"] = 0
    session["correct_count"] = 0
    session["message"] = None
    session["message_type"] = None
    if mode == "daily":
        # Back to the daily flow -- clear any temporary exclusion from a
        # previous "all" play-through so it doesn't leak into the next one.
        session.pop("excluded_answer", None)

@app.route("/images/<path:filename>")
def serve_image(filename):
    """Serve the already-generated AI images from the images/ folder."""
    return send_from_directory(IMAGES_DIR, filename)

@app.route("/")
def index():
    if "puzzle_index" not in session:
        reset_game()

    puzzles = get_puzzles()
    puzzle_index = session["puzzle_index"]

    if puzzle_index >= len(puzzles):
        return redirect(url_for("results"))

    puzzle = puzzles[puzzle_index]
    message = session.pop("message", None)
    message_type = session.pop("message_type", None)

    return render_template(
        "puzzle.html",
        puzzle=puzzle,
        mode=session.get("mode", "daily"),
        puzzle_number=puzzle_index + 1,
        total_puzzles=len(puzzles),
        attempt=session["attempt"],
        max_tries=MAX_TRIES,
        hint_count=session["hint_count"],
        max_hints=MAX_HINTS,
        message=message,
        message_type=message_type,
    )

@app.route("/guess", methods=["POST"])
def guess():
    puzzles = get_puzzles()
    puzzle_index = session.get("puzzle_index", 0)

    if puzzle_index >= len(puzzles):
        return redirect(url_for("results"))

    puzzle = puzzles[puzzle_index]

    action = request.form.get("action")

    if action == "hint":
        if session["hint_count"] >= MAX_HINTS:
            session["message"] = "You're all out of hints -- try a guess!"
            session["message_type"] = "error"
        else:
            session["hint_count"] += 1
            hint_text = hints.give_hint(puzzle["answer"], session["hint_count"])
            session["message"], session["message_type"] = message_colors.hint_message(hint_text)
        return redirect(url_for("index"))

    if action == "skip":
        _advance_puzzle(correct=False)
        return redirect(url_for("index"))

    # Otherwise, it's a real guess.
    user_guess = request.form.get("guess", "")

    if answer_store.check_answer(user_guess, puzzle):
        session["correct_count"] += 1
        _advance_puzzle(correct=True)
        return redirect(url_for("index"))

    session["attempt"] += 1
    if session["attempt"] > MAX_TRIES:
        session["message"], session["message_type"] = message_colors.wrong_guess_message(
            f"Out of tries! The answer was: {puzzle['answer']}"
        )
        _advance_puzzle(correct=False)
    else:
        session["message"], session["message_type"] = message_colors.wrong_guess_message(
            "Not quite -- try again."
        )

    return redirect(url_for("index"))

def _advance_puzzle(correct):
    session["puzzle_index"] += 1
    session["attempt"] = 1
    session["hint_count"] = 0

@app.route("/results")
def results():
    puzzles = get_puzzles()
    correct_count = session.get("correct_count", 0)
    total = len(puzzles)
    title = score_summary.get_title(correct_count, total)
    mode = session.get("mode", "daily")

    return render_template("result.html", correct_count=correct_count, total=total, title=title, mode=mode)

@app.route("/restart")
def restart():
    reset_game(mode="daily")
    return redirect(url_for("index"))

@app.route("/more")
def more_puzzles():
    """After finishing today's puzzle, let the player keep going and play
    through the rest of the puzzle list at their own pace. If they actually
    solved today's puzzle, leave it out of that list for this session so
    they don't immediately run into the same puzzle again."""
    if session.get("mode") == "daily" and session.get("correct_count", 0) > 0:
        todays_puzzle = get_puzzle_of_the_day()
        if todays_puzzle:
            session["excluded_answer"] = todays_puzzle[0]["answer"]

    reset_game(mode="all")
    return redirect(url_for("index"))

# ---------------------------------------------------------------------------
# Admin page (Week 6) -- hidden from regular players, no login yet per the
# instructor's note that auth "will come later". Lets us type in any new
# word/phrase, have the AI break it into clues, generate the images for
# the "concept" clues, and save the whole thing as a new playable puzzle --
# without touching any code.
# ---------------------------------------------------------------------------

@app.route("/admin", methods=["GET", "POST"])
def admin():
    message = None
    draft = session.get("draft_puzzle")

    if request.method == "POST":
        action = request.form.get("action")

        # Step 1: generate the clue breakdown + image prompts, but DON'T
        # generate images yet -- show the prompts first so they can be
        # reviewed/edited (per instructor feedback).
        if action == "generate_clues":
            phrase = request.form.get("phrase", "").strip()

            if not phrase:
                message = "Please type a word or phrase first."
            elif any(p["answer"].strip().lower() == phrase.lower() for p in answer_store.load_puzzles()):
                message = f"\"{phrase}\" is already a puzzle -- pick a different word or phrase."
            else:
                puzzle = ai_clue_generator.generate_clues_ai(phrase)

                if not puzzle:
                    message = f"Couldn't generate clues for \"{phrase}\" -- try a different word or phrase."
                else:
                    session["draft_puzzle"] = puzzle
                    draft = puzzle

        # Discard the current draft without saving anything.
        elif action == "cancel_draft":
            session.pop("draft_puzzle", None)
            draft = None
            message = "Cancelled -- draft discarded."

        # Step 2: take the (possibly edited) prompts from the review form,
        # generate the actual images, and save the puzzle.
        elif action == "confirm_puzzle":
            if not draft:
                message = "No puzzle draft to confirm -- generate one first."
            else:
                for i, clue in enumerate(draft["clues"]):
                    if clue["type"] == "concept":
                        edited_prompt = request.form.get(f"prompt_{i}", "").strip()
                        if edited_prompt:
                            clue["image_prompt"] = edited_prompt

                for clue in draft["clues"]:
                    if clue["type"] == "concept" and clue.get("image_prompt"):
                        clue["image_path"] = image_generator.generate_image(clue["image_prompt"])

                answer_store.add_puzzle(draft)
                message = f"Added new puzzle for \"{draft['phrase']}\"!"
                session.pop("draft_puzzle", None)
                draft = None

        # Remove an existing puzzle from the list.
        elif action == "delete_puzzle":
            answer_to_delete = request.form.get("answer", "")
            if answer_store.delete_puzzle(answer_to_delete):
                message = f"Deleted puzzle \"{answer_to_delete}\"."
            else:
                message = f"Couldn't find a puzzle matching \"{answer_to_delete}\" to delete."

    puzzles = answer_store.load_puzzles()
    return render_template("admin.html", message=message, puzzles=puzzles, draft=draft)

if __name__ == "__main__":
    app.run(debug=True)