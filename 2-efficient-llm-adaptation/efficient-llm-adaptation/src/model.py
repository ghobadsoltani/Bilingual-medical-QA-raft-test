"""
Model setup with LoRA adaptation.

LoRA (Low-Rank Adaptation) allows efficient fine-tuning by adding small trainable
matrices to a frozen pre-trained model, rather than updating all weights.

Key idea: ΔW = B·A
  - B: learned matrix of shape (hidden_dim, rank)
  - A: learned matrix of shape (rank, hidden_dim)
  - rank << hidden_dim, so ~900x fewer parameters than full fine-tune
"""

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from peft import get_peft_model, LoraConfig, TaskType
from typing import Tuple

from .config import ExperimentConfig


class LoRAModel:
    """Wrapper for creating and managing LoRA-adapted transformer models."""
    
    def __init__(self, config: ExperimentConfig, device: str = "cuda"):
        """
        Initialize LoRA model wrapper.
        
        Args:
            config: Experiment configuration (contains model name, LoRA settings, etc.)
            device: "cuda" for GPU, "cpu" for CPU
        """
        self.config = config
        self.device = device
        self.base_model = None
        self.model = None
        self.tokenizer = None
    
    def setup(self) -> Tuple[torch.nn.Module, object]:
        """
        Load base model from Hugging Face Hub and apply LoRA.
        
        Returns:
            Tuple of (lora_model, tokenizer)
        """
        print(f"Loading base model: {self.config.model.base_model}")
        
        # Step 1: Load tokenizer (converts text to numbers for the model)
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model.base_model
        )
        # Add padding token if not present (needed for batched inference)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Step 2: Load pre-trained model
        # device_map="auto" loads to GPU if available, else CPU
        self.base_model = AutoModelForSequenceClassification.from_pretrained(
            self.config.model.base_model,
            num_labels=self.config.model.num_labels,
            device_map=self.device if self.device == "cuda" else None
        )
        
        # Step 3: Create LoRA configuration
        # This tells PEFT which layers to adapt and how
        lora_config = LoraConfig(
            r=self.config.lora.r,  # Rank: 8 = small but effective
            lora_alpha=self.config.lora.lora_alpha,  # Scaling
            target_modules=self.config.lora.target_modules,  # Which layers (Q, V)
            lora_dropout=self.config.lora.lora_dropout,  # Regularization
            bias=self.config.lora.bias,  # Don't adapt bias terms
            task_type=TaskType.SEQ_CLS  # Sequence classification task
        )
        
        # Step 4: Apply LoRA to the base model
        # This wraps the model and adds LoRA matrices to target layers
        self.model = get_peft_model(self.base_model, lora_config)
        
        # Step 5: Move to device (GPU or CPU)
        if self.device == "cpu":
            self.model = self.model.to("cpu")
        
        print(self._get_parameter_summary())
        
        return self.model, self.tokenizer
    
    def _get_parameter_summary(self) -> str:
        """Generate summary of parameter efficiency."""
        total_params = sum(p.numel() for p in self.base_model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        # Calculate efficiency metrics
        efficiency = (trainable_params / total_params) * 100
        reduction = total_params / trainable_params if trainable_params > 0 else 0
        
        # Estimate memory savings (4 bytes per parameter for float32 gradients)
        grad_mem_full = (total_params * 4) / 1e6  # MB
        grad_mem_lora = (trainable_params * 4) / 1e6  # MB
        
        summary = (
            f"\n{'='*60}\n"
            f"LoRA Model Parameter Summary\n"
            f"{'='*60}\n"
            f"Total Parameters (frozen):     {total_params:>12,}\n"
            f"Trainable Parameters (LoRA):  {trainable_params:>12,}\n"
            f"Efficiency Ratio:              {efficiency:>12.2f}%\n"
            f"Reduction Factor:              {reduction:>12.0f}x\n"
            f"\nMemory Savings (training):\n"
            f"  Full fine-tune gradients:     {grad_mem_full:>12.1f} MB\n"
            f"  LoRA gradients:               {grad_mem_lora:>12.1f} MB\n"
            f"  Savings:                      {grad_mem_full - grad_mem_lora:>12.1f} MB ({((grad_mem_full - grad_mem_lora) / grad_mem_full * 100):.0f}%)\n"
            f"{'='*60}\n"
        )
        return summary
    
    def get_model(self) -> torch.nn.Module:
        """Get the LoRA-adapted model."""
        if self.model is None:
            raise RuntimeError("Model not initialized. Call setup() first.")
        return self.model
    
    def get_tokenizer(self) -> object:
        """Get the tokenizer."""
        if self.tokenizer is None:
            raise RuntimeError("Tokenizer not initialized. Call setup() first.")
        return self.tokenizer
    
    def save_adapter(self, save_path: str) -> None:
        """
        Save only the LoRA adapter weights (very lightweight).
        
        This is the main benefit of LoRA: save ~74KB instead of 252MB!
        
        Args:
            save_path: Directory to save adapter
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call setup() first.")
        
        print(f"Saving LoRA adapter to {save_path}")
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)
        print("✓ Adapter saved!")

