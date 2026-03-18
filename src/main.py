"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def print_recommendations(recommendations: list) -> None:
    """Prints the top recommended songs in a clean, readable CLI format."""
    print("\n" + "=" * 45)
    print("  🎵  Top Music Recommendations")
    print("=" * 45 + "\n")

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} — {song['artist']}")
        print(f"   Score: {score:.2f}")
        print(f"   Reasons:")
        for reason in explanation.split(" | "):
            print(f"     • {reason}")
        print()

    print("=" * 45)


def main() -> None:
    songs = load_songs("data/songs.csv")

    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "target_energy": 0.80,
        "target_valence": 0.75,
        "target_acousticness": 0.15,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)
    print_recommendations(recommendations)


if __name__ == "__main__":
    main()
