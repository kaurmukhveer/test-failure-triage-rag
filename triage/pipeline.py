"""The full RAG pipeline: retrieve -> prompt -> generate -> verify.

The embedder and generator are passed in ("dependency injection"), so tests
can swap the real Gemini calls for fakes and run offline, for free.
"""

from dataclasses import dataclass

from triage.generator import TriageAnswer, build_prompt, parse_answer
from triage.vector_store import SearchResult, VectorStore


@dataclass
class TriageResult:
    answer: TriageAnswer
    sources: list[SearchResult]


class TriageAssistant:
    def __init__(self, store: VectorStore, generator, k: int = 3):
        self.store = store
        self.generator = generator
        self.k = k

    def triage(self, log: str) -> TriageResult:
        sources = self.store.search(log, k=self.k)               # 1. retrieve
        prompt = build_prompt(log, sources)                       # 2. augment
        raw = self.generator.generate(prompt)                     # 3. generate
        allowed = {s.chunk.id for s in sources}
        answer = parse_answer(raw, allowed_ids=allowed)           # 4. verify
        return TriageResult(answer=answer, sources=sources)
