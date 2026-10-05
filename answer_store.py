
# Takes puzzles built by clue_generator.py and saves them (with their
# answers) to a JSON file, so they persist between runs instead of only


import json
import os

import clue_generator

PUZZLES_FILE = os.path.join(os.path.dirname(__file__), "puzzles.json")


def build_and_save_all():
    """
    Generate a puzzle for every word in clue_generator's test set and save
    the whole batch to puzzles.json. Safe to call again later -- it just
    rebuilds the file from the current test set.
    """
    puzzles = []
    for word in clue_generator.available_test_words():
        puzzle = clue_generator.generate_clues(word)
        if puzzle:
            puzzles.append(puzzle)

    with open(PUZZLES_FILE, "w") as f:
        json.dump(puzzles, f, indent=2)

    return puzzles


def load_puzzles():
    """
    Load saved puzzles from disk. If the file doesn't exist yet (first run),
    build it first so there's always something to play.
    """
    if not os.path.exists(PUZZLES_FILE):
        return build_and_save_all()

    with open(PUZZLES_FILE, "r") as f:
        return json.load(f)


def check_answer(guess, puzzle):
    """Case-insensitive, whitespace-trimmed answer check."""
    return guess.strip().lower() == puzzle["answer"].strip().lower()