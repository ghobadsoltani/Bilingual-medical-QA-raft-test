# Architecture & Design Patterns Reference

**Quick reference for explaining design decisions in interviews.**

---

## 🏗️ Architectural Pattern: Layered Pipeline

```
┌─────────────────────────────────────────────────────┐
│             User Interface Layer                    │
│           (CLI: main.py, UI: app.py)                │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│         Orchestration Layer                         │
│              (pipeline.py)                          │
│  - build_index(): Data ingestion & indexing         │
│  - ask(): RAG query pipeline                        │
└────┬────────────────────────────────────────────┬───┘
     │                                            │
┌────▼───────────────┐          ┌────────────────▼────┐
│   Index Building   │          │   Query Processing  │
├────────────────────┤          ├─────────────────────┤
│ • document_loader  │          │ • embedder (query)  │
│ • chunker          │          │ • retriever         │
│ • embedder         │          │ • generator         │
│ • vector_store     │          │ • result formatter  │
└────────────────────┘          └─────────────────────┘
```

**Rationale:**
- **Separation of Concerns** — Each layer has one job
- **Reusability** — Components work independently
- **Testability** — Easy to mock and test each layer
- **Scalability** — Swap layers without rewriting others

---

## 🧩 Design Patterns Used

### 1. **Factory Pattern** (`vector_store.py`)

```python
class FaissVectorStore:
    @classmethod
    def load(cls, index_dir: Path) -> "FaissVectorStore":
        # Create instance from saved artifacts
        store = cls(dimension=meta["dimension"])
        store.index = faiss.read_index(...)
        store.chunks = pickle.load(...)
        return store

def build_vector_store(chunks, embedder, index_dir):
    # Factory function to create and persist index
    store = FaissVectorStore(dimension=embedder.dimension)
    store.add_chunks(chunks, embeddings)
    store.save(index_dir)
    return store
```

**Why:** Encapsulates object creation logic. Makes testing easier (mock the factory).

---

### 2. **Strategy Pattern** (`retriever.py` + `vector_store.py`)

```python
class Retriever:
    def __init__(self, embedder: Embedder, vector_store: FaissVectorStore, top_k: int):
        # Inject strategy (vector_store can be swapped)
        self.vector_store = vector_store
        self.embedder = embedder
```

**Why:** Decouple search strategy from retrieval logic. Swap FAISS → ChromaDB without touching retriever.

---

### 3. **Template Method Pattern** (`pipeline.py`)

```python
class MedicalRAGPipeline:
    def build_index(self) -> dict:
        # Template: fixed sequence
        documents = load_documents(...)
        chunks = chunk_documents(...)
        embedder = Embedder(...)
        store = build_vector_store(...)  # Template call
        return stats

    def ask(self, question: str) -> dict:
        # Template: fixed sequence
        self._ensure_loaded()
        retrieved = self.retriever.retrieve(question)  # Template call
        context = self.retriever.format_context(retrieved)
        result = self.generator.generate_with_sources(...)  # Template call
        return result
```

**Why:** Define algorithm skeleton; subclasses implement details. Here, each method is the "template" for its stage.

---

### 4. **Lazy Initialization Pattern** (`pipeline.py`)

```python
def _ensure_loaded(self) -> None:
    if self.embedder is None:
        self.embedder = Embedder(self.embedding_model)
    if self.retriever is None:
        store = FaissVectorStore.load(self.index_dir)
        self.retriever = Retriever(...)
    if self.generator is None:
        self.generator = AnswerGenerator(...)
```

**Why:** Defer expensive operations (model loading) until needed. First query is slow; rest are fast.

---

### 5. **Dataclass for Clear Contracts** (throughout)

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

@dataclass
class RetrievedChunk:
    chunk: TextChunk
    score: float
```

**Why:** Explicit contract (what data flows through the pipeline). Type hints catch bugs early. Hashable for JSON serialization.

---

### 6. **Configuration Object Pattern** (`config.py`)

```python
# src/config.py — Single source of truth
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"
CHUNK_SIZE = 400
TOP_K = 3
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

