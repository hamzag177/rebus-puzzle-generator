# the real web interface, replacing the terminal play loop.
# Runs with Flask

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

def get_puzzles():
    return answer_store.load_puzzles()

def reset_game():
    session["puzzle_index"] = 0
    session["attempt"] = 1
    session["hint_count"] = 0
    session["correct_count"] = 0
    session["message"] = None
    session["message_type"] = None

@app.route("/images/<path:filename>")
def serve_image(filename):
    """Serve the already-generated AI images from the images/ folder."""
    return send_from_directory(IMAGES_DIR, filename)

@app.route("/")
def index():
    puzzles = get_puzzles()

    if "puzzle_index" not in session:
        reset_game()

    puzzle_index = session["puzzle_index"]

    if puzzle_index >= len(puzzles):
        return redirect(url_for("results"))

    puzzle = puzzles[puzzle_index]
    message = session.pop("message", None)
    message_type = session.pop("message_type", None)

    return render_template(
        "puzzle.html",
        puzzle=puzzle,
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

    return render_template("result.html", correct_count=correct_count, total=total, title=title)

@app.route("/restart")
def restart():
    reset_game()
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

    if request.method == "POST":
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
                # Only generate an image the first time -- image_generator
                # already skips the API call if the file exists on disk,
                # so re-running this is always safe and won't waste calls.
                for clue in puzzle["clues"]:
                    if clue["type"] == "concept" and clue.get("image_prompt"):
                        clue["image_path"] = image_generator.generate_image(clue["image_prompt"])

                answer_store.add_puzzle(puzzle)
                message = f"Added new puzzle for \"{phrase}\"!"

    puzzles = answer_store.load_puzzles()
    return render_template("admin.html", message=message, puzzles=puzzles)

if __name__ == "__main__":
    app.run(debug=True)