"""
Evaluation script for trained LoRA models.
Computes metrics, generates plots, and provides detailed analysis.
"""

import argparse
import json
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import torch
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from peft import PeftModel
from tqdm import tqdm

from .config import ExperimentConfig
from .utils import create_logger


logger = create_logger(__name__)


class Evaluator:
    """Evaluates LoRA-adapted models."""
    
    def __init__(self, model_path: str, config_path: str = None, device: str = "cuda"):
        """
        Initialize evaluator.
        
        Args:
            model_path: Path to saved LoRA model
            config_path: Path to config file
            device: Device to use
        """
        self.model_path = Path(model_path)
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        
        # Load config if available
        self.config = None
        if config_path:
            self.config = ExperimentConfig.from_yaml(config_path)
        else:
            config_file = self.model_path.parent / "config.json"
            if config_file.exists():
                with open(config_file) as f:
                    config_dict = json.load(f)
                    self.config = config_dict  # Store as dict
        
        self.model = None
        self.tokenizer = None
        self.predictions = None
        self.labels = None
    
    def load_model(self):
        """Load LoRA model."""
        logger.info(f"Loading model from {self.model_path}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        
        # Load base model
        base_model_name = self.config['model']['base_model'] if self.config else "distilbert-base-uncased"
        base_model = AutoModelForSequenceClassification.from_pretrained(
            base_model_name,
            num_labels=2,
            device_map=self.device
        )
        
        # Load LoRA adapter
        self.model = PeftModel.from_pretrained(base_model, self.model_path)
        self.model = self.model.to(self.device)
        self.model.eval()
    
    def predict_batch(self, texts, batch_size=32):
        """
        Get predictions for a batch of texts.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for inference
            
        Returns:
            Array of predictions
        """
        all_predictions = []
        
        with torch.no_grad():
            for i in tqdm(range(0, len(texts), batch_size), desc="Predicting"):
                batch_texts = texts[i:i+batch_size]
                
                # Tokenize
                inputs = self.tokenizer(
                    batch_texts,
                    return_tensors='pt',
                    padding=True,
                    truncation=True,
                    max_length=128
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Predict
                outputs = self.model(**inputs)
                logits = outputs.logits
                predictions = logits.argmax(dim=-1)
                
                all_predictions.extend(predictions.cpu().numpy())
        
        return np.array(all_predictions)
    
    def evaluate(self, texts, labels):
        """
        Evaluate model on texts and labels.
        
        Args:
            texts: List of input texts
            labels: Array of ground truth labels
            
        Returns:
            Dictionary with metrics
        """
        logger.info(f"Evaluating on {len(texts)} samples")
        
        # Get predictions
        predictions = self.predict_batch(texts)
        self.predictions = predictions
        self.labels = labels
        
        # Compute metrics
        accuracy = accuracy_score(labels, predictions)
        
        # Classification report
        report = classification_report(
            labels, predictions,
            target_names=['Negative', 'Positive'],
            output_dict=True
        )
        
        # Confusion matrix
        cm = confusion_matrix(labels, predictions)
        
        results = {
            'accuracy': accuracy,
            'classification_report': report,
            'confusion_matrix': cm.tolist()
        }
        
        return results
    
    def print_results(self, results):
        """Print evaluation results."""
        logger.info("\n" + "="*60)
        logger.info("Evaluation Results")
        logger.info("="*60)
        
        logger.info(f"\nAccuracy: {results['accuracy']:.4f}")
        logger.info("\nClassification Report:")
        
        report = results['classification_report']
        logger.info(f"{'Class':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
        logger.info("-" * 51)
        
        for class_name in ['Negative', 'Positive']:
            metrics = report[class_name]
            logger.info(
                f"{class_name:<15} {metrics['precision']:<12.4f} "
                f"{metrics['recall']:<12.4f} {metrics['f1-score']:<12.4f}"
            )
        
        # Macro averages
        macro = report['macro avg']
        logger.info(f"{'Macro Avg':<15} {macro['precision']:<12.4f} "
                   f"{macro['recall']:<12.4f} {macro['f1-score']:<12.4f}")
    
    def plot_results(self, output_dir: str = "./results"):
        """Generate and save evaluation plots."""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Confusion matrix plot
        fig, ax = plt.subplots(figsize=(8, 6))
        cm = confusion_matrix(self.labels, self.predictions)
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=['Negative', 'Positive'],
            yticklabels=['Negative', 'Positive'],
            ax=ax
        )
        ax.set_ylabel('True Label')
        ax.set_xlabel('Predicted Label')
        ax.set_title('Confusion Matrix - LoRA Sentiment Classification')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'confusion_matrix.png', dpi=150)
        logger.info(f"Saved confusion matrix plot to {output_dir / 'confusion_matrix.png'}")
        plt.close()
    
    def save_results(self, results, output_dir: str = "./results"):
        """Save results to JSON."""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        results_path = output_dir / "evaluation_results.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Saved results to {results_path}")


def main():
    """Main evaluation script."""
    parser = argparse.ArgumentParser(description="Evaluate LoRA model")
    parser.add_argument(
        "--model_path",
        type=str,
        default="./results/lora_model",
        help="Path to LoRA model"
    )
    parser.add_argument(
        "--data_path",
        type=str,
        default="./results/test_data.pkl",
        help="Path to test data"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./results",
        help="Output directory for evaluation results"
    )
    
    args = parser.parse_args()
    
    # Load test data
    logger.info(f"Loading test data from {args.data_path}")
    with open(args.data_path, 'rb') as f:
        test_data = pickle.load(f)
    
    texts = test_data['texts']
    labels = test_data['labels']
    
    # Initialize evaluator
    evaluator = Evaluator(args.model_path, device="cuda")
    evaluator.load_model()
    
    # Evaluate
    results = evaluator.evaluate(texts, labels)
    
    # Print and save
    evaluator.print_results(results)
    evaluator.plot_results(args.output_dir)
    evaluator.save_results(results, args.output_dir)
    
    logger.info("\nEvaluation completed!")


if __name__ == "__main__":
    main()
