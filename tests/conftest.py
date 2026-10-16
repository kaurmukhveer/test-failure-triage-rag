"""Shared test helpers: fake embedder and fake LLM.

Analogy: a flight simulator. We test the pilot's procedures without burning
real fuel (API calls, money, network). Tests run offline and give the same
result every time.
"""

import re

import numpy as np
import pytest

from triage.embeddings import normalize
from triage.knowledge_base import load_known_issues
from triage.vector_store import VectorStore


class FakeEmbedder:
    """Bag-of-words vectors: shared words -> similar vectors. Deterministic."""

    DIM = 512

    def _vector(self, text: str) -> np.ndarray:
        v = np.zeros(self.DIM)
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            v[sum(map(ord, word)) % self.DIM] += 1
        return v

    def embed_documents(self, texts):
        return normalize(np.array([self._vector(t) for t in texts]))

    def embed_query(self, text):
        return normalize(np.array([self._vector(text)]))[0]


class FakeGenerator:
    """Returns a canned reply and remembers the prompt it was given."""

    def __init__(self, reply: str):
        self.reply = reply
        self.last_prompt = None

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.reply


@pytest.fixture
def chunks():
    return load_known_issues("data/known_issues.md")


@pytest.fixture
def store(chunks):
    s = VectorStore(FakeEmbedder())
    s.add(chunks)
    return s
