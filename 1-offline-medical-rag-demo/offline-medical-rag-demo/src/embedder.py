"""Dense embeddings using sentence-transformers.

Provides ~384-dimensional vectors for similarity search via FAISS.
"""

import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    """Wrapper around a local SentenceTransformer model."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    @property
    def dimension(self) -> int:
        return int(self.model.get_sentence_embedding_dimension())

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Return float32 array of shape (n_texts, dimension)."""
        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 8,
            normalize_embeddings=False,
        )
        return np.asarray(vectors, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """Return a single query vector of shape (dimension,)."""
        vector = self.embed_texts([query])[0]
        return vector
