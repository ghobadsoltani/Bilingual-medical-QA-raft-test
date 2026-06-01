# Quick Start Guide

Get up and running with this LoRA fine-tuning project in 5 minutes.

## Option 1: Jupyter Notebook (Easiest)

```bash
# Install dependencies
pip install -r requirements.txt

# Start Jupyter
jupyter notebook notebooks/experiment.ipynb
```

Run cells sequentially. You'll see parameter counts, quick training, and analysis.

## Option 2: Command Line (Reproducible)

```bash
# Install
pip install -r requirements.txt

# Train (3 epochs, ~8 minutes on GPU)
python src/train.py --config configs/default_config.yaml --output_dir ./results

# Evaluate
python src/evaluate.py --model_path ./results/lora_model --output_dir ./results
```

## Troubleshooting

### CUDA out of memory?
Edit `configs/default_config.yaml`:
```yaml
training:
  batch_size: 16  # Reduce from 32
  gradient_accumulation_steps: 2  # Maintain effective batch size
```

### Slow on CPU?
Use a smaller dataset:
```yaml
data:
  max_samples: 2000  # Reduce from 8000
```

### ModuleNotFoundError?
Make sure you're running from the project root:
```bash
cd efficient-llm-adaptation
python src/train.py --config configs/default_config.yaml
```

## Files Overview

- `src/config.py` — Configuration management
- `src/model.py` — LoRA model setup
- `src/train.py` — Training loop
- `src/evaluate.py` — Evaluation and metrics
- `src/utils.py` — Helper functions
- `configs/default_config.yaml` — Hyperparameters
- `notebooks/experiment.ipynb` — Interactive exploration

## Customize It

Change `configs/default_config.yaml`:
- `base_model`: Try "bert-base-uncased", "gpt2", "microsoft/phi-2"
- `lora.r`: Try 4, 8, 16 (higher = more parameters)
- `training.epochs`: More epochs for better accuracy
- `data.max_samples`: Increase for better results

## Next Steps

1. **Run the notebook** for intuition
2. **Run training** for full results
3. **Modify config** and compare results
4. **Document findings** in `results/`
5. **Share your modifications** on GitHub!

---

Questions? See the full README.md for deep dives into LoRA, Q&A, and research directions.
