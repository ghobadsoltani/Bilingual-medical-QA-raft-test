# Interview Deep Dive — Extended Q&A Guide

This document provides 15+ common follow-up questions and concise, confident answers. Study these alongside the code to ace technical discussions.

---

## 🎯 Core RAG Concepts

### 1. **Explain the RAG pipeline in 30 seconds.**

**Answer:**
> RAG has three steps:
> 1. **Retrieve** — Given a user question, find the K most relevant documents/chunks in your corpus using semantic search
> 2. **Augment** — Combine the question + retrieved documents into a single prompt
> 3. **Generate** — Pass the augmented prompt to a language model, which produces a grounded answer
>
> This approach leverages the retriever's strength (finding relevant info) and the generator's strength (composing fluent answers), while reducing hallucinations by forcing the model to cite sources.

---

### 2. **What's the difference between dense and sparse retrieval?**

**Answer:**
> **Sparse (keyword-based):** Uses BM25, TF-IDF, or inverted indexes. Fast, interpretable, works well for exact phrase matches. Downsides: misses semantic synonyms ("car" ≠ "vehicle").
>
> **Dense (semantic):** Uses embeddings (like sentence-transformers) to find semantically similar text, even if keywords don't overlap. Slower (but fast enough with FAISS) and more powerful. This project uses dense.
>
> **Hybrid:** Best of both worlds—combine keyword search + dense search, re-rank. Future improvement.

---

### 3. **Why normalize vectors before FAISS search?**

**Answer:**
> Normalized vectors map cosine similarity to inner product (dot product). That is:
> ```
> cos_sim(A, B) = A·B / (|A| |B|)  ←→  if |A|=|B|=1, then cos_sim(A, B) = A·B
> ```
>
> FAISS's IndexFlatIP (inner product) is optimized for dot product. So we normalize, then use IndexFlatIP, and get cosine similarity. This is faster than explicit cosine distance and is standard practice.

---

### 4. **Why use small models (MiniLM, flan-t5-small)?**

**Answer:**
> Trade-offs:
> - **Small = fast + low memory** → Portfolio demo, CPU-friendly, instant startup
> - **Large = higher quality** → Better at nuance, fewer errors
>
> For this demo, small is ideal. For production medical advice, you'd use larger + fine-tuned models. The code is model-agnostic; swapping models is just changing `config.py`.

---

### 5. **What is chunk overlap and why does it matter?**

**Answer:**
> Chunking a 10K-character document into 400-char chunks with no overlap can split important context. E.g., a sentence might be split across two chunks, losing coherence.
>
> **With overlap:** The last 80 chars of chunk N become the first 80 chars of chunk N+1. This preserves context continuity. Trade-off: more vectors to store/search (redundancy), but better retrieval quality.
>
> In this project: `CHUNK_SIZE=400, CHUNK_OVERLAP=80 → step=320`. Tunable in `config.py`.

---

## 🔍 Technical Deep Dives

### 6. **Walk me through building the FAISS index.**

**Answer:**
> In `pipeline.py.build_index()`:
> 1. Load documents → `load_documents()` returns `Document` objects (title, text)
> 2. Chunk docs → `chunk_documents()` returns `TextChunk` objects (id, text, metadata)
> 3. Embed all chunks → `embedder.embed_texts()` returns float32 array of shape `(n_chunks, 384)`
> 4. Create FAISS index → `FaissVectorStore()` initializes IndexFlatIP with dimension 384
> 5. Add vectors + metadata → `store.add_chunks(chunks, embeddings)` normalizes and inserts
> 6. Persist → `store.save()` writes FAISS binary + pickle + JSON metadata to disk
>
> First run downloads models (~2–3 mins); subsequent runs are instant.

---

### 7. **How do you persist chunk metadata alongside the FAISS index?**

