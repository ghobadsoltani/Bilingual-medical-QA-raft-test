# Pre-Publish Checklist for GitHub

Use this checklist before pushing to GitHub to ensure professional quality.

---

## 🎯 Code Quality

- [ ] **No syntax errors:** `python -m py_compile src/*.py main.py app.py scripts/*.py`
- [ ] **All imports work:** `python -c "from src.pipeline import MedicalRAGPipeline; print('OK')"`
- [ ] **Docstrings on all modules:** Each `.py` file has a module-level docstring
- [ ] **Type hints:** Function signatures include type hints (e.g., `def foo(x: str) -> bool:`)
- [ ] **No hardcoded paths:** Everything uses `config.py` or `Path()` objects
- [ ] **Error messages are helpful:** Users know what went wrong and how to fix it
- [ ] **No `print()` for logging:** Use structured output (JSON, exceptions)

**Quick check:**
```bash
cd offline-medical-rag-demo
python -m py_compile src/*.py main.py app.py
python -c "from src.pipeline import MedicalRAGPipeline; print('✓ Imports OK')"
```

---

## 📁 File Organization

- [ ] **Project root has:** `README.md`, `LICENSE`, `.gitignore`, `requirements.txt`
- [ ] **src/ folder:** All 8 modules present + `__init__.py`
  - `config.py`, `document_loader.py`, `chunker.py`, `embedder.py`
  - `vector_store.py`, `retriever.py`, `generator.py`, `pipeline.py`
- [ ] **data/documents/:** At least 3 `.txt` files with real content
- [ ] **data/index/:** Does NOT exist yet (created on first `--build-index`, gitignored)
- [ ] **scripts/:** `build_index.py` present
- [ ] **tests/:** `__init__.py` and `test_pipeline.py` present
- [ ] **docs/:** `INTERVIEW.md` and `ARCHITECTURE.md` present
- [ ] **notebooks/:** Has `README.md` explaining optional use
- [ ] **No extraneous files:** No `.DS_Store`, `*.pyc`, `.venv/`, or temporary files

**Quick check:**
```bash
cd offline-medical-rag-demo
ls -la src/
ls -la data/documents/
git status  # Should show clean or only doc files
```

---

## 📖 Documentation

