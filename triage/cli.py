"""Command-line entry point.

Usage:
    python -m triage.cli search "OSError: [Errno 28] No space left on device"
"""

import argparse

from dotenv import load_dotenv

from triage.embeddings import GeminiEmbedder
from triage.knowledge_base import load_known_issues
from triage.vector_store import VectorStore

KNOWLEDGE_BASE = "data/known_issues.md"


def build_store() -> VectorStore:
    store = VectorStore(GeminiEmbedder())
    store.add(load_known_issues(KNOWLEDGE_BASE))
    return store


def main() -> None:
    load_dotenv()  # reads GEMINI_API_KEY (and optional model names) from .env

    parser = argparse.ArgumentParser(description="Test-failure triage assistant")
    sub = parser.add_subparsers(dest="command", required=True)
    search = sub.add_parser("search", help="find the closest known issues")
    search.add_argument("log", help="the failure log text")
    search.add_argument("-k", type=int, default=3, help="how many results")
    args = parser.parse_args()

    store = build_store()
    if args.command == "search":
        for rank, result in enumerate(store.search(args.log, k=args.k), start=1):
            print(f"{rank}. {result.chunk.id}  score={result.score:.3f}  {result.chunk.title}")


if __name__ == "__main__":
    main()
