# Setup, Testing & Validation Checklist

**Use this guide to ensure everything works before pushing to GitHub or showing in interviews.**

---

## ✅ Pre-Deployment Checklist

### Environment

- [ ] Python 3.10+ installed (`python --version`)
- [ ] Virtual environment created and activated (`.venv`)
- [ ] `pip install -r requirements.txt` succeeds without errors
- [ ] All imports work: `python -c "from src.pipeline import MedicalRAGPipeline; print('OK')"`

### File Structure

- [ ] `data/documents/` exists and contains at least 3 `.txt` files
- [ ] `src/` has all required modules: `config.py`, `document_loader.py`, `chunker.py`, `embedder.py`, `vector_store.py`, `retriever.py`, `generator.py`, `pipeline.py`
- [ ] `main.py` and `app.py` exist in project root
- [ ] `README.md`, `LICENSE`, `.gitignore`, `requirements.txt` all present

### Code Quality

- [ ] Run `python -m py_compile src/*.py main.py app.py` (checks syntax)
- [ ] No hardcoded paths (everything uses `config.py` or `Path()`)
- [ ] Docstrings on classes and public methods
- [ ] Type hints present (especially on function signatures)

---

## 🧪 Test Suite

### Test 1: Basic Import & Initialization

```bash
python -c "
from src.pipeline import MedicalRAGPipeline
from src.config import DOCUMENTS_DIR, INDEX_DIR
print(f'Documents: {DOCUMENTS_DIR}')
print(f'Index: {INDEX_DIR}')
print('✓ Imports OK')
"
```

**Expected:** No errors, paths print correctly.

---

### Test 2: Document Loading

```bash
python -c "
from src.document_loader import load_documents
from src.config import DOCUMENTS_DIR
docs = load_documents(DOCUMENTS_DIR)
print(f'✓ Loaded {len(docs)} documents')
for doc in docs:
    print(f'  - {doc.title}: {len(doc.text)} chars')
"
```

**Expected:** 3+ documents loaded, titles extracted.

---

### Test 3: Chunking

```bash
python -c "
from src.document_loader import load_documents
from src.chunker import chunk_documents
from src.config import DOCUMENTS_DIR, CHUNK_SIZE, CHUNK_OVERLAP
docs = load_documents(DOCUMENTS_DIR)
chunks = chunk_documents(docs, CHUNK_SIZE, CHUNK_OVERLAP)
print(f'✓ Created {len(chunks)} chunks')
print(f'  First chunk: {chunks[0].chunk_id}')
print(f'  Text sample: {chunks[0].text[:100]}...')
"
```

**Expected:** 30–100+ chunks created, first chunk readable.

---

### Test 4: Embedding

```bash
python -c "
from src.embedder import Embedder
from src.config import EMBEDDING_MODEL
embedder = Embedder(EMBEDDING_MODEL)
print(f'✓ Embedder loaded: {EMBEDDING_MODEL}')
print(f'  Dimension: {embedder.dimension}')
sample = embedder.embed_query('What is diabetes?')
print(f'  Query embedding shape: {sample.shape}')
"
```

**Expected:** Embedder loads (may download ~100 MB on first run), dimension=384.

---

### Test 5: Full Index Build

```bash
python main.py --build-index
```

**Expected output:**
```
Index built successfully.
{
  "documents": 3,
  "chunks": XX,
  "index_path": "b:\\git\\1\\offline-medical-rag-demo\\data\\index",
  "vectors": XX
}
```

**After run:**
- [ ] Check `data/index/` exists with:
  - `index.faiss` (binary, ~1–5 MB)
  - `chunks.pkl` (binary, ~500 KB–1 MB)
  - `meta.json` (text, readable)

---

### Test 6: Single Query (CLI)

```bash
python main.py --question "What is type 2 diabetes?"
```

**Expected output:**
```
=== Answer ===
[Generated answer from flan-t5-small, ~1–3 sentences]

=== Sources ===
- Type 2 Diabetes — Overview for Patients and Caregivers (diabetes_overview) [diabetes_overview__chunk_0] score=0.8765
- ... (up to 3 sources)
```

