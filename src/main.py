"""
Command line runner for the Music Recommender Simulation.

Run with:  python -m src.main

Two modes:
  - Type a natural language request → Gemma parses it, recommender scores, Gemma explains
  - Press Enter with no input       → runs the built-in demo profile
"""

import sys
import io

# Ensure UTF-8 output on Windows so model responses with emoji don't crash
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from tabulate import tabulate
from src.recommender import load_songs, recommend_songs
from src.ai_layer import parse_user_input, explain_results, check_quality

_DEMO_PREFS = {
    "genre": "pop",
    "mood": "happy",
    "target_energy": 0.80,
    "target_valence": 0.75,
    "target_acousticness": 0.15,
    "target_decade": 2020,
    "target_mood_tags": ["happy", "uplifting"],
}


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

    print("\n" + "=" * 75)
    print("  BeatScouter — AI Music Recommender")
    print("=" * 75)
    print("  Describe the music you want, or press Enter for demo mode.")
    print("-" * 75)

    user_input = input("  Your request: ").strip()

    if user_input:
        print("\n  [Agent] Parsing your request...")
        try:
            user_prefs = parse_user_input(user_input)
        except EnvironmentError as e:
            print(f"\n  [Error] {e}")
            print("  Falling back to demo mode.\n")
            user_prefs = _DEMO_PREFS
            user_input = None

        if user_input:
            print(f"  [Agent] Parsed: genre={user_prefs.get('genre')}, "
                  f"mood={user_prefs.get('mood')}, "
                  f"energy={user_prefs.get('target_energy')}, "
                  f"acousticness={user_prefs.get('target_acousticness')}")

            # --- Agent loop: run → check quality → retry if needed ---
            MAX_RETRIES = 2
            for attempt in range(1, MAX_RETRIES + 2):
                print(f"\n  [Agent] Running recommender (attempt {attempt})...")
                recommendations = recommend_songs(user_prefs, songs, k=5)

                quality = check_quality(recommendations)
                print(f"  [Agent] Quality check: {quality['reason']}")

                if quality["good"]:
                    print(f"  [Agent] Results accepted.\n")
                    break

                if attempt <= MAX_RETRIES:
                    adjustment = quality["adjustment"]
                    if adjustment.get("_drop_genre"):
                        print(f"  [Agent] Dropping genre constraint — searching all genres...")
                        user_prefs = {k: v for k, v in user_prefs.items() if k != "genre"}
                    else:
                        user_prefs.update(adjustment)
                else:
                    print(f"  [Agent] Max retries reached — using best results available.\n")

            print_recommendations(recommendations)

            print("  [Agent] Generating explanation...")
            print("-" * 75)
            explanation = explain_results(user_input, recommendations)
            print(f"\n  {explanation}\n")
    else:
        print("\n  Running demo mode (pop/happy profile)...\n")
        recommendations = recommend_songs(_DEMO_PREFS, songs, k=5)
        print_recommendations(recommendations)


if __name__ == "__main__":
    main()
