# Safety Considerations

## Why Medical AI Demands Higher Standards

Medical errors have direct health consequences. Standard AI benchmarks don't apply.

## Core Problem: Hallucination

### What Happens
```
Query: "Can I take aspirin with warfarin?"
LLM: "Yes, they work synergistically."
Reality: Dangerous interaction; increases bleeding risk 2-3x.
```

### Solution: Mandatory Grounding

```python
# Every answer MUST cite retrieved documents
IF no retrieved document answers query:
    THEN: "Information not in knowledge base. Consult physician."
ELSE:
    Generate answer from documents with explicit citations
```

### Layer-Based Approach

1. **Retrieval Quality** – Better documents reduce hallucination
2. **Explicit Grounding** – Require citations, refuse to answer if unsure
3. **Confidence Thresholds** – Only present high-confidence answers
4. **Human Review** – Flag low-confidence for expert validation

## Model Capability Boundaries

### Safe for 7B Models (With Grounding)
- ✅ Information retrieval
- ✅ Document summarization
- ✅ Symptom classification

### Not Safe for 7B Models
- ❌ Autonomous diagnosis
- ❌ Drug dosing calculations
- ❌ Risk stratification without review

### General Rule
```
Simple tasks (lookup)          → 7B + grounding OK
Moderate (classification)      → 13B with validation
Complex (reasoning/diagnosis)  → Require clinician review
```

## Privacy & Compliance

**Key Regulations:**
- **HIPAA:** Protected health info can't leave secure environment
- **GDPR:** Patient data needs explicit consent
- **Local laws:** Country-specific requirements

**Practical Options:**
1. **Offline systems** (most secure) – Run locally, no external calls
2. **Secure cloud** (compliant) – HIPAA-certified AWS/Azure
3. **De-identified data** (balanced) – Remove identifiers

## Uncertainty & Confidence

LLMs don't know what they don't know. Always quantify uncertainty:

```python
# Method 1: Retrieval confidence
high_conf = max_document_similarity > 0.85
low_conf = max_document_similarity < 0.70

# Method 2: Abstention
if confidence < 0.75:
    return "Cannot answer reliably. Recommend expert consultation."
```

**Present to users:**
- ❌ "Patient likely has MI" (hides uncertainty)
- ✅ "Based on documents, MI is likely. Recommend ECG to confirm." (transparent)

## Regulatory Path

For clinical applications:
1. **Define intended use** clearly
2. **Conduct validation study** (even small is better than none)
3. **Document limitations** explicitly
4. **Maintain audit trail** of decisions
5. **Plan for updates** and revalidation

## Human-AI Collaboration

**Right approach:**
```
Clinician + AI System  ✅ Better than either alone

Clinician alone        ✅ Limited but reliable
AI system alone        ❌ Fast but unreliable
```

**Good interface design:**
- Show retrieval results + confidence
- Highlight uncertain areas
- Enable quick override
- Log all disagreements (improvement signal)

## Failure Mode Checklist

- [ ] Hallucination: System cites sources? Claims verifiable?
- [ ] Outdated info: System knows cutoff date?
- [ ] Domain mismatch: Works outside training scope?
- [ ] Context blindness: Misses important patient context?
- [ ] Overconfidence: Communicates uncertainty?
- [ ] Drift: Performance degrades over time?

---

**Last updated:** 2026-06-01
