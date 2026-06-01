# Retrieval Strategies

## Two-Layer Architecture

Good retrieval requires **both** semantic and keyword matching:

```
Query → [Semantic Path (embeddings)]  →  Top-20
     → [Keyword Path (BM25)]          ↓
                                    Hybrid Merge
                                      ↓
                                    Top-10
```

## Strategy 1: Semantic Search (Embeddings)

**Strengths:**
- Captures synonyms: "heart attack" finds "MI" discussions
- Robust to paraphrasing: "reduced kidney function" → "renal impairment"

**Weaknesses:**
- Misses exact terminology
- Slower than BM25
- Requires domain-specific models for medical text

## Strategy 2: Keyword Search (BM25)

**Strengths:**
- Fast, matches exact terms
- Great for acronyms and specific medications
- No model needed (statistical algorithm)

**Weaknesses:**
- Misses synonyms
- Poor for general medical queries
- Ignores semantic relationships

## Strategy 3: Hybrid (Recommended)

Combine both using **Reciprocal Rank Fusion (RRF)**:

```python
def rrf(bm25_rank, semantic_rank, k=60):
    return 1/(k + bm25_rank) + 1/(k + semantic_rank)
```

**Why RRF:**
- No parameter tuning needed
- Handles different score scales
- Simple, effective, proven

**Performance:** Hybrid typically 15-25% better than either alone on medical queries.

## Chunking Strategy

**Key insight:** How you split documents affects everything.

### By Document Type

| Type | Strategy | Chunk Size |
|------|----------|-----------|
| Clinical Notes | Sentence-based | 100-150 tokens |
| Research Abstracts | Fixed (0% overlap) | 256-512 tokens |
| Guidelines | Respect hierarchy | 200-400 tokens |

**Best practice:** Test on your data. Domain-specific chunk sizes matter.

## Evaluation

### Without Labels (Quick)
- Manual spot-check: Review top-5 results on 20 queries
- Look for: Relevant docs present? No noise?

### With Labels (Gold Standard)
- **Precision@10:** % of top-10 results relevant
- **MRR:** Rank position of first relevant doc
- **NDCG:** Weighted ranking quality

**Target:** Precision@10 ≥ 80% for medical applications

## Common Mistakes

- ❌ Using only embeddings (misses exact matches)
- ❌ Large fixed-size chunks (information dilution)
- ❌ No preprocessing (acronyms fail)
- ❌ Not caching embeddings (latency explosion)
- ❌ No evaluation (flying blind)

## Optimization Checklist

- [ ] Embeddings: Domain-appropriate?
- [ ] Chunking: Tested multiple sizes?
- [ ] Hybrid: Running semantic + BM25?
- [ ] Evaluation: Tested on 20+ queries?
- [ ] Caching: Embeddings cached?
- [ ] Latency: Full pipeline < 500ms?

---

**Last updated:** 2026-06-01
