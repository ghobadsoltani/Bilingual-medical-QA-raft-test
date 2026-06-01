"""FAISS vector index with chunk metadata persistence.

Stores vectors and chunk objects separately for transparency.
Uses L2-normalization for cosine similarity via inner product.
"""

import json
import pickle
from dataclasses import asdict
from pathlib import Path

import faiss
import numpy as np

from src.chunker import TextChunk
from src.embedder import Embedder


def _normalize(vectors: np.ndarray) -> np.ndarray:
    """L2-normalize rows for cosine similarity via inner product."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return vectors / norms


class FaissVectorStore:
    """In-memory FAISS index with save/load support."""

    def __init__(self, dimension: int) -> None:
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.chunks: list[TextChunk] = []

    def add_chunks(self, chunks: list[TextChunk], embeddings: np.ndarray) -> None:
        if len(chunks) != embeddings.shape[0]:
            raise ValueError("Number of chunks must match number of embeddings.")
        normalized = _normalize(embeddings.astype(np.float32))
        self.index.add(normalized)
        self.chunks.extend(chunks)

    def search(self, query_embedding: np.ndarray, top_k: int) -> list[tuple[TextChunk, float]]:
        if self.index.ntotal == 0:
            return []

        query = _normalize(query_embedding.astype(np.float32).reshape(1, -1))
        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query, k)

        results: list[tuple[TextChunk, float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            results.append((self.chunks[idx], float(score)))
        return results

    def save(self, index_dir: Path) -> None:
        index_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(index_dir / "index.faiss"))

        payload = [asdict(chunk) for chunk in self.chunks]
        with open(index_dir / "chunks.pkl", "wb") as handle:
            pickle.dump(payload, handle)

        meta = {
            "dimension": self.dimension,
            "num_vectors": self.index.ntotal,
        }
        (index_dir / "meta.json").write_text(
            json.dumps(meta, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, index_dir: Path) -> "FaissVectorStore":
        meta_path = index_dir / "meta.json"
        if not meta_path.exists():
            raise FileNotFoundError(
                f"Index not found at {index_dir}. Run: python main.py --build-index"
            )

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        store = cls(dimension=meta["dimension"])
        store.index = faiss.read_index(str(index_dir / "index.faiss"))

        with open(index_dir / "chunks.pkl", "rb") as handle:
            payload = pickle.load(handle)
        store.chunks = [TextChunk(**item) for item in payload]
        return store


def build_vector_store(
    chunks: list[TextChunk],
    embedder: Embedder,
    index_dir: Path,
) -> FaissVectorStore:
    """Embed all chunks and persist a FAISS index."""
    texts = [chunk.text for chunk in chunks]
    embeddings = embedder.embed_texts(texts)

    store = FaissVectorStore(dimension=embedder.dimension)
    store.add_chunks(chunks, embeddings)
    store.save(index_dir)
    return store
