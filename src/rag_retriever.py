"""
RAG Retriever: loads the music knowledge base and retrieves relevant passages
for a given query using TF-IDF keyword overlap scoring.

Multi-source: queries genres.md, moods.md, and music_theory.md simultaneously,
returning the top-k passages ranked by relevance across all sources.
"""

import os
import re
from typing import List, Tuple

KNOWLEDGE_BASE_DIR = os.path.join(
    os.path.dirname(__file__), "..", "data", "knowledge_base"
)


def _load_file(path: str) -> List[Tuple[str, str]]:
    """Parse a markdown file into (heading, body) passage tuples."""
    passages = []
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Split on level-2 headings (## Heading)
    sections = re.split(r"\n## ", content)
    for section in sections:
        if not section.strip():
            continue
        lines = section.strip().splitlines()
        heading = lines[0].lstrip("# ").strip()
        body = " ".join(lines[1:]).strip()
        if heading and body:
            passages.append((heading, body))
    return passages


def load_knowledge_base(kb_dir: str = KNOWLEDGE_BASE_DIR) -> List[Tuple[str, str, str]]:
    """Load all .md files from the knowledge base directory.

    Returns a list of (source_file, heading, body) tuples.
    """
    passages = []
    for filename in sorted(os.listdir(kb_dir)):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(kb_dir, filename)
        for heading, body in _load_file(filepath):
            passages.append((filename, heading, body))
    return passages


def _tfidf_score(query_tokens: List[str], passage_text: str) -> float:
    """Simple term-frequency overlap score between query tokens and passage text."""
    passage_lower = passage_text.lower()
    passage_tokens = set(re.findall(r"\b\w+\b", passage_lower))
    matches = sum(1 for token in query_tokens if token in passage_tokens)
    # Normalize by passage length to avoid bias toward longer passages
    if not passage_tokens:
        return 0.0
    return matches / (1 + len(passage_tokens) ** 0.3)


def retrieve_context(
    query: str,
    kb_dir: str = KNOWLEDGE_BASE_DIR,
    k: int = 4,
) -> List[str]:
    """Retrieve the top-k most relevant passages for the given query.

    Queries all knowledge base sources simultaneously and returns a flat list
    of passage text strings, ranked by TF-IDF keyword overlap.

    Args:
        query: Free-form query string (e.g., "pop happy high energy").
        kb_dir: Path to the knowledge base directory.
        k: Number of top passages to return.

    Returns:
        List of passage strings (heading + body), most relevant first.
    """
    passages = load_knowledge_base(kb_dir)
    if not passages:
        return []

    query_tokens = [t.lower() for t in re.findall(r"\b\w+\b", query)]

    scored = []
    for source, heading, body in passages:
        combined_text = f"{heading} {body}"
        # Boost score if the heading directly matches a query token
        score = _tfidf_score(query_tokens, combined_text)
        if heading.lower() in query_tokens:
            score += 1.5
        scored.append((score, source, heading, body))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:k]

    return [f"[{source} — {heading}]\n{body}" for _, source, heading, body in top]


def retrieve_context_for_recommendation(
    genre: str,
    mood: str,
    energy: float,
    kb_dir: str = KNOWLEDGE_BASE_DIR,
) -> List[str]:
    """Convenience wrapper: build a query from song attributes and retrieve context."""
    energy_label = "high energy" if energy >= 0.7 else ("low energy" if energy <= 0.35 else "medium energy")
    query = f"{genre} {mood} {energy_label} music tempo danceability valence"
    return retrieve_context(query, kb_dir=kb_dir, k=4)
