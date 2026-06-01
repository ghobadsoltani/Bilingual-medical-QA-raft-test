# Example Results and Experiments

This folder demonstrates what successful training looks like.

## Files

- **example_training_history.json** — Sample training metrics
- **example_evaluation_results.json** — Sample evaluation output

## How to Generate Your Own

After running training:

```bash
# Training creates these files automatically:
# results/training_history.json
# results/evaluation_results.json
# results/lora_model/
```

## Typical Results

**Training Progress (2 epochs):**
```
Epoch 1/2
  Train Loss: 0.512 | Eval Loss: 0.418 | Eval Accuracy: 0.782

Epoch 2/2
  Train Loss: 0.285 | Eval Loss: 0.312 | Eval Accuracy: 0.828
```

**Final Metrics:**
- Accuracy: ~83%
- F1 Score: ~0.83
- Precision: ~0.83
- Recall: ~0.83

**Parameter Efficiency:**
- Base model: 66,362,368 params
- LoRA: 73,728 params
- Reduction: 900x
- Memory savings: ~265 MB

---

## Experiment Ideas

1. **Rank Sensitivity**: Train with r=4, r=8, r=16 and compare
2. **Dataset Size**: Compare 1K vs 2K vs 8K samples
3. **Model Comparison**: DistilBERT vs BERT vs RoBERTa
4. **Different Tasks**: Try different Hugging Face datasets

Document your experiments and share!
