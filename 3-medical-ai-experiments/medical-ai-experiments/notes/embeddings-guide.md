# Embeddings Guide

## What Are Embeddings?

Embeddings convert text into numerical vectors that capture semantic meaning. A sentence becomes a list of numbers where similar meanings map to nearby vectors.

```
Input:  "Myocardial infarction is caused by coronary occlusion"
Output: [0.12, -0.34, 0.89, ..., 0.02]  ← 384 numbers encoding meaning
```

## Why Embeddings Matter

1. **Semantic Similarity:** Related medical terms have similar vectors
   - "Heart attack" ≈ "Myocardial infarction"
   - System groups these concepts even without exact keywords

2. **Computational Efficiency:** Compare thousands of documents in milliseconds using cosine similarity

## Model Selection for Medical Text

### Comparison

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| all-MiniLM-L6-v2 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Prototyping |
| all-mpnet-base-v2 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Balanced |
| PubMedBERT | ⭐⭐ | ⭐⭐⭐⭐⭐ | Medical-critical |

### Decision Tree

```
Do you have GPU + time?
├─ Yes → Use PubMedBERT (best quality)
└─ No → Use all-MiniLM (good enough, fast)

Priority: Latency < 100ms?
├─ Yes → all-MiniLM
└─ No → all-mpnet (better quality)
```

## Common Pitfalls

| Issue | Problem | Solution |
|-------|---------|----------|
| Acronyms | "MI" unrecognized | Expand before encoding |
| Negation | "NOT diabetic" misunderstood | Use domain models |
| Rare terms | Medical jargon absent | Use PubMedBERT |
| Large corpus | Encoding takes too long | Cache embeddings |

## Best Practices

1. **Cache embeddings** – Encode documents once, reuse forever
2. **Test on YOUR data** – General benchmarks don't transfer
3. **Use 384D vectors** – Sweet spot for medical (fast + accurate)
4. **Preprocess text** – Expand abbreviations, normalize units
5. **Evaluate empirically** – Run precision@10 on 20 test queries

## References

- Sentence-BERT paper: "Sentence Embeddings using Siamese BERT-Networks"
- sentence-transformers library: https://www.sbert.net/
- Medical models: PubMedBERT, SciBERT, BioSimBERT

---

**Last updated:** 2026-06-01
