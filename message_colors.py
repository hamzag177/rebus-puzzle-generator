# message_colors.py

def wrong_guess_message(text):
    """Returns (message_text, message_type) for a wrong guess."""
    return text, "error"

def hint_message(hint):
    """Returns (message_text, message_type) for a hint."""
    return f"Hint: {hint}", "hint"

def correct_guess_message(points=None):
    """Returns (message_text, message_type) for a correct guess. Includes
    the points earned if given one (see scoring.calculate_points)."""
    if points is not None:
        return f"Correct! +{points} points", "success"
    return "Correct! Nice work.", "success"

if __name__ == "__main__":
    print(wrong_guess_message("Not quite, try again!"))
    print(hint_message("_ _ _ _ _"))
    print(correct_guess_message())
    print(correct_guess_message(80))