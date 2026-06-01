# Architecture & Design Guide

## System Overview

```
┌─────────────────────────────────────────┐
│         User Interface                  │
│    (CLI: main.py, Web: app.py)          │
└────────────────┬────────────────────────┘
                 │
        ┌────────▼─────────┐
        │ MedicalRAGPipeline│
        │  (orchestrator)  │
        └────┬─────────────┘
             │
    ┌────────┴─────────────────────┐
    │                              │
┌───▼──────────┐        ┌──────────▼────┐
│ build_index()│        │   ask()        │
├───────────────┤        ├────────────────┤
│ Load docs     │        │ Embed query    │
│ → Chunk       │        │ Retrieve chunks│
│ → Embed       │        │ Format context │
│ → Save index  │        │ Generate answer│
└───────────────┘        └────────────────┘
```

---

## Module Responsibilities

| Module | Job | Input | Output |
|--------|-----|-------|--------|
| `config.py` | Settings | — | Constants (chunk size, models, paths) |
| `document_loader.py` | Load .txt files | File paths | `Document` objects |
| `chunker.py` | Split text | `Document` list | `TextChunk` list |
| `embedder.py` | Create vectors | Text strings | Float32 embeddings |
| `vector_store.py` | Index + persist | Chunks + embeddings | FAISS binary + pickle |
| `retriever.py` | Semantic search | Query string | `RetrievedChunk` list |
| `generator.py` | Generate answer | Question + context | Answer + sources |
| `pipeline.py` | Orchestrate | Documents or query | Index stats or result dict |

---

## Data Flow: Build Index

```
.txt files
    │
    ├─→ document_loader.load_documents()
    │        └─→ List[Document]
    │            {doc_id, title, text, source_path}
    │
    ├─→ chunker.chunk_documents()
    │        └─→ List[TextChunk]
    │            {chunk_id, doc_id, title, text, chunk_index}
    │
    ├─→ embedder.embed_texts()
    │        └─→ np.ndarray (n_chunks, 384)
    │
    ├─→ FaissVectorStore()
    │        └─→ Add chunks to index
    │
    └─→ store.save()
             ├─→ index.faiss (binary)
             ├─→ chunks.pkl (binary)
             └─→ meta.json {dimension, num_vectors}
```

---

## Data Flow: Query

```
User: "What is diabetes?"
    │
    ├─→ pipeline.ask(question)
    │        │
    │        ├─→ embedder.embed_query()
    │        │        └─→ query_vector (384,)
    │        │
    │        ├─→ retriever.retrieve()
    │        │        ├─→ vector_store.search()
    │        │        │        └─→ FAISS: top-k similarity
    │        │        └─→ List[RetrievedChunk]
    │        │
    │        ├─→ retriever.format_context()
    │        │        └─→ context_str (≤ 2000 chars)
    │        │
    │        ├─→ generator.generate()
    │        │        ├─→ build_prompt()
    │        │        ├─→ run LLM pipeline
    │        │        └─→ answer_str
    │        │
    │        └─→ generator.generate_with_sources()
    │                 └─→ Dict {answer, sources}
    │
    └─→ Return to user
```

---

## Design Patterns

### 1. **Factory Pattern** — Vector Store Creation

```python
# Encapsulates index creation
def build_vector_store(chunks, embedder, index_dir):
    vectors = embedder.embed_texts([c.text for c in chunks])
    store = FaissVectorStore(embedder.dimension)
    store.add_chunks(chunks, vectors)
    store.save(index_dir)
    return store
```

**Why:** Isolates index setup logic; easy to swap for ChromaDB factory.

---

### 2. **Strategy Pattern** — Pluggable Retriever

```python
class Retriever:
    def __init__(self, embedder: Embedder, vector_store: VectorStore):
        self.embedder = embedder
        self.vector_store = vector_store  # ← Strategy can be swapped
```

**Why:** Different vector stores (FAISS, ChromaDB, Pinecone) share same retriever interface.

---

### 3. **Template Method** — Pipeline Stages

```python
class MedicalRAGPipeline:
    def build_index(self):
        # Template: fixed sequence
        documents = load_documents()          # Step 1
        chunks = chunk_documents(documents)   # Step 2
        embedder = Embedder()                 # Step 3
        store = build_vector_store(chunks, embedder)  # Step 4 (template call)
        return stats
```

**Why:** Clear algorithm skeleton; subclasses could override individual steps.

---

### 4. **Lazy Initialization** — Deferred Model Loading

```python
def _ensure_loaded(self):
    if self.embedder is None:
        self.embedder = Embedder(...)  # ← Only load when needed
    if self.retriever is None:
        self.retriever = Retriever(...)
```

**Why:** No startup overhead; first query is slow, rest are instant.

---

### 5. **Dataclass Contracts** — Clear Data Flow

```python
@dataclass
class Document:
    doc_id: str
    title: str
    text: str
    source_path: str

@dataclass
class TextChunk:
    chunk_id: str
    doc_id: str
    title: str
    text: str
    chunk_index: int
```

