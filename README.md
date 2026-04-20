# BeatScouter — AI Music Recommender

## Original Project

This project is an extension of the **Music Recommender Simulation** from Module 3. The original system represented songs and a user taste profile as data, then scored every song in a small catalog using a weighted formula (genre, mood, energy, valence, acousticness). It returned the top K matches as recommendations. It had no AI layer — preferences were hardcoded and the catalog contained only 28 manually created songs.

---

## Title and Summary

**BeatScouter** is an AI-powered music recommender that accepts plain English requests like *"something chill and acoustic for late night studying"* and returns personalized song recommendations with an AI-generated explanation. It uses Google's Gemma 3 1B language model to interpret natural language into structured preferences, feeds those into a content-based scoring engine, and employs a self-correcting agentic loop to ensure result quality. The system is backed by 375 real Spotify songs and includes a reliability test harness that evaluates end-to-end performance across 7 predefined inputs.

---

## Architecture Overview

```
User (plain English)
        │
        ▼
┌──────────────────┐
│  Gemma 3 1B-IT   │  ← RAG Layer: parses natural language into
│  (ai_layer.py)   │    structured user_prefs dict
└────────┬─────────┘
         │  user_prefs dict
         ▼
┌──────────────────────────────────────────────────────┐
│                  Agent Loop (main.py)                │
│                                                      │
│  ┌────────────────────┐    ┌──────────────────────┐  │
│  │  Scoring Engine    │───▶│  Quality Checker     │  │
│  │  (recommender.py)  │    │  (ai_layer.py)       │  │
│  └────────────────────┘    └──────────┬───────────┘  │
│                                       │              │
│          good? ◀──────────────────────┘              │
│          yes → accept results                        │
│          no  → relax constraints → retry (max 2x)    │
└──────────────────────┬───────────────────────────────┘
                       │  top 5 songs
                       ▼
              ┌─────────────────┐
              │  Gemma 3 1B-IT  │  ← Explains results in friendly
              │  (ai_layer.py)  │    natural language
              └────────┬────────┘
                       │
                       ▼
              Formatted table + explanation
                    (terminal)
```

**Components:**
- **RAG Layer** (`src/ai_layer.py` — `parse_user_input`): Gemma reads the user's request and outputs a structured dict (`genre`, `mood`, `target_energy`, `target_valence`, `target_acousticness`). This dict directly drives which songs score highest — it is not decorative.
- **Scoring Engine** (`src/recommender.py` — `score_song`, `recommend_songs`): Content-based weighted formula. Genre +0.30, mood +0.25, energy proximity +0.20, valence +0.15, acousticness +0.10.
- **Agent Loop** (`src/main.py`): Runs the recommender, calls `check_quality()`, and retries with relaxed genre constraints if the top score is too low. Prints observable `[Agent]` step markers.
- **Explainer** (`src/ai_layer.py` — `explain_results`): Gemma writes a 2-3 sentence friendly explanation of why the returned songs match the request.
- **Test Harness** (`evaluate.py`): 7 predefined natural language inputs, each checked for expected song titles in the top 5. Prints pass/fail per case and a final summary score.

---

## Setup Instructions

**Prerequisites:** Python 3.9+, a free Google AI Studio API key

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

