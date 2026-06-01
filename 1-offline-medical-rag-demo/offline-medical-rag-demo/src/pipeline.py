"""Orchestrates the complete RAG workflow.

Index building: load documents → chunk → embed → persist FAISS index.
Query: embed question → retrieve context → generate grounded answer.
"""

from pathlib import Path

from src import config
from src.chunker import chunk_documents
from src.document_loader import load_documents
from src.embedder import Embedder
from src.generator import AnswerGenerator
from src.retriever import Retriever
from src.vector_store import FaissVectorStore, build_vector_store


class MedicalRAGPipeline:
    """Orchestrates document ingestion, retrieval, and generation."""

    def __init__(
        self,
        documents_dir: Path | None = None,
        index_dir: Path | None = None,
        embedding_model: str = config.EMBEDDING_MODEL,
        generation_model: str = config.GENERATION_MODEL,
        top_k: int = config.TOP_K,
    ) -> None:
        self.documents_dir = documents_dir or config.DOCUMENTS_DIR
        self.index_dir = index_dir or config.INDEX_DIR
        self.embedding_model = embedding_model
        self.generation_model = generation_model
        self.top_k = top_k

        self.embedder: Embedder | None = None
        self.retriever: Retriever | None = None
        self.generator: AnswerGenerator | None = None

    def build_index(self) -> dict:
        """Load documents, chunk, embed, and save FAISS index."""
        documents = load_documents(self.documents_dir)
        chunks = chunk_documents(
            documents,
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
        )

        self.embedder = Embedder(self.embedding_model)
        store = build_vector_store(chunks, self.embedder, self.index_dir)

        return {
            "documents": len(documents),
            "chunks": len(chunks),
            "index_path": str(self.index_dir),
            "vectors": store.index.ntotal,
        }

    def _ensure_loaded(self) -> None:
        if self.embedder is None:
            self.embedder = Embedder(self.embedding_model)
        if self.retriever is None:
            store = FaissVectorStore.load(self.index_dir)
            self.retriever = Retriever(self.embedder, store, top_k=self.top_k)
        if self.generator is None:
            self.generator = AnswerGenerator(
                self.generation_model,
                max_new_tokens=config.MAX_NEW_TOKENS,
            )

    def ask(self, question: str) -> dict:
        """Run retrieval + grounded generation for one question."""
        self._ensure_loaded()
        assert self.retriever is not None
        assert self.generator is not None

        retrieved = self.retriever.retrieve(question)
        context = self.retriever.format_context(
            retrieved,
            max_chars=config.MAX_CONTEXT_CHARS,
        )
        result = self.generator.generate_with_sources(question, retrieved, context)
        result["question"] = question
        result["context_preview"] = context[:500] + ("..." if len(context) > 500 else "")
        return result
