from src.recommender import Song, UserProfile, Recommender, score_song, recommend_songs
from src.ai_layer import check_quality


# ── Shared fixtures ────────────────────────────────────────────────────────────

def make_song(id, title, genre, mood, energy=0.5, valence=0.5, acousticness=0.5):
    return Song(
        id=id, title=title, artist="Test Artist",
        genre=genre, mood=mood, energy=energy,
        tempo_bpm=120, valence=valence, danceability=0.5,
        acousticness=acousticness,
    )

def song_to_dict(song, popularity=50):
    return {
        'id': song.id, 'title': song.title, 'artist': song.artist,
        'genre': song.genre, 'mood': song.mood, 'energy': song.energy,
        'tempo_bpm': song.tempo_bpm, 'valence': song.valence,
        'danceability': song.danceability, 'acousticness': song.acousticness,
        'popularity': popularity, 'release_decade': 2020, 'mood_tags': [],
    }

def make_small_recommender() -> Recommender:
    return Recommender([
        make_song(1, "Test Pop Track", "pop", "happy", energy=0.8, acousticness=0.2),
        make_song(2, "Chill Lofi Loop", "lofi", "chill", energy=0.4, acousticness=0.9),
    ])


# ── OOP interface tests ────────────────────────────────────────────────────────

def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop", favorite_mood="happy",
        target_energy=0.8, likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop", favorite_mood="happy",
        target_energy=0.8, likes_acoustic=False,
    )
    rec = make_small_recommender()
    explanation = rec.explain_recommendation(user, rec.songs[0])

    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ── Scoring engine tests ───────────────────────────────────────────────────────

def test_genre_match_adds_0_30():
    prefs = {'genre': 'pop', 'mood': 'chill', 'target_energy': 0.5,
             'target_valence': 0.5, 'target_acousticness': 0.5}
    song = song_to_dict(make_song(1, "A", "pop", "happy"))
    score, _ = score_song(prefs, song)

    song_wrong_genre = song_to_dict(make_song(2, "B", "jazz", "happy"))
    score_wrong, _ = score_song(prefs, song_wrong_genre)

    assert round(score - score_wrong, 2) == 0.30


def test_mood_match_adds_0_25():
    prefs = {'genre': 'jazz', 'mood': 'chill', 'target_energy': 0.5,
             'target_valence': 0.5, 'target_acousticness': 0.5}
    song_right = song_to_dict(make_song(1, "A", "jazz", "chill"))
    song_wrong  = song_to_dict(make_song(2, "B", "jazz", "intense"))

    score_right, _ = score_song(prefs, song_right)
    score_wrong, _ = score_song(prefs, song_wrong)

    assert round(score_right - score_wrong, 2) == 0.25


def test_three_songs_ranked_correctly():
    prefs = {'genre': 'pop', 'mood': 'happy', 'target_energy': 0.9,
             'target_valence': 0.5, 'target_acousticness': 0.5}
    perfect  = song_to_dict(make_song(1, "Perfect",  "pop",  "happy",  energy=0.9))
    partial  = song_to_dict(make_song(2, "Partial",  "pop",  "chill",  energy=0.9))
    weakest  = song_to_dict(make_song(3, "Weakest",  "jazz", "chill",  energy=0.1))

    results = recommend_songs(prefs, [weakest, perfect, partial], k=3)
    titles = [r[0]['title'] for r in results]

    assert titles[0] == "Perfect"
    assert titles[1] == "Partial"
    assert titles[2] == "Weakest"


def test_perfect_match_score_close_to_1():
    prefs = {'genre': 'pop', 'mood': 'happy', 'target_energy': 0.5,
             'target_valence': 0.5, 'target_acousticness': 0.5}
    song = song_to_dict(make_song(1, "A", "pop", "happy",
                                  energy=0.5, valence=0.5, acousticness=0.5),
                        popularity=100)
    score, _ = score_song(prefs, song)

    assert score >= 0.90


def test_recommend_returns_at_most_k_results():
    prefs = {'genre': 'pop', 'mood': 'happy', 'target_energy': 0.5,
             'target_valence': 0.5, 'target_acousticness': 0.5}
    songs = [song_to_dict(make_song(i, f"Song {i}", "pop", "happy")) for i in range(10)]

    assert len(recommend_songs(prefs, songs, k=3)) == 3
    assert len(recommend_songs(prefs, songs, k=10)) == 10


# ── Agent quality check tests ──────────────────────────────────────────────────

def _make_result(score, genre="pop"):
    song = {'title': 'T', 'artist': 'A', 'genre': genre, 'mood': 'happy',
            'energy': 0.5, 'valence': 0.5}
    return (song, score, "reasons")


def test_check_quality_accepts_strong_results():
    results = [_make_result(0.80), _make_result(0.70), _make_result(0.60),
               _make_result(0.50), _make_result(0.40)]
    quality = check_quality(results)

    assert quality["good"] is True


def test_check_quality_rejects_low_scores():
    results = [_make_result(0.40), _make_result(0.35), _make_result(0.30),
               _make_result(0.25), _make_result(0.20)]
    quality = check_quality(results)

    assert quality["good"] is False
    assert quality["adjustment"].get("_drop_genre") is True


def test_check_quality_rejects_same_genre_mediocre():
    results = [_make_result(0.65, "jazz"), _make_result(0.62, "jazz"),
               _make_result(0.60, "jazz"), _make_result(0.55), _make_result(0.50)]
    quality = check_quality(results)

    assert quality["good"] is False
    assert quality["adjustment"].get("_drop_genre") is True


def test_check_quality_empty_returns_not_good():
    quality = check_quality([])

    assert quality["good"] is False
