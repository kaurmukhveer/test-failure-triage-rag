# Test-Failure Triage Assistant (RAG)

![CI](https://github.com/kaurmukhveer/test-failure-triage-rag/actions/workflows/ci.yml/badge.svg)

A Python command-line tool that takes a failing test's log, retrieves the most relevant
**known-issue notes** using embeddings and vector similarity search, and asks an LLM to
explain the likely cause and fix, **citing only the notes it was given**. If no note fits,
it says so instead of guessing.

> All data in `data/` is **synthetic** and was written for this project. No real company logs are used.

## How it works

```
failure log
    │
    ▼
1. Retrieve   embed the log (Gemini embeddings) → cosine similarity against
              the known-issue notes → top-k notes
    │
    ▼
2. Augment    build a prompt containing ONLY the retrieved notes + the log
    │
    ▼
3. Generate   LLM returns structured JSON: issue_id, confidence, cause, fix, reasoning
    │
    ▼
4. Verify     the cited issue_id must be one of the retrieved notes;
              otherwise the citation is removed and a warning is shown
```

| Module | Responsibility |
|---|---|
| `triage/knowledge_base.py` | Splits `known_issues.md` into one chunk per known issue |
| `triage/embeddings.py` | Gemini embeddings (`RETRIEVAL_DOCUMENT` / `RETRIEVAL_QUERY`), L2-normalized |
| `triage/vector_store.py` | In-memory vector store; cosine similarity via dot product of normalized vectors |
| `triage/generator.py` | Grounded prompt, JSON output, citation check |
| `triage/pipeline.py` | Retrieve → augment → generate → verify |
| `triage/cli.py` | `search` and `triage` commands |
| `scripts/evaluate.py` | Scores retrieval and end-to-end accuracy against labelled logs |

## Design decisions

- **Grounding and "no match".** The prompt allows only the retrieved notes and requires `null`
  when none apply. One labelled log (LOG-013) has no matching issue to test this.
- **Search scores alone can't detect a non-match.** All notes are about test failures, so even
  unrelated notes score around 0.6. The LLM's judgement over the retrieved text decides the match.
- **Citation guardrail.** The model's answer is checked against the retrieved IDs; an unknown
  citation is dropped rather than trusted.
- **Prompt-injection hygiene.** The log is wrapped in tags and treated as untrusted data.
- **Repeatable output.** `temperature=0` and JSON output make answers deterministic enough to evaluate.
- **numpy instead of a vector database.** With 12 notes, a vector DB adds setup without benefit.
  At scale, the `VectorStore` class would be replaced by Chroma, FAISS or pgvector behind the same interface.
- **Dependency injection.** The embedder and LLM are passed in, so tests swap them for fakes.
- **Model names in config.** `EMBED_MODEL` and `GEN_MODEL` live in `.env` because hosted model names change.

## Evaluation

`scripts/evaluate.py` runs every labelled log in `data/test_logs.json` through the full pipeline and reports:

- **Retrieval hit@1 / hit@3**: is the correct note ranked first / within the top 3?
- **Triage accuracy**: does the final answer name the correct issue, or correctly report no match?

Latest results: see [`results/eval_results.md`](results/eval_results.md).
The dataset is small and synthetic, so these numbers show the method works, not production accuracy.

## Testing

```bash
pytest -v
```

Unit tests cover chunking, vector search ranking, prompt construction, JSON parsing, the citation
guardrail and the end-to-end pipeline. They use a fake embedder and a fake LLM, so they run offline
with no API key. GitHub Actions runs them on every push (Python 3.11 and 3.12).

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then add your Gemini API key
python scripts/check_gemini.py  # confirms the key and model names work

python -m triage.cli search "Killed. Process completed with exit code 137."
python -m triage.cli triage "OSError: [Errno 28] No space left on device"
python scripts/evaluate.py
```

Run commands from the project root. A free Gemini API key is available from Google AI Studio.

## Limitations and next steps

- Small synthetic knowledge base; real logs are longer and noisier.
- No persistent index: notes are re-embedded on each run (fine for 12 notes).
- Next: chunking long logs, a persistent vector database, a larger evaluation set, and an
  agentic step that chooses between searching known issues and past failure history.

Built with AI-assisted development; every component was reviewed, tested and run locally.
