"""
Agentic Workflow: orchestrates the full recommendation pipeline in 5 observable steps.

Each step logs its output to stdout so the reasoning chain is visible. This is the
primary entry point for the AI-enhanced recommendation system — it replaces direct
calls to recommend_songs() in the original Project 3.

Steps:
  1. Analyze preferences  — validate input and characterize what the listener wants
  2. Retrieve context     — RAG lookup across all knowledge base sources
  3. Score candidates     — run the existing rule-based scorer to get top-K songs
  4. Generate explanations — Claude generates a rich explanation for each top song
  5. Evaluate confidence  — compute and report confidence scores, emit any warnings
"""

from typing import Dict, Any, List, Tuple
import os
import sys

# Ensure project root is on sys.path regardless of how this file is invoked
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.recommender import load_songs, recommend_songs
from src.rag_retriever import retrieve_context_for_recommendation
from src.ai_explainer import generate_explanation, generate_profile_summary
from src.guardrails import validate_user_prefs, compute_confidence, check_output_quality

SONGS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")


def _step(n: int, label: str) -> None:
    print(f"\n[STEP {n}] {label}")
    print("-" * 50)


def run(
    user_prefs: Dict[str, Any],
    label: str = "Listener",
    k: int = 5,
    songs_path: str = SONGS_PATH,
    mode: str = "balanced",
) -> List[Dict[str, Any]]:
    """Run the full 5-step agentic recommendation pipeline.

    Args:
        user_prefs: Dict with 'genre', 'mood', 'energy' (and optionally others).
        label: Display name for this listener profile.
        k: Number of recommendations to return.
        songs_path: Path to the songs CSV file.
        mode: Scoring mode passed to the rule-based recommender.

    Returns:
        List of result dicts, each containing:
          - song: the song dict
          - score: float rule-based score
          - rule_explanation: original rule-based reason string
          - ai_explanation: Claude-generated explanation
          - confidence: float confidence score
    """
    print(f"\n{'=' * 60}")
    print(f"  MUSIC RECOMMENDER — AI AGENT")
    print(f"  Profile: {label}")
    print(f"  Preferences: genre={user_prefs.get('genre')}, "
          f"mood={user_prefs.get('mood')}, "
          f"energy={user_prefs.get('energy', 0.5):.2f}")
    print(f"{'=' * 60}")

    # ── STEP 1: Analyze preferences ──────────────────────────────
    _step(1, "Analyzing user preferences")
    try:
        _, warnings = validate_user_prefs(user_prefs)
    except Exception as e:
        print(f"  ERROR: {e}")
        raise

    genre = str(user_prefs.get("genre", "")).lower()
    mood = str(user_prefs.get("mood", "")).lower()
    energy = float(user_prefs.get("energy", 0.5))
    energy_label = "high" if energy >= 0.7 else ("low" if energy <= 0.35 else "medium")

    print(f"  Listener is seeking: {genre} music with a {mood} mood at {energy_label} energy ({energy:.2f})")
    if warnings:
        for w in warnings:
            print(f"  WARNING: {w}")

    # ── STEP 2: Retrieve context ──────────────────────────────────
    _step(2, "Retrieving music context from knowledge base")
    context_passages = retrieve_context_for_recommendation(genre, mood, energy)
    print(f"  Retrieved {len(context_passages)} passages:")
    for passage in context_passages:
        header = passage.split("\n")[0]
        print(f"    • {header}")

    # ── STEP 3: Score candidates ──────────────────────────────────
    _step(3, "Scoring song candidates with rule-based engine")
    songs = load_songs(songs_path)
    scored_results = recommend_songs(user_prefs, songs, k=k, mode=mode)
    print(f"  Top {len(scored_results)} candidates (rule-based scores):")
    for song, score, reasons in scored_results:
        print(f"    {score:5.2f}  {song['title']} by {song['artist']} [{song['genre']}]")

    # ── STEP 4: Generate AI explanations ─────────────────────────
    _step(4, "Generating AI explanations via Claude")
    results = []
    for i, (song, score, rule_explanation) in enumerate(scored_results, 1):
        print(f"  Explaining #{i}: {song['title']}...", end=" ", flush=True)
        try:
            ai_explanation = generate_explanation(song, user_prefs, context_passages)
            print("done")
        except Exception as e:
            ai_explanation = f"[AI explanation unavailable: {e}]"
            print(f"failed ({e})")
        results.append({
            "song": song,
            "score": score,
            "rule_explanation": rule_explanation,
            "ai_explanation": ai_explanation,
            "confidence": 0.0,  # filled in step 5
        })

    # ── STEP 5: Evaluate confidence ───────────────────────────────
    _step(5, "Evaluating recommendation confidence")
    confidence = compute_confidence(scored_results)
    quality_warnings = check_output_quality(scored_results, confidence)

    for result in results:
        result["confidence"] = confidence

    print(f"  Overall confidence score: {confidence:.2f}")
    if quality_warnings:
        for w in quality_warnings:
            print(f"  WARNING: {w}")
    else:
        print("  Output quality check: OK")

    # ── Final output ──────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"  RECOMMENDATIONS FOR: {label}")
    print(f"  Confidence: {confidence:.2f} | Mode: {mode}")
    print(f"{'=' * 60}")
    for i, result in enumerate(results, 1):
        song = result["song"]
        print(f"\n  #{i}  {song['title']} — {song['artist']}")
        print(f"       Genre: {song['genre']} | Mood: {song['mood']} | "
              f"Energy: {song.get('energy', '?')} | Score: {result['score']:.2f}")
        print(f"       {result['ai_explanation']}")

    return results