### README.md
- [ ] **Concise** (~200 lines max)
- [ ] **"What it does"** section explains the pipeline simply
- [ ] **"Quick Start"** section is accurate and tested
- [ ] **"Project Structure"** describes folder layout
- [ ] **"Technical Stack"** table shows key choices
- [ ] **"Limitations"** section is honest
- [ ] **"License"** mentioned (MIT)
- [ ] **Links to docs/** for deeper dives

### docs/INTERVIEW.md
- [ ] **5-minute pitch** included
- [ ] **15+ Q&A** with confident answers
- [ ] **Practice flow** provided
- [ ] **Confidence boosters** included

### docs/ARCHITECTURE.md
- [ ] **System overview** with diagrams
- [ ] **Design patterns** explained
- [ ] **Data flow** illustrated
- [ ] **Scaling roadmap** included

---

## 🧪 Testing & Validation

### Environment Setup
- [ ] **Create fresh venv:** `python -m venv .venv_test`
- [ ] **Activate:** `.venv_test\Scripts\activate`
- [ ] **Install deps:** `pip install -r requirements.txt`
- [ ] **All imports work:** `python -c "from src.pipeline import MedicalRAGPipeline; print('OK')"`

### Functional Tests
- [ ] **Build index succeeds:** `python main.py --build-index`
  - Produces: `data/index/index.faiss`, `chunks.pkl`, `meta.json`
  - Outputs document count, chunk count, vector count
  
- [ ] **CLI queries work:**
  ```bash
  python main.py --question "What is type 2 diabetes?"
  python main.py --question "How do I treat a burn?"
  ```
  - Both return answers with source metadata
  
- [ ] **Streamlit UI works:**
  ```bash
  streamlit run app.py
  ```
  - Opens in browser
  - Index building button works
  - Query input accepts questions
  - Results display correctly

### Edge Cases
- [ ] **Empty question:** `python main.py --question ""` — Handled gracefully
- [ ] **Out-of-scope query:** `python main.py --question "quantum computing"` — Returns fallback
- [ ] **Very long query:** Handled without errors
- [ ] **Special characters:** Unicode handled without errors

---

## 🔍 Git Configuration

### .gitignore
- [ ] **Python artifacts excluded:** `__pycache__/`, `*.pyc`, `*.egg-info/`
- [ ] **Virtual environments excluded:** `.venv/`, `venv/`, `env/`
- [ ] **Built index excluded:** `data/index/`, `*.faiss`, `*.pkl`
- [ ] **Model caches excluded:** `.cache/`, `models/`
- [ ] **IDE artifacts excluded:** `.idea/`, `.vscode/`

**Verify:**
```bash
git add .
git status  # Should show only tracked files, not .venv/, __pycache__, data/index/, etc.
```

### Commit History
- [ ] **No large files committed:** Check `git ls-files -l | sort -k5 -rh` (all < 10 MB)
- [ ] **No secret keys or credentials**
- [ ] **No intermediate build artifacts**

---

## 📝 README Content Verification

**Quick checklist of critical sections:**

- [ ] Disclaimer about educational use
- [ ] Quick Start (3 steps: setup, build, query)
- [ ] Project structure clearly shown
- [ ] Technical stack table present
- [ ] Key limitations listed (at least 3–5)
- [ ] Future improvements listed
- [ ] License (MIT)
- [ ] Links to docs/ for deeper dives

---

## 🚀 Before First Push

1. **Clean up:**
   ```bash
   find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
   find . -type d -name .pytest_cache -exec rm -r {} + 2>/dev/null
   find . -name "*.pyc" -delete
   ```

2. **Verify .gitignore:**
   ```bash
   git status  # Should show no ignored files
   ```

3. **Final test run:**
   ```bash
   python main.py --build-index
   python main.py --question "What is diabetes?"
   ```

4. **Commit:**
   ```bash
   git add .
   git commit -m "Initial: offline medical RAG demo for portfolio"
   ```

5. **Push:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/offline-medical-rag-demo.git
   git push -u origin main
   ```

---

## ✅ GitHub Repository Setup

### On GitHub Website

- [ ] **Repository name:** `offline-medical-rag-demo`
- [ ] **Description:** "Offline RAG for medical Q&A — modular Python, FAISS, sentence-transformers, no APIs"
- [ ] **Public:** Yes
- [ ] **README:** Auto-detected (top of page)
- [ ] **Add topics:** `rag`, `nlp`, `retrieval-augmented-generation`, `faiss`, `embeddings`, `portfolio`
- [ ] **Add link to docs:** Optional (GitHub auto-detects `docs/` folder)

---

## 🎓 Interview Prep Verification

- [ ] **30-second pitch** practiced (use in README intro)
- [ ] **Can explain each module** in < 1 minute
- [ ] **Can live-demo** on laptop (build index + 2 queries)
- [ ] **Can discuss limitations** honestly
- [ ] **Can walk through architecture** (data flow diagrams in docs)
- [ ] **Can answer 10+ Q&A** from `docs/INTERVIEW.md`

**Practice run:**
1. Clone repo into fresh folder
2. Setup venv
3. Run `pip install -r requirements.txt`
4. Run `python main.py --build-index`
5. Run 3 queries
6. Explain what each module does
7. Discuss 2–3 limitations

**Expected time:** ~15 minutes total

---

## 📊 Final Checklist Summary

| Category | Status | Notes |
|----------|--------|-------|
| Code Quality | ✓ | All modules have docstrings, type hints |
| File Organization | ✓ | Proper folder structure, no extraneous files |
| Documentation | ✓ | README concise, docs/ folder with guides |
| Testing | ✓ | Manual tests pass, edge cases handled |
| Git Config | ✓ | .gitignore correct, no secrets committed |
| Interview Ready | ✓ | Can explain and demo the system |

---

## 🚨 Common Mistakes to Avoid

❌ **DON'T:**
- Commit `.venv/`, `__pycache__/`, or `data/index/`
- Leave hardcoded paths (should use `config.py`)
- Include personal notes or TODO comments
- Have long module docstrings (keep concise)
- Forget to update README after changes
- Push without testing locally first

✅ **DO:**
- Test setup from a fresh virtual environment
- Keep documentation concise and links to code
- Use type hints consistently
- Return meaningful error messages
- Test CLI, UI, and edge cases before pushing
- Review your own code first (pretend you're a reviewer)

---

## 🎉 You're Ready!

Once all items are checked:
1. ✅ Code is clean and well-documented
2. ✅ Project structure is professional
3. ✅ Tests pass (manual validation)
4. ✅ Setup is reproducible for others
5. ✅ You can explain the entire system
6. ✅ GitHub repo is set up and public

**Push it, share it, and ace those interviews! 🚀**

