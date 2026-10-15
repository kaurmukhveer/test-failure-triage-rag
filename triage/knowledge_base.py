"""Load the known-issues knowledge base and cut it into chunks.

Analogy: the knowledge base is a textbook, and each chunk is one index card.
We cut on every "## " heading, so one known issue = one card.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chunk:
    id: str      # e.g. "KI-001"
    title: str   # e.g. "Test database not ready at startup"
    text: str    # the full section text that gets embedded


def split_into_chunks(markdown: str) -> list[Chunk]:
    """Split markdown into one chunk per '## ' section.

    A heading looks like: "## KI-001: Test database not ready at startup"
    Anything before the first '## ' (the document title) is skipped.
    """
    chunks = []
    sections = markdown.split("\n## ")[1:]  # [0] is the title area before the first issue

    for section in sections:
        heading, _, body = section.partition("\n")
        chunk_id, _, title = heading.partition(":")
        chunks.append(
            Chunk(
                id=chunk_id.strip(),
                title=title.strip(),
                text=f"{heading.strip()}\n{body.strip()}",
            )
        )
    return chunks


def load_known_issues(path: str | Path) -> list[Chunk]:
    """Read the markdown file and return its chunks."""
    markdown = Path(path).read_text(encoding="utf-8")
    return split_into_chunks(markdown)
