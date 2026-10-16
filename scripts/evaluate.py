"""Evaluate the system against the labelled test logs (the "answer key").

Two scores:
  * Retrieval hit@1 / hit@3: was the correct note ranked 1st / in the top 3?
    (Only for logs that HAVE a known issue.)
  * Triage accuracy: did the final answer name the right issue, or correctly
    say "no match" for logs without a known issue?

Run from the project root (uses the real Gemini API, about 26 calls):
    python scripts/evaluate.py
Results are printed and saved to results/eval_results.md
"""

import json
import sys
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # so "triage" imports work

from triage.cli import build_store
from triage.generator import GeminiGenerator
from triage.pipeline import TriageAssistant

LOGS = "data/test_logs.json"
OUTPUT = Path("results/eval_results.md")
PAUSE_SECONDS = 4  # stay under free-tier requests-per-minute limits


def main() -> None:
    load_dotenv()
    cases = json.loads(Path(LOGS).read_text(encoding="utf-8"))
    store = build_store()
    generator = GeminiGenerator()
    assistant = TriageAssistant(store, generator, k=3)

    rows, hit1, hit3, correct, with_issue = [], 0, 0, 0, 0
    for case in cases:
        expected = case["expected_issue"]
        result = assistant.triage(case["log"])
        retrieved = [s.chunk.id for s in result.sources]
        predicted = result.answer.issue_id

        if expected is not None:
            with_issue += 1
            hit1 += retrieved[0] == expected
            hit3 += expected in retrieved
        is_correct = predicted == expected
        correct += is_correct

        rows.append(
            f"| {case['id']} | {expected or 'none'} | {', '.join(retrieved)} "
            f"| {predicted or 'none'} | {'✅' if is_correct else '❌'} |"
        )
        print(rows[-1])
        time.sleep(PAUSE_SECONDS)

    summary = [
        f"- Retrieval hit@1: {hit1}/{with_issue} ({hit1 / with_issue:.0%})",
        f"- Retrieval hit@3: {hit3}/{with_issue} ({hit3 / with_issue:.0%})",
        f"- Triage accuracy (incl. no-match cases): {correct}/{len(cases)} ({correct / len(cases):.0%})",
    ]
    print("\n".join(summary))

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(
        "\n".join(
            [
                "# Evaluation results",
                "",
                f"Run on {date.today()} with embedding model `{store.embedder.model}` "
                f"and generation model `{generator.model}`, k=3, on {len(cases)} synthetic labelled logs.",
                "",
                *summary,
                "",
                "| Log | Expected | Retrieved (top 3) | Predicted | Correct |",
                "|---|---|---|---|---|",
                *rows,
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"\nSaved to {OUTPUT}")


if __name__ == "__main__":
    main()
