"""
Training loop for LoRA fine-tuning.

This script:
  1. Loads a dataset (IMDb reviews in this example)
  2. Creates a LoRA-adapted model
  3. Trains for a few epochs (fine-tunes the LoRA parameters)
  4. Saves the best checkpoint
  5. Evaluates on a test set

Runtime: ~4 minutes on GPU (batch_size=16, 2 epochs, 2K samples)
         ~15 minutes on CPU
Memory: ~2-4 GB
"""

import json
import pickle
import argparse
import torch
from pathlib import Path
from torch.optim import AdamW
from torch.utils.data import DataLoader, random_split
from transformers import get_linear_schedule_with_warmup
from datasets import load_dataset
from tqdm import tqdm

from .config import ExperimentConfig
from .model import LoRAModel
from .utils import set_seed, create_logger


logger = create_logger(__name__)


class Trainer:
    """Handles the full training pipeline: setup, training, evaluation, saving."""
    
    def __init__(self, config: ExperimentConfig, output_dir: str = "./results"):
        """
        Initialize trainer.
        
        Args:
            config: Experiment configuration (hyperparameters, model, etc.)
            output_dir: Where to save checkpoints and results
        """
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Use GPU if available, otherwise CPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Track the best model
        self.best_eval_loss = float('inf')
        self.patience_counter = 0  # For early stopping
        
        # Record metrics to plot later
        self.training_history = {
            'train_loss': [],
            'eval_loss': [],
            'eval_accuracy': []
        }
    
    def prepare_data(self) -> tuple:
        """
        Load and tokenize the IMDb dataset.
        
        Tokenization: converts words/text into numbers the model can process.
        
        Returns:
            Tuple of (train_dataloader, eval_dataloader, test_data)
        """
        logger.info(f"Loading dataset: {self.config.data.dataset_name}")
        
        # Load from Hugging Face Hub (auto-downloads if not cached)
        dataset = load_dataset(self.config.data.dataset_name, split='train')
        
        # Limit dataset size for quick iteration (makes training fast)
        if self.config.data.max_samples and len(dataset) > self.config.data.max_samples:
            dataset = dataset.select(range(self.config.data.max_samples))
            logger.info(f"Using {self.config.data.max_samples} samples (full dataset: {len(dataset)} samples)")
        
        # Tokenize: convert text to token IDs
        # Padding: pad short reviews to max_length
        # Truncation: cut long reviews to max_length
        def tokenize_fn(batch):
            return self.tokenizer(
                batch['text'],
                truncation=True,
                padding='max_length',
                max_length=self.config.data.max_length
            )
        
        logger.info("Tokenizing dataset...")
        dataset = dataset.map(tokenize_fn, batched=True, remove_columns=['text'])
        dataset = dataset.rename_column('label', 'labels')
        dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'labels'])
        
        # Split into train and eval sets
        train_size = int(len(dataset) * self.config.data.train_test_split)
        eval_size = len(dataset) - train_size
        
        train_dataset, eval_dataset = random_split(dataset, [train_size, eval_size])
        
        # Create data loaders (batches and shuffles data)
        train_dataloader = DataLoader(
            train_dataset,
            batch_size=self.config.training.batch_size,
            shuffle=True  # Shuffle improves training
        )
        eval_dataloader = DataLoader(
            eval_dataset,
            batch_size=self.config.training.batch_size,
            shuffle=False  # Don't shuffle evaluation
        )
        
        logger.info(f"Train: {len(train_dataset)} samples | Eval: {len(eval_dataset)} samples")
        
        # Save eval data for later use
        test_data = {
            'texts': [dataset[i]['input_ids'] for i in range(len(eval_dataset))],
            'labels': [dataset[i]['labels'] for i in range(len(eval_dataset))]
        }
        
        return train_dataloader, eval_dataloader, test_data
    
    def train_epoch(self, model, train_dataloader, optimizer, scheduler):
        """
        Train for one epoch.
        
        What happens:
          1. For each batch of reviews:
             - Forward pass: get predictions from model
             - Compute loss (how wrong were we?)
             - Backward pass: compute gradients (how much to adjust weights?)
             - Optimizer step: update LoRA matrices based on gradients
        
        Returns:
            Average training loss for this epoch
        """
        model.train()  # Set to training mode (enables dropout, etc.)
        total_loss = 0.0
        
        progress_bar = tqdm(train_dataloader, desc="Training", leave=False)
        
        for batch_idx, batch in enumerate(progress_bar):
            # Move batch to device (GPU or CPU)
            batch = {k: v.to(self.device) for k, v in batch.items()}
            
            # Forward pass: feed reviews to model, get loss
            outputs = model(**batch)
            loss = outputs.loss
            
            # Backward pass: compute gradients (how to update weights)
            loss.backward()
            
            total_loss += loss.item()
            
            # Gradient clipping: prevent exploding gradients
            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                self.config.training.max_grad_norm
            )
            
            # Optimizer step: update LoRA weights
            optimizer.step()
            scheduler.step()  # Adjust learning rate
            optimizer.zero_grad()  # Reset gradients for next batch
            
            progress_bar.set_postfix({'loss': total_loss / (batch_idx + 1)})
        
        return total_loss / len(train_dataloader)
    
    def evaluate(self, model, eval_dataloader):
        """
        Evaluate on validation set.
        
        Returns:
            Tuple of (average_loss, accuracy)
        """
        model.eval()  # Set to evaluation mode (disables dropout, etc.)
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():  # Don't compute gradients (faster, less memory)
            for batch in tqdm(eval_dataloader, desc="Evaluating", leave=False):
                batch = {k: v.to(self.device) for k, v in batch.items()}
                
                # Forward pass (no backward needed)
                outputs = model(**batch)
                loss = outputs.loss
                logits = outputs.logits  # Raw predictions before softmax
                
                total_loss += loss.item()
                
                # Get predicted class (0 or 1)
                predictions = logits.argmax(dim=-1)
                correct += (predictions == batch['labels']).sum().item()
                total += batch['labels'].size(0)
        
        avg_loss = total_loss / len(eval_dataloader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def train(self, model, train_dataloader, eval_dataloader):
        """
        Full training loop with early stopping.
        
        Early stopping: Stop training if validation loss doesn't improve for a few epochs.
        This prevents overfitting (memorizing the training data).
        
        Returns:
            Trained model
        """
        # Create optimizer (updates the LoRA weights)
        # We only optimize the LoRA parameters because base weights are frozen
        optimizer = AdamW(
            model.parameters(),
            lr=self.config.training.learning_rate,
            weight_decay=self.config.training.weight_decay
        )
        
        # Learning rate scheduler: gradually reduces learning rate over training
        # This helps: fast learning early, fine-tuning later
        total_steps = len(train_dataloader) * self.config.training.epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=self.config.training.warmup_steps,
            num_training_steps=total_steps
        )
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting training: {self.config.training.epochs} epochs")
        logger.info(f"Total steps: {total_steps} | Device: {self.device}")
        logger.info(f"{'='*60}\n")
        
        # Main training loop
        for epoch in range(self.config.training.epochs):
            logger.info(f"Epoch {epoch + 1}/{self.config.training.epochs}")
            
            # Train for one epoch
            train_loss = self.train_epoch(model, train_dataloader, optimizer, scheduler)
            self.training_history['train_loss'].append(train_loss)
            
            # Evaluate on validation set
            eval_loss, eval_accuracy = self.evaluate(model, eval_dataloader)
            self.training_history['eval_loss'].append(eval_loss)
            self.training_history['eval_accuracy'].append(eval_accuracy)
            
            logger.info(
                f"  Train Loss: {train_loss:.4f} | "
                f"Eval Loss: {eval_loss:.4f} | "
                f"Eval Accuracy: {eval_accuracy:.4f}"
            )
            
            # Save best model (lowest validation loss)
            if eval_loss < self.best_eval_loss:
                self.best_eval_loss = eval_loss
                self.patience_counter = 0
                
                checkpoint_dir = self.output_dir / "lora_model"
                model.save_adapter(str(checkpoint_dir))
                logger.info(f"  ✓ Saved best model (loss improved!)")
                
            else:
                self.patience_counter += 1
                if self.patience_counter >= self.config.training.early_stopping_patience:
                    logger.info(f"  ⚠ No improvement for {self.patience_counter} epochs. Stopping early.")
                    break
        
        logger.info("\n✓ Training complete!")
        return model
    
    def save_results(self):
        """Save training history and config."""
        # Save config
        config_path = self.output_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(self.config.to_dict(), f, indent=2)
        
        # Save history
        history_path = self.output_dir / "training_history.json"
        with open(history_path, 'w') as f:
            json.dump(self.training_history, f, indent=2)
        
        logger.info(f"Results saved to {self.output_dir}")


