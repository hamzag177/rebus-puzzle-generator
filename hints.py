
def give_hint(answer, hint_count):
    """
    Return a hint for a rebus puzzle answer.

    Hint 1: show one blank for each letter (spaces between words are kept).
    Hint 2+: reveal the first letter and show blanks for the rest.
    """
    if not answer or hint_count <= 0:
        return ""

    def blank(word):
        return "_" * len(word)

    words = answer.split(" ")

    if hint_count == 1:
        return " ".join(blank(w) for w in words)

    # hint_count 2+: reveal the first letter of the whole answer,
    # blank out the rest.
    first_word = words[0]
    revealed_first_word = first_word[0] + blank(first_word[1:])
    rest = [blank(w) for w in words[1:]]
    return " ".join([revealed_first_word] + rest)


if __name__ == "__main__":
    for answer in ["computer", "ice cream"]:
        print(f"\nAnswer (for testing): {answer}")
        print("Hint 1:", give_hint(answer, 1))
        print("Hint 2:", give_hint(answer, 2))