# 🎯 Interview Preparation Quick Reference Card

**Medical AI Internship Interview - 1 Page Cheat Sheet**

---

## YOUR PROJECT IN 30 SECONDS

**Problem**: How do we build reliable medical QA systems with constraints?  
(Offline, small models, safety)

**Solution**: RAG pipeline with grounding  
(embeddings → chunking → retrieval → grounding → small models)

**Key Finding**: Grounding reduces hallucination 65% → 8%  
Small models work *with* grounding; fail without it

**Impact**: Demonstrates end-to-end system design for medical AI

---

## THE 5-NOTEBOOK STORY

| # | Notebook | Question | Finding |
|---|----------|----------|---------|
| 1 | Embeddings | Which model? | Domain-specific 15-20% better; latency trade-off |
| 2 | Chunking | How to split? | Sentence-based > fixed-size; domain-aware adds 12% |
| 3 | Retrieval | Semantic or keyword? | Hybrid 82% vs 68/64% alone; use RRF |
| 4 | QA Grounding | Reduce hallucination? | Yes: 65% → 8% with retrieval |
| 5 | Small Models | Can 7B work? | With grounding yes (78%); without no (45%) |

**Narrative**: Data quality compounds through pipeline → grounding essential → small models viable

---

## STRONG ANSWERS TO TOP 3 QUESTIONS

### Q1: Tell us about your project
**A**: "RAG for medical QA with constraints (offline, 7B models). Embeddings → chunking → retrieval → grounding → validation. Key finding: grounding cuts hallucination 65% → 8%, makes small models viable."

### Q2: Why these experiments?
**A**: "Dependency chain: embeddings first (foundation), then chunking (what gets embedded), then retrieval (search quality), then grounding (use retrieval), then models (feasibility). Each layer builds on previous one. No wasted effort."

### Q3: Main learning?
**A**: "System is global not local. One optimization helps only if downstream components use it. Better embeddings help only if retrieval ranks them well. Better retrieval helps only if LLM can use it. This is why order matters."

---

## KEY NUMBERS TO REMEMBER

- **Domain embeddings**: 15-20% better than general on medical text
- **Sentence chunking**: 18% better precision than fixed-size
- **Domain-aware chunking**: +12% vs sentence-based
- **Hybrid retrieval**: 82% precision vs 68% semantic / 64% BM25 alone
- **Hallucination reduction**: 65% → 8% with grounding
- **Small model accuracy**: 78% (with grounding) vs 45% (without)
- **Latency**: SciBERT 200ms, MiniLM 50ms
- **Learning path**: ~100 minutes total for all 5 notebooks

---

## LIKELY FOLLOW-UPS (Prep These)

1. **Trade-offs**: How do you decide between X and Y?
   - Context matters (offline? cloud? cost? accuracy?)
   - No universal answer; depends on constraints

2. **Failures**: Where does your system break?
   - Out-of-distribution queries
   - Numerical reasoning (7B struggles with math)
   - Contradictory sources

3. **Scale**: How would this work for a hospital?
   - Distributed vector DB
   - GPU inference for <500ms latency
   - On-premises for HIPAA privacy
   - Monitoring for when system fails

4. **Comparison to GPT-4/Claude**: How does this compare?
   - Mine: transparent, controllable, privacy-preserving, 1/10th cost
   - Theirs: more capable, general knowledge, less transparent

5. **What's next?**: What would you improve?
   - Real medical datasets (MIMIC, PubMed)
   - Domain expert validation
   - Richer evaluation metrics
   - Clinician-in-the-loop interface

---

## WEAK ANSWERS TO AVOID ❌

- "I built a medical AI system using machine learning" (too vague)
- "This is production-ready" (untested on real patients, regulatory issues)
- "I'm not sure why embeddings matter" (shows lack of understanding)
- "My system is 90% accurate" (needs context: on what? synthetic? real?)
- "I optimized for latency" (in medicine, accuracy > speed)
- "Small models are useless" (wrong; they work with grounding)
- "I used some embedding model from HuggingFace" (unprofessional; know details)

---

## MEDICAL AI CONTEXT ⚠️

**Your competitive advantage**: You understand medical stakes
- Hallucination can harm patients
- Privacy (HIPAA) matters
- Regulatory compliance required
- Need clinician verification
- This is learning lab, not production

**Show you know**:
- "This is validated on synthetic data, not real patients"
- "Real deployment needs regulatory approval, clinician involvement"
- "Medical errors have consequences; can't just optimize for accuracy metrics"

---

## STRUCTURE YOUR ANSWERS (Recommended Format)

**Q: [Question]**

1. **Direct answer** (30 sec): Directly answer question; no preamble
2. **Evidence** (1-2 min): Show data/results/reasoning
3. **Why it matters** (30 sec): Connect to real-world impact
4. **Honest limitations** (30 sec): What you didn't test; what's needed

Total: 2-3 minutes per question

---

## BEFORE INTERVIEW

- [ ] Reread your README
- [ ] Run each notebook (verify they work)
- [ ] Know your tech stack by name (Sentence Transformers, FAISS, BM25, RRF)
- [ ] Prepare 2-3 failure cases with honesty
- [ ] Identify 3 things you'd do differently
- [ ] Prepare 2-3 questions to ask interviewer
- [ ] Practice saying numbers (15-20%, 65% → 8%, 78% vs 45%)

---

## CLOSING QUESTION: "What Would You Ask?"

**Show intellectual engagement**:
- "How do you think about the fairness problem—does your system work equally well for all demographics?"
- "What's your approach to regulatory compliance for medical AI?"
- "How do you balance innovation speed with validation rigor?"

This flips the interview. Shows you think strategically about the problem.

---

## FINAL MINDSET

- ✅ You did thoughtful work
- ✅ You can articulate why it matters
- ✅ You understand limitations
- ✅ You have a roadmap to production
- ✅ You're intellectually honest
- ✅ You care about the problem

**You belong in an AI/ML interview.** Be confident, be clear, be honest.

---

**Good luck! 🚀**