def main():
    """Main training script."""
    parser = argparse.ArgumentParser(description="Train LoRA adapter")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/default_config.yaml",
        help="Path to config file"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./results",
        help="Output directory for checkpoints"
    )
    
    args = parser.parse_args()
    
    # Load config
    config = ExperimentConfig.from_yaml(args.config)
    set_seed(config.training.seed)
    
    # Setup
    logger.info("\n" + "="*60)
    logger.info("Efficient LLM Adaptation with LoRA")
    logger.info("="*60)
    logger.info(str(config))
    
    # Initialize model
    lora_model = LoRAModel(config, device=args.output_dir)
    model, tokenizer = lora_model.setup()
    
    # Initialize trainer
    trainer = Trainer(config, output_dir=args.output_dir)
    trainer.tokenizer = tokenizer
    
    # Prepare data
    train_dataloader, eval_dataloader, test_data = trainer.prepare_data()
    
    # Train
    model = trainer.train(model, train_dataloader, eval_dataloader)
    
    # Save results
    trainer.save_results()
    
    # Save test data for evaluation
    test_data_path = args.output_dir / Path("test_data.pkl")
    with open(test_data_path, 'wb') as f:
        pickle.dump(test_data, f)
    
    logger.info("\nTraining completed!")


if __name__ == "__main__":
    main()
