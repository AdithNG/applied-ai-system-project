"""
Guardrails: input validation, output confidence scoring, and safety checks.

Provides:
- validate_user_prefs(): checks input before sending to the recommendation pipeline
- compute_confidence(): scores how confident the system is in its top recommendation
- check_output_quality(): warns when recommendations are weak or degenerate
"""

from typing import Dict, List, Tuple, Any

KNOWN_GENRES = {
    "pop", "lofi", "rock", "classical", "jazz", "hip-hop",
    "electronic", "ambient", "r&b", "indie",
}

KNOWN_MOODS = {
    "happy", "chill", "intense", "sad", "energetic",
    "romantic", "melancholic", "focused", "relaxed",
}


class ValidationError(Exception):
    pass


def validate_user_prefs(prefs: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate user preference dict before running the recommendation pipeline.

    Returns (is_valid, list_of_warnings). Hard errors raise ValidationError.
    Soft mismatches (unknown genre/mood) return warnings but allow the pipeline
    to continue with reduced confidence.

    Args:
        prefs: Dict with keys 'genre', 'mood', 'energy' (and optionally others).

    Returns:
        (True, []) if fully valid; (True, [warnings]) if soft issues; raises on hard errors.
    """
    warnings = []

    # --- Hard validations ---
    if "energy" not in prefs:
        raise ValidationError("Missing required field: 'energy'")
    if "genre" not in prefs:
        raise ValidationError("Missing required field: 'genre'")
    if "mood" not in prefs:
        raise ValidationError("Missing required field: 'mood'")

    try:
        energy = float(prefs["energy"])
    except (TypeError, ValueError):
        raise ValidationError(f"'energy' must be a number, got: {prefs['energy']!r}")

    if not (0.0 <= energy <= 1.0):
        raise ValidationError(f"'energy' must be between 0.0 and 1.0, got: {energy}")

    # --- Soft warnings ---
    genre = str(prefs["genre"]).lower().strip()
    if genre not in KNOWN_GENRES:
        warnings.append(
            f"Unknown genre '{genre}'. Known genres: {sorted(KNOWN_GENRES)}. "
            "Recommendations may be less accurate."
        )

    mood = str(prefs["mood"]).lower().strip()
    if mood not in KNOWN_MOODS:
        warnings.append(
            f"Unknown mood '{mood}'. Known moods: {sorted(KNOWN_MOODS)}. "
            "Recommendations may be less accurate."
        )

    return True, warnings


def compute_confidence(scored_results: List[Tuple[Any, float, Any]]) -> float:
    """Compute a confidence score (0.0–1.0) for the top recommendation.

    Uses the gap between the top score and second score relative to the top score.
    A large gap means the top pick is clearly better than alternatives (high confidence).
    A small gap means many songs scored similarly (lower confidence).

    Args:
        scored_results: List of (song, score, explanation) tuples, sorted descending.

    Returns:
        Confidence float in [0.0, 1.0].
    """
    if not scored_results:
        return 0.0
    if len(scored_results) == 1:
        return 1.0

    top_score = scored_results[0][1]
    second_score = scored_results[1][1]

    if top_score <= 0:
        return 0.0

    # Margin-based confidence: how much better is #1 than #2?
    margin = top_score - second_score
    confidence = min(1.0, margin / (top_score * 0.4 + 0.1))
    return round(confidence, 2)


def check_output_quality(
    scored_results: List[Tuple[Any, float, Any]],
    confidence: float,
) -> List[str]:
    """Check output quality and return a list of warning strings.

    Args:
        scored_results: Top-k results from the recommender.
        confidence: Confidence score from compute_confidence().

    Returns:
        List of warning strings (empty if quality is acceptable).
    """
    warnings = []

    if not scored_results:
        warnings.append("No recommendations were generated.")
        return warnings

    top_score = scored_results[0][1]
    if top_score < 1.0:
        warnings.append(
            f"Low overall match quality (top score: {top_score:.2f}). "
            "No songs closely match your preferences — try adjusting genre or mood."
        )

    if confidence < 0.2:
        warnings.append(
            f"Low confidence ({confidence:.2f}): many songs scored similarly. "
            "The top recommendation is not strongly differentiated."
        )

    return warnings