**Why:** 
- Avoid magic numbers scattered in code
- Easy to adjust for different environments
- Imported everywhere, single change updates whole system

---

### 7. **Error Handling & Validation**

```python
# document_loader.py
if not documents_dir.is_dir():
    raise FileNotFoundError(f"Documents directory not found: {documents_dir}")

# chunker.py
if chunk_overlap >= chunk_size:
    raise ValueError("chunk_overlap must be smaller than chunk_size")

# vector_store.py
if not meta_path.exists():
    raise FileNotFoundError(
        f"Index not found at {index_dir}. Run: python main.py --build-index"
    )
```

**Why:** Fail fast with clear messages. Helps users debug.

---

## 🔄 Data Flow Diagrams

### Build Index

```
.txt files
    │
    ▼
load_documents()
    │ → List[Document]
    ▼
chunk_documents()
    │ → List[TextChunk]
    ▼
embedder.embed_texts()
    │ → np.ndarray (n_chunks, 384)
    ▼
FaissVectorStore.add_chunks()
    │ → (index, chunks_list)
    ▼
store.save()
    │
    ├─→ index.faiss (binary)
    ├─→ chunks.pkl (binary)
    └─→ meta.json (text)
```

---

### Ask Query

```
"What is diabetes?"
    │
    ▼
embedder.embed_query()
    │ → query_vector (384,)
    ▼
retriever.retrieve()
    │ → Retriever.vector_store.search()
    │   → FAISS search
    │ → List[RetrievedChunk]
    ▼
retriever.format_context()
    │ → context_str (≤ 2000 chars)
    ▼
generator.generate()
    │ → build_prompt()
    │ → run pipeline("text2text-generation")
    │ → answer_str
    ▼
generator.generate_with_sources()
    │
    ├─→ answer (str)
    └─→ sources (List[{doc_id, chunk_id, score}])
```

---

## 💾 Persistence Strategy

### Index Artifacts

```
data/index/
├── index.faiss       # Binary FAISS index (serialized vectors)
├── chunks.pkl        # Pickle: List[TextChunk] with metadata
└── meta.json         # {"dimension": 384, "num_vectors": 150}
```

**Why three files?**
- **index.faiss** → Fast FAISS-specific serialization
- **chunks.pkl** → Full metadata (title, text, IDs) for human-readable results
- **meta.json** → Validation (dimension must match) + debugging

**Load order:**
1. Read meta.json (validate dimension)
2. Load index.faiss into FAISS
3. Deserialize chunks.pkl
4. Verify counts match

---

## 🔐 Type Safety & Contracts

### Explicit Types Throughout

```python
def load_documents(documents_dir: Path) -> list[Document]:
    """Signature is a contract: needs Path, returns List[Document]."""

def chunk_documents(
    documents: list[Document],
    chunk_size: int = 400,
    chunk_overlap: int = 80,
) -> list[TextChunk]:
    """Clear inputs/outputs; no surprises."""

def embed_texts(self, texts: list[str]) -> np.ndarray:
    """Shape: (len(texts), 384)."""
```

**Benefits:**
- IDE autocomplete works
- Type checker (mypy, pyright) catches errors
- Documentation is executable

---

## 📊 Extensibility Hooks

### Easy to Extend

**Swap models:**
```python
# src/config.py
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"  # Larger model
GENERATION_MODEL = "meta-llama/Llama-2-7b-hf"  # Stronger generator
```
Then rerun index build. No code changes needed.

**Swap vector store:**
```python
# src/vector_store.py → Create ChromaVectorStore class
class ChromaVectorStore:
    def search(self, query_embedding, top_k) -> list[tuple[TextChunk, float]]:
        # Use ChromaDB instead of FAISS
```
Then inject into retriever.

**Swap retriever:**
```python
# src/retriever.py → Add reranking
class RetrieveWithReranker(Retriever):
    def retrieve(self, query):
        hits = super().retrieve(query)  # Get top-k
        reranked = rerank_with_cross_encoder(hits)  # Refine
        return reranked
```

