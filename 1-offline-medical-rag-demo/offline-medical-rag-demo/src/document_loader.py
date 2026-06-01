"""Load plain-text documents from data/documents/.

Handles UTF-8 encoding and optional 'Title:' headers for display names.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Document:
    """A single source document with metadata."""

    doc_id: str
    title: str
    text: str
    source_path: str


def _extract_title(text: str, fallback: str) -> str:
    """Use first 'Title:' line if present, else filename stem."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("title:"):
            return stripped.split(":", 1)[1].strip()
    return fallback


def load_documents(documents_dir: Path) -> list[Document]:
    """
    Load all .txt files from documents_dir.

    Raises:
        FileNotFoundError: If the directory does not exist.
        ValueError: If no .txt files are found.
    """
    if not documents_dir.is_dir():
        raise FileNotFoundError(f"Documents directory not found: {documents_dir}")

    paths = sorted(documents_dir.glob("*.txt"))
    if not paths:
        raise ValueError(f"No .txt files found in {documents_dir}")

    documents: list[Document] = []
    for path in paths:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        doc_id = path.stem
        title = _extract_title(text, fallback=doc_id.replace("_", " ").title())
        documents.append(
            Document(
                doc_id=doc_id,
                title=title,
                text=text,
                source_path=str(path),
            )
        )

    if not documents:
        raise ValueError("All document files were empty.")

    return documents
