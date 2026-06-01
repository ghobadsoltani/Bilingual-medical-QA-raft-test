# Design & Architecture Guide

## 📐 Project Architecture

This project follows a clean, modular architecture suitable for both learning and production deployment.

```
efficient-llm-adaptation/
│
├── src/                          # Core library
│   ├── config.py                 # Configuration (YAML → Python dataclasses)
│   ├── model.py                  # LoRA model initialization
│   ├── train.py                  # Training loop with validation
│   ├── evaluate.py               # Evaluation, metrics, visualization
│   └── utils.py                  # Helpers (logging, plotting, seeds)
│
├── notebooks/                    # Interactive exploration
│   └── experiment.ipynb          # Guided walkthrough with visualizations
│
├── configs/                      # Configuration files
│   └── default_config.yaml       # Hyperparameters (easy to modify)
│
├── results/                      # Training outputs
│   ├── lora_model/               # Saved LoRA weights (only ~74KB!)
│   ├── training_history.json     # Loss curves
│   └── evaluation_results.json   # Test metrics
│
├── README.md                     # Comprehensive documentation
├── QUICKSTART.md                 # Get running in 5 minutes
├── setup.py                      # Optional: pip install -e .
├── requirements.txt              # Dependencies
└── .gitignore                    # Git ignore patterns
```

---

## 🎯 Design Principles

### 1. **Configuration-Driven**
All hyperparameters live in `configs/default_config.yaml`, not hardcoded:
- Easy to experiment with different settings
- Reproducibility (config is saved with results)
- YAML is human-readable

### 2. **Modular & Reusable**
Each component is standalone:
- `config.py` → Load and validate configuration
- `model.py` → Initialize model with LoRA
- `train.py` → Training loop (can be imported)
- `evaluate.py` → Evaluation pipeline
- No spaghetti code or circular dependencies

### 3. **Production-Ready Patterns**
- Logging via Python's `logging` module
- Device handling (GPU/CPU automatic)
- Checkpoint saving (best model only)
- Reproducible seeds (same results every run)

### 4. **Learner-Friendly**
- Clear variable names and docstrings
- Comments explaining *why*, not just *what*
- Jupyter notebook for interactive learning
- Scripts for reproducible results

---

## 🔍 Key Components Explained

### `config.py`
**Purpose**: Centralized configuration management

```python
@dataclass
class ExperimentConfig:
    model: ModelConfig        # Base model choice
    lora: LoRAConfig         # LoRA hyperparameters
    training: TrainingConfig # Optimizer, learning rate, etc.
    data: DataConfig         # Dataset and preprocessing
```

**Why this design?**
- Dataclasses provide type hints and validation
- Hierarchical structure mirrors the problem domain
- YAML parsing is clean and extensible
- Can easily add new config sections

### `model.py`
**Purpose**: LoRA model setup with Hugging Face + PEFT

**Key function: `LoRAModel.setup()`**
```python
def setup(self):
    # 1. Load tokenizer
    # 2. Load base model
    # 3. Create LoRA config
    # 4. Apply LoRA with get_peft_model()
    # 5. Print parameter statistics
```

**Why PEFT?**
- Official Hugging Face library for efficient adapters
- Supports LoRA, QLoRA, Adapters, Prefix Tuning, etc.
- Production-grade code quality
- Easy switching between methods

### `train.py`
**Purpose**: Training loop with validation and early stopping

**Design choices:**
- **Gradient accumulation**: Simulate larger batch sizes on limited memory
- **Learning rate scheduling**: Warmup + linear decay (standard for transformers)
- **Early stopping**: Patience counter prevents overfitting
- **Best model saving**: Only saves checkpoint when eval loss improves
- **Reproducibility**: Seed set before everything

**Why not use Hugging Face Trainer?**
- Educational project (Trainer is a black box for learning)
- Custom evaluation loop is clearer for understanding
- Trainer adds unnecessary complexity for this scale

### `evaluate.py`
**Purpose**: Comprehensive evaluation with metrics and plots

**Generates:**
- Accuracy, Precision, Recall, F1-Score (per-class)
- Confusion matrix visualization
- Structured JSON report
- Classification report (scikit-learn)

---

## 🔄 Training Pipeline

```
1. Load Config (YAML)
   ↓
2. Initialize Model with LoRA
   ↓
3. Load & Tokenize Dataset
   ↓
4. Train Loop (3 epochs):
   ├─ Forward pass
   ├─ Backward pass (only LoRA gradients)
   ├─ Gradient clipping & optimization
   └─ Validation
   ↓
5. Save Best Checkpoint
   ↓
6. Evaluate on Test Set
   ↓
7. Save Results (JSON, plots)
```

**Time Complexity:**
- One epoch with 8K samples, batch size 32: ~2-3 min on RTX 2060
- Full training (3 epochs): ~8-10 min
- CPU: ~8 minutes for 1K samples

---

## 💾 Memory Breakdown

### DistilBERT + LoRA (rank=8)

