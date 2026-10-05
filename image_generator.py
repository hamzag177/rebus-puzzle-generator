
# Turns a clue's image_prompt into an actual AI-generated image file, using


import json
import os
import time
import urllib.error
import urllib.request

import answer_store

try:
    from config_local import HF_TOKEN
except ImportError:
    HF_TOKEN = None

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")
MODEL_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-3-medium-diffusers"
MAX_RETRIES = 4


def _prompt_to_filename(prompt):
    safe = "".join(c if c.isalnum() else "_" for c in prompt.lower())
    safe = "_".join(filter(None, safe.split("_")))
    return safe[:60] + ".jpg"


def generate_image(prompt, out_dir=IMAGES_DIR):
    """
    Generate an image for a single prompt via Hugging Face and save it to
    out_dir. Returns the local file path, or None if generation failed.
    """
    if not HF_TOKEN or HF_TOKEN == "PASTE_YOUR_TOKEN_HERE":
        print("  [no Hugging Face token set -- see config_local.py]")
        return None

    os.makedirs(out_dir, exist_ok=True)
    filename = _prompt_to_filename(prompt)
    filepath = os.path.join(out_dir, filename)

    if os.path.exists(filepath):
        return filepath

    body = json.dumps({"inputs": prompt}).encode("utf-8")
    req = urllib.request.Request(
        MODEL_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                image_bytes = response.read()
                with open(filepath, "wb") as f:
                    f.write(image_bytes)
                return filepath

        except urllib.error.HTTPError as e:
            # 503 usually means the model is "cold" and still loading on
            # Hugging Face's servers -- worth waiting and retrying.
            if e.code == 503 and attempt < MAX_RETRIES:
                print(f"  [model loading, retrying in 20s... (attempt {attempt}/{MAX_RETRIES})]")
                time.sleep(20)
                continue
            print(f"  [image generation failed for '{prompt}': HTTP {e.code} {e.reason}]")
            return None

        except Exception as e:
            print(f"  [image generation failed for '{prompt}': {e}]")
            return None

    return None


def generate_images_for_puzzle(puzzle):
    for clue in puzzle["clues"]:
        if clue["type"] == "concept":
            print(f"Generating image for: {clue['image_prompt']}")
            clue["image_path"] = generate_image(clue["image_prompt"])
        else:
            clue["image_path"] = None
    return puzzle


def generate_images_for_all_puzzles():
    puzzles = answer_store.load_puzzles()
    for puzzle in puzzles:
        print(f"\n=== {puzzle['phrase']} ===")
        generate_images_for_puzzle(puzzle)

    with open(answer_store.PUZZLES_FILE, "w") as f:
        json.dump(puzzles, f, indent=2)

    return puzzles


if __name__ == "__main__":
    generate_images_for_all_puzzles()
    print("\nDone. Images saved to the images/ folder, puzzles.json updated with image_path.")