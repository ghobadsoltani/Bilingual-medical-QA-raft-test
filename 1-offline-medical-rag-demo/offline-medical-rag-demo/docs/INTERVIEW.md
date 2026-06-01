# Interview Preparation Guide

## The 5-Minute Pitch

> "I built an offline RAG system for medical Q&A. It demonstrates end-to-end NLP: loading documents, creating embeddings, building a vector index, retrieving context, and generating grounded answers. Everything runs locally using FAISS and sentence-transformers—no cloud APIs. The code is modular and designed to be easy to explain."

---

## Core RAG Questions

### 1. What is RAG and why use it?

**Answer:**
> Retrieval-Augmented Generation combines document retrieval with generative models. Instead of relying on a model's parametric memory (which can be outdated or wrong), RAG first retrieves relevant documents from your corpus, then passes them as context to the generator. This grounds answers in sources, reduces hallucinations, and lets you update knowledge by editing documents—no retraining needed.
>
> For medical content, this is critical: answers must be traceable to reliable sources.

---

### 2. Why FAISS instead of a database?

**Answer:**
> FAISS (Facebook AI Similarity Search) provides lightning-fast vector search on CPU. For a demo, this is ideal: no server setup, instant startup, fully offline, beginner-friendly. Trade-off: approximate search (good recall, not perfect). For production at scale (1M+ vectors), you'd consider Milvus, Weaviate, or Pinecone. But FAISS teaches the core concepts and is sufficient for portfolio work.

---

### 3. How do you reduce hallucinations?

**Answer:**
> Multiple layers:
> 1. **Context injection** — Only pass retrieved chunks to the LLM; the prompt explicitly says "answer only from context"
> 2. **Small model** — flan-t5-small is less prone to verbose hallucinations than larger models
> 3. **Source transparency** — Return which chunk each answer came from; this encourages accountability
> 4. **Graceful fallback** — If no relevant context found, return a transparent message
>
> This is the baseline. Advanced strategies: reranking (filter low-quality hits), citation enforcement (require sentences to map to chunks), and evaluation harnesses (test against ground truth).

---

### 4. What happens if retrieval fails?

**Answer:**
> If the query has no semantic match in the corpus, FAISS returns empty or low-scoring results. The retriever passes empty/minimal context to the generator. The generator's prompt says "if context is insufficient, say you cannot answer"—so it returns a fallback message instead of hallucinating. The UI also shows which sources were retrieved (empty = user knows search failed).

---

### 5. How would you scale this?

**Answer:**
> Key improvements:
> 1. **Larger corpus** — FAISS handles millions of vectors, but chunking strategy becomes critical
> 2. **Structure-aware chunking** — Split by paragraphs/headers, preserve metadata (preserves more context)
> 3. **Reranking** — Cross-encoder to re-score FAISS top-K (usually 5-10% quality uplift)
> 4. **Stronger LLM** — Mistral or Phi instead of flan-t5-small
> 5. **Evaluation harness** — Test Q&A set + metrics (retrieval recall, answer faithfulness)
> 6. **Caching & async** — Cache embeddings, serve with async API (FastAPI)
> 7. **Fine-tuning** — If domain-specific, fine-tune embedder or generator on your corpus
> 8. **Production hardening** — Monitoring, logging, compliance (HIPAA if PHI involved)

---

## Technical Deep-Dives

### 6. Why normalize vectors before FAISS search?

**Answer:**
> FAISS's IndexFlatIP (inner product index) does dot product search. Normalized vectors make dot product equal to cosine similarity:
> ```
> cos_similarity(A, B) = A·B / (|A| × |B|)
> If |A| = |B| = 1, then cos_similarity = A·B
> ```
> So we normalize all vectors to unit length, then use inner product search. This is both mathematically equivalent to cosine similarity and much faster.

---

### 7. How do you persist chunks alongside the FAISS index?

**Answer:**
> FAISS only stores vectors. Solution:
> - Keep a parallel Python list of `TextChunk` dataclass objects (with metadata: doc_id, title, text)
> - Pickle this list alongside the FAISS binary (simple, fast serialization)
> - Store dimension + vector count in JSON for validation
> - On load: read FAISS binary + pickle; the index order matches the list order
>
> For 1M+ vectors, use a proper vector DB with built-in metadata (Milvus, Weaviate) or PostgreSQL with pgvector.

---

### 8. Why character-level chunking instead of semantic splitting?

**Answer:**
> Character-level chunking is simple and deterministic (no surprises). Downsides: can split sentences/ideas awkwardly.
>
> Semantic splitting (by paragraphs, headers) is better but more complex. For a demo, character-level with overlap is acceptable. The overlap preserves context across boundaries. In production, I'd use recursive splitting: split by paragraphs → sentences → tokens (until under chunk_size).

---

### 9. Why lazy initialization in the pipeline?

**Answer:**
> Models are heavy (~500 MB–1 GB downloaded first run). Lazy loading defers this cost:
> ```python
> def _ensure_loaded(self):
>     if self.embedder is None:
>         self.embedder = Embedder(...)  # Load only when needed
> ```
> Benefits: Pipeline instantiates instantly; first query loads models (slow, 5–10 sec); subsequent queries are fast (2–3 sec). No startup overhead. Better UX for CLI and Streamlit.

---

### 10. What type hints are used and why?

