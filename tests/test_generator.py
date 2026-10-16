import json

import pytest

from triage.generator import build_prompt, parse_answer

VALID = {
    "issue_id": "KI-006",
    "confidence": "high",
    "likely_cause": "Disk full",
    "suggested_fix": "Clean up artifacts",
    "reasoning": "Log says no space left",
}


def test_prompt_contains_notes_log_and_rules(store):
    results = store.search("No space left on device", k=3)
    prompt = build_prompt("No space left on device", results)
    for r in results:
        assert r.chunk.id in prompt
    assert "<failure_log>\nNo space left on device\n</failure_log>" in prompt
    assert "Use ONLY the known-issue notes" in prompt


def test_valid_answer_is_parsed():
    answer = parse_answer(json.dumps(VALID), allowed_ids={"KI-006", "KI-004"})
    assert answer.issue_id == "KI-006"
    assert answer.confidence == "high"
    assert answer.warnings == []


def test_markdown_code_fences_are_stripped():
    raw = "```json\n" + json.dumps(VALID) + "\n```"
    assert parse_answer(raw, allowed_ids={"KI-006"}).issue_id == "KI-006"


def test_citation_not_retrieved_is_removed_with_warning():
    answer = parse_answer(json.dumps({**VALID, "issue_id": "KI-999"}), allowed_ids={"KI-006"})
    assert answer.issue_id is None
    assert "KI-999" in answer.warnings[0]


@pytest.mark.parametrize("value", [None, "null", ""])
def test_no_match_values_become_none(value):
    answer = parse_answer(json.dumps({**VALID, "issue_id": value}), allowed_ids={"KI-006"})
    assert answer.issue_id is None
    assert answer.warnings == []


def test_invalid_json_raises():
    with pytest.raises(json.JSONDecodeError):
        parse_answer("not json", allowed_ids=set())
