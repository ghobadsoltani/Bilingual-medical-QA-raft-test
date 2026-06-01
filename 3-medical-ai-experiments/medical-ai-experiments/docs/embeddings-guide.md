# Embeddings Deep Dive

## What Are Embeddings?

Embeddings are **numerical representations** of text that capture semantic meaning. A model converts a sentence or document into a vector of numbers (e.g., 384-dimensional or 768-dimensional).

```
Input:  "Myocardial infarction is caused by coronary artery occlusion"
         ↓ [SentenceTransformer model]
Output: [0.12, -0.34, 0.89, ..., 0.02]  ← 384 numbers
```

### Why Embeddings Matter for Retrieval

Two key properties make embeddings useful for medical AI:

1. **Semantic Similarity:** Similar medical texts have similar embeddings
   - "heart attack" and "myocardial infarction" → very close vectors
   - "hypertension" and "high blood pressure" → close vectors
   
2. **Computationally Efficient:** Easy to compare embeddings using cosine similarity
   - Comparing all documents to a query takes O(n) operations
   - Can index millions of embeddings for fast retrieval

## How Embeddings Are Created

### Architecture: Sentence Transformers

Most modern embeddings use **Sentence-BERT (SBERT)**:

1. Input text → BERT encoder → Pooling layer (mean/max) → Normalized vector
2. Training: Contrastive learning on sentence pairs
   - Positive pairs: Similar sentences → embeddings close
   - Negative pairs: Dissimilar sentences → embeddings far

### Domain-Specific vs General Embeddings

| Model | Domain | Training Data | Strengths | Limitations |
|-------|--------|---|---|---|
| all-MiniLM-L6-v2 | General | Web data | Small, fast | Generic medical terms |
| PubMedBERT | Biomedical | PubMed abstracts | Medical terminology | Slower, larger |
| BioSimBERT | Biomedical | Clinical notes + abstracts | Clinical language | Research-focused |
| all-mpnet-base-v2 | General | Web data | Quality semantic | Moderate size (110M) |

**Empirical finding:** Domain-specific models perform 15-20% better on medical retrieval tasks, but require more compute.

## Vector Space Intuition

In embedding space, medical concepts form meaningful clusters:

```
       ↑ Cardiac Domain
       |
Sepsis •----• Pneumonia (Infection cluster)
       |
Diabetic • Hypertension (Metabolic cluster)
```

- Documents about similar diseases are nearby
- Query and relevant documents have high cosine similarity
- Irrelevant documents are far away

## Measuring Embedding Quality

For medical text, use:

1. **Retrieval Precision@k** – Of top-k retrieved docs, how many are relevant?
2. **Mean Reciprocal Rank (MRR)** – Rank position of first relevant document
3. **NDCG (Normalized Discounted Cumulative Gain)** – Weighted ranking quality

## Limitations & Failure Modes

### When Embeddings Fail

1. **Rare medical terms** not in training data
   - Solution: Use domain-specific embeddings or fine-tune

2. **Negation handling** – "NOT hypertensive" vs "hypertensive"
   - Embeddings sometimes miss negation nuance
   - Solution: Preprocessing (explicit negation markers)

3. **Acronyms** – "MI" (myocardial infarction), "ARDS" (respiratory distress)
   - Generic models often don't understand medical abbreviations
   - Solution: Expand acronyms before encoding

4. **Multi-word concepts** – Order matters
   - "Drug A with drug B" vs "Drug B with drug A"
   - Solution: Use models trained on clinical text

### Computational Trade-offs

| Dimension | Speed | Quality |
|-----------|-------|---------|
| 64 | ✅ Fastest | ❌ Too lossy |
| 384 | ✅ Fast | ✅ Good |
| 768 | ⚠️ Slower | ✅ Better |
| 1024 | ❌ Slow | ✅ Best |

**Recommendation:** 384D embedding is sweet spot for medical RAG.

## Best Practices for Medical Embeddings

1. **Preprocess medical text:**
   - Expand common abbreviations: "MI" → "myocardial infarction"
   - Normalize units: "5 mg/kg" → standardized format
   - Handle negations: "NOT intolerant" vs "intolerant"

2. **Choose models based on constraints:**
   - Prototype? Use all-MiniLM-L6-v2 (fast, acceptable)
   - Production with GPU? Use domain-specific models
   - Offline system? Use smaller models

3. **Evaluate on YOUR data:**
   - General metrics don't transfer to medical domain
   - Test on subset of your documents with relevance labels
   - Measure precision@10 on actual medical queries

4. **Cache embeddings:**
   - Encode documents once, store vectors
   - Only encode new documents + user queries
   - Massive latency reduction (encoding is the bottleneck)

## Embeddings vs Other Approaches

| Approach | Latency | Quality | Interpretability |
|----------|---------|---------|------------------|
| **Embeddings** | Fast | Good | Low (black-box) |
| **BM25 (keywords)** | Very fast | Limited | Very high |
| **Hybrid** | Moderate | Best | Medium |
| **Cross-encoder reranking** | Slow | Excellent | Low |

**Recommendation:** Embeddings + BM25 hybrid for medical RAG.

## References & Resources

- **Paper:** "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks" (2019)
- **Code:** [sentence-transformers library](https://www.sbert.net/)
- **Medical models:** PubMedBERT, BioSimBERT, SciBERT
- **Evaluation:** BEIR benchmark (standardized retrieval evaluation)

---

**Last Updated:** 2026-05-31
