# Results Directory

Training outputs will be saved here:

- `lora_model/` — Trained LoRA adapter weights
- `training_history.json` — Loss and accuracy curves
- `config.json` — Configuration used for training
- `evaluation_results.json` — Test set metrics
- `confusion_matrix.png` — Visualization of predictions
- `test_data.pkl` — Tokenized test data for evaluation

After running training, you can load and evaluate models:

```bash
python src/evaluate.py --model_path ./results/lora_model --output_dir ./results
```
