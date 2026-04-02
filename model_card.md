# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder is designed to suggest songs from a small catalog based on a user's preferred genre, mood, and energy level. It is built for classroom exploration — specifically to demonstrate how content-based filtering works by matching song attributes to user preferences.

This system is **not** intended for real users or production deployment. It assumes a single static taste profile per session and has no ability to learn from user behavior over time.

---

## 3. How the Model Works

VibeFinder scores every song in the catalog against a user's preferences and returns the top matches.

For each song, the system asks three questions:

1. **Does the genre match?** If so, the song gets +2.0 points. This is the heaviest signal — genre is treated as the most important filter.
2. **Does the mood match?** A match adds +1.0 point. "Happy" and "intense" are treated as completely separate categories with no overlap.
3. **How close is the energy level?** Energy is measured on a 0–1 scale. A song with energy 0.8 scores 1.0 proximity points when the user wants 0.8, and 0.5 points when the user wants 0.3. Closer = more points.
4. **Acoustic bonus** (OOP interface only): If the user prefers acoustic music and the song is highly acoustic, it gets +0.5 extra points.

Once every song has a total score, the system sorts them from highest to lowest and returns the top five. Each recommendation comes with a plain-language explanation like: "genre match (+2.0), mood match (+1.0), energy proximity (+0.82)."

---

## 4. Data

The catalog is `data/songs.csv`, containing **20 songs**.

**Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, country, r&b, classical, electronic, metal

**Moods represented:** happy, chill, intense, moody, focused, relaxed, energetic, romantic, sad, aggressive

Songs were generated for this simulation and do not represent real-world releases. The starter set of 10 songs leaned heavily toward pop and lofi. Ten additional songs were added to cover underrepresented genres (hip-hop, classical, electronic, metal, country, r&b) and moods (sad, romantic, energetic, aggressive).

**Limitations of the data:** All songs are fictional. Audio feature values (energy, valence, etc.) were chosen to be plausible but are not derived from actual audio analysis. The catalog is far too small for meaningful diversity in recommendations.

---

## 5. Strengths

- **Transparent and explainable**: Every recommendation includes a specific reason. There is no black box.
- **Deterministic**: The same user profile always produces the same ranking — easy to test and debug.
- **Works well for dominant taste profiles**: A user who strongly prefers one genre and mood (e.g., lofi + chill) will consistently see their preferred songs at the top.
- **Fast**: Scoring 20 songs takes microseconds. The algorithm scales linearly.

---

## 6. Limitations and Bias

- **Genre string matching is brittle**: "indie pop" and "pop" are treated as completely different genres even though they overlap musically. A user who types "Hip Hop" (capital H) gets zero genre points against "hip-hop" in the catalog.
- **Filter bubble**: The genre weight (+2.0) is strong enough that users almost always see their own genre at the top. Songs from other genres are rarely surfaced, even when they closely match on energy and mood.
- **Pop overrepresentation**: The starter catalog had 2 pop songs and 3 lofi songs among its 10. Pop users were better served than jazz or synthwave users simply because of catalog size.
- **Only one continuous feature scored**: Valence, danceability, and tempo are stored but ignored by the scoring function. Two songs with very different vibes (e.g., very danceable vs. not) can score identically.
- **No personalization over time**: The system has no memory of skips, replays, or explicit likes. Every session starts fresh.
- **Conflicting preferences produce odd results**: A user who wants `mood: sad` and `energy: 0.9` may get "aggressive metal" because energy is close and there's nothing else matching sadness at high energy — not necessarily a useful recommendation.

---

## 7. Evaluation

Three user profiles were tested manually:

| Profile | Top Result | Observation |
|---|---|---|
| `{genre: pop, mood: happy, energy: 0.8}` | Sunrise City | Genre + mood + energy all matched — correct and intuitive |
| `{genre: lofi, mood: chill, energy: 0.4}` | Library Rain | Correct, both lofi/chill songs scored equally high |
| `{genre: rock, mood: intense, energy: 0.9}` | Storm Runner | Only one rock song in catalog — it dominated completely |

One logic experiment was run: doubling the energy weight made rankings more sensitive to energy gaps. Songs with matching genre but mismatched energy dropped noticeably. The default weights felt better balanced.

A mood-only experiment (removing genre scoring) showed that genre dominates: without it, many unrelated songs tied in score, making the recommendations much less useful.

---

## 8. Future Work

- **Fuzzy genre matching**: Use embeddings or a genre taxonomy so that "indie pop" can partially match "pop," and "r&b" can partially match "soul."
- **Score more features**: Add valence and danceability to the scoring function so the system can distinguish between a "happy party song" and a "happy slow ballad."
- **Diversity penalty**: Prevent the top 5 from being dominated by one genre or artist. After selecting the top result, penalize other songs from the same genre slightly to encourage variety.
- **Collaborative signals**: Track which songs users skip or replay and adjust weights over time. Pure content-based filtering misses the "this is technically my genre but I'm tired of it" signal entirely.
- **Larger catalog**: 20 songs is too small to expose real recommendation patterns. A catalog of 500+ songs would better reveal how the scoring behaves across edge cases.

---

## 9. Personal Reflection

Building VibeFinder made the invisible visible: recommendations are math, not intuition. The system doesn't "know" that Midnight Coding sounds good while coding — it just knows that the numbers match. That gap between what the algorithm computes and what a human experiences as a good recommendation is where most of the interesting problems in AI live.

The most surprising discovery was how much the genre weight controlled the entire output. A +2.0 bonus for genre match versus +1.0 for mood means that genre mismatches are nearly unrecoverable. Real platforms like Spotify likely use learned embeddings where "indie pop" and "pop" share 80% of their genre vector — so the gap isn't binary. This project made that design choice feel concrete and necessary, not abstract.

If I kept developing this, I'd start by replacing exact string matching with a small similarity lookup table, then add valence to the score. Those two changes alone would produce noticeably more interesting recommendations without changing the core architecture.
