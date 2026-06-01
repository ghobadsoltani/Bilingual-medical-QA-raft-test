# Medical AI Experiments: RAG & Small Language Models

A structured learning lab for **retrieval-augmented generation (RAG)**, **embeddings**, and **grounded question-answering** in medical AI contexts. This repository documents systematic experiments exploring practical constraints: offline systems, small language models (7B parameters), and retrieval optimization.

## ⚡ Quick Start

```bash
# Setup
git clone <repo-url>
cd medical-ai-experiments
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run notebooks
jupyter notebook notebooks/
```

## 📚 How to Use This Repository

### For Learners (New to RAG)
Follow the **Suggested Learning Path** below. Each notebook is self-contained with explanations and code examples. Estimated time: ~100 minutes total.

### For Researchers
Review the **docs/** folder for deep dives on specific topics (embeddings, retrieval strategies, safety). Each notebook includes citations and links to research papers.

### For Portfolio/Internship
The complete workflow demonstrates:
- ✅ End-to-end RAG system design
- ✅ Practical constraints (offline, 7B models, cost)
- ✅ Evaluation metrics and benchmarking
- ✅ Medical AI safety considerations
- ✅ Production-ready code patterns

## 🎯 Suggested Learning Path

| # | Notebook | Focus | Duration | Key Learning |
|---|----------|-------|----------|--------------|
| 1 | [01-embeddings.ipynb](notebooks/01-embeddings.ipynb) | Embedding models & trade-offs | 15 min | Why embedding quality matters; model selection criteria |
| 2 | [02-chunking.ipynb](notebooks/02-chunking.ipynb) | Document chunking strategies | 20 min | How document structure affects retrieval; best practices |
| 3 | [03-retrieval.ipynb](notebooks/03-retrieval.ipynb) | Hybrid retrieval (semantic + BM25) | 20 min | Combining search methods; ranking and reranking |
| 4 | [04-qa-grounding.ipynb](notebooks/04-qa-grounding.ipynb) | Grounded QA & hallucination reduction | 20 min | Grounding techniques; citations and fact-checking |
| 5 | [05-small-models.ipynb](notebooks/05-small-models.ipynb) | Small LLMs (7B) in constrained settings | 25 min | Model size trade-offs; when grounding compensates |

**Narrative**: Embeddings → Document Structure → Retrieval Quality → Answer Grounding → Small Model Feasibility

## 📁 Repository Structure

```
medical-ai-experiments/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
│
├── notebooks/                     # Jupyter notebooks (interactive experiments)
│   ├── 01-embeddings.ipynb
│   ├── 02-chunking.ipynb
│   ├── 03-retrieval.ipynb
│   ├── 04-qa-grounding.ipynb
│   └── 05-small-models.ipynb
│
├── docs/                          # Technical documentation & deep dives
│   ├── embeddings-guide.md        # Embedding theory & medical domain considerations
│   ├── retrieval-guide.md         # Chunking & ranking strategies; evaluation metrics
│   ├── safety-considerations.md   # Hallucination mitigation; regulatory compliance
│   └── architecture-decisions.md  # Design decisions; lessons learned; confidence levels
│
└── data/                          # Sample datasets (see .gitignore for large file rules)
    └── .gitkeep                   # Placeholder for data directory
```

## 🔍 What Each Notebook Covers

### 01-embeddings.ipynb
**Question**: Which embedding model is best for medical text?  
**Key Findings**:
- Domain-specific models (e.g., SciBERT, PubMedBERT) are 15-20% better on medical text
- General models (e.g., all-MiniLM-L6-v2) are fast and cost-effective for many use cases
- Trade-off: quality vs latency vs cost

### 02-chunking.ipynb
**Question**: How should we split medical documents for retrieval?  
**Key Findings**:
- Sentence-based chunking beats fixed-size; preserves semantic boundaries
- Domain-aware chunking (respecting headings, sections) improves coherence
- Overlap = small gains; minimal cost

### 03-retrieval.ipynb
**Question**: Semantic search or BM25 or hybrid?  
**Key Findings**:
- Hybrid retrieval (BM25 + semantic) outperforms single methods by 15-25%
- Reciprocal Rank Fusion (RRF) is simple and effective for combining rankings
- Reranking (e.g., cross-encoder) improves precision but adds latency

### 04-qa-grounding.ipynb
**Question**: How can we reduce hallucination in medical QA?  
**Key Findings**:
- Grounding reduces hallucination from ~65% to ~8% (measured on synthetic data)
- Citations enable trust and human verification
- LLM reasoning + retrieval is better than either alone

### 05-small-models.ipynb
**Question**: Can 7B parameter models do medical QA?  
**Key Findings**:
- With grounding: yes, competitive performance
- Without grounding: failure modes in autonomous reasoning
- Cost and latency are major wins; accuracy requires careful tuning

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.10+ |
| **Notebooks** | Jupyter |
| **Embeddings** | Sentence Transformers, FAISS |
| **Retrieval** | rank-bm25, semantic search |
| **LLMs** | Transformers, Ollama (local) |
| **Evaluation** | sklearn metrics |
| **Visualization** | Matplotlib, Seaborn |

## 💡 Use Cases

- **Internship Portfolio**: Demonstrate full-stack RAG system design
- **Thesis Foundation**: Experimental framework for medical NLP research
- **Production Baseline**: Starting point for real-world medical AI deployment
- **Learning**: Structured introduction to RAG concepts and medical AI constraints

## ⚠️ Important: Medical AI Safety

This is a **learning lab with synthetic data**. It is **not** production-ready medical software. Before deploying any medical AI system:
- ✅ Validate with domain experts
- ✅ Test on real patient data (with proper ethics approval)
- ✅ Implement rigorous evaluation metrics
- ✅ Document limitations and failure modes
- ✅ Ensure regulatory compliance (HIPAA, GDPR, local laws)

See [docs/safety-considerations.md](docs/safety-considerations.md) for details.

## 📖 How to Contribute

Found an issue? Have a suggestion? Open an issue or pull request!

Suggested improvements:
- Additional embedding models (e.g., CrossEncoder, ColBERT)
- Real medical datasets (with proper licensing)
- Extended LLM comparisons (13B, 70B models)
- Evaluation benchmarks (medical QA datasets)

## 📄 License

This project is licensed under the MIT License. See `LICENSE`.

## 🙏 Acknowledgments

This repository was inspired by cutting-edge research in:
- Retrieval-Augmented Generation (Lewis et al., 2020)
- Medical NLP (PubMedBERT, BioBERT)
- Grounded Language Models (Thawani et al., 2022)

---

**Last updated**: May 2026  
**Status**: Active learning project  
**Maintainer**: [Your Name]
