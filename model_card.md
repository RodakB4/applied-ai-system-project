# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

BeatScouter

---

## 2. Intended Use

This system recommends the top K songs from a small catalog by scoring each song against a user's stated preferences for genre, mood, energy, valence, and acousticness. It is built for classroom exploration only and assumes the user can fully describe their taste upfront. It does not learn from behavior or adapt over time.

---

## 3. How the Model Works

The system takes a user profile that describes what kind of music they are in the mood for, things like their favorite genre, how energetic they want the song to feel, and whether they prefer acoustic or electronic sounds. It then goes through every song in the catalog and gives each one a score based on how well it matches that profile. Genre and mood are worth the most points since they are the biggest indicators of whether a song fits. The numeric features like energy and valence are scored by how close the song's value is to what the user wants, so a song that is right on target gets full points and one that is way off gets close to zero. All the individual scores get added up into one final number and the top results are returned as recommendations.

---

## 4. Data

The catalog has 20 songs covering a wide range of genres including lofi, pop, rock, metal, jazz, classical, afrobeat, k-pop, reggae, bossa nova, drill, latin, gospel, ambient, synthwave, and indie pop. Moods range from chill and happy to intense, melancholic, nostalgic, and aggressive. I added 10 songs to the original 10 to increase genre diversity. The dataset is still very small and reflects a pretty specific taste range. There is nothing from country, R&B, hip hop, or EDM, and most genres only have one song which limits how useful the recommendations can be for users outside the lofi or pop range.

---

## 5. Strengths

The system works best when the user's preferred genre has more than one song in the catalog, like lofi or pop, because it can actually rank within the genre using numeric features. The score explanation for each song is readable and makes it easy to see exactly why a song ranked where it did. For straightforward profiles like a chill lofi listener or an upbeat pop fan, the top results feel natural and match what you would expect. The system also handled weird edge cases like missing genres and extreme numeric targets without breaking.

---

## 6. Limitations and Bias

Genre carries 30% of the total score as a binary match, which means a song from the wrong genre gets a 0.30 penalty right away even if it sounds exactly like what the user wants. Most genres in the dataset only have one song, so users with niche taste basically get one real recommendation and then filler. Mood and valence both measure similar things so they can double reward the same quality when they agree, and when they conflict the mood label always wins. The numeric formula treats being too high and too low as equally bad, which does not always match how listeners actually feel about a song being a little too calm versus way too intense. Users who want very extreme energy or very acoustic sounds end up with lower scores across the board because the math runs out of room at the edges.

---

## 7. Evaluation

I tested the system with nine stress profiles including a genre that was not in the catalog at all, all numeric targets set to 0.50, and profiles with contradictions like a metal fan who wanted near zero energy. For each profile I looked at whether the top result made sense and whether the score breakdown matched the ranking. The most surprising result was that genre and mood together were strong enough to push a high energy metal song to the top for a user who specifically wanted calm music, just because the labels matched. Numeric features worked well for ranking songs within the same genre. The system returned results without errors for all nine profiles including ones with float values at 0.001 and 0.999.

---

## 8. Future Work

The biggest improvement would be lowering the genre weight and adding fallback genres so the system can recommend cross genre songs that match the vibe instead of just the label. Adding a target valence field to the user profile would also help since right now valence is tracked for songs but not explicitly asked of the user. It would be interesting to add a diversity check so the top five results do not all come from the same genre. Longer term, adding even a basic feedback loop where skips or replays adjust the weights over time would make it feel much more like a real recommender.

---

## 9. Personal Reflection

Building this made me realize how much of a recommendation is just math on top of labels. I assumed the numeric features like energy and valence would do most of the work but they ended up being pretty weak compared to genre and mood. The stress tests were the most useful part because they showed cases where the system was technically working but giving answers that felt wrong, like recommending a loud metal song to someone who wanted something quiet. It made me think differently about apps like Spotify because there is clearly a lot more going on under the hood than matching a genre label. Even a simple system like this has real tradeoffs that would affect real users if it were deployed.
