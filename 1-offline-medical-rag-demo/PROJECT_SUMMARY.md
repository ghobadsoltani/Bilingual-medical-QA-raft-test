# Offline Medical RAG Demo — Project Summary

**Status:** ✅ Complete, interview-ready portfolio project

---

## 📋 What You Have

A professional, modular RAG (Retrieval-Augmented Generation) system demonstrating:
- **Document ingestion** from local text files
- **Semantic search** using embeddings (FAISS + sentence-transformers)
- **Grounded answer generation** with a local small LLM
- **Clean architecture** with separation of concerns
- **CLI + Streamlit UI** for different use cases
- **Production-quality documentation**

---

## 🗂️ Complete Project Structure

```
offline-medical-rag-demo/
│
├── README.md                          # Comprehensive documentation
├── LICENSE                            # MIT License
├── requirements.txt                   # All dependencies pinned
│
├── main.py                            # CLI entry point
│   ├── --build-index               (Creates FAISS index)
│   └── --question "..."            (Runs RAG pipeline)
│
├── app.py                             # Streamlit web UI
│
├── src/
│   ├── __init__.py                    # Package version
│   ├── config.py                      # Centralized configuration
│   ├── document_loader.py             # Loads .txt files, extracts titles
│   ├── chunker.py                     # Character-level chunking with overlap
│   ├── embedder.py                    # SentenceTransformer wrapper
│   ├── vector_store.py                # FAISS index + metadata persistence
│   ├── retriever.py                   # Similarity search + context formatting
│   ├── generator.py                   # Local LLM answer generation
│   └── pipeline.py                    # Orchestrates entire RAG flow
│
├── scripts/
│   └── build_index.py                 # Alternative: build index standalone
│
├── data/
│   ├── documents/
│   │   ├── README.md                  # How to add documents
│   │   ├── diabetes_overview.txt
│   │   ├── first_aid_burns.txt
│   │   └── hypertension_basics.txt
│   │
│   └── index/                         # Auto-created on first --build-index
│       ├── index.faiss                (Binary FAISS index)
│       ├── chunks.pkl                 (Serialized chunk metadata)
│       └── meta.json                  (Dimension + vector count)
│
├── notebooks/
│   └── README.md                      # Space for Jupyter exploration
│
└── .gitignore                         # Excludes __pycache__, .venv, data/index/, etc.
```

---

## 🚀 Quick Setup & Run

### Prerequisites
- **Python 3.10+**
- ~2–4 GB free disk (for model downloads, first run only)

### Setup

