# the real web interface, replacing the terminal play loop.
# Runs with Flask



import os

from flask import Flask, redirect, render_template, request, send_from_directory, session, url_for

import answer_store
import hints

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-later"  # fine for a class project, not for production

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

    return render_template(
        "puzzle.html",
        puzzle=puzzle,
        puzzle_number=puzzle_index + 1,
        total_puzzles=len(puzzles),
        attempt=session["attempt"],
        max_tries=MAX_TRIES,
        hint_count=session["hint_count"],
        max_hints=MAX_HINTS,
        message=session.get("message"),
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
        else:
            session["hint_count"] += 1
            hint_text = hints.give_hint(puzzle["answer"], session["hint_count"])
            session["message"] = f"Hint: {hint_text}"
        return redirect(url_for("index"))

    if action == "skip":
        _advance_puzzle(correct=False)
        return redirect(url_for("index"))

    # Otherwise, it's a real guess.
    user_guess = request.form.get("guess", "")

    if answer_store.check_answer(user_guess, puzzle):
        session["correct_count"] += 1
        session["message"] = "Correct! \U0001F389"
        _advance_puzzle(correct=True)
        return redirect(url_for("index"))

    session["attempt"] += 1
    if session["attempt"] > MAX_TRIES:
        session["message"] = f"Out of tries! The answer was: {puzzle['answer']}"
        _advance_puzzle(correct=False)
    else:
        session["message"] = "Not quite -- try again."

    return redirect(url_for("index"))


def _advance_puzzle(correct):
    session["puzzle_index"] += 1
    session["attempt"] = 1
    session["hint_count"] = 0
    if not correct:
        # Keep whatever "out of tries" / "skipped" message is already set
        # by the caller -- just move on to the next puzzle.
        pass


@app.route("/results")
def results():
    puzzles = get_puzzles()
    correct_count = session.get("correct_count", 0)
    total = len(puzzles)

    return render_template("result.html", correct_count=correct_count, total=total)


@app.route("/restart")
def restart():
    reset_game()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)