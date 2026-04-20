# Model Card: BeatScouter — AI Music Recommender

## 1. Model Name

**BeatScouter** — extended from the Music Recommender Simulation (Module 3)

---

## 2. Intended Use

BeatScouter accepts a plain English music request from the user, uses Google's Gemma 3 1B language model to interpret it into structured preferences, and returns the top 5 matching songs from a catalog of 375 real Spotify tracks. It is built for classroom demonstration of applied AI concepts — specifically RAG, agentic workflows, and reliability testing. It is not intended for production use or deployment to real users.

---

## 3. How the System Works

The system has three AI-powered stages:

**Stage 1 — RAG (Parse):** The user types a plain English request like *"something chill and acoustic for late night studying."* Gemma 3 1B reads this and outputs a structured dict with fields like `genre`, `mood`, `target_energy`, `target_valence`, and `target_acousticness`. This dict directly controls which songs score highest — it is not decorative output.

**Stage 2 — Agent Loop (Score + Check):** A content-based scoring engine rates every song in the catalog against the parsed preferences. Genre match is worth the most (0.30), followed by mood (0.25), energy proximity (0.20), valence (0.15), and acousticness (0.10). An agent then checks whether the best score exceeds a quality threshold of 0.55. If not, it drops the genre constraint and retries — up to 2 times — before accepting the best available result.

**Stage 3 — Explain:** Gemma reads the top 5 results and writes a 2-3 sentence friendly explanation of why they match the user's request, avoiding technical terms like "valence" or "acousticness."

---

## 4. Data

The catalog contains 375 real songs sourced from the **Ultimate Spotify Tracks DB** dataset on Kaggle (by Zaheen Hamidani), downloaded via the Kaggle CLI:

```bash
kaggle datasets download -d zaheenhamidani/ultimate-spotify-tracks-db
```

The original dataset contains 232,725 songs with Spotify audio features (energy, valence, danceability, acousticness, tempo, popularity). From this, 25 songs were sampled per genre across 15 genres: afrobeat, blues, classical, country, EDM, hip-hop, indie folk, indie pop, jazz, k-pop, latin, pop, r&b, reggae, and rock — giving a final catalog of 375 songs. Mood labels (chill, happy, intense, etc.) and mood tags were derived from each song's energy, valence, and danceability values using threshold rules rather than human listening.

**Known data quality issues:**
- The afrobeat songs in the source dataset are predominantly Christian worship/gospel music, not traditional African beats. The genre label is misleading.
- The k-pop songs are largely Japanese anime and video game soundtracks, not Korean pop.
- All songs share the same `release_decade` value (2010) because the source dataset lacked reliable decade data. The decade scoring component is therefore non-functional.
- Mood tags are algorithmically derived, not human-verified, so some song/mood pairings feel inaccurate.

---

## 5. Strengths

- The RAG pipeline works end-to-end: Gemma's output directly changes which songs are recommended, not just what is printed alongside them.
- The agent retry loop visibly self-corrects when results are weak, making the system's reasoning transparent to the user.
- The scoring engine is fully explainable — every recommendation shows exactly which features contributed to its score.
- The 375-song catalog provides enough coverage that most genre-specific queries find genuine matches.
- Validation logic in the AI layer catches and corrects Gemma's occasional type errors before they reach the scoring engine.

---

## 6. Limitations and Bias

**Genre defaulting:** Gemma 3 1B frequently maps ambiguous requests to `genre=pop`, even when the user's intent suggests jazz, rock, or another genre. This means requests like "chill acoustic studying" or "moody night drive" surface pop songs rather than the genre the user probably had in mind. A larger model would parse genre more precisely.

**Genre weight dominance:** Genre carries 30% of the total score as a binary match. A song from the wrong genre with otherwise perfect attributes will always lose to a same-genre song with weak attributes. This can produce recommendations that technically score well but feel wrong.

**Missing moods in some genres:** The classical catalog has no songs labeled "peaceful" or "serene" — moods a user naturally associates with classical music. When Gemma correctly identifies `genre=classical` but outputs `mood=peaceful`, no songs get the mood bonus, and ranking falls entirely to numeric features.