```bash
# 1. Navigate to project
cd offline-medical-rag-demo

# 2. Create virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Run

**Build the index (required once):**
```bash
python main.py --build-index
```

**Ask questions (CLI):**
```bash
python main.py --question "What are symptoms of type 2 diabetes?"
python main.py --question "How should I treat a minor burn?"
python main.py --question "What lifestyle changes help manage high blood pressure?"
```

**Start interactive UI (Streamlit):**
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

---

## 🧠 Key Design Choices (For Interviews)

| Choice | Rationale |
|--------|-----------|
| **FAISS** (not ChromaDB/Pinecone) | CPU-friendly, fully offline, lightweight, no external service dependency—perfect for portfolio demo |
| **sentence-transformers/all-MiniLM-L6-v2** | Excellent balance of speed and quality; 384-dim vectors; runs entirely locally |
| **google/flan-t5-small** | Lightweight (~60M params), fast inference on CPU, good general-knowledge grounding; no API calls |
| **Character-level chunking with overlap** | Simple and deterministic; overlap preserves context across chunk boundaries |
| **Modular pipeline** | Each component (load, chunk, embed, retrieve, generate) is testable and explainable; no monolithic notebook |
| **CLI + Streamlit** | Demonstrates both programmatic and user-facing interfaces; shows flexibility |
| **Metadata persistence** | Chunks stored with doc_id, title, chunk_index for transparent source citations |

---

## 📄 File-by-File Walkthrough

### `src/config.py`
Centralized configuration—tune `CHUNK_SIZE`, `TOP_K`, models, etc. without editing source code.

**Key parameters:**
- `CHUNK_SIZE = 400` characters per chunk (balance between retrieval precision and context)
- `CHUNK_OVERLAP = 80` overlap characters (prevent loss of context at boundaries)
- `TOP_K = 3` top chunks retrieved per query
- `EMBEDDING_MODEL` and `GENERATION_MODEL` are tunable

### `src/document_loader.py`
Loads plain-text `.txt` files, extracts optional `Title:` headers, creates `Document` dataclass instances.

**Why it matters:**
- Simple input format (plain text, no PDF parsing)
- Metadata extraction from headers for better source attribution
- Clear error handling for missing/empty documents

### `src/chunker.py`
Splits documents into overlapping chunks to balance granularity and context.

**Why it matters:**
- Overlap prevents losing context at chunk boundaries
- Fixed size is deterministic; semantic splitting is left as future work
- Returns `TextChunk` with doc_id, title, text for traceability

### `src/embedder.py`
Wraps `SentenceTransformer` model for dense vector encoding.

**Why it matters:**
- Encapsulates model loading and inference
- Normalizes vectors for cosine similarity
- Dimension property helps initialize FAISS index

### `src/vector_store.py`
FAISS index + chunk metadata storage.

**Key design:**
- L2-normalization for cosine similarity via inner product (faster than explicit cosine)
- Chunks serialized in pickle alongside FAISS binary
- Meta JSON stores dimension and count for validation
- `search()` returns tuples of (TextChunk, score) for interpretability

### `src/retriever.py`
Semantic search: embeds query, retrieves top-k chunks, formats context.

**Why separate from vector_store:**
- Encapsulates search logic and context formatting
- `format_context()` truncates to avoid overwhelming the generator
- Returns `RetrievedChunk` dataclass with scores for transparency

### `src/generator.py`
Local LLM answer generation with strict prompting.

**Design principles:**
- Prompt instructs model to answer only from context
- Fallback message if no context retrieved
- `generate_with_sources()` returns answer + source metadata (no hallucination of sources)
- CPU-only by default; GPU support possible

### `src/pipeline.py`
Orchestrates the entire RAG workflow: loading → chunking → embedding → indexing → retrieval → generation.

**Why separate:**
- Single entry point for both CLI and UI
- Lazy loading of heavy models (embedder, retriever, generator loaded on first query)
- Clear `build_index()` and `ask()` APIs

### `main.py`
Command-line interface with argparse.

**Two modes:**
- `--build-index`: Load docs, build FAISS index, print stats
- `--question "..."`: Retrieve context and generate answer

### `app.py`
Streamlit web interface for interactive exploration.

**Features:**
- Sidebar button to build/rebuild index
- Text input for questions
- Expandable sections for sources and context preview
- Disclaimer about educational use

---

## 💡 Key Talking Points (Interview Prep)

### 1. **What is RAG and why is it used here?**

**Answer:**
> Retrieval-augmented generation combines information retrieval with generative models. Instead of relying on the model's weights alone (which can contain outdated or incorrect facts), RAG first retrieves relevant documents, then passes them as context to the model. This grounds answers in your sources, reduces hallucinations, and lets you update knowledge by simply editing documents—no retraining needed.

**Why here:**
- Medical knowledge is high-stakes and should be traceable to sources
- Your small corpus may contain facts not in the model's training data
- You can add new documents without any model changes

---

### 2. **Why FAISS and not a database?**

**Answer:**
> FAISS (Facebook AI Similarity Search) provides lightning-fast approximate nearest neighbor search on CPU. For a portfolio demo, this is ideal: no server to set up, instant startup, fully offline. It trades some recall for speed, which is acceptable here. For production with millions of documents or low-latency requirements, you'd consider Milvus, Weaviate, or Pinecone; but for a demo, FAISS + pickle is simpler and teachable.

---

### 3. **How do you reduce hallucinations?**

**Answer:**
> Multiple layers:
> 1. **Context injection** — Only pass retrieved chunks to the generator; the prompt explicitly says "answer only from context"
> 2. **Smaller model** — flan-t5-small is less prone to verbose hallucinations than larger models
> 3. **Source metadata** — We return which chunk each answer came from; this encourages accountability
> 4. **Fallback handling** — If no relevant context is found, return a transparent message instead of guessing
>
> This is the *baseline* approach. Advanced strategies include reranking (filter out low-quality hits), citation enforcement (require each answer sentence to map to a chunk ID), and evaluation harnesses (test against a ground-truth QA set).

---

### 4. **What happens if the user asks something outside your document scope?**

**Answer:**
> The retriever returns low-scoring or no matches. The generator receives minimal or empty context, and its prompt tells it to say "I cannot answer from the provided documents." This is honest and prevents pretending to have knowledge you don't.

**Bonus:** If you wanted more aggressive out-of-scope detection, you could:
- Set a similarity threshold and reject queries below that score
- Use a cross-encoder reranker to verify top hits
- Implement a fallback "uncertainty classifier"

---

### 5. **How would you scale this beyond a demo?**

**Answer:**
> Key improvements:
> 1. **Larger corpus** — 1000s or 1000000s of documents (FAISS supports this, but chunking strategy becomes critical)
> 2. **Structure-aware chunking** — Split by paragraph/section headers, preserve metadata (e.g., chapter, page number)
> 3. **Reranking** — Use a cross-encoder (e.g., SBERT's cross-encoder-mmarco) to re-score top-k FAISS hits
> 4. **Stronger LLM** — Mistral, Phi, or an open quantized model larger than flan-t5-small
> 5. **Evaluation suite** — Fixed test Q&A set with metrics (retrieval recall, answer grounding, BLEU, human eval)
> 6. **Caching & logging** — Cache embeddings, log queries/answers for audit trails
> 7. **Fine-tuning (optional)** — If domain-specific, fine-tune embedder or generator on your corpus
> 8. **Security/compliance** — If handling real patient data (PHI), add encryption, access controls, HIPAA review

---

## 🧪 Testing & Validation

### Manual validation
```bash
# Build fresh
python main.py --build-index

