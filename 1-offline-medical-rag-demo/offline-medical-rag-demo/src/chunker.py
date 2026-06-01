"""Split documents into fixed-size overlapping chunks.

Overlap preserves context across chunk boundaries for better retrieval.
"""

from dataclasses import dataclass

from src.document_loader import Document


@dataclass
class TextChunk:
    """A chunk of text linked to its parent document."""

    chunk_id: str
    doc_id: str
    title: str
    text: str
    chunk_index: int


def chunk_documents(
    documents: list[Document],
    chunk_size: int = 400,
    chunk_overlap: int = 80,
) -> list[TextChunk]:
    """
    Split each document into fixed-size character chunks with overlap.

    Args:
        documents: Loaded source documents.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Characters shared between consecutive chunks.
    """
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[TextChunk] = []
    step = chunk_size - chunk_overlap

    for doc in documents:
        text = doc.text
        start = 0
        index = 0

        while start < len(text):
            piece = text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    TextChunk(
                        chunk_id=f"{doc.doc_id}__chunk_{index}",
                        doc_id=doc.doc_id,
                        title=doc.title,
                        text=piece,
                        chunk_index=index,
                    )
                )
                index += 1
            start += step

    return chunks
