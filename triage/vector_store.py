"""A tiny in-memory vector store.

Analogy: a map with a pin for every index card. Given the pin for a question,
we return the k nearest card pins. Real systems use Chroma, FAISS or pgvector
for millions of pins; for 12 cards, plain numpy is clearer and just as correct.
"""

from dataclasses import dataclass

import numpy as np

from triage.knowledge_base import Chunk


@dataclass
class SearchResult:
    chunk: Chunk
    score: float  # cosine similarity: closer to 1.0 = more similar


class VectorStore:
    def __init__(self, embedder):
        self.embedder = embedder
        self.chunks: list[Chunk] = []
        self.vectors: np.ndarray | None = None

    def add(self, chunks: list[Chunk]) -> None:
        """Embed all chunks in ONE API call and keep the vectors."""
        self.chunks = chunks
        self.vectors = self.embedder.embed_documents([c.text for c in chunks])

    def search(self, query: str, k: int = 3) -> list[SearchResult]:
        """Return the k chunks whose meaning is closest to the query."""
        if self.vectors is None:
            raise ValueError("The store is empty. Call add() first.")

        query_vector = self.embedder.embed_query(query)
        scores = self.vectors @ query_vector          # one dot product per chunk
        best = np.argsort(scores)[::-1][:k]            # indices of highest scores first
        return [SearchResult(self.chunks[i], float(scores[i])) for i in best]
