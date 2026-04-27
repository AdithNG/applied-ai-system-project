# Reflection: Applied AI Music Recommender (Project 4)

## What This Project Taught Me About AI

Building VibeFinder 2.0 made one thing clear: the most valuable part of adding AI to a system is not the output — it's the *reasoning layer* that connects inputs to outputs in a way humans can understand.

The original recommender (Project 3) was correct but opaque. It told you a song scored 3.98 and gave you a breakdown of the math. This project adds a layer that says: *here's why these numbers matter for you specifically, given what you said you're looking for*. That shift from arithmetic to explanation is where AI creates real value.

The more surprising lesson was how little the underlying scoring changed. The rule-based engine from Project 3 still does all the ranking. Claude never decides which song to recommend — it only describes the decision after the fact. This is a deliberate design choice and, I think, the right one: transparent rule-based logic is easier to audit and debug than a black-box LLM ranking. The AI handles language; the rules handle decisions.

---

## Limitations and Biases

**Genre domination (inherited from Project 3):** The +2.0 genre weight means genre match always outranks energy mismatch. A "high-energy classical" user still gets quiet piano pieces. This is a structural problem, not a bug.

**Small catalog:** 20 songs. Underrepresented genres (jazz, rock) give poor results because the algorithm runs out of matching songs after the first pick. Confidence scores are systematically low for these users.

**AI explanation hallucinations:** Claude can only see the attributes in the CSV — it cannot hear the music. Occasionally it makes specific claims about a song's "warm production" or "organic texture" that aren't directly supported by the data. These sound authoritative but may be invented.

**Keyword RAG limitations:** The retriever uses TF-IDF keyword overlap, which fails on synonyms. A user querying for "lo-fi" (hyphenated) would not retrieve passages about "lofi" (unhyphenated).

---

## Could This System Be Misused?

The main risk is over-trust. The AI explanations are fluent and specific, which makes them sound like expert analysis. A user might take "this track's acousticness of 0.71 perfectly complements your preference for organic textures" as genuine insight when it is actually a template applied to a number.

**Mitigations built in:**
- Confidence scores surface when recommendations are weakly differentiated
- The README and model card are explicit that this is an educational prototype
- Input validation prevents nonsensical queries from reaching the AI layer

---

## What Surprised Me During Testing

Two things:

**1. The confidence scores were more informative than expected.** For well-represented genres (pop, lofi), confidence hovered around 0.6–0.8, correctly reflecting that there was a clear winner. For jazz and classical, it dropped to 0.2–0.3, accurately signaling that many songs were tied near the top. The formula (`margin / (top_score × 0.4 + 0.1)`) was a first guess — seeing it behave sensibly without tuning was a genuine surprise.

**2. The RAG retrieval improved explanation coherence noticeably.** Early tests without context injection produced generic explanations ("this song matches your energy preference"). With the knowledge base passages providing genre and mood context, Claude's explanations became specific and grounded. The difference was visible immediately, which validated the RAG approach over a simple "ask Claude with no context" approach.

---

## AI Collaboration During This Project

**Claude Code (this assistant)** was used for architecture planning, code generation, and debugging throughout the project.

**One instance where AI suggestions were helpful:**

When designing the RAG component, the suggestion to use TF-IDF keyword overlap instead of vector embeddings was correct and practical. For a 3-file knowledge base with ~30 passages, embeddings would have required an additional dependency (`sentence-transformers` or OpenAI embeddings) and added complexity with minimal quality improvement. The simpler approach was recommended with clear reasoning — and it worked exactly as described.

**One instance where AI suggestions were flawed:**

The first draft of `agent.py` used bare relative imports (`from recommender import load_songs`) that assumed the script was executed from inside the `src/` directory. Running `python src/main.py` from the project root caused a `ModuleNotFoundError`. The fix required diagnosing the Python path resolution issue and adjusting to `from src.recommender import ...` with a `sys.path.insert()` guard. The AI had generated syntactically valid code for a different execution context than the one in use — a reminder that generated code needs to be tested in the actual environment, not just reviewed for syntax.

---

## Future Improvements

1. **Fuzzy genre matching** — a small lookup table (pop ↔ indie pop, r&b ↔ soul) would fix the hard genre boundary without requiring ML
2. **Vector-based RAG** — sentence embeddings would handle synonym variation and improve retrieval quality
3. **Confidence-aware Claude prompting** — when confidence is low, the prompt should instruct Claude to acknowledge the uncertainty explicitly
4. **Larger catalog** — 20 songs is a proof-of-concept; real utility requires hundreds of songs per genre
5. **Session learning** — tracking which recommendations a user accepts or skips would let the system update weights dynamically
