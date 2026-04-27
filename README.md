# Applied AI Music Recommender

## Base Project

This system extends **Project 3: Music Recommender Simulation** (CodePath AI110, Module 3).

The original project was a rule-based content-filtering recommender. Given a user's preferred genre, mood, and energy level, it scored every song in a 20-song catalog using hardcoded weights (genre +2.0, mood +1.0, energy proximity up to +1.0) and returned ranked results with mechanical explanations like:

> `Sunrise City - Score: 3.98 | Because: genre match (+2.0), mood match (+1.0), energy proximity (+0.98)`

It demonstrated how recommendation algorithms work but lacked any real AI intelligence. It couldn't explain *why* the match mattered to this listener, and it had no ability to reason about context or uncertainty.

---

## What's New in This Version

This version wraps the original scoring engine with a full AI pipeline:

| Component | What It Does |
|---|---|
| **RAG Retriever** | Queries a music knowledge base (genres, moods, music theory) and retrieves context passages relevant to the listener's preferences |
| **AI Explainer** | Uses the Claude API to generate rich, natural-language explanations for each recommendation, informed by the retrieved context |
| **Agentic Workflow** | Orchestrates the full pipeline in 5 observable steps with logged intermediate output |
| **Guardrails** | Validates input before the pipeline runs and computes a confidence score for the output |
| **Test Harness** | Evaluates the system on 7 predefined profiles and prints a pass/fail summary |

The rule-based scorer from Project 3 is **unchanged**. The AI layer wraps it, giving it context and language it previously lacked.

### Stretch Features Implemented

| Stretch Feature | Implementation |
|---|---|
| ✅ **RAG Enhancement** (+2) | Three custom knowledge base sources (`genres.md`, `moods.md`, `music_theory.md`) queried simultaneously via multi-source TF-IDF retrieval. Retrieved passages are passed directly to Claude to ground each explanation in real music context. |
| ✅ **Agentic Workflow Enhancement** (+2) | `src/agent.py` runs a 5-step reasoning chain with every intermediate step logged to stdout: preference analysis, RAG retrieval, rule-based scoring, AI explanation generation, and confidence evaluation. |
| ✅ **Test Harness / Evaluation Script** (+2) | `tests/test_harness.py` evaluates the system on 7 predefined profiles (including guardrail and adversarial cases) and prints a pass/fail summary with scores and confidence ratings. Run: `py tests/test_harness.py` |

---

## System Architecture

```
User Input (genre, mood, energy)
         |
         v
   +-----------------+
   |   Guardrails    |  <- input validation (energy range, known genre/mood)
   +------+----------+
          | valid input
          v
   +----------------------+
   |  Rule-Based Scorer   |  <- recommender.py (unchanged from Project 3)
   |  score_song() x 20  |    returns top-K with numeric scores
   +------+---------------+
          | top-K candidates
          v
   +----------------------+       +------------------------------+
   |    RAG Retriever     |------>|  Knowledge Base (3 sources)  |
   |  rag_retriever.py    |<------|  genres.md / moods.md /      |
   +------+---------------+       |  music_theory.md             |
          | relevant passages     +------------------------------+
          v
   +----------------------+
   |    Claude API        |  <- ai_explainer.py
   |  (ai_explainer.py)   |    generates explanation per song
   +------+---------------+
          | AI explanations
          v
   +----------------------+
   |  Confidence Scoring  |  <- guardrails.py compute_confidence()
   |  + Quality Checks    |    warns if output is weak
   +------+---------------+
          |
          v
   Final Recommendations with AI explanations + confidence score
```

The `agent.py` module orchestrates all steps and logs each one to stdout.

---

## Setup

### 1. Prerequisites

