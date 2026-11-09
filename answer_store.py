import json, os
PUZZLES_FILE = os.path.join(os.path.dirname(__file__), "puzzles.json")

def load_puzzles():
    if not os.path.exists(PUZZLES_FILE):
        return []
    with open(PUZZLES_FILE) as f:
        return json.load(f)

def check_answer(guess, puzzle):
    return guess.strip().lower() == puzzle["answer"].strip().lower()

def add_puzzle(puzzle):
    puzzles = load_puzzles()
    puzzles.append(puzzle)
    with open(PUZZLES_FILE, "w") as f:
        json.dump(puzzles, f, indent=2)
    return puzzles

def delete_puzzle(answer):
    """
    Remove a puzzle by its exact answer (case-insensitive). Returns True if
    a puzzle was actually removed, False if no puzzle matched.
    """
    puzzles = load_puzzles()
    before_count = len(puzzles)
    puzzles = [p for p in puzzles if p["answer"].strip().lower() != answer.strip().lower()]

    with open(PUZZLES_FILE, "w") as f:
        json.dump(puzzles, f, indent=2)

    return len(puzzles) < before_count