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
    Required by src/main.py

    Each dictionary looks like:
    {
        'id': 1,
        'title': 'Sunrise City',
        'artist': 'Neon Echo',
        'genre': 'pop',
        'mood': 'happy',
        'energy': 0.82,
        'tempo_bpm': 118.0,
        'valence': 0.84,
        'danceability': 0.79,
        'acousticness': 0.18
    }
    """
    import csv

    songs = []

    with open(csv_path, newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            song = {
                'id':           int(row['id']),
                'title':        row['title'],
                'artist':       row['artist'],
                'genre':        row['genre'],
                'mood':         row['mood'],
                'energy':       float(row['energy']),
                'tempo_bpm':    float(row['tempo_bpm']),
                'valence':      float(row['valence']),
                'danceability': float(row['danceability']),
                'acousticness': float(row['acousticness']),
            }
            songs.append(song)

    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against a user's preferences.

    Returns:
        score   - a float between 0.0 and 1.0
        reasons - a list of strings explaining each component of the score

    user_prefs keys: genre, mood, target_energy, target_valence, target_acousticness
    song keys:       genre, mood, energy, valence, acousticness (plus others)
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

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Scores all songs, ranks them, and returns the top k matches.
    Required by src/main.py

    Returns a list of tuples: (song_dict, score, explanation_string)
    """
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
