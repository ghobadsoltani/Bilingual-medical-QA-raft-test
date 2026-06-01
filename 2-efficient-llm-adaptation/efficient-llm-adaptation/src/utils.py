"""
Utility functions for logging, visualization, and common operations.
"""

import logging
import random
import numpy as np
import torch
import matplotlib.pyplot as plt
import json
from pathlib import Path
from typing import Dict, List


def set_seed(seed: int = 42):
    """
    Set random seed for reproducibility.
    
    Args:
        seed: Random seed value
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def create_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Create a configured logger.
    
    Args:
        name: Logger name
        log_file: Optional file to log to
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def plot_training_history(history: Dict[str, List[float]], output_path: str = None):
    """
    Plot training history.
    
    Args:
        history: Dictionary with 'train_loss', 'eval_loss', 'eval_accuracy'
        output_path: Path to save figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Loss plot
    axes[0].plot(history['train_loss'], label='Train Loss', marker='o')
    axes[0].plot(history['eval_loss'], label='Eval Loss', marker='s')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Training & Evaluation Loss')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Accuracy plot
    axes[1].plot(history['eval_accuracy'], label='Eval Accuracy', marker='o', color='green')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy')
    axes[1].set_title('Evaluation Accuracy')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150)
        print(f"Saved plot to {output_path}")
    
    plt.show()


def load_config_from_json(json_path: str) -> Dict:
    """
    Load configuration from JSON file.
    
    Args:
        json_path: Path to JSON config
        
    Returns:
        Configuration dictionary
    """
    with open(json_path, 'r') as f:
        config = json.load(f)
    return config


def count_parameters(model) -> Dict[str, int]:
    """
    Count total and trainable parameters in model.
    
    Args:
        model: PyTorch model
        
    Returns:
        Dictionary with parameter counts
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    frozen_params = total_params - trainable_params
    
    return {
        'total': total_params,
        'trainable': trainable_params,
        'frozen': frozen_params,
        'efficiency_ratio': (trainable_params / total_params) * 100
    }


def print_parameter_summary(model, name: str = "Model"):
    """
    Print parameter summary.
    
    Args:
        model: PyTorch model
        name: Model name for printing
    """
    params = count_parameters(model)
    
    print(f"\n{name} Parameter Summary:")
    print(f"  Total Parameters: {params['total']:,}")
    print(f"  Trainable Parameters: {params['trainable']:,}")
    print(f"  Frozen Parameters: {params['frozen']:,}")
    print(f"  Efficiency Ratio: {params['efficiency_ratio']:.2f}%")
    if params['total'] > params['trainable']:
        reduction = params['total'] / params['trainable']
        print(f"  Reduction Factor: {reduction:.0f}x")