- Python 3.9+
- An [Anthropic API key](https://console.anthropic.com/)

### 2. Clone and install

```bash
git clone https://github.com/AdithNG/applied-ai-system-project.git
cd applied-ai-system-project
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### 3. Configure your API key

```bash
cp .env.example .env
# Open .env and replace your_api_key_here with your actual Anthropic API key
```

### 4. Run the recommender

```bash
py src/main.py
```

### 5. Run the test harness

```bash
py tests/test_harness.py
```

### 6. Run the original unit tests

```bash
py -m pytest tests/test_recommender.py
```

---

## Sample Interactions

### Profile 1: High-Energy Pop

**Input:**
```python
{"genre": "pop", "mood": "happy", "energy": 0.8}
```

**Agent output (abbreviated):**
```
[STEP 1] Analyzing user preferences
  Listener is seeking: pop music with a happy mood at high energy (0.80)

[STEP 2] Retrieving music context from knowledge base
  Retrieved 4 passages:
    - [genres.md - pop]
    - [moods.md - happy]
    - [music_theory.md - Energy (0.0 - 1.0)]
    - [music_theory.md - Valence (0.0 - 1.0)]

[STEP 3] Scoring song candidates with rule-based engine
  Top 5 candidates (rule-based scores):
   4.41  Sunrise City by Neon Echo [pop]
   3.28  Gym Hero by Max Pulse [pop]
   ...

[STEP 4] Generating AI explanations via Claude
  Explaining #1: Sunrise City... done

[STEP 5] Evaluating recommendation confidence
  Overall confidence score: 0.61

RECOMMENDATIONS FOR: High-Energy Pop
  #1  Sunrise City - Neon Echo
       Genre: pop | Mood: happy | Energy: 0.82 | Score: 4.41
       This track is a near-perfect match. Its bright, summery pop production
       and 0.82 energy sit right at your target level, while the upbeat happy
       mood aligns exactly with what you're seeking. The high danceability (0.79)
       and valence (0.84) confirm this is designed to energize and uplift.
```

---

### Profile 2: Chill Lo-Fi Study Session

**Input:**
```python
{"genre": "lofi", "mood": "chill", "energy": 0.4}
```

**Sample AI explanation:**
> The calm, focused texture of this track sits perfectly at your target energy. The 0.42 level and 78 BPM tempo create exactly the unhurried pace lo-fi listeners seek during focused work. Its high acousticness (0.71) adds a warm, organic quality that distinguishes it from more electronic lo-fi, and the detailed "calm focused ambient" mood tag confirms it's engineered for the same headspace you're in.

---

### Profile 3: Guardrail in action (invalid input)

**Input:**
```python
{"genre": "pop", "mood": "happy", "energy": 1.5}
```

**Output:**
```
ValidationError: 'energy' must be between 0.0 and 1.0, got: 1.5
```

---

## Design Decisions

**Why keep the rule-based scorer?**
The original scoring engine is fast, transparent, and correct. It reliably surfaces genre/mood/energy matches. Rather than replacing it with an LLM (which would be slower, more expensive, and less consistent), the AI layer adds context and language on top of the proven numeric foundation.

**Why keyword-based RAG instead of vector embeddings?**
For a 20-song catalog and a 3-file knowledge base, vector embeddings would be overengineered. TF-IDF keyword overlap is fast, requires no external services, and is fully explainable. The retrieval quality is strong because the knowledge base terms closely match the genre/mood vocabulary in the dataset.

**Why cache the system prompt?**
The Claude API's `cache_control` flag on the system prompt avoids re-sending the full instruction text on every API call. With 5+ explanation calls per profile, caching reduces both latency and cost.

**Trade-offs accepted:**
- The knowledge base is manually written, which means it can go stale if new genres are added to the dataset.
- Keyword retrieval fails on synonyms (e.g., "lofi" vs "lo-fi"). A vector-based approach would handle this better at the cost of added complexity.
- AI explanations add 1-2 seconds per song. For a 5-song result set, that's 5-10 seconds of API calls per profile.

---

## Testing Summary

The test harness (`tests/test_harness.py`) runs 7 profiles:

| Profile | Type | Result |
|---|---|---|
| High-Energy Pop | Standard | PASS |
| Chill Lo-Fi | Standard | PASS |
| Deep Intense Rock | Standard | PASS |
| Adversarial: Sad Classical | Edge case | PASS (low threshold) |
| Jazz Relaxed | Underrepresented genre | PASS |
| Invalid energy (1.5) | Guardrail test | PASS (error caught) |
| Unknown genre warning | Guardrail test | PASS (warning issued) |

The original unit tests in `tests/test_recommender.py` all continue to pass. The new AI layer does not touch the scoring engine.

**What didn't work well:** Confidence scores are low (~0.2-0.3) for underrepresented genres (jazz, classical) because many songs score similarly in the absence of a genre match. This is a known limitation of the small catalog, not a bug.

---

## Reflection

See [model_card.md](model_card.md) for the full reflection on AI collaboration, limitations, and ethics.

---

## Demo Walkthrough

[Watch the demo walkthrough on Loom](https://www.loom.com/share/c2cd9312c8574c2caf14840aff39a226)

---

## Repository Structure

```
applied-ai-system-project/
├── src/
│   ├── recommender.py        # Original Project 3 scoring engine (unchanged)
│   ├── main.py               # Entry point - runs 3 profiles through agent pipeline
│   ├── agent.py              # 5-step agentic workflow with step logging
│   ├── ai_explainer.py       # Claude API integration for explanations
│   ├── rag_retriever.py      # Knowledge base loader and context retriever
│   └── guardrails.py         # Input validation and confidence scoring
├── data/
│   ├── songs.csv             # 20-song catalog with 15 attributes each
│   └── knowledge_base/
│       ├── genres.md         # Genre descriptions for RAG context
│       ├── moods.md          # Mood descriptions for RAG context
│       └── music_theory.md   # Audio feature reference for RAG context
├── tests/
│   ├── test_recommender.py   # Original Project 3 unit tests
│   └── test_harness.py       # Project 4 evaluation script (7 profiles)
├── assets/                   # Screenshots and architecture diagram
├── .env.example              # API key template
├── requirements.txt
└── README.md
```