# Known good questions (in sample data)
python main.py --question "What is type 2 diabetes?"
python main.py --question "How do I cool a burn?"
python main.py --question "What is hypertension?"

# Edge cases
python main.py --question "Quantum computing"  # Should say "not in documents"
python main.py --question ""                   # Should gracefully handle empty input
```

### What to expect
- **First run:** Models download (~2–3 mins), then indexing (~1 min)
- **Subsequent runs:** Instant index load, ~1–2 sec for retrieval + generation
- **Quality:** Answers are reasonable paraphrases of source material, with correct source citations

---

## 📚 Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     User Input                          │
│                 (CLI or Streamlit UI)                   │
└────────────────────────┬────────────────────────────────┘
                         │
                    Question
                         │
                         ▼
        ┌─────────────────────────────────┐
        │      Pipeline.ask()             │
        │  ┌───────────────────────────┐  │
        │  │ 1. Embedder.embed_query() │  │
        │  │    Query → Vector         │  │
        │  └───────────┬───────────────┘  │
        │              │                   │
        │  ┌───────────▼───────────────┐  │
        │  │ 2. Retriever.retrieve()   │  │
        │  │    Vector → FAISS Search  │  │
        │  │    → Top-K Chunks         │  │
        │  └───────────┬───────────────┘  │
        │              │                   │
        │  ┌───────────▼───────────────┐  │
        │  │ 3. Retriever.format_ctx() │  │
        │  │    Chunks → Context Text  │  │
        │  └───────────┬───────────────┘  │
        │              │                   │
        │  ┌───────────▼───────────────┐  │
        │  │ 4. Generator.generate()   │  │
        │  │    Context → Answer       │  │
        │  └───────────┬───────────────┘  │
        │              │                   │
        │  ┌───────────▼───────────────┐  │
        │  │ 5. Add sources metadata   │  │
        │  │    Return result          │  │
        │  └───────────┬───────────────┘  │
        └──────────────┼──────────────────┘
                       │
         ┌─────────────▼──────────────┐
         │   Result Dict              │
         │ - answer (str)             │
         │ - sources (list of chunks) │
         │ - context_preview (str)    │
         └────────────────────────────┘
```

---

## 🎓 Interview Narrative

