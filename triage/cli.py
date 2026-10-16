"""Command-line entry point. Run from the project root (the folder containing triage/).

Usage:
    python -m triage.cli search "OSError: [Errno 28] No space left on device"
    python -m triage.cli triage "OSError: [Errno 28] No space left on device"
"""

import argparse

from dotenv import load_dotenv

from triage.embeddings import GeminiEmbedder
from triage.generator import GeminiGenerator
from triage.knowledge_base import load_known_issues
from triage.pipeline import TriageAssistant
from triage.vector_store import VectorStore

KNOWLEDGE_BASE = "data/known_issues.md"


def build_store() -> VectorStore:
    store = VectorStore(GeminiEmbedder())
    store.add(load_known_issues(KNOWLEDGE_BASE))
    return store


def print_sources(results) -> None:
    for rank, result in enumerate(results, start=1):
        print(f"  {rank}. {result.chunk.id}  score={result.score:.3f}  {result.chunk.title}")


def main() -> None:
    load_dotenv()  # reads GEMINI_API_KEY (and optional model names) from .env

    parser = argparse.ArgumentParser(description="Test-failure triage assistant")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in [
        ("search", "show the closest known issues (retrieval only)"),
        ("triage", "retrieve known issues and generate a cited diagnosis"),
    ]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("log", help="the failure log text")
        p.add_argument("-k", type=int, default=3, help="how many notes to retrieve")
    args = parser.parse_args()

    store = build_store()

    if args.command == "search":
        print_sources(store.search(args.log, k=args.k))
        return

    result = TriageAssistant(store, GeminiGenerator(), k=args.k).triage(args.log)
    a = result.answer
    print(f"Matched issue : {a.issue_id or 'NO KNOWN ISSUE MATCHES'}")
    print(f"Confidence    : {a.confidence}")
    if a.issue_id:
        print(f"Likely cause  : {a.likely_cause}")
        print(f"Suggested fix : {a.suggested_fix}")
    print(f"Reasoning     : {a.reasoning}")
    for w in a.warnings:
        print(f"WARNING       : {w}")
    print("Retrieved notes (sources):")
    print_sources(result.sources)


if __name__ == "__main__":
    main()
