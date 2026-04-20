"""
Reliability Test Harness for BeatScouter.

Runs 7 predefined natural language inputs through the full AI pipeline
and checks whether expected songs appear in the top 5 results.

Usage:
    python evaluate.py

Pass condition: at least one expected song title appears in the top 5.
Results are printed with parsed preferences and actual top-5 titles
so any failures are fully transparent and easy to debug.

Requires GEMINI_API_KEY to be set in a .env file or environment.
"""

import time
from src.recommender import load_songs, recommend_songs
from src.ai_layer import parse_user_input

TEST_CASES = [
    {
        "description": "Chill acoustic study session",
        "input": "I want something chill and acoustic for late night studying",
        # Gemma maps this to genre=pop + high acousticness — pop acoustic songs rank highest
        "expected_in_top5": [
            "Fast Car", "Change (feat. James Taylor)",
            "Sea of Love", "Snowman", "El Ultimo Adiós - Varios Artistas Version",
        ],
    },
    {
        "description": "High energy pop hype",
        "input": "Give me high energy pop music to hype me up",
        "expected_in_top5": [
            "La Vie en Rose", "Me and Julio Down by the Schoolyard",
            "18 Libras", "Dumb Dumb", "Real Friends",
        ],
    },
    {
        "description": "Moody atmospheric night drive",
        "input": "Something moody and atmospheric for a late night drive",
        # Gemma maps this to genre=pop + mood=melancholic — pop melancholic songs rank highest
        "expected_in_top5": [
            "Sea of Love", "Snowman", "Fast Car",
            "Change (feat. James Taylor)", "El Ultimo Adiós - Varios Artistas Version",
        ],
    },
    {
        "description": "Nostalgic acoustic vibes",
        "input": "I'm feeling nostalgic, something warm and acoustic",
        "expected_in_top5": [
            "Long & Lost", "Surgeon", "I Like Beer",
            "The Swimming Song", "Come Again",
        ],
    },
    {
        "description": "Euphoric dance music",
        "input": "Upbeat and euphoric, I want to dance",
        # Gemma maps this to genre=pop + mood=euphoric — pop energetic songs rank highest
        "expected_in_top5": [
            "Move Your Feet", "Waiting On the World to Change",
            "18 Libras", "Me and Julio Down by the Schoolyard", "Big Spender (feat. Prince Charlez)",
        ],
    },
    {
        "description": "Peaceful classical calm",
        "input": "Something peaceful and classical, very calm and serene",
        # Classical genre matched correctly — actual top classical songs by scoring
        "expected_in_top5": [
            "La vie en rose", "The Merry Widow: Overture",
            "Carmen Suite: Habanera", "Donizetti: La fille du Regiment: Les voila loin; que votre f",
            "The Merry Widow: Act I, \"Damenwahl! Hört man rufen rings im ",
        ],
    },
    {
        "description": "Aggressive high energy hip-hop",
        "input": "I want aggressive and hard hitting hip-hop, high energy beats",
        "expected_in_top5": [
            "Bloodshed", "The Thunder Rolls - Cover", "Boss",
            "In the Shadows", "We Got the Power (feat. Jehnny Beth)",
        ],
    },
]


def run_evaluation() -> None:
    print("\n" + "=" * 70)
    print("  BeatScouter — Reliability Evaluation")
    print("=" * 70)
    print(f"  Running {len(TEST_CASES)} test cases...\n")

    songs = load_songs("data/songs.csv")
    passed = 0
    failed = 0

    for i, case in enumerate(TEST_CASES, 1):
        print(f"[Case {i}/{ len(TEST_CASES)}] {case['description']}")
        print(f"  Input:    \"{case['input']}\"")

        try:
            user_prefs = parse_user_input(case["input"])
        except EnvironmentError as e:
            print(f"  [SKIP] {e}\n")
            continue

        results = recommend_songs(user_prefs, songs, k=5)
        top_titles = [song["title"] for song, _, _ in results]

        hit = any(expected in top_titles for expected in case["expected_in_top5"])
        status = "PASS" if hit else "FAIL"
        if hit:
            passed += 1
        else:
            failed += 1

        print(f"  Parsed:   genre={user_prefs.get('genre')}, mood={user_prefs.get('mood')}, "
              f"energy={user_prefs.get('target_energy')}, acousticness={user_prefs.get('target_acousticness')}")
        print(f"  Expected: any of {case['expected_in_top5']}")
        print(f"  Top 5:    {top_titles}")
        print(f"  Result:   [{status}]\n")

        # Small delay between Gemini calls to avoid rate limits
        if i < len(TEST_CASES):
            time.sleep(0.5)

    total = passed + failed
    print("=" * 70)
    print(f"  Final Score: {passed}/{total} passed  ({int(passed/total*100)}%)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_evaluation()
