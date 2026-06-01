"""Convenience script to build the vector index."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.pipeline import MedicalRAGPipeline


if __name__ == "__main__":
    print("Building FAISS index...")
    stats = MedicalRAGPipeline().build_index()
    print(f"✓ Built index: {stats['chunks']} chunks from {stats['documents']} documents")
    print(f"  Location: {stats['index_path']}")

