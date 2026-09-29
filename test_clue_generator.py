
#
# Simple demo/test harness
# working across the whole test set. Run with: python3 test_clue_generator.py

import clue_generator


def main():
    words = clue_generator.available_test_words()
    print(f"Clue generation v1 -- {len(words)} words in the test set\n")

    for word in words:
        puzzle = clue_generator.generate_clues(word)
        print(f"'{word}' ->")
        for clue in puzzle["clues"]:
            if clue["type"] == "concept":
                print(f"    [{clue['segment']}]  (image prompt: {clue['image_prompt']})")
            else:
                print(f"    [{clue['segment']}]  (shown as text, no image)")
        print()


    print("Unknown word check:")
    result = clue_generator.generate_clues("xylophone")
    print(f"  generate_clues('xylophone') -> {result}")


if __name__ == "__main__":
    main()