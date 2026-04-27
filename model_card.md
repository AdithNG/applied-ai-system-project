# Model Card: Applied AI Music Recommender

## 1. Model Name

**VibeFinder 2.0** — an AI-augmented music recommendation system built on the rule-based VibeFinder 1.0 (Project 3).

---

## 2. Goal / Task

VibeFinder 2.0 recommends songs from a catalog based on a listener's stated preferences (genre, mood, energy level), then uses the Claude AI model and a music knowledge base to generate rich, context-aware explanations for each recommendation.

It extends the original rule-based system by answering not just *which* songs match, but *why* they match in a way that is meaningful to the listener.

---

## 3. Algorithm Summary

The system runs in five steps:

1. **Input validation** — guardrails check that energy is in range, genre/mood are known
2. **Rule-based scoring** — the original Project 3 weighted scorer ranks all 20 songs (genre +2.0, mood +1.0, energy proximity 0–1.0)
3. **RAG context retrieval** — a TF-IDF keyword retriever queries three knowledge base files (genres.md, moods.md, music_theory.md) and returns the most relevant passages
4. **AI explanation generation** — Claude (claude-sonnet-4-6) generates a 2–3 sentence natural language explanation for each top song, using the retrieved passages as grounding context
5. **Confidence scoring** — the score gap between #1 and #2 is used to compute a confidence value (0–1) for the overall recommendation

The numeric ranking comes entirely from the rule-based engine. Claude only adds language and context.

---

## 4. Data Used

**Song catalog:** `data/songs.csv` — 20 fictional songs with 15 attributes each (genre, mood, energy, tempo_bpm, valence, danceability, acousticness, popularity, liveness, speechiness, detailed_mood, release_decade, id, title, artist).

**Knowledge base:**
- `data/knowledge_base/genres.md` — descriptions of 10 music genres
- `data/knowledge_base/moods.md` — descriptions of 9 mood categories
- `data/knowledge_base/music_theory.md` — explanations of 9 audio attributes (energy, tempo, valence, etc.)

**AI model:** Anthropic Claude (claude-sonnet-4-6), accessed via the Anthropic API. The model was not fine-tuned; it uses a structured system prompt and per-request context injection.

All songs are fictional. Knowledge base descriptions are manually written.

---

## 5. Observed Behavior and Biases

**Inherited from Project 3:**
- Genre dominates scoring (+2.0 vs max +1.0 for energy), so a genre match with wrong energy outranks a perfect energy match in a different genre. A "classical, sad, high energy" user still gets quiet classical pieces.
- Underrepresented genres (jazz, rock) give poor results because the catalog has only 1–2 songs per genre.
- Exact string matching means "Hip Hop" ≠ "hip-hop".

**New in VibeFinder 2.0:**
- AI explanations are generally accurate but occasionally hallucinate specific claims about a song's production style that aren't supported by the CSV attributes. Claude cannot hear the music — it only sees numbers.
- RAG retrieval is keyword-based and fails on synonyms (e.g., "lofi" and "lo-fi" are not matched as equivalent).
- Confidence scores are systematically low (~0.2) for underrepresented genres because multiple songs score similarly when no genre match is available. This is an honest reflection of weak recommendations, but it may alarm users unnecessarily.

---

## 6. Evaluation Process

**Test harness** (`tests/test_harness.py`) — 7 profiles covering standard use, adversarial edge cases, and guardrail behavior:

| Profile | Expected | Result |
|---|---|---|
| High-Energy Pop | Pop in top-3 | PASS |
| Chill Lo-Fi | Lofi in top-3 | PASS |
| Deep Intense Rock | Rock in top-3 | PASS |
| Adversarial: Sad Classical | Classical in top-3 (low threshold) | PASS |
| Jazz Relaxed | Jazz in top-3 (low threshold) | PASS |
| Invalid energy (1.5) | ValidationError raised | PASS |
| Unknown genre "synthwave" | Warning issued | PASS |

All 10 original Project 3 unit tests continue to pass — the AI layer does not alter the underlying scoring logic.

---

## 7. Limitations and Potential Misuse

**Limitations:**
- 20-song catalog is far too small for real deployment. Genre coverage is uneven.
- Claude explanations reflect the attributes in the CSV — they cannot assess actual sound quality, production value, or cultural context.
- No user history or session learning. Every run treats the listener as a fresh user.
- API calls add 1–2 seconds per explanation. A 5-song result set takes 5–10 seconds.

**Misuse concerns:**
- The AI explanations sound authoritative. A user might trust them more than warranted for a small, fictional catalog.
- Confidence scores could be misinterpreted as a measure of explanation accuracy rather than recommendation differentiation.
- The system could reinforce genre filter bubbles — a pop listener will always receive pop recommendations, with no mechanism for discovery or serendipity.

**Safeguards in place:**
- Input validation rejects out-of-range energy values and warns on unknown genres/moods.
- Low-confidence warnings alert users when recommendations are weakly differentiated.
- The README and model card are explicit that this is an educational prototype, not a production system.

---

## 8. Reflection on AI Collaboration

**How AI was used during development:**

Claude Code (this assistant) was used throughout the project for code generation, architecture planning, and debugging. The workflow was collaborative — I described the desired behavior, the AI proposed implementations, and I reviewed, adjusted, and integrated them.

**One instance where AI suggestions were genuinely helpful:**

When designing the RAG retriever, the initial instinct was to use a vector embedding library (like sentence-transformers) for semantic search. Claude suggested that for a 3-file knowledge base with ~30 passages, TF-IDF keyword overlap would be simpler, faster, and more transparent — and that the vocabulary in the knowledge base files was specific enough that keyword matching would perform nearly as well as embeddings. This was correct. The simpler approach works well and makes the retrieval logic easy to understand and debug.

**One instance where AI suggestions were flawed or needed correction:**

In the first draft of `agent.py`, the agent imported `from recommender import load_songs` using a relative import path that assumed the script was run from inside the `src/` directory. This caused `ModuleNotFoundError` when running `python src/main.py` from the project root. The fix — adding `sys.path.insert(0, ...)` and using `from src.recommender import ...` — required diagnosing the import resolution issue manually. The AI had generated working code for a different execution context than the one actually being used.

---

## 9. Ideas for Improvement

- **Fuzzy genre matching**: A similarity table (pop ↔ indie pop, r&b ↔ soul) would fix the hard genre boundary problem without requiring a machine learning model.
- **Vector-based RAG**: Replacing TF-IDF with sentence embeddings would handle synonym variation and improve retrieval for niche queries.
- **Confidence-aware explanations**: When confidence is low, Claude should acknowledge uncertainty in the explanation ("This is a partial match — no songs in the catalog closely fit your genre preference").
- **Diverse output by default**: A diversity penalty (similar to `recommend_diverse()` from Project 3) should be the default, not an option.
- **Caching explanations**: The same song + similar profile combinations could reuse cached explanations to reduce API costs.
