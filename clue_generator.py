# clue_generator.py
#
# Clue generation v1.

#
# Data format (confirmed):
#
#   {
#       "phrase": "understand",       # the full original phrase
#       "answer": "understand",       # what counts as a correct guess
#       "clues": [
#           {
#               "segment": "UNDER",       # the piece of the word/phrase
#               "type": "concept",        # "concept" = should be drawn as an image
#                                         # "text"    = should be shown as literal letters/word
#               "image_prompt": "an arrow pointing straight down"
#           },
#           {
#               "segment": "STAND",
#               "type": "concept",
#               "image_prompt": "a person standing upright"
#           }
#       ]
#   }
#
#
# with type == "concept", send clue["image_prompt"] to the image API. For
# type == "text", just render the segment as text/letters -- no image needed.

_TEST_SET = {
    "understand": [
        {"segment": "UNDER", "type": "concept", "image_prompt": "an arrow pointing straight down, under a line"},
        {"segment": "STAND", "type": "concept", "image_prompt": "a person standing upright"},
    ],
    "believe": [
        {"segment": "BEE", "type": "concept", "image_prompt": "a honeybee"},
        {"segment": "LEAF", "type": "concept", "image_prompt": "a single green leaf"},
    ],
    "ice cream": [
        {"segment": "EYE", "type": "concept", "image_prompt": "a close-up of a human eye"},
        {"segment": "SCREAM", "type": "concept", "image_prompt": "a person screaming, mouth wide open"},
    ],
    "forgive": [
        {"segment": "FOUR", "type": "text", "image_prompt": None},
        {"segment": "GIVE", "type": "concept", "image_prompt": "two hands passing a gift box"},
    ],
    "before": [
        {"segment": "BEE", "type": "concept", "image_prompt": "a honeybee"},
        {"segment": "FOUR", "type": "text", "image_prompt": None},
    ],
    "sunflower": [
        {"segment": "SUN", "type": "concept", "image_prompt": "a bright cartoon sun"},
        {"segment": "FLOWER", "type": "concept", "image_prompt": "a single blooming flower"},
    ],
    "download": [
        {"segment": "DOWN", "type": "concept", "image_prompt": "an arrow pointing down"},
        {"segment": "LOAD", "type": "concept", "image_prompt": "a cardboard box being carried"},
    ],
    "outlaw": [
        {"segment": "OUT", "type": "text", "image_prompt": None},
        {"segment": "LAW", "type": "concept", "image_prompt": "a courtroom gavel"},
    ],
}


def generate_clues(phrase):
    """
    Rule-based clue breakdown for a small, hand-built test set of words.
    Returns the agreed puzzle data format, or None if the phrase isn't in
    our test set yet.
    """
    key = phrase.strip().lower()
    if key not in _TEST_SET:
        return None

    return {
        "phrase": key,
        "answer": key,
        "clues": _TEST_SET[key],
    }


def available_test_words():
    """What we can currently generate clues for."""
    return list(_TEST_SET.keys())