# Example Configurations

This folder contains configuration examples for different scenarios.

## Files

- **default_config.yaml** — Balanced for student learning (2K samples, 2 epochs)
- **fast_config.yaml** — Quick test on CPU (1K samples, 1 epoch)
- **full_training_config.yaml** — Better accuracy (8K samples, 3 epochs)
- **different_model_config.yaml** — Using BERT instead of DistilBERT

## How to Use

```bash
# Use a specific config
python src/train.py --config configs/examples/fast_config.yaml

# Or modify default_config.yaml directly
python src/train.py --config configs/default_config.yaml
```

## Recommended Starting Points

**First time? Use default_config.yaml**
- Fast enough to see results (~4 min GPU)
- Good accuracy to understand LoRA
- Reasonable memory requirements

**Want it even faster? Use fast_config.yaml**
- ~2 min on GPU
- Still shows LoRA effectiveness
- Good for testing setup

**Want better accuracy? Use full_training_config.yaml**
- ~8 min on GPU
- Larger dataset = higher accuracy
- Requires more patience!