**Answer:**
> FAISS stores only vectors; metadata isn't built-in. Solution:
> - **Metadata as parallel array** → Keep a Python list of `TextChunk` objects in memory
> - **Save to pickle** → `pickle.dump(chunks, "chunks.pkl")` — safe, portable
> - **Metadata JSON** → Store dimension and vector count for validation
>
> On load: re-read FAISS binary + pickle. The index order matches the list order, so `index.search(...)[1][i]` gives the i-th chunk. This is simple and scales to ~1M vectors.
>
> *Production note:* For 100M+ vectors, use a real vector DB (Milvus, Weaviate) with built-in metadata.

---

### 8. **What happens if two chunks have identical text?**

**Answer:**
> Nothing special. FAISS indexes both as separate vectors. When retrieving:
> - Both will have identical embeddings (same high score)
> - Both will be returned if TOP_K ≥ 2
> - The generator sees both in context and has some redundancy
>
> This is fine—we don't deduplicate. For a real system, you might:
> - De-duplicate chunks before embedding
> - Use a reranker to remove near-duplicates
> - Log similarity stats to monitor corpus quality

---

### 9. **Why pickle for chunk storage and not JSON?**

**Answer:**
> Good question. JSON would be human-readable and more portable:
> - ✅ JSON: readable, version-stable, language-agnostic
> - ✅ Pickle: fast, compact, preserves Python dataclasses exactly
>
> I chose pickle for speed (large corpus could have 100K+ chunks). For a real project, I'd use JSON or Parquet + an optimized format (Arrow). Pickle is sufficient here and avoids string serialization overhead.

---

### 10. **What's your prompting strategy to reduce hallucinations?**

**Answer:**
> See `generator.py.build_prompt()`:
> ```python
> "You are a helpful medical education assistant. "
> "Answer ONLY using the context below. "
> "If the context does not contain enough information, "
> "say you cannot answer from the provided documents. "
> "Do not give personal medical advice.\n\n"
> f"Context:\n{context}\n\n"
> f"Question: {question}\n\n"
> "Answer:"
> ```
>
> Key elements:
> 1. **Role** — "medical education assistant" (narrows scope)
> 2. **Instruction** — "ONLY using context below" (explicit constraint)
> 3. **Graceful fallback** — "cannot answer" ≠ fabrication
> 4. **Boundary** — "not medical advice" (liability protection)
>
> This is **instruction prompting**, not perfect but standard. Advanced: use in-context examples (few-shot) or fine-tuning.

---

### 11. **How do you handle questions outside your document scope?**

**Answer:**
> Three layers:
>
> 1. **Retriever** → If query is out-of-scope (e.g., "quantum computing"), FAISS returns low-scoring or zero matches
> 2. **Context check** → If context is empty, `generator.generate()` returns a fallback message
> 3. **Prompt instruction** → Even if retriever finds something tangentially related, the prompt says "answer only from context"
>
> Example: User asks "Quantum computing?" → retriever returns nothing → context is empty → user gets "I cannot answer from the provided documents."
>
> *Better approach:* Set a similarity threshold (e.g., top score < 0.3 → reject), or use a classifier to detect out-of-scope queries.

---

## 🏗️ Architecture & Design

### 12. **Why separate `retriever.py` and `vector_store.py`?**

**Answer:**
> **Single Responsibility Principle:**
> - `vector_store.py` = **"How do I store and search vectors?"** (FAISS mechanics, persistence)
> - `retriever.py` = **"How do I find relevant context for a query?"** (search logic, formatting, scoring)
>
> Separating them makes code testable and reusable:
> - Swap FAISS for Milvus/ChromaDB without touching retriever logic
> - Swap retriever strategy (e.g., add reranking) without touching vector store
>
> This is clean architecture / hexagonal design.

---

### 13. **What's the trade-off between modular code and performance?**

**Answer:**
> Modular code has function call overhead (~5–10% in Python), but buys maintainability, testability, and reusability.
>
> For this demo: **correctness > performance**. RAG latency is dominated by:
> 1. Model download (first run, one-time)
> 2. Embedding inference (retrieval)
> 3. LLM generation (answer)
>
> Function call overhead is noise. In production, you'd profile to find real bottlenecks (usually model inference, not function calls).

---

### 14. **How would you optimize for latency?**

