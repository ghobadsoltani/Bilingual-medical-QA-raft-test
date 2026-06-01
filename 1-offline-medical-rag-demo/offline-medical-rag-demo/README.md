# Offline Medical RAG Demo

A lightweight, **fully offline** retrieval-augmented generation system for answering questions over medical education documents. Built for learning and internship portfolios—modular Python, clean architecture, no cloud APIs.

> **⚠️ Disclaimer:** Educational use only. Not a medical device, not clinically validated. Always consult healthcare professionals for medical decisions.

## What It Does

```
Documents → Chunks → Embeddings → FAISS Index
                                      ↓
                              User Question
                                      ↓
                          Retrieve Top-K Chunks
                                      ↓
                       Generate Grounded Answer
```

This system demonstrates a complete RAG pipeline:
1. Load medical documents (plain `.txt` files)
2. Split into chunks with overlap for better retrieval
3. Create dense embeddings using [sentence-transformers](https://www.sbert.net/)
4. Store vectors in [FAISS](https://github.com/facebookresearch/faiss) for fast similarity search
5. Retrieve relevant chunks and generate answers using a local LLM

## Quick Start

```bash
# 1. Setup (2 minutes)
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# 2. Build index (one-time, ~1-3 mins)
python main.py --build-index

# 3. Ask questions
python main.py --question "What is type 2 diabetes?"
python main.py --question "How do I treat a burn?"

# 4. Web UI (optional)
streamlit run app.py
```

## Project Structure

```
offline-medical-rag-demo/
├── src/
│   ├── config.py                # Settings (chunk size, models, etc.)
│   ├── document_loader.py        # Load .txt files
│   ├── chunker.py               # Create overlapping chunks
│   ├── embedder.py              # SentenceTransformer wrapper
│   ├── vector_store.py          # FAISS + metadata persistence
│   ├── retriever.py             # Semantic search
│   ├── generator.py             # Local LLM generation
│   └── pipeline.py              # Orchestrates RAG flow
│
├── data/
│   ├── documents/               # Add your .txt files here
│   │   ├── diabetes_overview.txt
│   │   ├── first_aid_burns.txt
│   │   └── hypertension_basics.txt
│   └── index/                   # Auto-created (gitignored)
│
├── main.py                       # CLI: build-index & ask questions
├── app.py                        # Streamlit web UI
├── docs/
│   ├── INTERVIEW.md              # Interview Q&A prep
│   └── ARCHITECTURE.md           # Design patterns & scaling
│
└── tests/
    └── test_pipeline.py          # Example test structure
```

## Technical Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 | Fast, 384-dim, runs on CPU |
| **Search** | FAISS | Offline, no DB needed, fast |
| **Generation** | google/flan-t5-small | ~60M params, local, no APIs |
| **Storage** | Pickle + FAISS binary | Simple & efficient |

## Customization

Edit `src/config.py`:
```python
CHUNK_SIZE = 400              # Characters per chunk
CHUNK_OVERLAP = 80            # Overlap to preserve context
TOP_K = 3                     # Results per query
EMBEDDING_MODEL = "..."       # Try: BAAI/bge-large-en, etc.
GENERATION_MODEL = "..."      # Try: Mistral, Phi, etc.
```

Then rebuild: `python main.py --build-index`

## Key Design Choices

- **Modular architecture** — Each component is isolated and testable
- **Type hints throughout** — Better IDE support and fewer bugs
- **No external services** — Everything runs locally, offline-friendly
- **Lazy model loading** — First query is slower; rest are fast (no startup overhead)
- **Explicit error messages** — Users know what went wrong and how to fix it
- **Metadata persistence** — Track chunk IDs and similarity scores for transparency

## Limitations

- Small corpus (3 sample docs) — not real-world scale
- Character-level chunking — no semantic structure awareness
- Small LLM — can paraphrase poorly; not clinically validated
- No reranking or citation enforcement
- CPU-only by default (GPU support available)
- No evaluation suite (no automated quality metrics)

## Future Improvements

- [ ] Better chunking (recursive splitting by headers/paragraphs)
- [ ] Reranking layer (cross-encoder)
- [ ] Stronger local LLM (Mistral, Phi)
- [ ] Explicit citations (map answer sentences to chunks)
- [ ] Evaluation framework (test Q&A, faithfulness metrics)
- [ ] Dockerfile for reproducibility
- [ ] ChromaDB option (if persistence metadata needed)

## Interview Prep

**Deep-dive Q&A:** See [docs/INTERVIEW.md](docs/INTERVIEW.md)  
- What is RAG and why use it?
- Why FAISS vs. traditional databases?
- How do you reduce hallucinations?
- How would you scale to 1M+ documents?
- And 16+ more questions with confident answers

**Architecture & Design:** See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)  
- Design patterns used (Factory, Strategy, Template Method)
- SOLID principles applied
- Extensibility hooks (swap components)
- Scalability roadmap

## License

MIT

---

**Made for AI/ML internship portfolios.** Clean code, honest about tradeoffs, ready to explain.
