"""
Applied AI Music Recommender — main entry point.

Runs the full 5-step agentic pipeline for three listener profiles, demonstrating:
  - Input validation and guardrails
  - Multi-source RAG context retrieval
  - Rule-based scoring (unchanged from Project 3)
  - Claude-powered AI explanations
  - Confidence scoring and output quality checks

Run with: python src/main.py
Requires: ANTHROPIC_API_KEY in .env file (see .env.example)
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import src.agent as agent


def main() -> None:
    # ── Profile 1: High-Energy Pop ────────────────────────────────
    agent.run(
        user_prefs={"genre": "pop", "mood": "happy", "energy": 0.8},
        label="High-Energy Pop",
    )

    # ── Profile 2: Chill Lo-Fi ────────────────────────────────────
    agent.run(
        user_prefs={"genre": "lofi", "mood": "chill", "energy": 0.4},
        label="Chill Lo-Fi Study Session",
    )

    # ── Profile 3: Deep Intense Rock ─────────────────────────────
    agent.run(
        user_prefs={"genre": "rock", "mood": "intense", "energy": 0.9},
        label="Deep Intense Rock",
    )


if __name__ == "__main__":
    main()
