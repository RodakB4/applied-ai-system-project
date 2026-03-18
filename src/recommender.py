from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file and returns them as a list of dictionaries.
    """
    import csv

    songs = []

    with open(csv_path, newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            song = {
                'id':             int(row['id']),
                'title':          row['title'],
                'artist':         row['artist'],
                'genre':          row['genre'],
                'mood':           row['mood'],
                'energy':         float(row['energy']),
                'tempo_bpm':      float(row['tempo_bpm']),
                'valence':        float(row['valence']),
                'danceability':   float(row['danceability']),
                'acousticness':   float(row['acousticness']),
                'popularity':     int(row['popularity']),
                'release_decade': int(row['release_decade']),
                'mood_tags':      row['mood_tags'].split('|'),
            }
            songs.append(song)

    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Compute a weighted score and explanation for a song based on user preferences.
    """
    score = 0.0
    reasons = []

    # --- Categorical features (binary match) ---

    if song['genre'] == user_prefs['genre']:
        score += 0.30
        reasons.append("genre match (+0.30)")
    else:
        reasons.append(f"genre no match ({song['genre']} != {user_prefs['genre']}) (+0.00)")

    if song['mood'] == user_prefs['mood']:
        score += 0.25
        reasons.append("mood match (+0.25)")
    else:
        reasons.append(f"mood no match ({song['mood']} != {user_prefs['mood']}) (+0.00)")

    # --- Numeric features (proximity: reward closeness to target) ---

    energy_score = 0.20 * (1 - abs(song['energy'] - user_prefs['target_energy']))
    score += energy_score
    reasons.append(f"energy close (+{energy_score:.2f})")

    valence_score = 0.15 * (1 - abs(song['valence'] - user_prefs['target_valence']))
    score += valence_score
    reasons.append(f"valence close (+{valence_score:.2f})")

    acousticness_score = 0.10 * (1 - abs(song['acousticness'] - user_prefs['target_acousticness']))
    score += acousticness_score
    reasons.append(f"acousticness close (+{acousticness_score:.2f})")

    # --- Popularity: higher popularity = higher bonus, max +0.10 ---

    popularity_score = 0.10 * (song['popularity'] / 100)
    score += popularity_score
    reasons.append(f"popularity {song['popularity']}/100 (+{popularity_score:.2f})")

    # --- Release decade: proximity within 20 years, max +0.05 ---

    if 'target_decade' in user_prefs:
        decade_diff = abs(song['release_decade'] - user_prefs['target_decade'])
        decade_proximity = max(0.0, 1 - decade_diff / 20)
        decade_score = 0.05 * decade_proximity
        score += decade_score
        reasons.append(f"decade {song['release_decade']} (+{decade_score:.2f})")

    # --- Mood tags: partial credit for each matching tag, max +0.10 ---

    if user_prefs.get('target_mood_tags'):
        user_tags = set(user_prefs['target_mood_tags'])
        song_tags = set(song['mood_tags'])
        matches = len(user_tags & song_tags)
        tag_score = 0.10 * (matches / len(user_tags))
        score += tag_score
        reasons.append(f"mood tags {matches}/{len(user_tags)} match (+{tag_score:.2f})")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Rank songs by score and return the top k recommendations with reasons."""
    # Step 1: Score every song
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = " | ".join(reasons)
        scored.append((song, score, explanation))

    # Step 2: Sort by score, highest first
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)

    # Step 3: Return the top k results
    return ranked[:k]
