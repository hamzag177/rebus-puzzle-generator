
# Originally written for a terminal program (ANSI color codes like \033[91m),
# adapted here for the web version -- instead of coloring text directly, we
# just label each message with a "type" ("error" or "hint"), and the HTML
# template (puzzle.html) + CSS (style.css) handle the actual coloring.
# red for wrong guesses, green for hints.

def wrong_guess_message(text):
    """Returns (message_text, message_type) for a wrong guess."""
    return text, "error"

def hint_message(hint):
    """Returns (message_text, message_type) for a hint."""
    return f"Hint: {hint}", "hint"

if __name__ == "__main__":
    print(wrong_guess_message("Not quite, try again!"))
    print(hint_message("_ _ _ _ _"))