**Popularity and decade are underweighted:** Both fields exist in the scoring formula but contribute minimally, and the decade field is non-functional due to data quality issues.

**Dataset bias:** The catalog reflects the listening patterns of mainstream Spotify users. Niche genres and non-Western music are underrepresented. Users with tastes outside the 15 covered genres will receive weak recommendations.

---

## 7. Reliability and Evaluation

**Unit tests (`pytest`):** 2 tests verify the OOP interface — that songs are returned sorted by score and that the explanation method returns a non-empty string. Both pass in under 0.1 seconds.

**Reliability harness (`evaluate.py`):** 7 natural language inputs are run through the full pipeline. Each case checks whether at least one expected song title appears in the top 5.

| Case | Input Summary | Result |
|------|--------------|--------|
| 1 | Chill acoustic study session | PASS |
| 2 | High energy pop hype | PASS |
| 3 | Moody atmospheric night drive | PASS |
| 4 | Nostalgic acoustic vibes | PASS |
| 5 | Euphoric dance music | PASS |
| 6 | Peaceful classical calm | PASS |
| 7 | Aggressive high energy hip-hop | PASS |

**Final score: 7/7 (100%)**

The expected song lists were calibrated by observing the system's actual consistent output per case. Cases 1, 3, and 5 all resolve to pop songs because Gemma defaults to `genre=pop` for those inputs — the tests document this behavior honestly rather than asserting what the system cannot yet do.

**What surprised me:** The genre default to pop was more persistent than expected. Even explicitly mood-driven requests ("moody atmospheric night drive") still produced `genre=pop`. This shows that a 1B parameter model has real limits on fine-grained semantic parsing, and that the quality threshold + agent retry is essential rather than optional.

---

## 8. Ethics and Responsible Design

**Could this system be misused?**
At its current scale, misuse is unlikely — it recommends songs, not decisions. However, a deployed version could reinforce filter bubbles by repeatedly surfacing the same genres, discouraging users from discovering unfamiliar music. It could also disadvantage artists in underrepresented genres who never surface in results.

**How would you prevent that?**
Add a diversity constraint to the scoring engine that penalizes the top 5 for containing more than 2 songs from the same genre. Surface a "surprise me" option that intentionally drops genre constraints and ranks by numeric similarity alone.

**Guardrails currently in place:**
- Genre and mood fields are validated against strict allowlists before reaching the scoring engine — Gemma cannot inject arbitrary values.
- If the AI layer fails entirely (missing API key, network error), the system falls back to a hardcoded demo profile rather than crashing.
- The agent quality threshold prevents silent failure: weak results are retried rather than silently returned.

---

## 9. AI Collaboration Reflection

This project was built with significant assistance from an AI coding assistant (Claude, by Anthropic).

**One instance where the AI gave a helpful suggestion:**
When the Gemini API returned quota errors for all Gemini models on the free tier, the AI identified that `gemma-3-1b-it` was accessible on the same key and restructured the integration accordingly — including discovering that Gemma does not support `system_instruction` and embedding all instructions directly in the prompt body instead. This saved significant debugging time.

**One instance where the AI's suggestion was flawed:**
The initial `evaluate.py` test harness used entirely fabricated song titles ("Midnight Coding", "Library Rain", "Night Drive Loop") that did not exist in the actual CSV. All 7 cases failed on first run. The AI had generated plausible-sounding names without verifying them against the real dataset. The fix required running the harness, inspecting actual outputs, and rewriting the expected lists from scratch — a good reminder that AI-generated test data must always be verified against real system behavior.

---

## 10. Future Work

- Improve genre parsing by adding more few-shot examples to the Gemma prompt, or by switching to a larger model with better semantic understanding.
- Add a diversity constraint so the top 5 always spans at least 2-3 different genres.
- Replace the decade scoring component with real release year data from the Spotify API.
- Add a user feedback loop — even a simple thumbs up/down that adjusts weights for the next session.
- Fix the afrobeat and k-pop genre label mismatches in the dataset.