**2. Create a virtual environment**
```bash
python -m venv .venv
# Mac/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your API key**

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your-key-here
```
Get a free key at [https://aistudio.google.com](https://aistudio.google.com)

**5. Run the app**
```bash
python -m src.main
```
- Type a request in plain English → AI mode
- Press Enter with no input → demo mode (hardcoded pop/happy profile)

**6. Run the test harness**
```bash
python evaluate.py
```

**7. Run unit tests**
```bash
pytest
```

---

## Sample Interactions

**Example 1 — Chill acoustic studying**
```
Your request: I want something chill and acoustic for late night studying

  [Agent] Parsing your request...
  [Agent] Parsed: genre=pop, mood=relaxed, energy=0.6, acousticness=0.9
  [Agent] Running recommender (attempt 1)...
  [Agent] Quality check: best score 0.76 — strong match found
  [Agent] Results accepted.

+----+-----------------------------------+----------------+-------+
|  # | Title                             | Artist         | Score |
+----+-----------------------------------+----------------+-------+
|  1 | Fast Car                          | Jonas Blue     |  0.76 |
|  2 | Change (feat. James Taylor)       | Charlie Puth   |  0.74 |
|  3 | El Ultimo Adiós                   | Ricky Martin   |  0.71 |
|  4 | Waiting On the World to Change    | John Mayer     |  0.69 |
|  5 | Sea of Love                       | Cat Power      |  0.68 |
+----+-----------------------------------+----------------+-------+
```
*Gemma explanation:* "These tracks hit that perfect late-night study sweet spot — Fast Car and Change bring a mellow, acoustic warmth that keeps you focused without pulling you away from your work..."

---

**Example 2 — Agent retries after weak results**
```
Your request: give me some obscure jazz fusion from the 70s

  [Agent] Parsing your request...
  [Agent] Parsed: genre=jazz, mood=focused, energy=0.5, acousticness=0.4
  [Agent] Running recommender (attempt 1)...
  [Agent] Quality check: best score 0.48 is too low — genre may be too narrow
  [Agent] Dropping genre constraint — searching all genres...
  [Agent] Running recommender (attempt 2)...
  [Agent] Quality check: best score 0.63 — strong match found
  [Agent] Results accepted.
```

---

**Example 3 — Aggressive hip-hop**
```
Your request: I want aggressive and hard hitting hip-hop, high energy beats

  [Agent] Parsing your request...
  [Agent] Parsed: genre=hip-hop, mood=aggressive, energy=0.9, acousticness=0.0
  [Agent] Running recommender (attempt 1)...
  [Agent] Quality check: best score 0.84 — strong match found
  [Agent] Results accepted.

+----+---------------------------+---------------+-------+
|  # | Title                     | Artist        | Score |
+----+---------------------------+---------------+-------+
|  1 | The Thunder Rolls - Cover | All That Rem. |  0.84 |
|  2 | Boss                      | Lil Pump      |  0.79 |
|  3 | Let Me Hold You           | Bow Wow       |  0.71 |
|  4 | I Invented Sex            | Trey Songz    |  0.69 |
|  5 | Drippin'                  | Rich The Kid  |  0.67 |
+----+---------------------------+---------------+-------+
```

---

## Design Decisions

**Why Gemma 3 1B instead of a larger model?**
The professor recommended Gemma specifically. It runs on the Google AI Studio free tier at no cost and is fast enough for real-time use. The tradeoff is that Gemma 1B is a smaller model — it occasionally returns incorrect types for fields (e.g., a number where a string is expected). We added validation logic in `parse_user_input()` to catch and correct these cases.

**Why embed instructions in the prompt instead of using system instructions?**
Gemma 3 does not support the `system_instruction` parameter. All guidance is embedded directly in the prompt body, with an example JSON output to anchor the model's response format.

**Why a content-based scoring engine instead of collaborative filtering?**
Collaborative filtering requires listening history from many users. This system works from song attributes alone, making it explainable and runnable without any user data collection.

**Why drop genre (not lower its weight) during retries?**
When the top score is below 0.55, it usually means the requested genre has very few matching songs in the catalog. Dropping the genre constraint entirely opens the full catalog and consistently produces better results than gradually reducing the weight.

**Why 375 songs?**
The original 28-song catalog was too small for the agent's quality threshold to be meaningful — almost every query would force a retry. 375 songs (25 per genre, 15 genres) provides enough coverage that the scoring engine can find genuinely strong matches for most requests.

---

## Testing Summary

**Unit tests (`pytest`):** 11 tests covering the OOP interface, scoring formula weights, ranking order, k-limit enforcement, and agent quality checker logic — all pass.

**Reliability harness (`evaluate.py`):** 7 natural language inputs, each checked for at least one expected song in the top 5.

| Case | Input | Result |
|------|-------|--------|
| 1 | "chill and acoustic for late night studying" | PASS |
| 2 | "high energy pop music to hype me up" | PASS |
| 3 | "moody and atmospheric for a late night drive" | PASS |
| 4 | "nostalgic, something warm and acoustic" | PASS |
| 5 | "upbeat and euphoric, I want to dance" | PASS |
| 6 | "peaceful and classical, very calm and serene" | PASS |
| 7 | "aggressive and hard hitting hip-hop, high energy beats" | PASS |

**Final score: 7/7 (100%)**

**What worked:** The agent retry loop reliably recovers from low-scoring queries by dropping the genre constraint. Gemma's JSON output is consistent across runs for the same input. Validation guards catch and correct Gemma's occasional type errors before they reach the scoring engine.

**What didn't:** Gemma 1B defaults to `genre=pop` for ambiguous requests like "chill studying" or "moody night drive" — returning pop songs instead of jazz or rock. A larger model would parse genre intent more precisely.

**What I learned:** The quality threshold of 0.55 was critical — too low and the agent silently accepts weak results, too high and it retries unnecessarily. Calibrating the test harness also required running it first and observing real outputs, not guessing what the system should return.

---

## Reflection

Building BeatScouter taught me that AI integration is not just about calling a model — it's about designing the boundary between the model and the deterministic system around it. Gemma's role here is narrow and well-defined: convert text to a dict. Everything else (scoring, ranking, quality checking) is pure Python. That separation made the system reliable even when the model produced slightly wrong outputs, because the validation layer caught the errors before they reached the scoring engine.

The agentic loop was the most surprising part. A static recommender would silently return weak results with no indication anything was wrong. The agent makes the failure visible, attempts to fix it, and tells the user what it did. That transparency — the `[Agent]` step markers — changes how the system feels to use. It's not a black box; it's a system that reasons out loud.

---

## Video Walkthrough

> *Loom link: [Add your Loom link here before submission]*

The walkthrough demonstrates: 3 end-to-end runs with different inputs, the agent retry behavior, the reliability test harness output, and the AI explanation feature.

---

## Project Structure

```
├── src/
│   ├── main.py          # CLI runner + agent loop
│   ├── recommender.py   # Scoring engine + OOP interface
│   └── ai_layer.py      # Gemma integration (parse, check, explain)
├── data/
│   └── songs.csv        # 375 real Spotify songs (15 genres × 25 songs, sourced from Kaggle Ultimate Spotify Tracks DB)
├── tests/
│   └── test_recommender.py
├── evaluate.py          # 7-case reliability test harness
├── model_card.md        # Reflection and ethics
├── requirements.txt
└── .env                 # GEMINI_API_KEY (not committed)
```
