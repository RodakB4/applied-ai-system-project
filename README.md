# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

This project implements a simplified **content-based music recommender** focused on *vibe similarity*. Given a user profile — describing their preferred genre, mood, energy level, valence, and acoustic feel — the system scores every song in the catalog by how closely it matches those preferences. Songs are ranked from best to worst match, and the top K results are returned as recommendations. No listening history or other users are involved; the system works purely from song attributes and stated user taste.

---

### Song Features Used

Each `Song` in the catalog is described by the following attributes:

| Feature | Type | What It Captures |
|---|---|---|
| `genre` | categorical | The broad musical style (e.g., lo-fi, pop, rock, ambient) |
| `mood` | categorical | The emotional intent (e.g., chill, happy, intense, focused) |
| `energy` | float (0–1) | How high-energy or low-key the track feels |
| `valence` | float (0–1) | Musical positivity — low = dark/melancholic, high = bright/uplifting |
| `acousticness` | float (0–1) | How organic/acoustic vs. electronic/produced the track sounds |
| `tempo_bpm` | float (BPM) | The speed of the track in beats per minute |
| `danceability` | float (0–1) | How suitable the track is for dancing |

### User Profile Features Used

Each `UserProfile` stores the user's preferences that the recommender scores against:

| Field | Type | What It Represents |
|---|---|---|
| `favorite_genre` | string | The genre the user most wants to hear |
| `favorite_mood` | string | The mood the user is looking for |
| `target_energy` | float (0–1) | The energy level the user wants in a song |
| `target_valence` | float (0–1) | The emotional tone the user is looking for |
| `likes_acoustic` | bool | Whether the user prefers acoustic over electronic sound |

---

### Algorithm Recipe

Each song receives a score between 0.0 and 1.0 calculated as a weighted sum of five components:

| Component | Formula | Max Points |
|---|---|---|
| Genre match | `1.0 if song.genre == favorite_genre else 0.0` | 0.30 |
| Mood match | `1.0 if song.mood == favorite_mood else 0.0` | 0.25 |
| Energy similarity | `0.20 × (1 − \|song.energy − target_energy\|)` | 0.20 |
| Valence similarity | `0.15 × (1 − \|song.valence − target_valence\|)` | 0.15 |
| Acousticness similarity | `0.10 × (1 − \|song.acousticness − target_acousticness\|)` | 0.10 |

**Final score:**

```
score = genre_score + mood_score + energy_score + valence_score + acousticness_score
```

After scoring all songs, they are sorted in descending order and the top K are returned as recommendations.

---

### Potential Biases & Limitations

- **Genre over-prioritization.** Genre carries 30% of the total score. A song from a different genre with an otherwise near-perfect vibe match will always be outranked by a same-genre song, even if the same-genre song sounds worse to the listener.
- **Cross-genre misses.** A chill ambient track and a chill lo-fi track may feel identical to a listener, but the system treats them as different because the genre label doesn't match. Good recommendations can be filtered out this way.
- **Small dataset.** The catalog contains only 20 songs. With so few options, the system may return weak matches simply because nothing better exists — a limitation that would not exist at real-world scale.
- **No learning from behavior.** The system never updates based on what the user skips, replays, or saves. Every session starts fresh from the same static profile, so it cannot improve or adapt over time.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

