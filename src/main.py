"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from tabulate import tabulate
from src.recommender import load_songs, recommend_songs


def print_recommendations(recommendations: list) -> None:
    """Prints the top recommended songs as a formatted table."""
    print("\n" + "=" * 75)
    print("  Top Music Recommendations")
    print("=" * 75 + "\n")

    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        reasons = "\n".join(f"  {r}" for r in explanation.split(" | "))
        rows.append([rank, song['title'], song['artist'], f"{score:.2f}", reasons])

    print(tabulate(
        rows,
        headers=["#", "Title", "Artist", "Score", "Reasons"],
        tablefmt="outline",
        colalign=("center", "left", "left", "center", "left"),
    ))

    print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "target_energy": 0.80,
        "target_valence": 0.75,
        "target_acousticness": 0.15,
        "target_decade": 2020,
        "target_mood_tags": ["happy", "uplifting"],
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)
    print_recommendations(recommendations)


if __name__ == "__main__":
    main()
