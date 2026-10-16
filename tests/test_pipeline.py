import json

from triage.pipeline import TriageAssistant
from tests.conftest import FakeGenerator


def test_pipeline_retrieves_then_generates(store):
    reply = json.dumps({"issue_id": "KI-006", "confidence": "high"})
    generator = FakeGenerator(reply)
    result = TriageAssistant(store, generator, k=3).triage("No space left on device")

    assert len(result.sources) == 3
    assert result.answer.issue_id == "KI-006"
    for source in result.sources:          # the LLM was shown exactly the retrieved notes
        assert source.chunk.id in generator.last_prompt


def test_pipeline_blocks_hallucinated_citation(store):
    generator = FakeGenerator(json.dumps({"issue_id": "KI-404", "confidence": "high"}))
    result = TriageAssistant(store, generator).triage("No space left on device")
    assert result.answer.issue_id is None
    assert result.answer.warnings


def test_pipeline_reports_no_match(store):
    generator = FakeGenerator(json.dumps({"issue_id": None, "confidence": "low"}))
    result = TriageAssistant(store, generator).triage("throughput 910 Mbps below 950")
    assert result.answer.issue_id is None