---

## 🎯 SOLID Principles Applied

| Principle | How It's Used |
|-----------|---------------|
| **S**ingle Responsibility | Each module does one thing (document_loader loads, chunker chunks, etc.) |
| **O**pen/Closed | Open for extension (swap components), closed for modification (don't rewrite core logic) |
| **L**iskov Substitution | Different vector stores (FAISS, ChromaDB) can swap without breaking retriever |
| **I**nterface Segregation | Classes only expose what they need (embedder only cares about embedding, not retrieval) |
| **D**ependency Inversion | Pipeline depends on abstractions (Embedder, Retriever, Generator), not concrete implementations |

---

## 🚨 Anti-Patterns Avoided

### ❌ NOT Used

1. **God Class** — Pipeline delegates, doesn't do everything
2. **Global State** — Config is imported but not mutated globally
3. **Tight Coupling** — Dependency injection (pipeline passes embedder to retriever)
4. **Magic Strings** — config.py centralizes constants
5. **Silent Failures** — Explicit errors with helpful messages
6. **No Documentation** — Docstrings + README explain design

---

## 🔬 Testing Strategy (Future)

### Unit Test Structure

```python
# tests/test_chunker.py
def test_chunker_overlap():
    docs = [Document(..., text="a b c d e...")]
    chunks = chunk_documents(docs, 10, 5)
    assert chunks[0].text[-5:] == chunks[1].text[:5]  # Overlap verified

# tests/test_retriever.py
def test_retriever_empty_index():
    embedder = Mock()
    store = Mock(search=Mock(return_value=[]))
    retriever = Retriever(embedder, store)
    result = retriever.retrieve("test")
    assert result == []

# tests/test_generator.py
def test_generator_with_empty_context():
    gen = AnswerGenerator(...)
    answer = gen.generate("question", "")
    assert "cannot answer" in answer.lower()
```

**Coverage targets:** ≥80% logic, 100% error paths.

---

## 📈 Scalability Roadmap

### Current (Portfolio)
- ~1K–10K documents max
- Single-threaded Python
- CPU-only
- In-memory metadata

### Scale 1 (10K–100K docs)
- Approximate FAISS index (IndexIVF)
- Batch embedding pipeline
- Metadata caching layer

### Scale 2 (100K–1M docs)
- Distributed FAISS (multiple shards)
- PostgreSQL for metadata + filtering
- GPU inference (batch queries)
- Async API (FastAPI)

### Scale 3 (1M+ docs)
- Managed vector DB (Pinecone, Weaviate)
- Kubernetes for orchestration
- Fine-tuned embedder/generator
- Real-time index updates

---

## 🎓 Teaching Value

**What this codebase teaches:**

1. **Software Engineering 101** — Modularity, separation of concerns, clear interfaces
2. **ML Systems Design** — From data to model to user (not just Jupyter notebooks)
3. **NLP Fundamentals** — Embeddings, vector search, generation, prompting
4. **Best Practices** — Error handling, type hints, docstrings, config management
5. **Full-Stack Thinking** — From CLI to web UI to backend logic

This is **intentionally simple** to be understandable, but **intentionally professional** to be portfolio-worthy.

---

## 📚 Further Reading

### RAG
- [RAGAS: RAG Assessment](https://arxiv.org/abs/2309.15217)
- [LangChain RAG guide](https://python.langchain.com/docs/use_cases/question_answering/)

### Vector Search
- [Approximate Nearest Neighbor Search](https://en.wikipedia.org/wiki/Nearest_neighbor_search)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)

### Embeddings
- [Sentence-BERT](https://www.sbert.net/)
- [What are embeddings?](https://platform.openai.com/docs/guides/embeddings)

### LLMs & Generation
- [HuggingFace Model Hub](https://huggingface.co/models)
- [Prompt Engineering](https://platform.openai.com/docs/guides/prompt-engineering)

---

**End of Architecture Reference.**

