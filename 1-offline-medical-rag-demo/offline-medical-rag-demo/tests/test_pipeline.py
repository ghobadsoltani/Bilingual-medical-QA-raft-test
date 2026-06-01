"""Example test structure for offline medical RAG demo.

Run with: pytest tests/test_pipeline.py -v
"""

import pytest
from pathlib import Path

from src.document_loader import load_documents, Document
from src.chunker import chunk_documents
from src.embedder import Embedder
from src.config import DOCUMENTS_DIR, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP


class TestDocumentLoader:
    """Test document loading functionality."""

    def test_load_documents_from_sample_data(self):
        """Verify that sample documents load correctly."""
        docs = load_documents(DOCUMENTS_DIR)
        assert len(docs) > 0, "Should load at least one document"
        assert all(isinstance(d, Document) for d in docs)

    def test_document_has_required_fields(self):
        """Verify document structure."""
        docs = load_documents(DOCUMENTS_DIR)
        doc = docs[0]
        assert doc.doc_id
        assert doc.title
        assert doc.text
        assert doc.source_path


class TestChunker:
    """Test document chunking."""

    def test_chunking_preserves_overlap(self):
        """Verify that consecutive chunks overlap as expected."""
        docs = [
            Document(
                doc_id="test",
                title="Test",
                text="a b c d e f g h i j k l m n o p q r s t u v w x y z",
                source_path="/tmp/test.txt",
            )
        ]
        chunks = chunk_documents(
            docs, chunk_size=10, chunk_overlap=5
        )
        assert len(chunks) > 1

        # Verify overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            overlap_text = chunks[i].text[-5:]
            next_start = chunks[i + 1].text[:5]
            # Chunks should share some boundary (character overlap)
            assert len(overlap_text) > 0 and len(next_start) > 0

    def test_chunk_has_metadata(self):
        """Verify chunk structure includes proper metadata."""
        docs = [
            Document(
                doc_id="test_doc",
                title="Test Title",
                text="sample text",
                source_path="/tmp/test.txt",
            )
        ]
        chunks = chunk_documents(docs)
        chunk = chunks[0]
        assert chunk.doc_id == "test_doc"
        assert chunk.title == "Test Title"
        assert chunk.chunk_index == 0


class TestEmbedder:
    """Test embedding generation."""

    def test_embedder_initializes(self):
        """Verify embedder loads without error."""
        embedder = Embedder(EMBEDDING_MODEL)
        assert embedder.dimension == 384  # MiniLM is 384-dim

    def test_embed_query_returns_vector(self):
        """Verify query embedding works and has correct shape."""
        embedder = Embedder(EMBEDDING_MODEL)
        vector = embedder.embed_query("test query")
        assert vector.shape == (384,)
        assert vector.dtype == "float32"

    def test_embed_texts_batch(self):
        """Verify batch embedding works."""
        embedder = Embedder(EMBEDDING_MODEL)
        texts = ["sample text 1", "sample text 2", "sample text 3"]
        vectors = embedder.embed_texts(texts)
        assert vectors.shape == (3, 384)
        assert vectors.dtype == "float32"


class TestIntegration:
    """End-to-end integration tests."""

    def test_documents_load_and_chunk(self):
        """Verify full load → chunk pipeline works."""
        docs = load_documents(DOCUMENTS_DIR)
        chunks = chunk_documents(docs, CHUNK_SIZE, CHUNK_OVERLAP)
        assert len(chunks) > len(docs), "Should create multiple chunks per document"
        assert all(chunk.chunk_id for chunk in chunks)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
