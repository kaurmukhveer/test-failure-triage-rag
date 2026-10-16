import pytest

from triage.vector_store import VectorStore
from tests.conftest import FakeEmbedder


def test_search_returns_k_results_best_first(store):
    results = store.search("No space left on device", k=3)
    assert len(results) == 3
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_obvious_query_finds_the_right_issue(store):
    top = store.search("No space left on device while writing build artifacts", k=1)[0]
    assert top.chunk.id == "KI-006"


def test_scores_are_cosine_similarities(store):
    for r in store.search("connection refused port 5432", k=12):
        assert -1.0001 <= r.score <= 1.0001


def test_search_on_empty_store_raises():
    with pytest.raises(ValueError):
        VectorStore(FakeEmbedder()).search("anything")