| Component | Size |
|-----------|------|
| Model parameters (frozen) | 252 MB |
| LoRA weights (trainable) | 280 KB |
| Activations (one batch) | 64 MB |
| Optimizer state (Adam) | ~280 KB × 2 (m, v) |
| **Total for training** | ~330 MB |

### Why LoRA Saves Memory

Full fine-tuning requires:
- `W` (66M params × 4 bytes) = 264 MB
- `∇W` (gradients) = 264 MB
- Optimizer state (m, v) = 528 MB
- **Total** ≈ 1 GB

With LoRA:
- Base `W` frozen → no gradients
- Only `A`, `B` trainable
- Becomes ~35 MB for training

---

## 🎓 How to Extend This Project

### Adding a New Model
Edit `configs/default_config.yaml`:
```yaml
model:
  base_model: "microsoft/phi-2"  # Any HF Hub model
  num_labels: 2
```

### Adding QLoRA (for larger models)
In `src/model.py`:
```python
from peft import prepare_model_for_kbit_training

model = AutoModelForSequenceClassification.from_pretrained(
    ...,
    quantization_config=BitsAndBytesConfig(
        load_in_4bit=True,
        ...
    )
)
model = prepare_model_for_kbit_training(model)
```

### Multi-GPU Training
In `src/train.py`:
```python
from torch.nn import DataParallel
model = DataParallel(model)  # or use accelerate library
```

### Different Task (e.g., token classification)
1. Change `TaskType` in `model.py`:
   ```python
   task_type=TaskType.TOKEN_CLS
   ```
2. Update dataset preprocessing in `train.py`
3. Adjust output layer size

---

## ✅ Testing & Validation

### Manual Testing
```bash
# Quick test (1 epoch, 100 steps)
python src/train.py --config configs/default_config.yaml

# Full training
# Modify default_config.yaml: set epochs: 3

# Evaluate
python src/evaluate.py --model_path ./results/lora_model
```

### Reproducibility Checklist
- [ ] Random seed set in `train.py`
- [ ] Deterministic dataloader (shuffle=True only in training)
- [ ] Device handling tested on both GPU and CPU
- [ ] Results saved with config (compare across runs)

---

## 🚀 Deployment Considerations

### Inference Only
```python
from transformers import pipeline
from peft import PeftModel

# Load once
base = AutoModelForSequenceClassification.from_pretrained(...)
model = PeftModel.from_pretrained(base, "results/lora_model")
model.eval()

# Use many times
predictions = model(...)
```

### Merge Weights (Optional)
```python
model = model.merge_and_unload()  # Fuses LoRA into base weights
torch.save(model.state_dict(), "merged_model.pt")
# Now: single model, no LoRA overhead
```

### Serving Multiple Adapters
```python
# Same base model, different adapters
base = load_base_model()

adapters = {
    'sentiment': PeftModel.from_pretrained(base, "adapters/sentiment"),
    'emotion': PeftModel.from_pretrained(base, "adapters/emotion"),
}

# Route requests:
# request_type == 'sentiment' → use adapters['sentiment']
```

---

## 📊 Benchmarking Your Results

After training, analyze in `results/`:

1. **Training History** (`training_history.json`):
   - Plot loss curves
   - Check if learning is smooth
   - Look for overfitting (eval loss diverging from train)

2. **Evaluation Results** (`evaluation_results.json`):
   - Per-class F1 scores
   - Confusion matrix (which classes confused?)
   - Compare LoRA vs. baseline (if available)

3. **Experiment Log** (save to results/):
   ```json
   {
     "experiment": "sentiment_lora_r8",
     "date": "2024-01-15",
     "config_hash": "abc123",
     "test_accuracy": 0.868,
     "notes": "Achieved 86.8% with 900x parameter reduction"
   }
   ```

---

## 🎯 Interview Talking Points

When discussing this project:

1. **Architecture**: "Modular design with YAML config for easy experimentation"
2. **LoRA**: "Reduced parameters 900x, kept accuracy competitive"
3. **Reproducibility**: "Fixed seeds, saved configs, deterministic dataloader"
4. **Scalability**: "Same code works for different models and tasks"
5. **Production-ready**: "Checkpoint management, proper logging, error handling"

---

## 🔗 Related Work & References

**Parameter-Efficient Fine-Tuning Methods:**
- LoRA (2021) — What we use
- QLoRA (2023) — LoRA + 4-bit quantization
- Adapters — Module-based adaptation
- Prefix Tuning — Learnable prompt prefixes

**Implementation:**
- PEFT library — Official Hugging Face implementation
- Transformers library — Pre-trained models
- accelerate — Multi-GPU training

**Best Practices:**
- Warmup → faster convergence
- Gradient clipping → stable training
- Early stopping → prevent overfitting
- Config files → reproducibility

---

Good luck! This project is designed to be a solid foundation for understanding parameter-efficient fine-tuning. Feel free to extend it and share your improvements! 🚀
