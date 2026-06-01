# Decisions Log

Evolution of thinking across experiments. Updated as insights emerge.

## Embeddings: General vs Domain-Specific

### Initial Assumption ❌
"General embeddings good enough for medical."

### Reality (Experiment 01)
- all-MiniLM: 65% precision@10
- PubMedBERT: 78% precision@10 (+20%)
- Trade-off: 3x slower, larger model

### Decision ✅
**Start with all-MiniLM. Upgrade to domain models if quality insufficient.**

Reasoning: Prototyping speed matters. Model swaps are trivial.

---

## Chunking: Size Matters

### Initial Assumption ❌
"Larger chunks capture more context → better."

### Reality (Experiment 02)
- Fixed 512-token chunks: dilute relevance signals
- Sentence-based 100-150 tokens: optimal for medical
- Document type matters (clinical ≠ research)

### Decision ✅
**Use sentence-based chunking; 100-150 tokens for medical documents.**

Reasoning: Smaller chunks + multiple hits > larger chunks + fewer hits in medical context.

---

## Retrieval: Hybrid is Essential

### Initial Assumption ❌
"Embeddings capture everything; BM25 unnecessary."

### Reality (Experiment 03)
- Semantic-only misses acronyms (STEMI, ARDS)
- BM25-only misses synonyms
- Hybrid: 15-25% improvement

### Decision ✅
**Implement hybrid retrieval with RRF ranking.**

Reasoning: Medical language has specific terminology + need for semantic matching. RRF is robust, parameter-free.

---

## Grounding: Non-Negotiable

### Initial Assumption ⚠️
"Smart models can answer reliably."

### Reality (Experiment 04)
- Non-grounded: 65% hallucination
- Grounded: 8% hallucination
- Simultaneously improves quality + interpretability

### Decision ✅
**Mandatory grounding: All answers must cite sources.**

Reasoning: Medical context = hallucination unacceptable. Grounding forces safe behavior.

---

## Small Models: Accept Constraints

### Initial Assumption ⚠️
"7B models can handle medical reasoning with good prompting."

### Reality (Experiment 05)
- Drug interactions: 35% accurate (dangerous)
- Dosage calculations: 28% accurate (unsafe)
- With grounding: 75%+ for retrieval tasks

### Decision ✅
**Use 7B for retrieval-only; 13B+ for reasoning.**

Reasoning: Accept the constraint. RAG (retrieval + synthesis) is right approach for medical AI.

---

## Architecture Evolution

```
V1 (Naive):
  Query → Embedding → Top-5 → LLM → Answer
  ❌ High hallucination, no transparency

V2 (Better):
  Query → Embedding → Top-5 → Grounded LLM → Answer + Citations
  ✅ Lower hallucination, transparent

V3 (Recommended):
  Query → [Embedding + BM25] → Hybrid Rank → Grounded LLM → Answer + Citations
  ✅ Best quality, safe, interpretable
```

---

## Key Insights

### Insight 1: RAG > Fine-Tuning for Medical
- No labeled data overhead
- Updates are document-level, not model-level
- Safety baked in (grounding)
- More interpretable

### Insight 2: Hybrid Search Essential
Medical language needs:
- Formal terms (embeddings capture)
- Acronyms (BM25 captures)
- Neither alone sufficient

### Insight 3: Chunking Underrated
- Wrong strategy → information loss
- Right strategy → 10% quality gain without model changes
- Often overlooked but high-leverage

### Insight 4: Grounding is a Feature
Counter-intuitive: Forcing citations actually helps:
- Reduces hallucination
- Makes answers shorter, actionable
- Provides audit trail
- Builds trust

### Insight 5: Accept Constraints
- 7B models insufficient for autonomous reasoning
- That's OK; RAG systems don't need autonomous reasoning
- Better to augment clinicians than replace them

---

## Decision Rationale

| Decision | Alternative | Why This Path |
|----------|-------------|---------------|
| Sentence chunking | Fixed-size | Respects natural boundaries; better for unstructured medical text |
| Hybrid retrieval | Embedding-only | Medical terms demand exact matching |
| RRF ranking | Learned weights | No labeled data; RRF is robust |
| 7B + grounding | 13B fine-tuned | Privacy, cost, safety; grounding compensates |
| Retrieval focus | Reasoning focus | Right problem for medical setting |

---

## Confidence Levels

| Finding | Level | Reason |
|---------|-------|--------|
| Grounding reduces hallucination | ⭐⭐⭐⭐⭐ | Consistent across models; large effect |
| Hybrid > semantic-only | ⭐⭐⭐⭐ | Tested multiple query types |
| Sentence chunking optimal | ⭐⭐⭐ | Limited corpus; needs more validation |
| 7B + grounding works | ⭐⭐⭐⭐ | Clear improvement, specific constraints |

---

**Last updated:** 2026-06-01
