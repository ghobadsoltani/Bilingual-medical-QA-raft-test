"""
CLI entry point for the offline medical RAG demo.

Usage:
    python main.py --build-index
    python main.py --question "What are symptoms of type 2 diabetes?"
"""

import argparse
import json
import sys
from pathlib import Path

# Allow imports when running from project root
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import MedicalRAGPipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Offline medical RAG demo — build index or ask questions."
    )
    parser.add_argument(
        "--build-index",
        action="store_true",
        help="Load documents, create embeddings, and save FAISS index.",
    )
    parser.add_argument(
        "--question",
        type=str,
        help="Ask a question against the built index.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pipeline = MedicalRAGPipeline()

    if args.build_index:
        stats = pipeline.build_index()
        print("Index built successfully.")
        print(json.dumps(stats, indent=2))
        return

    if args.question:
        result = pipeline.ask(args.question)
        print("\n=== Answer ===")
        print(result["answer"])
        print("\n=== Sources ===")
        for source in result["sources"]:
            print(
                f"- {source['title']} ({source['doc_id']}) "
                f"[{source['chunk_id']}] score={source['score']}"
            )
        return

    print("Provide --build-index or --question. Example:")
    print('  python main.py --build-index')
    print('  python main.py --question "How should minor burns be cooled?"')


if __name__ == "__main__":
    main()
