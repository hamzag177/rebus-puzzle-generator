# REBUS Puzzle Generator

A web-based rebus puzzle game built with Flask. Players solve picture-and-word
puzzles by guessing the phrase a set of visual clues represents (for example,
an image of a bee next to the word "FOUR" = **"before"**). Puzzles can be
generated automatically with AI: an LLM breaks a typed phrase into clue
segments, and an image-generation API illustrates each visual clue.

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [How to Play](#how-to-play)
- [Admin Guide](#admin-guide)
- [Scoring System](#scoring-system)
- [Game Modes](#game-modes)
- [Known Limitations / Future Work](#known-limitations--future-work)
- [Project Goals](#project-goals)

---

## Features

- **Puzzle of the Day** — a single featured puzzle that's the same for every
  player on a given day, and automatically rotates to a new one at midnight.
- **Browse Puzzles** — jump into any puzzle from a list, and it automatically
  continues through the rest of the puzzle set in sequence until all of them
  have been played.
- **AI-assisted puzzle creation** — admins type any word or phrase and the
  app breaks it into rebus clues automatically, with a review step to edit
  image descriptions before the final images are generated.
- **Hint system** — up to 2 hints per puzzle, with a limited number of
  guesses before the answer is revealed.
- **Scoring system** — points awarded based on how quickly a puzzle is
  solved and how many hints were used, tracked for the whole session.
- **Admin panel** — add, preview, and delete puzzles, protected by a
  passcode login so regular players can't access it.
- **Responsive, polished UI** — flat navigation bar, landing page, and
  consistent styling across every screen.

---

## How It Works

1. An admin types a word or phrase into the admin panel (e.g. `"sunflower"`).
2. **Google Gemini** breaks the phrase into clue segments — some shown as
   plain text (like "FOUR"), others described as an image concept (like "a
   single sunflower").
3. For every image-based clue, **Hugging Face's Stable Diffusion API**
   generates an actual image from that description.
4. The admin reviews/edits the clue breakdown before the images are
   generated and the puzzle is saved.
5. The finished puzzle — a mix of images and text snippets — becomes
   playable immediately through the Daily Puzzle, Browse Puzzles, or both.

If either AI call fails or no API key is configured, the app falls back
gracefully (a hand-written test set of puzzles, or a text placeholder)
instead of crashing.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Templating | Jinja2 |
| Frontend | HTML, CSS (no JS framework — vanilla JS for form handling) |
| Clue generation | Google Gemini API |
| Image generation | Hugging Face Inference API (Stable Diffusion 2.1) |
| Data storage | `puzzles.json` (flat-file, no database) |
| Session state | Flask's built-in signed session cookies |

---

## Project Structure

```
rebus_demo/
├── app.py                   # Main Flask app — all routes live here
├── answer_store.py          # Load/save/check puzzles in puzzles.json
├── ai_clue_generator.py     # Calls Gemini to break a phrase into clues
├── clue_generator.py        # Hand-written fallback clue set
├── image_generator.py       # Calls Hugging Face to generate clue images
├── hints.py                 # Hint text logic
├── scoring.py               # Point calculation for solved puzzles
├── message_colors.py        # Styled success/error/hint message text
├── score_summary.py         # "Great job!" / "Keep practicing!" summary text
├── config_local.py          # Local secrets (gitignored — see Configuration)
├── puzzles.json             # All saved puzzles
├── images/                  # AI-generated puzzle images
├── templates/
│   ├── _header.html         # Shared nav bar, included on every page
│   ├── home.html            # Landing page
│   ├── puzzle.html          # Main gameplay screen
│   ├── result.html          # Completion / results screen
│   ├── browse.html          # Browse Puzzles list
│   ├── how_to_play.html     # Rules explainer page
│   ├── admin.html           # Admin panel
│   └── admin_login.html     # Admin passcode login
└── static/
    └── style.css            # All styling
```

---

## Setup & Installation

**Requirements:** Python 3.9+

1. Clone the repository and navigate into the project folder.
2. Install dependencies:
   ```
   pip install flask
   ```
3. Create your local config file (see [Configuration](#configuration) below).
4. Run the app (see [Running the App](#running-the-app)).

---

## Configuration

API keys and the admin passcode are kept out of source control in a file
called `config_local.py`, which is listed in `.gitignore` and must **never**
be committed. Create it in the project root with the following:

```python
# config_local.py
GEMINI_API_KEY = "your-gemini-api-key-here"
HF_TOKEN = "your-hugging-face-token-here"
ADMIN_PASSCODE = "your-chosen-admin-passcode"
```

- `GEMINI_API_KEY` — used by `ai_clue_generator.py` for AI clue breakdowns.
- `HF_TOKEN` — used by `image_generator.py` for AI image generation.
- `ADMIN_PASSCODE` — required to log into the `/admin` panel.

If any of these are missing, the app still runs: clue generation falls back
to a small hand-written word list, image generation is skipped, and the
admin panel simply can't be logged into until a passcode is set.

---

## Running the App

```
python app.py
```

By default this runs at **http://127.0.0.1:5000**. Open that address in a
browser to land on the home page.

---

## How to Play

1. From the Main Menu, choose **Daily Puzzle** or **Browse Puzzles**.
2. Look at the clues (images and/or text) and guess the phrase they spell
   out together.
3. Use **Hint** if stuck (up to 2 per puzzle), or **Skip** to move on.
4. You have 3 guesses per puzzle before the answer is revealed.
5. After the Daily Puzzle, you can keep playing through the rest of the
   puzzle set with **Play More Puzzles**.

A full rules explainer is also available in-app under **How to Play**.

---

## Admin Guide

1. Click **Admin** in the nav bar.
2. Enter the passcode set in `config_local.py`.
3. Type any word or phrase and click **Generate Puzzle** — the AI will break
   it into clue segments and show you the image description for each
   visual clue.
4. Edit any image description if needed, then click **Generate Images &
   Save Puzzle** to finalize it.
5. Existing puzzles are listed below the form and can be deleted from there.
6. Click **Log out of admin** when finished.

---

## Scoring System

Points are awarded only when a puzzle is solved correctly:

| Attempt solved on | Base points |
|---|---|
| 1st try | 100 |
| 2nd try | 50 |
| 3rd try | 25 |
| After running out of tries | 0 |

Each hint used subtracts 10 points from that puzzle's total (never going
below 0). Points accumulate in a running total shown throughout the
session, across the Daily Puzzle, Browse Puzzles, and Play More Puzzles.

---

## Game Modes

| Mode | How it's reached | Behavior |
|---|---|---|
| **Daily** | Default / "Daily Puzzle" link | One featured puzzle, same for everyone that calendar day |
| **All** | "Play More Puzzles" after the Daily Puzzle | Plays through every remaining puzzle in order |
| **Single/Browse** | Picking a puzzle on the Browse page | Starts at the chosen puzzle, then continues through the rest of the set in order until all have been played |

---

## Known Limitations / Future Work

- Puzzle data is stored in a flat JSON file rather than a database — fine
  for a small/medium puzzle set, but wouldn't scale to a large catalog.
- No user accounts — scores and progress reset with a new browser session.
- Difficulty tiers (easy/medium/hard puzzle types) were discussed as a
  future enhancement but are not yet implemented.

---

## Project Goals

- Build an AI-assisted REBUS puzzle system.
- Use AI to generate the clues.
- Use AI to assist with image generation.
- Generate REBUS puzzles.
- Generate and maintain answers for the puzzles.
- Allow users to play/solve the generated puzzles.
- Display the "puzzle of the day" so that a new puzzle shows up on the
  website each day.
- Have the ability for users to see multiple puzzles so that they can play
  the puzzles at their own pace.
- Explore how AI can help create interesting and meaningful puzzles.
