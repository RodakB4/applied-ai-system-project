"""
AI layer for the Music Recommender.

Uses Google's Gemma 3 1B (via Google AI Studio API) to:
  - parse_user_input: convert plain English into a structured user_prefs dict
  - explain_results: generate a friendly natural language summary of recommendations

Note: Gemma does not support system instructions, so all instructions
are embedded directly in the prompt.
"""

import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

_VALID_GENRES = [
    "pop", "lofi", "rock", "ambient", "jazz", "synthwave", "indie pop",
    "afrobeat", "classical", "drill", "k-pop", "latin", "reggae", "gospel",
    "bossa nova", "metal", "r&b", "hip-hop", "edm", "country", "funk",
    "indie folk", "trap", "blues",
]

_VALID_MOODS = [
    "happy", "chill", "intense", "focused", "relaxed", "moody", "euphoric",
    "peaceful", "energetic", "nostalgic", "aggressive", "romantic", "joyful",
    "melancholic", "festive", "uplifting",
]

_NEUTRAL_PREFS = {
    "genre": "pop",
    "mood": "chill",
    "target_energy": 0.5,
    "target_valence": 0.5,
    "target_acousticness": 0.5,
}


def _get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY not set. Add it to a .env file:\n"
            "  GEMINI_API_KEY=your-key-here\n"
            "Get a free key at: https://aistudio.google.com"
        )
    return genai.Client(api_key=api_key)


def parse_user_input(natural_language: str) -> dict:
    """Convert a plain English music request into a user_prefs dict for the scoring engine."""
    client = _get_client()

    prompt = f"""You are a music preference parser. Read the user's request and return ONLY a JSON object.
No explanation. No markdown fences. Just the raw JSON.

Rules:
- "genre" must be a string chosen from: {", ".join(_VALID_GENRES)}. Pick the closest match. Default: "pop".
- "mood" must be a string chosen from: {", ".join(_VALID_MOODS)}. Pick the closest match. Default: "chill".
- "target_energy" must be a number between 0.0 (very calm) and 1.0 (very intense).
- "target_valence" must be a number between 0.0 (dark/sad) and 1.0 (bright/happy).
- "target_acousticness" must be a number between 0.0 (electronic) and 1.0 (acoustic).

Example output:
{{"genre": "lofi", "mood": "chill", "target_energy": 0.35, "target_valence": 0.6, "target_acousticness": 0.8}}

User request: {natural_language}

JSON:"""

    response = client.models.generate_content(
        model="gemma-3-1b-it",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=150,
            temperature=0.1,
        ),
    )

    raw = response.text.strip()

    # Strip markdown fences if model wraps the JSON anyway
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                raw = part
                break

    # Extract just the JSON object if there's extra text
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    try:
        prefs = json.loads(raw)
        # Validate and correct types — Gemma 1B sometimes returns numbers for string fields
        if not isinstance(prefs.get("genre"), str) or prefs["genre"] not in _VALID_GENRES:
            prefs["genre"] = _NEUTRAL_PREFS["genre"]
        if not isinstance(prefs.get("mood"), str) or prefs["mood"] not in _VALID_MOODS:
            prefs["mood"] = _NEUTRAL_PREFS["mood"]
        for key in ("target_energy", "target_valence", "target_acousticness"):
            if not isinstance(prefs.get(key), (int, float)):
                prefs[key] = _NEUTRAL_PREFS[key]
            else:
                prefs[key] = max(0.0, min(1.0, float(prefs[key])))
    except json.JSONDecodeError:
        print("[ai_layer] Warning: could not parse model response. Using neutral defaults.")
        prefs = _NEUTRAL_PREFS.copy()

    return prefs


def check_quality(recommendations: list) -> dict:
    """
    Agent quality check — inspects top results and decides whether to retry.
    Returns a dict with:
      - "good": bool — whether results are acceptable
      - "reason": str — why the agent made this decision
      - "adjustment": dict — preference changes to try if not good (empty if good)
    """
    if not recommendations:
        return {"good": False, "reason": "no results returned", "adjustment": {"genre": "pop"}}

    top_score = recommendations[0][1]
    top_song = recommendations[0][0]

    # Check 1: top score too low — genre likely has no strong matches
    if top_score < 0.55:
        return {
            "good": False,
            "reason": f"best score {top_score:.2f} is too low — genre may be too narrow",
            "adjustment": {"_drop_genre": True},
        }

    # Check 2: top songs all same genre but user may want variety
    genres_in_top = [s["genre"] for s, _, _ in recommendations[:3]]
    if len(set(genres_in_top)) == 1 and top_score < 0.70:
        return {
            "good": False,
            "reason": f"all top results are '{genres_in_top[0]}' with mediocre scores — broadening search",
            "adjustment": {"_drop_genre": True},
        }

    return {"good": True, "reason": f"best score {top_score:.2f} — strong match found", "adjustment": {}}


def explain_results(user_input: str, recommendations: list) -> str:
    """Generate a friendly natural language explanation of the top recommendations."""
    client = _get_client()

    song_lines = "\n".join(
        f'  - "{song["title"]}" by {song["artist"]} ({song["genre"]}, {song["mood"]})'
        for song, _, _ in recommendations
    )

    prompt = f"""You are a friendly music concierge. Write 2-3 warm, enthusiastic sentences explaining
why the songs below are a great match for what the user asked for. Be conversational and specific
to the song titles. Do not mention technical terms like valence, acousticness, or scoring.

User asked for: "{user_input}"

Top recommended songs:
{song_lines}

Your explanation:"""

    response = client.models.generate_content(
        model="gemma-3-1b-it",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=200,
            temperature=0.7,
        ),
    )

    return response.text.strip()