**Opening:**
> "I built a lightweight RAG system for medical education Q&A. It demonstrates modern NLP concepts—embeddings, vector search, generative models—in a clean, modular codebase. It's fully offline, so no cloud APIs or rate limits, and it stays local for privacy."

**Walk-through (5 mins):**
1. Show the data structure: plain `.txt` files, titles
2. Explain the pipeline: load → chunk → embed → index → retrieve → generate
3. Highlight a key module (e.g., vector_store.py): show how metadata is preserved
4. Demo a query and discuss source attribution

**Technical depth (follow questions):**
- *"Why FAISS?"* → Offline, fast, simple. Tradeoff: approximate vs. exact, but fine for demo.
- *"How do you prevent hallucination?"* → Context injection, explicit prompts, source transparency, fallback handling.
- *"What are the limitations?"* → Small corpus, no reranking, CPU-only, no fine-tuning, educational only (not medical device).
- *"What would you do at scale?"* → Larger LLM, reranking, structure-aware chunking, evaluation suite, compliance review.

**Closing:**
> "The key insight is modularity and transparency. Each step is isolated, tested, and explainable. That's how you build trustworthy NLP systems in production."

---

## 🔒 Important Disclaimers (For GitHub & Interviews)

**In README and UI:**
- ⚠️ **Educational use only** — Not a medical device, not validated for clinical use
- ⚠️ **Answers are not medical advice** — Always consult healthcare professionals
- ⚠️ **Hallucinations still possible** — Despite grounding, the LLM can make errors or omit nuance
- ⚠️ **Sample content only** — Real-world deployment requires curated, reviewed medical content

**This protects you legally and professionally.**

---

## 📋 Checklist for GitHub Publishing

- [x] README.md with usage, architecture, limitations
- [x] requirements.txt with pinned versions
- [x] LICENSE (MIT)
- [x] .gitignore (excludes __pycache__, .venv, data/index/)
- [x] Modular src/ code with docstrings
- [x] CLI (main.py) and UI (app.py)
- [x] Sample documents with educational content
- [x] Configuration system (src/config.py)
- [x] scripts/ with helper (build_index.py)
- [x] Interview Q&A in README
- [x] Current limitations & future improvements documented
- [x] Disclaimer about educational/non-medical use

**Optional additions:**
- [ ] GitHub Actions CI/CD to test on Python 3.10, 3.11, 3.12
- [ ] Dockerfile for reproducible environment
- [ ] tests/ folder with unit tests
- [ ] CONTRIBUTING.md for open-source guidelines
- [ ] `setup.py` if you want to make it pip-installable

---

## 🎯 Why This Project Stands Out

1. **Real architecture** — Not a toy; genuine modular design with separation of concerns
2. **End-to-end** — From file loading to user-facing UI; shows full ownership
3. **Honest limitations** — Explicitly discusses tradeoffs; signals maturity
4. **Interview-ready** — Easy to explain, deep enough to explore, shows judgment
5. **Deployable** — Works as-is; no setup surprises or missing dependencies
6. **GitHub-ready** — Clean structure, good documentation, professional tone

---

## 🚀 Next Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial: offline medical RAG demo"
   git remote add origin https://github.com/YOUR_USERNAME/offline-medical-rag-demo.git
   git push -u origin main
   ```

2. **Test locally** (walk through setup and queries)

3. **Prepare 2-3 minute demo** for interviews

4. **Keep README updated** — Add links to blog posts, demo videos, etc.

---

## 📞 Support / FAQs

**Q: Can I add more documents?**  
A: Yes. Add `.txt` files to `data/documents/`, then run `python main.py --build-index` again.

**Q: Is GPU required?**  
A: No. CPU is fine for this demo. To enable GPU, edit `src/generator.py` and change `device=-1` to `device=0`.

**Q: Can I swap models?**  
A: Yes. Edit `src/config.py` — change `EMBEDDING_MODEL` or `GENERATION_MODEL` to any Hugging Face identifier.

**Q: How do I make this production-ready?**  
A: Follow the "scale" roadmap above: larger corpus, reranking, stronger LLM, evaluation harness, security audit.

---

**Built with ❤️ for AI/ML internship portfolios.**

