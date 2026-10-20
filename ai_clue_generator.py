
# Week 6: AI-assisted clue generation. Given any word or phrase, asks
# Google's Gemini model to break it into rebus clue pieces (the same
# "segment / type / image_prompt" format used everywhere else in the
# project), instead of only working for the 8 words hand-written into
# clue_generator.py's _TEST_SET.
#
# Falls back to the hand-written dictionary (clue_generator.generate_clues)
# if the AI call fails for any reason, so the admin page never just breaks.

import json
import urllib.error
import urllib.request

import clue_generator

try:
    from config_local import GEMINI_API_KEY
except ImportError:
    GEMINI_API_KEY = None

API_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"

# Tells Gemini exactly what shape of JSON to hand back, so we don't have to
# parse free-form text.
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "clues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "segment": {"type": "string"},
                    "type": {"type": "string", "enum": ["concept", "text"]},
                    "image_prompt": {"type": "string"},
                },
                "required": ["segment", "type"],
            },
        },
    },
    "required": ["answer", "clues"],
}

PROMPT_TEMPLATE = """You are helping build a REBUS puzzle (like the classic picture+word puzzles).

Break the word or phrase "{phrase}" into 2-4 clue pieces that, when read in
order and said out loud, sound like the original word or phrase. This can
use real sub-words, homophone tricks (like "ice cream" -> "eye" + "scream"),
or a mix.

For each piece, decide:
- "segment": the piece of text itself, in capital letters (e.g. "UNDER")
- "type": "concept" if the piece has a clear, drawable picture (a physical
  object, animal, action, or scene), or "text" if it doesn't (like a short
  connector or a piece with no clean image)
- "image_prompt": for "concept" pieces only, a short plain-English
  description an AI image generator could draw (e.g. "a person standing
  upright"). Leave this out for "text" pieces.

The "answer" field should be the original phrase, lowercase.
"""


MAX_RETRIES = 3

def _call_gemini(phrase):
    if not GEMINI_API_KEY or GEMINI_API_KEY == "PASTE_YOUR_GEMINI_KEY_HERE":
        return None

    body = json.dumps({
        "model": "gemini-3.8-flash",
        "input": PROMPT_TEMPLATE.format(phrase=phrase),
        "response_format": {
            "type": "text",
            "mime_type": "application/json",
            "schema": RESPONSE_SCHEMA,
        },
    }).encode("utf-8")

    for attempt in range(1, MAX_RETRIES + 1):
        req = urllib.request.Request(
            API_URL,
            data=body,
            headers={
                "x-goog-api-key": GEMINI_API_KEY,
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read())
                break  # got a response, stop retrying
        except urllib.error.HTTPError as e:
            # 503 usually means Gemini is overloaded right now -- worth a retry.
            if e.code == 503 and attempt < MAX_RETRIES:
                print(f"  [Gemini overloaded, retrying... (attempt {attempt}/{MAX_RETRIES})]")
                continue
            print(f"  [AI clue generation failed: HTTP {e.code} {e.reason}]")
            return None
        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"  [AI call failed ({e}), retrying... (attempt {attempt}/{MAX_RETRIES})]")
                continue
            print(f"  [AI clue generation failed: {e}]")
            return None
    else:
        return None

    for step in result.get("steps", []):
        if step.get("type") != "model_output":
            continue
        for item in step.get("content", []):
            if item.get("type") == "text":
                try:
                    return json.loads(item["text"])
                except json.JSONDecodeError:
                    print("  [AI clue generation failed: response wasn't valid JSON]")
                    return None

    print("  [AI clue generation failed: no model output in response]")
    return None


def generate_clues_ai(phrase):
    """
    Generate a puzzle dict for any word/phrase using the AI model. Falls
    back to the hand-written dictionary (clue_generator.generate_clues) if
    the word is already known there, or if the AI call fails.

    Returns the same shape as clue_generator.generate_clues(): a dict with
    "phrase", "answer", and "clues" -- or None if nothing worked.
    """
    phrase = phrase.strip().lower()
    if not phrase:
        return None

    existing = clue_generator.generate_clues(phrase)
    if existing:
        return existing

    ai_result = _call_gemini(phrase)
    if not ai_result:
        return None

    # Make sure "text" clues don't carry a stray image_prompt, and fill in
    # a default for any "concept" clue missing one, so the rest of the
    # project (image_generator.py) never has to special-case this.
    clues = []
    for clue in ai_result.get("clues", []):
        clue_type = clue.get("type", "text")
        clues.append({
            "segment": clue.get("segment", "").upper(),
            "type": clue_type,
            "image_prompt": clue.get("image_prompt") if clue_type == "concept" else None,
        })

    return {
        "phrase": phrase,
        "answer": ai_result.get("answer", phrase),
        "clues": clues,
    }


if __name__ == "__main__":
    # Quick manual test -- run this file directly.
    test_word = "carpet"
    result = generate_clues_ai(test_word)
    print(json.dumps(result, indent=2))