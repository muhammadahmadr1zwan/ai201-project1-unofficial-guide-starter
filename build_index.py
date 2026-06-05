"""Build the ChromaDB vector index from data/chunks.json."""

from __future__ import annotations

import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from retrieve import build_index, CHUNKS_PATH, CHROMA_PATH, COLLECTION_NAME, EMBEDDING_MODEL


def main() -> int:
    parser = argparse.ArgumentParser(description="Embed chunks and load into ChromaDB")
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="Append to existing collection instead of rebuilding",
    )
    args = parser.parse_args()

    print(f"Embedding model: {EMBEDDING_MODEL}")
    print(f"Chunks file: {CHUNKS_PATH}")
    print(f"Chroma path: {CHROMA_PATH}")
    print(f"Collection: {COLLECTION_NAME}")

    count = build_index(reset=not args.no_reset)
    print(f"\nIndexed {count} chunks successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
