
# the actual play loop -- show a puzzle's clues, take guesses,
# retry on a wrong answer, reveal the answer if the player gives up or runs
# out of tries, then move on to the next puzzle.


import answer_store

MAX_TRIES = 3


def show_clues(puzzle):
    print("\nHere's the puzzle:\n")
    for clue in puzzle["clues"]:
        if clue["type"] == "concept":
            # Stand-in for a real generated image, until Kowsar's image-gen
            # work is wired in.
            print(f"  [IMAGE: {clue['image_prompt']}]")
        else:
            print(f"  {clue['segment']}")
    print()


def play_puzzle(puzzle):
    show_clues(puzzle)

    for attempt in range(1, MAX_TRIES + 1):
        guess = input(f"Your guess (try {attempt}/{MAX_TRIES}, or type 'skip'): ").strip()

        if guess.lower() == "skip":
            break

        if answer_store.check_answer(guess, puzzle):
            print("Correct! 🎉\n")
            return True

        if attempt < MAX_TRIES:
            print("Not quite -- try again.\n")
        else:
            print("Out of tries.\n")

    print(f"The answer was: {puzzle['answer']}\n")
    return False


def main():
    print("=== REBUS Puzzle -- Play Loop ===")
    puzzles = answer_store.load_puzzles()
    print(f"Loaded {len(puzzles)} puzzle(s).\n")

    correct_count = 0
    for i, puzzle in enumerate(puzzles, start=1):
        print(f"--- Puzzle {i} of {len(puzzles)} ---")
        if play_puzzle(puzzle):
            correct_count += 1

    print(f"Done! You solved {correct_count} out of {len(puzzles)} puzzles.")


if __name__ == "__main__":
    main()