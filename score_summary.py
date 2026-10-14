# turn a final score into a fun title to show the player.

def get_title(correct_answers, total_puzzles):
    """
    Return a title string based on how many puzzles were solved.
    """
    if total_puzzles == 0:
        return "No puzzles were played."

    score = (correct_answers / total_puzzles) * 100

    if score >= 80:
        return "Great Job!"
    elif score >= 50:
        return "Not bad!"
    else:
        return "Keep practicing!"


if __name__ == "__main__":
    # Quick test -- run this file directly to see it in action.
    print(get_title(8, 8))   # Great Job!
    print(get_title(5, 8))   # Not bad!
    print(get_title(1, 8))   # Keep practicing!
    print(get_title(0, 0))   # No puzzles were played.