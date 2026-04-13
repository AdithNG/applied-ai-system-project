"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def print_recommendations(label: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    recommendations = recommend_songs(user_prefs, songs, k=k)
    print(f"\n{'=' * 50}")
    print(f"Profile: {label}")
    print(f"Preferences: {user_prefs}")
    print(f"{'=' * 50}")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Profile 1: High-Energy Pop
    print_recommendations(
        "High-Energy Pop",
        {"genre": "pop", "mood": "happy", "energy": 0.8},
        songs,
    )

    # Profile 2: Chill Lofi
    print_recommendations(
        "Chill Lofi",
        {"genre": "lofi", "mood": "chill", "energy": 0.4},
        songs,
    )

    # Profile 3: Deep Intense Rock
    print_recommendations(
        "Deep Intense Rock",
        {"genre": "rock", "mood": "intense", "energy": 0.9},
        songs,
    )


if __name__ == "__main__":
    main()
