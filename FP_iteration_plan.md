# FP Iteration Plan — REBUS

**Team:** Hamza & Kowsar
**Project:** AI-assisted REBUS puzzle system

## 1. Project Plan

### Overview

REBUS is a new project (not an enhancement of an existing system), so this plan focuses on design, research, and building the system from scratch across the remaining weekly iterations.

### Roles

- **Hamza (backend):** clue generation logic, answer generation/storage/checking
- **Kowsar (frontend/AI media):** AI-assisted image generation, play/solve interface

We sync weekly to integrate our pieces, and the final evaluation phase is done together.

### Definition of Done

The project is considered complete when a user can:

1. Be shown an AI-generated REBUS puzzle (image + clue elements),
2. Submit a guess for what the puzzle represents,
3. Have that guess checked against a maintained answer, and
4. See feedback on whether they solved it correctly.

### Weekly Iteration Plan

Each iteration, both of us work in parallel on our own area (backend vs. image/interface), then sync at the end of the week to integrate and test together.

| Week | Hamza (Backend) | Kowsar (Image Gen / Interface) | Weekly Goal | Deliver |
|------|-------------------------|----------------------------------------|-------------------|---------|
| 1 (done) | Set up repo, basic `Puzzle` data structure | Reviewed project requirements together | Shared understanding of scope | Pushed to GitHub |
| 2 | Draft Project Plan + Preliminary Design | Draft Research + Risks | Combine into one FP2 doc | This file + FP2 signoff |
| 3 | Clue generation v1: rule-based/manual clue breakdown for a small test set of words | Research/prototype image-gen API options and test calls | Confirm clue data format both sides will use | Demo in breakout room |
| 4 | Answer storage v1: persist puzzles/answers (JSON file) + answer-checking function | Image generation v1: AI-generated images for individual clue elements | Check that the clue format feeds cleanly into image generation | Demo |
| 5 | AI-assisted clue generation: integrate an LLM to generate/suggest clue breakdowns | Play interface v1: display puzzle image(s) + clue, accept a guess | Confirm interface can call backend's checking function | Demo |
| 6 | Refine/test AI clue generation against manual baseline | Refine generated images, connect them to clue elements in the interface | Playtest a few generated puzzles end-to-end | Demo |
| 7 | Wire answer-checking fully into the play interface | Polish play interface UI/UX | Full flow test: generate → play → check | Demo |
| 8 | Integration: connect clue generation + answer storage + image generation + play interface into one flow | Integration: same, from the interface/image side | End-to-end test with several puzzles | Demo |
| 9 | Polish + edge cases: error handling, ambiguous guesses, replay/reset | Polish + edge cases: image/interface bugs, difficulty variety | Broader testing with outside testers if possible | Demo |
| 10 | Final evaluation: review against Definition of Done | Final evaluation: same, plus write-up on how AI helped create meaningful puzzles | Final review together | Final delivery + self-evaluation |

---

## 2. Preliminary Design

### Technology Stack (current thinking — subject to change)

- **Programming language:** Python — matches our existing repo/CLI runner from iteration 1, and has strong support for both AI API integration and quick prototyping.
- **Backend:** Plain Python modules for now (clue generation, answer storage/checking); may introduce a lightweight framework (e.g., Flask) once we move from CLI to a web-based play interface.
- **Frontend / Play Interface:** Starting as a CLI for early milestones (fastest to build/test); planning to move to a simple web UI (Flask + HTML/CSS, or Streamlit for speed) once core logic is stable, so users can play without a terminal.
- **Database / Storage:** JSON file storage to start (simple, version-controllable, easy to inspect); may move to SQLite if the puzzle set grows large enough that JSON becomes unwieldy.
- **AI/LLM Services:** An LLM API (e.g., OpenAI or similar) for AI-assisted clue generation; an image-generation API (e.g., DALL·E or similar) for the visual clue elements. Exact provider TBD based on cost/free-tier availability.
- **Authentication:** None planned initially — puzzles are meant to be playable without login for this scope. May revisit if we add saved progress/scoring.
- **Deployment:** Local/CLI for early iterations; if we move to a web interface, likely a free-tier host (e.g., Render, Railway, or similar) for the demo.
- **Development tools:** GitHub for version control, VS Code, and AI/LLM tools (e.g., Claude/ChatGPT) for code assistance during development.

### Rationale

We're prioritizing tools that let us move fast and validate the core AI-assisted puzzle loop (clue → image → guess → check) before investing in polish like a full web UI, auth, or a production database. Python keeps both of our workstreams (backend logic and image/interface work) in one language, which simplifies integration during our weekly sync.

---

## 3. Research

We researched three games that are similar to our project:

- **Dingbats:** Players look at pictures and words to guess a hidden phrase.
- **Rebus Puzzles:** Players solve picture puzzles and can use hints when they get stuck.
- **Rebus Master:** Players solve different rebus puzzles online or on their phones.

These games gave us ideas for a simple play screen with a puzzle image, answer box, submit button, and hint button.

## 4. Risks

- **Confusing AI images:** The AI might create an image that does not match the answer. We will test the images and replace any confusing ones.
- **Answer-checking problems:** Players may type the correct answer differently. We will ignore capitalization, punctuation, and extra spaces.
- **Limited time:** We may not finish every feature. We will complete the basic game first and add extra features if we have time.
