"""
Test Harness: evaluates the AI recommendation system on predefined listener profiles
and prints a pass/fail summary with scores and confidence ratings.

A test PASSES if the expected top genre appears in the top-3 recommendations.
A test FAILS if zero songs of the expected genre appear in the top-3.

Run with: python tests/test_harness.py
Requires: ANTHROPIC_API_KEY in .env file
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.recommender import load_songs, recommend_songs
from src.guardrails import validate_user_prefs, compute_confidence, check_output_quality

SONGS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")

TEST_PROFILES = [
    {
        "label": "High-Energy Pop",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.8},
        "expected_genre": "pop",
        "min_expected_score": 3.0,
    },
    {
        "label": "Chill Lo-Fi",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.4},
        "expected_genre": "lofi",
        "min_expected_score": 3.0,
    },
    {
        "label": "Deep Intense Rock",
        "prefs": {"genre": "rock", "mood": "intense", "energy": 0.9},
        "expected_genre": "rock",
        "min_expected_score": 3.0,
    },
    {
        "label": "Adversarial - Sad Classical",
        "prefs": {"genre": "classical", "mood": "sad", "energy": 0.3},
        "expected_genre": "classical",
        "min_expected_score": 1.0,  # lower threshold — small genre in dataset
    },
    {
        "label": "Jazz Relaxed",
        "prefs": {"genre": "jazz", "mood": "relaxed", "energy": 0.5},
        "expected_genre": "jazz",
        "min_expected_score": 1.0,  # jazz is underrepresented in the dataset
    },
    {
        "label": "Guardrail: Invalid Energy",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 1.5},
        "expected_genre": None,  # should raise ValidationError
        "min_expected_score": 0.0,
        "expect_validation_error": True,
    },
    {
        "label": "Guardrail: Unknown Genre Warning",
        "prefs": {"genre": "synthwave", "mood": "chill", "energy": 0.6},
        "expected_genre": None,
        "min_expected_score": 0.0,
        "expect_warning": True,
    },
]


def run_tests() -> None:
    songs = load_songs(SONGS_PATH)
    passed = 0
    failed = 0
    total = len(TEST_PROFILES)
    confidence_scores = []

    print("=" * 65)
    print("  MUSIC RECOMMENDER — TEST HARNESS")
    print("=" * 65)

    for i, test in enumerate(TEST_PROFILES, 1):
        label = test["label"]
        prefs = test["prefs"]
        expected_genre = test.get("expected_genre")
        min_score = test.get("min_expected_score", 1.0)
        expect_error = test.get("expect_validation_error", False)
        expect_warning = test.get("expect_warning", False)

        print(f"\nTest {i}/{total}: {label}")
        print(f"  Prefs: {prefs}")

        # Guardrail validation test
        if expect_error:
            try:
                validate_user_prefs(prefs)
                print(f"  FAIL — expected ValidationError but none was raised")
                failed += 1
            except Exception as e:
                print(f"  PASS — ValidationError correctly raised: {e}")
                passed += 1
            continue

        if expect_warning:
            _, warnings = validate_user_prefs(prefs)
            if warnings:
                print(f"  PASS — guardrail warning correctly issued: {warnings[0][:60]}...")
                passed += 1
            else:
                print(f"  FAIL — expected a guardrail warning but none was issued")
                failed += 1
            continue

        # Normal recommendation test
        try:
            _, validation_warnings = validate_user_prefs(prefs)
            if validation_warnings:
                print(f"  NOTE: {validation_warnings[0][:70]}")

            results = recommend_songs(prefs, songs, k=5)
            confidence = compute_confidence(results)
            quality_warnings = check_output_quality(results, confidence)
            confidence_scores.append(confidence)

            top_score = results[0][1] if results else 0.0
            top_genres = [r[0]["genre"] for r in results[:3]]

            score_ok = top_score >= min_score
            genre_ok = expected_genre in top_genres if expected_genre else True

            if score_ok and genre_ok:
                status = "PASS"
                passed += 1
            else:
                status = "FAIL"
                failed += 1
                if not score_ok:
                    print(f"  Reason: top score {top_score:.2f} < minimum {min_score:.2f}")
                if not genre_ok:
                    print(f"  Reason: expected '{expected_genre}' in top-3, got {top_genres}")

            print(f"  {status} — top score: {top_score:.2f} | confidence: {confidence:.2f} | top genres: {top_genres}")
            if quality_warnings:
                for w in quality_warnings:
                    print(f"  WARNING: {w}")

        except Exception as e:
            print(f"  ERROR — {e}")
            failed += 1

    # Summary
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    print(f"\n{'=' * 65}")
    print(f"  RESULTS: {passed}/{total} passed | {failed} failed")
    print(f"  Average confidence score: {avg_confidence:.2f}")
    print(f"{'=' * 65}\n")


if __name__ == "__main__":
    run_tests()
