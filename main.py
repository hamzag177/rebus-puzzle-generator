# main.py
from puzzles import get_puzzle, check_answer

def main():
    puzzle = get_puzzle()
    print("Clues:", puzzle["clues"])
    guess = input("Your guess: ")
    if check_answer(guess, puzzle):
        print("Correct!")
    else:
        print(f"Not quite. The answer was: {puzzle['answer']}")

if __name__ == "__main__":
    main()
