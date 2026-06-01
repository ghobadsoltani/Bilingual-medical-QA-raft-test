"""
Configuration management for LoRA fine-tuning experiments.
Loads YAML config and provides structured access to hyperparameters.
"""

import yaml
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class ModelConfig:
    """Model configuration."""
    base_model: str = "distilbert-base-uncased"
    num_labels: int = 2
    dropout: float = 0.1


@dataclass
class LoRAConfig:
    """LoRA-specific hyperparameters."""
    r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    target_modules: List[str] = None
    bias: str = "none"
    
    def __post_init__(self):
        if self.target_modules is None:
            self.target_modules = ["query", "value"]


@dataclass
class TrainingConfig:
    """Training hyperparameters."""
    epochs: int = 3
    batch_size: int = 32
    learning_rate: float = 1e-4
    warmup_steps: int = 100
    weight_decay: float = 0.01
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0
    eval_every: int = 100
    early_stopping_patience: int = 3
    seed: int = 42
    device: str = "cuda"  # "cuda" or "cpu"


@dataclass
class DataConfig:
    """Data loading configuration."""
    dataset_name: str = "imdb"
    split: str = "train"
    max_samples: int = 8000
    train_test_split: float = 0.9
    max_length: int = 128


@dataclass
class ExperimentConfig:
    """Full experiment configuration."""
    model: ModelConfig
    lora: LoRAConfig
    training: TrainingConfig
    data: DataConfig
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "ExperimentConfig":
        """Load configuration from YAML file."""
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        return cls(
            model=ModelConfig(**config_dict.get('model', {})),
            lora=LoRAConfig(**config_dict.get('lora', {})),
            training=TrainingConfig(**config_dict.get('training', {})),
            data=DataConfig(**config_dict.get('data', {}))
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for logging."""
        return {
            'model': self.model.__dict__,
            'lora': self.lora.__dict__,
            'training': self.training.__dict__,
            'data': self.data.__dict__
        }
    
    def __str__(self) -> str:
        """Pretty-print configuration."""
        lines = ["Experiment Configuration:", "=" * 50]
        for key, value in self.to_dict().items():
            lines.append(f"\n{key.upper()}:")
            for k, v in value.items():
                lines.append(f"  {k}: {v}")
        return "\n".join(lines)
