"""Central configuration for paths and model settings."""

from pathlib import Path

# Project root (offline-medical-rag-demo/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data paths
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"
INDEX_DIR = PROJECT_ROOT / "data" / "index"

# Chunking
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80

# Retrieval
TOP_K = 3

# Models (small, offline-friendly defaults)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GENERATION_MODEL = "google/flan-t5-small"

# Generation limits
MAX_CONTEXT_CHARS = 2000
MAX_NEW_TOKENS = 128
