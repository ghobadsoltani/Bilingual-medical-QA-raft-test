"""Semantic search over FAISS index.

Retrieves top-K chunks and formats them as context for generation.
"""

from dataclasses import dataclass

from src.chunker import TextChunk
from src.embedder import Embedder
from src.vector_store import FaissVectorStore


@dataclass
class RetrievedChunk:
    """A chunk returned by similarity search with score."""

    chunk: TextChunk
    score: float


class Retriever:
    """Semantic search over a built FAISS index."""

    def __init__(self, embedder: Embedder, vector_store: FaissVectorStore, top_k: int = 3):
        self.embedder = embedder
        self.vector_store = vector_store
        self.top_k = top_k

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        query_vector = self.embedder.embed_query(query)
        hits = self.vector_store.search(query_vector, top_k=self.top_k)
        return [RetrievedChunk(chunk=chunk, score=score) for chunk, score in hits]

    @staticmethod
    def format_context(retrieved: list[RetrievedChunk], max_chars: int) -> str:
        """Build a single context string from retrieved chunks."""
        parts: list[str] = []
        total = 0

        for item in retrieved:
            header = f"[{item.chunk.title} | score={item.score:.3f}]"
            block = f"{header}\n{item.chunk.text}"
            if total + len(block) > max_chars and parts:
                break
            parts.append(block)
            total += len(block)
            if total >= max_chars:
                break

        return "\n\n".join(parts)