**Answer:**
> If query latency is critical:
> 1. **Cache embeddings** — If the same queries repeat, cache their vectors
> 2. **Batch embedding** — Process multiple chunks at once
> 3. **FAISS GPU** — Use GPU IndexGPU if available (nvidia-faiss)
> 4. **Approximate search** — Use IndexIVF (faster but less accurate) instead of IndexFlatIP
> 5. **Model quantization** — Quantize embedder/generator for faster inference
> 6. **Fewer TOP_K** — Reduce `TOP_K=3` to `TOP_K=1` (trade accuracy for speed)
> 7. **Async generation** — In UI, load answer while user reviews sources (Streamlit doesn't need this; web server would)
>
> This project prioritizes simplicity; optimization is left to production scaling.

---

### 15. **What would you change if you had to handle 1M documents?**

**Answer:**
> Current design breaks at scale:
>
> 1. **FAISS index size** → FAISS handles 1M vectors fine, but IndexFlatIP becomes slow (linear scan). Solution: Use approximate index like IndexIVF or Hierarchical Navigable Small World (HNSW). FAISS supports this.
>
> 2. **Metadata persistence** → Pickle + list works for 100K chunks. At 1M, use Parquet or DB. Solution: SQLite or PostgreSQL with vector columns.
>
> 3. **Chunking strategy** → Character-level chunking is wasteful at scale. Solution: Recursive splitting by paragraph/header, preserve doc structure.
>
> 4. **Memory** → Keep entire corpus in RAM? Not feasible. Solution: Stream chunks, use vector DB's sharding, or distributed FAISS (faiss-bin / faiss-distributed).
>
> 5. **Model inference** → Single-threaded Python becomes bottleneck. Solution: Batch inference, multi-GPU, Triton Inference Server.
>
> 6. **Evaluation** → No test suite for quality. Solution: Build evaluation harness (test Q&A set, retrieval recall, answer grounding metrics).
>
> Takeaway: Modular design makes this refactoring easier (swap components), but the scale jump is significant.

---

## 🧪 Testing & Debugging

### 16. **How do you debug a bad answer?**

**Answer:**
> Four-step diagnostic:
>
> 1. **Check retrieval** — Are relevant chunks in the top-K results? If not, retriever failed (embedding/similarity issue).
> 2. **Check context** — Did the retriever format context correctly? Is the relevant info truncated?
> 3. **Check prompt** — Is the prompt clear? Did the instruction reach the model?
> 4. **Check model** — Is the LLM overfitting, hallucinating, or just low-quality?
>
> In code: Inspect `result["sources"]` and `result["context_preview"]` from the UI. High scores + correct context = generator problem. Low scores or missing chunks = retriever problem.

---

### 17. **What metrics would you use to evaluate RAG quality?**

**Answer:**
> **Retrieval metrics:**
> - Recall@K: % of relevant docs in top K results (binary judgment needed)
> - MRR (Mean Reciprocal Rank): Average position of first correct result
> - NDCG: Discounted cumulative gain (accounts for ranking order)
>
> **Generation metrics:**
> - ROUGE: Overlap between generated and reference answers (lexical, not semantic)
> - BLEU: Precision of n-grams
> - BERTScore: Semantic similarity (better than ROUGE for NLG)
> - Human eval: Relevance, grounding, clarity (gold standard, expensive)
>
> **Combined (end-to-end):**
> - Faithfulness: Is the answer grounded in context? (human or classifier-based)
> - Accuracy: Is the answer correct? (compare to expert baseline)
>
> For a quick demo: human eval on 10–20 questions (fast, builds intuition).

---

### 18. **What are the failure modes of your system?**

**Answer:**
> 1. **Retriever fails** → Query has no semantic match in corpus → returns irrelevant chunks → generator produces nonsense grounded in wrong context
> 2. **Context overwhelm** → Many chunks retrieved, context truncated, answer is incomplete
> 3. **Hallucination** → Model adds facts not in context despite prompt instruction (especially with larger models)
> 4. **Ambiguous query** → User question is vague → retriever can't pinpoint what's needed
> 5. **Model bias** → LLM trained on internet data, reflects societal biases (e.g., gender, race, medical misconceptions)
> 6. **Outdated corpus** → Medical knowledge evolves; old documents give obsolete advice
>
> Mitigation:
> - Test suite + human eval
> - Reranking to filter low-quality hits
> - Stricter prompting + citation enforcement
> - Regular corpus updates + expert review
> - Logging + monitoring for bias/errors

---

## 🎬 Interview Finale

### 19. **If you could spend one more week on this, what would you build?**

**Answer:**
> Priority order:
>
> 1. **Evaluation harness** (1–2 days) — Fixed Q&A test set + metrics (retrieval recall, answer grounding). Gives concrete proof of quality.
> 2. **Reranking** (1–2 days) — Cross-encoder to re-score FAISS results. Usually 5–10% quality uplift with minimal latency cost.
> 3. **Better chunking** (1–2 days) — Recursive split by paragraphs, preserve titles/structure. Often 10–20% retrieval quality improvement.
> 4. **Unit tests + CI** (1 day) — Pytest suite + GitHub Actions. Catches regressions.
> 5. **Dockerfile + deployment** (1 day) — Containerize for reproducibility & sharing.
>
> Why in this order? Evaluation is highest ROI (shows real quality). Reranking is next (straightforward, high-impact). Chunking requires more thought. Tests + deployment are infrastructure (good practice, lower impact on quality).

---

### 20. **What did you learn building this?**

**Answer:**
> 1. **End-to-end ownership** — Building a full system (not just a notebook) requires thinking about UX, errors, performance, and deployment. Hard but valuable.
> 2. **Modular design pays off** — Each component is testable and swappable. Without it, scaling gets messy.
> 3. **Prompting is an art** — Small wording changes in the prompt can shift answer quality significantly. No silver bullet.
> 4. **Metadata matters** — Storing chunk IDs + scores lets me trace errors back to source. Transparency is trust.
> 5. **Trade-offs are everywhere** — Small vs. large models, dense vs. sparse search, chunk size, TOP_K, etc. No one-size-fits-all answer; depends on use case.
> 6. **Documentation is code** — The README is as important as the code. Future me (or you) will appreciate it.

---

## 🎤 Confidence Boosters

**If asked something you don't know:**
- "That's a great question. I haven't explored that yet, but here's my intuition..." → Show reasoning, not just a gap.
- "In a real deployment, I'd [profile/test/measure] to decide..." → Show you think about tradeoffs.
- "Honestly, X is a known limitation of this approach. Industry-standard solutions are [Y, Z]..." → Acknowledge boundaries.

**Phrases to avoid:**
- ❌ "I just used ChatGPT to explain this..."
- ❌ "I'm not sure, but probably..." (instead: "I'd measure/test to find out")
- ❌ "This is the best approach" (always frame as tradeoff)

**Phrases to use:**
- ✅ "Here's the trade-off: [speed vs. accuracy / simplicity vs. power]..."
- ✅ "In production, you'd [scale / test / monitor] by doing X..."
- ✅ "I chose this because [code clarity / performance / maintainability]..."
- ✅ "If you wanted to optimize for [Y], I'd [approach]..."

---

## 📝 Practice Flow for Your Interview

1. **5 min**: Introduce the project + one demo query
2. **5 min**: Walk through the code (show vector_store.py + pipeline.py)
3. **10 min**: Answer technical questions (use this guide!)
4. **5 min**: Discuss limitations + what you'd improve
5. **5 min**: Answer interviewers' project-specific questions

**Total: ~30 mins (can expand or condense based on interest)**

---

## 🚀 Final Tips

- ✅ Practice the 30-second pitch (about RAG)
- ✅ Know the code cold (be ready to explain any line)
- ✅ Have a laptop ready to show it running
- ✅ Print this Q&A guide, review the night before
- ✅ Stay honest about tradeoffs (shows maturity)
- ✅ Show enthusiasm for the problem domain (medical AI, safety, etc.)

---

**Good luck! 🎯**