**Answer:**
> Full type hints:
> ```python
> def retrieve(self, query: str) -> list[RetrievedChunk]:
> def embed_texts(self, texts: list[str]) -> np.ndarray:
> ```
> Benefits:
> - IDE autocomplete works (faster development)
> - Type checker (mypy, pyright) catches errors early
> - Documentation is executable (types describe contracts)
> - Easier for colleagues to understand code
>
> Python best practice, especially for production systems.

---

## Design & Architecture

### 11. What design patterns are used?

**Answer:**
> 1. **Factory pattern** (vector_store.py) — `build_vector_store()` encapsulates index creation
> 2. **Strategy pattern** (retriever.py) — Inject vector store strategy; easy to swap FAISS ↔ ChromaDB
> 3. **Template method** (pipeline.py) — `build_index()` and `ask()` define algorithm skeletons
> 4. **Lazy initialization** (pipeline.py) — Defer expensive model loading
> 5. **Dataclass contracts** (throughout) — Clear data flow (Document → Chunk → Embedding)
> 6. **Configuration object** (config.py) — Single source of truth for constants

---

### 12. How is modularity achieved?

**Answer:**
> Each component has one job:
> - `document_loader.py` → Load documents
> - `chunker.py` → Split into chunks
> - `embedder.py` → Create embeddings
> - `vector_store.py` → Store & search
> - `retriever.py` → Semantic search logic
> - `generator.py` → Generate answers
> - `pipeline.py` → Orchestrate (glue it together)
>
> Benefits:
> - Each module is testable independently (mock dependencies)
> - Easy to swap components (e.g., FAISS → ChromaDB, flan-t5 → Mistral)
> - Clear error boundaries
> - Reusable in other projects

---

### 13. How would you evaluate this system?

**Answer:**
> **Retrieval metrics** (does search find relevant docs?):
> - Recall@K: % of relevant docs in top K
> - MRR (Mean Reciprocal Rank): average position of first correct result
> - NDCG: normalized discounted cumulative gain (accounts for ranking order)
>
> **Generation metrics** (is the answer good?):
> - ROUGE: n-gram overlap with reference answers
> - BERTScore: semantic similarity (better than ROUGE)
> - Faithfulness: is answer grounded in context? (classifier or human)
> - Accuracy: is the answer correct? (compare to expert baseline)
>
> For a quick demo: human eval on 10–20 test questions (fast, builds intuition).

---

### 14. What are failure modes?

**Answer:**
> 1. **Retriever fails** → Query has no semantic match → FAISS returns noise → nonsensical answer
> 2. **Context overwhelm** → Too many chunks → context truncated → incomplete answer
> 3. **Hallucination** → LLM adds facts despite "answer-only-from-context" instruction
> 4. **Ambiguous query** → User question is vague → retriever confused
> 5. **Model bias** → LLM reflects internet data biases (gender, medical stereotypes)
> 6. **Outdated corpus** → Documents not updated → stale knowledge
>
> Mitigations: test suite, reranking, stricter prompting, corpus reviews, logging + monitoring.

---

### 15. Why is documentation important?

**Answer:**
> Good documentation:
> - Lets others (and future you) understand intent without reading code
> - Shows you care about communication (important for teams)
> - Makes code reviewable ("why did you choose X?")
> - Reduces bugs (unclear assumptions → mistakes)
>
> For this project: docstrings, type hints, README, and architecture docs. Not excessive, but clear.

---

## Confidence Boosters

**If asked something unexpected:**

✅ *"That's a great question. Here's my thinking..."* → Show reasoning, not just a gap  
✅ *"I'd measure that empirically by..."* → Show you think about tradeoffs  
✅ *"In production, we'd handle this differently..."* → Show scalability thinking  
✅ *"Honestly, X is a known limitation; Y is industry-standard for that..."* → Acknowledge boundaries  

❌ *Avoid:* "I just used ChatGPT to explain this..."  
❌ *Avoid:* "I'm not sure, but probably..." (instead: "I'd test/measure to decide")  
❌ *Avoid:* "This is the best approach" (frame as tradeoffs)  

---

## Practice Schedule

**Day 1:** Know the 30-second pitch + project structure  
**Day 2:** Understand each module's job + data flow  
**Day 3:** Study design patterns + scaling roadmap  
**Day 4:** Practice the 5-minute demo on your laptop  
**Day 5:** Mock interview with a friend; answer 5 random Qs  
**Day 6:** Review this guide + edge cases  
**Interview day:** Relax, walk through code, ask clarifying Qs if confused  

---

## Example Interview Flow (30 mins)

1. **Intro (2 mins):** "I built a RAG system for medical Q&A..."
2. **Demo (3 mins):** Show `python main.py --build-index`, then `--question "..."`, then answer
3. **Code walkthrough (10 mins):**
   - Show README + project structure
   - Open `src/pipeline.py` → explain orchestration
   - Open `src/vector_store.py` → explain FAISS + metadata
   - Open `src/generator.py` → explain prompting
4. **Technical questions (10 mins):** Use questions 1–6 above
5. **Design questions (3 mins):** Ask about limitations, scaling
6. **Wrap-up (2 mins):** "Any questions for me?"

---

## Good Luck!

This is a real system that teaches the fundamentals. Know your code, explain tradeoffs honestly, and show enthusiasm for the problem domain. You've got this! 🚀