**Why:** Explicit contracts; IDE autocomplete; easier to refactor.

---

## SOLID Principles Applied

| Principle | How | Benefit |
|-----------|-----|---------|
| **S**ingle Responsibility | Each module does one thing | Easy to test, reuse, understand |
| **O**pen/Closed | Open for extension (add components), closed for modification | Swap FAISS for ChromaDB without rewriting core |
| **L**iskov Substitution | Different vector stores swap transparently | Flexible architecture |
| **I**nterface Segregation | Classes only expose what's needed | Minimal coupling |
| **D**ependency Inversion | `Pipeline` depends on abstractions (`Embedder`, `Retriever`), not concrete classes | Testable with mocks |

---

## Extensibility: How to Swap Components

### Swap Embedding Model

```python
# src/config.py
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"  # Swap this line
```

Rebuild: `python main.py --build-index`. Done!

### Swap Vector Store (FAISS → ChromaDB)

```python
# Create ChromaVectorStore class with same interface
class ChromaVectorStore:
    def add_chunks(self, chunks, embeddings): ...
    def search(self, query_embedding, top_k): ...
    def save(self, index_dir): ...
    @classmethod
    def load(cls, index_dir): ...

# In pipeline.py: swap FaissVectorStore → ChromaVectorStore
# Everything else unchanged!
```

### Add Reranking

```python
# src/retriever.py
class RetrieverWithReranker(Retriever):
    def retrieve(self, query):
        hits = super().retrieve(query)  # Get top-k
        reranked = cross_encoder.rank(query, hits)
        return reranked[:self.top_k]
```

---

## Scaling Roadmap

### Current (Portfolio)
- 1K–10K documents max
- Single-threaded Python
- CPU-only
- In-memory metadata

### Scale Level 1 (10K–100K docs)
- Approximate FAISS (IndexIVF instead of IndexFlatIP)
- Batch embedding pipeline
- Metadata caching layer

### Scale Level 2 (100K–1M docs)
- Distributed FAISS (multiple shards)
- PostgreSQL for metadata + filtering
- GPU inference (batch queries)
- Async FastAPI server

### Scale Level 3 (1M+ docs)
- Managed vector DB (Pinecone, Weaviate, Milvus)
- Kubernetes orchestration
- Fine-tuned embedder/generator on medical domain
- Real-time index updates
- Compliance review (HIPAA, privacy, bias)

---

## Testing Strategy

### Unit Tests

```python
# tests/test_chunker.py
def test_chunk_overlap():
    docs = [Document(doc_id="test", title="Test", text="a b c d e f g h", source_path="/tmp")]
    chunks = chunk_documents(docs, chunk_size=4, chunk_overlap=2)
    # Verify overlap: end of chunk N = start of chunk N+1
    assert chunks[0].text[-2:] == chunks[1].text[:2]

# tests/test_retriever.py
def test_retriever_empty_index():
    embedder = Mock()
    store = Mock(search=Mock(return_value=[]))
    retriever = Retriever(embedder, store, top_k=3)
    result = retriever.retrieve("test")
    assert result == []
```

### Integration Tests

```python
def test_full_rag_pipeline():
    pipeline = MedicalRAGPipeline()
    stats = pipeline.build_index()
    assert stats['documents'] > 0
    result = pipeline.ask("What is diabetes?")
    assert result['answer']
    assert result['sources']
```

---

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Load 3 documents | <1 sec | I/O bound |
| Create chunks | <1 sec | CPU bound (simple) |
| Embed 100 chunks | ~2–5 sec | GPU >> CPU |
| Build FAISS index | <1 sec | Fast |
| First query (cold model load) | ~5–10 sec | Model download + inference |
| Subsequent queries | ~2–3 sec | Cached models |

---

## Common Mistakes Avoided

❌ **NOT Done Here:**
- God class (pipeline delegates work, doesn't do everything)
- Global state (config is imported but immutable)
- Tight coupling (use dependency injection)
- Magic strings (constants in config.py)
- Silent failures (explicit errors)
- Poor documentation (docstrings + README)

✅ **Instead:**
- Separation of concerns
- Explicit dependencies
- Centralized configuration
- Clear error messages
- Type hints
- Good documentation

---

## Future Architecture Enhancements

1. **Hybrid Search** — Combine BM25 (keyword) + dense (semantic) + rerank
2. **Caching Layer** — Cache embeddings & results for common queries
3. **Async Processing** — FastAPI + async/await for scaling
4. **Monitoring** — Logs + metrics (queries, latencies, errors)
5. **A/B Testing** — Compare different models/strategies
6. **Fine-tuning** — Domain-specific embedder/generator
7. **Streaming** — Generate answers incrementally (better UX)

---

## Key Takeaway

> This codebase demonstrates **clean architecture principles** in ML: modularity, type safety, clear contracts, and thoughtful design. That's more important than raw performance or features. **Build systems you can explain and maintain, not systems that are clever.**