**Checklist:**
- [ ] Answer is present and reasonable
- [ ] Sources list chunk IDs and scores
- [ ] Response takes 1–5 seconds

---

### Test 7: Multiple Queries

```bash
python main.py --question "How do I treat a burn?"
python main.py --question "What is hypertension?"
python main.py --question "quantum computing and neural networks"
```

**Expected:**
- Burn query: References to "first_aid_burns.txt"
- Hypertension query: References to "hypertension_basics.txt"
- Quantum query: Fallback message (not in documents) or low-confidence answer

---

### Test 8: Streamlit UI

```bash
streamlit run app.py
```

**In browser (http://localhost:8501):**

1. [ ] Page loads without errors
2. [ ] Sidebar shows "Index ready: No" (if index not built) or "Index ready: Yes"
3. [ ] Click "Build / rebuild index" button → progress spinner → success message
4. [ ] Enter a question → "Get answer" button → answer + sources appear
5. [ ] Click "Retrieved sources" expandable → source list shows
6. [ ] Click "Context preview" expandable → truncated context visible

**Stop Streamlit:** Press Ctrl+C in terminal.

---

### Test 9: Edge Cases

**Empty question:**
```bash
python main.py --question ""
```
**Expected:** Graceful error or no answer (depends on argparse).

**Very long question:**
```bash
python main.py --question "What are all the possible symptoms and treatments and side effects and contraindications and alternative therapies for type 2 diabetes across all demographics and geographic regions?"
```
**Expected:** Answer still generates (prompt may truncate).

**Special characters:**
```bash
python main.py --question "What's the 101-year-old's risk? [50% & 50%]"
```
**Expected:** Handled without Unicode errors.

---

### Test 10: Index Rebuild After Document Change

1. Add a new `.txt` file to `data/documents/`:
   ```
   Title: COVID-19 Basics
   COVID-19 is ...
   ```
2. Run `python main.py --build-index`
3. Query: `python main.py --question "What is COVID-19?"`

**Expected:** New document indexed, retrievable in answer.

---

## 🔍 Code Review Checklist

### src/config.py
- [ ] All paths use `Path()` (not strings)
- [ ] Hyperparameters are grouped logically
- [ ] Defaults are reasonable (CHUNK_SIZE=400, TOP_K=3)

### src/document_loader.py
- [ ] `_extract_title()` handles "Title:" line correctly
- [ ] Graceful error if directory missing
- [ ] Error if no `.txt` files found
- [ ] Empty files skipped

### src/chunker.py
- [ ] Chunk overlap < chunk size (validated)
- [ ] Chunks are strippedof leading/trailing whitespace
- [ ] Each chunk has unique chunk_id (e.g., "doc_id__chunk_5")

### src/embedder.py
- [ ] `dimension` property works
- [ ] `embed_texts()` returns float32, not float64
- [ ] Progress bar shown only for large batches
- [ ] `embed_query()` returns 1D array (not 2D)

### src/vector_store.py
- [ ] `_normalize()` handles zero-norm vectors
- [ ] `search()` returns empty list if index empty
- [ ] `save()` creates directory if missing
- [ ] `load()` raises clear error if meta.json missing
- [ ] Chunks and index are in sync (same length)

### src/retriever.py
- [ ] `retrieve()` returns `RetrievedChunk` objects
- [ ] `format_context()` truncates to `max_chars`
- [ ] Score is rounded in output (readable, not 32 decimals)

### src/generator.py
- [ ] `build_prompt()` has disclaimer + instruction + context
- [ ] `generate()` handles empty context gracefully
- [ ] Lazy loading of pipeline (first call is slower, rest are cached)
- [ ] `generate_with_sources()` returns dict with "answer", "sources"

### src/pipeline.py
- [ ] `build_index()` returns stats dict
- [ ] `_ensure_loaded()` lazy-loads all models (efficient)
- [ ] `ask()` preserves question in result
- [ ] Context preview truncated to 500 chars (UI readable)

### main.py
- [ ] Argparse setup clear and documented
- [ ] `--build-index` runs without `--question`
- [ ] `--question` requires built index (good error message)
- [ ] Help text is friendly

### app.py
- [ ] Streamlit page config set
- [ ] Disclaimer visible
- [ ] Index check works
- [ ] "Build index" button creates index
- [ ] Query submission works
- [ ] Expandable sections for sources + context

---

## 📊 Performance Benchmarking

Time the following on a cold start (fresh terminal):

```bash
# Time 1: Index building
time python main.py --build-index

# Time 2: Query (first, models already cached)
time python main.py --question "What is diabetes?"

# Time 3: Query (second, everything cached)
time python main.py --question "What is hypertension?"
```

**Expected times:**
- Index build: ~1–3 mins (first run downloads models)
- Query 1: ~5–10 sec (generator warms up)
- Query 2–3: ~2–3 sec (all cached)

If significantly slower, check:
- [ ] CPU is not maxed out (no other processes consuming cores)
- [ ] Disk is not full (models need space)
- [ ] Python version is 3.10+ (older versions slower)
- [ ] No antivirus scanning every .py file

---

## 🐛 Debugging Tips

**"No such file or directory: data/index/"**
- Solution: Run `python main.py --build-index` first

**"No module named 'sentence_transformers'"**
- Solution: `pip install -r requirements.txt` in activated venv

**"CUDA out of memory"**
- Solution: Change `device=-1` in `src/generator.py` (use CPU instead)

**Extremely slow embedding**
- Symptom: First query takes >1 min
- Solution: This is normal on CPU. GPU recommended; set `device=0` if available

**Answer always says "I cannot answer"**
- Symptom: No relevant context found
- Debug: Run Test 6 with a known question (diabetes, burns, hypertension)
- Solution: Verify index exists (`data/index/meta.json`)

**Streamlit app crashes on "Get answer"**
- Solution: Check terminal for Python errors; share them in GitHub issues

---

## 🚀 Pre-GitHub Push

1. [ ] All tests pass (Test 1–10)
2. [ ] Code review checklist complete
3. [ ] `git status` shows only `offline-medical-rag-demo/` files (no user files, no `.pyc`)
4. [ ] `.gitignore` working: `data/index/`, `.venv/`, `__pycache__` not tracked
5. [ ] `README.md` is readable in browser (GitHub markdown renders well)
6. [ ] Run `git log --oneline` to verify commit history is clean

**Before push:**
```bash
# Clean up
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
rm -rf .venv/

# Verify .gitignore
git status  # Should show nothing or only untracked intended files

# Check syntax
python -m py_compile src/*.py main.py app.py

# Final push
git add .
git commit -m "Initial: offline medical RAG demo for portfolio"
git push -u origin main
```

---

## 📸 Screenshots for Portfolio

**Recommended screenshots to add to README or separate IMAGES.md:**

1. CLI output: `python main.py --build-index` → JSON stats
2. CLI query: `python main.py --question "..."` → Answer + sources
3. Streamlit UI: Sidebar with index status + main question box with answer
4. Streamlit expandable sources: Retrieved chunk list with scores
5. Streamlit context preview: Truncated context shown to user

---

## 🎯 Final Validation (Interview Prep)

**Day before interview:**
- [ ] Run setup from scratch (fresh venv, pip install)
- [ ] Demo 3 queries (diabetes, burns, hypertension)
- [ ] Show code in IDE (highlight key files)
- [ ] Time yourself: 5 mins to explain architecture + one query

**During interview:**
- [ ] Bring laptop + have repo cloned locally
- [ ] Show running demo, not slides
- [ ] Explain failure gracefully ("out-of-scope question" → fallback)
- [ ] Ask if they want to see specific code (show src/pipeline.py first, then dive deeper)

---

## ✨ Green Light to Ship

If all items are checked and tests pass, you're **ready to push to GitHub**. Congratulations! 🎉

Good luck! 🚀

