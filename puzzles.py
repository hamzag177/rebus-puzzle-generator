# puzzles.py

# Temporary hardcoded puzzle until AI generation is wired up
SAMPLE_PUZZLE = {
    "phrase": "understand",
    "clues": ["UNDER", "STAND"],
    "answer": "understand"
}

def get_puzzle():
    return SAMPLE_PUZZLE

def check_answer(guess, puzzle):
    return guess.strip().lower() == puzzle["answer"].lower()
