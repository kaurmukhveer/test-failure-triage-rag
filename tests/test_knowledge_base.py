from triage.knowledge_base import split_into_chunks


def test_one_chunk_per_known_issue(chunks):
    assert len(chunks) == 12
    assert chunks[0].id == "KI-001"
    assert chunks[-1].id == "KI-012"


def test_chunk_has_title_and_full_text(chunks):
    first = chunks[0]
    assert first.title == "Test database not ready at startup"
    assert first.text.startswith("KI-001")
    assert "**Fix:**" in first.text


def test_ids_are_unique(chunks):
    ids = [c.id for c in chunks]
    assert len(ids) == len(set(ids))


def test_text_before_first_heading_is_ignored():
    md = "# Title\nintro text\n## KI-100: Example\nbody"
    result = split_into_chunks(md)
    assert len(result) == 1
    assert result[0].id == "KI-100"
    assert "intro text" not in result[0].text


def test_no_sections_gives_no_chunks():
    assert split_into_chunks("# Only a title") == []
