"""Grounded answer generation with a local LLM.

Prompt-based generation constrained to answer only from context.
Returns both answer and source metadata.
"""

from transformers import pipeline

from src.retriever import RetrievedChunk


class AnswerGenerator:
    """Grounded answer generation with a small seq2seq model."""

    def __init__(self, model_name: str, max_new_tokens: int = 128) -> None:
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self._pipe = None

    def _get_pipeline(self):
        if self._pipe is None:
            self._pipe = pipeline(
                "text2text-generation",
                model=self.model_name,
                device=-1,  # CPU; change to 0 for GPU if available
            )
        return self._pipe

    @staticmethod
    def build_prompt(question: str, context: str) -> str:
        return (
            "You are a helpful medical education assistant. "
            "Answer ONLY using the context below. "
            "If the context does not contain enough information, say you cannot answer from the provided documents. "
            "Do not give personal medical advice.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

    def generate(self, question: str, context: str) -> str:
        if not context.strip():
            return (
                "No relevant context was retrieved. "
                "Try rephrasing your question or rebuild the index."
            )

        prompt = self.build_prompt(question, context)
        generator = self._get_pipeline()
        outputs = generator(
            prompt,
            max_new_tokens=self.max_new_tokens,
            do_sample=False,
            truncation=True,
        )
        answer = outputs[0]["generated_text"].strip()
        return answer

    def generate_with_sources(
        self,
        question: str,
        retrieved: list[RetrievedChunk],
        context: str,
    ) -> dict:
        answer = self.generate(question, context)
        sources = [
            {
                "doc_id": item.chunk.doc_id,
                "title": item.chunk.title,
                "chunk_id": item.chunk.chunk_id,
                "score": round(item.score, 4),
            }
            for item in retrieved
        ]
        return {"answer": answer, "sources": sources}
