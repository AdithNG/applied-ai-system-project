"""
AI Explainer: uses the Anthropic Claude API to generate rich, context-aware
explanations for music recommendations.

Integrates RAG context (retrieved from the knowledge base) with song attributes
and user preferences to produce explanations that are far more informative than
the rule-based "genre match (+2.0)" output from the original system.

Uses prompt caching on the system prompt to reduce latency and cost across
multiple explanation calls in the same session.
"""

import os
from typing import Dict, List, Any, Optional

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"

_client: Optional[anthropic.Anthropic] = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY is not set. "
                "Create a .env file with ANTHROPIC_API_KEY=your_key"
            )
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


_SYSTEM_PROMPT = """You are a music recommendation assistant with deep knowledge of music theory, genres, and listener psychology. Your job is to explain why a specific song is a good match for a listener's preferences.

You are given:
1. The listener's preferences (genre, mood, energy level)
2. A song's attributes (title, artist, genre, mood, energy, and other audio features)
3. Relevant context retrieved from a music knowledge base

Write a concise explanation (2-3 sentences) that:
- Explains specifically why this song fits the listener's preferences
- References at least one concrete audio attribute (energy, tempo, valence, danceability, etc.)
- Uses natural, engaging language — not dry statistics
- Acknowledges any meaningful mismatches honestly

Do not repeat the song title or artist name in the explanation (they will be shown separately).
Do not use bullet points — write in flowing prose."""


def generate_explanation(
    song: Dict[str, Any],
    user_prefs: Dict[str, Any],
    context_passages: List[str],
) -> str:
    """Generate a natural language explanation for why a song was recommended.

    Args:
        song: Song dict with title, artist, genre, mood, energy, and other attributes.
        user_prefs: User preference dict with genre, mood, energy.
        context_passages: Relevant passages retrieved from the knowledge base.

    Returns:
        A 2-3 sentence explanation string.
    """
    client = _get_client()

    context_text = "\n\n".join(context_passages) if context_passages else "No additional context available."

    user_message = f"""Listener preferences:
- Favorite genre: {user_prefs.get('genre', 'unknown')}
- Favorite mood: {user_prefs.get('mood', 'unknown')}
- Target energy: {user_prefs.get('energy', 0.5):.2f} (scale 0.0–1.0)

Song attributes:
- Genre: {song.get('genre', 'unknown')}
- Mood: {song.get('mood', 'unknown')}
- Energy: {song.get('energy', 0.5):.2f}
- Tempo: {song.get('tempo_bpm', '?')} BPM
- Valence (positivity): {song.get('valence', '?')}
- Danceability: {song.get('danceability', '?')}
- Acousticness: {song.get('acousticness', '?')}
- Detailed mood: {song.get('detailed_mood', 'not specified')}
- Release decade: {song.get('release_decade', 'unknown')}

Relevant music knowledge base context:
{context_text}

Write a 2-3 sentence explanation of why this song is a good match for this listener."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=[
            {
                "type": "text",
                "text": _SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text.strip()


def generate_profile_summary(
    user_prefs: Dict[str, Any],
    top_songs: List[Dict[str, Any]],
    context_passages: List[str],
) -> str:
    """Generate a one-paragraph summary of what this listener is looking for
    and why the recommended songs collectively match their taste.

    Args:
        user_prefs: User preference dict.
        top_songs: List of top recommended song dicts.
        context_passages: Relevant knowledge base passages.

    Returns:
        A short summary paragraph (3-4 sentences).
    """
    client = _get_client()

    context_text = "\n\n".join(context_passages[:2]) if context_passages else ""
    song_list = ", ".join(
        f"{s.get('title')} by {s.get('artist')} ({s.get('genre')})"
        for s in top_songs[:3]
    )

    user_message = f"""A listener has the following preferences:
- Genre: {user_prefs.get('genre')}
- Mood: {user_prefs.get('mood')}
- Energy: {user_prefs.get('energy', 0.5):.2f}

The top recommended songs are: {song_list}

Relevant context:
{context_text}

Write a 3-4 sentence listener profile summary explaining what kind of listening experience this person is seeking and why these songs are a strong collective match. Be specific and engaging."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=250,
        system=[
            {
                "type": "text",
                "text": _SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text.strip()
