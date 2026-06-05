"""Run ingestion, chunking, and checkpoint inspection for Milestone 3."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from chunk import Chunk, chunk_text
from ingest import ingest_all, load_cleaned_from_disk
from sources import SOURCES

ROOT = Path(__file__).resolve().parent
CHUNKS_PATH = ROOT / "data" / "chunks.json"


def documents_to_chunks(documents) -> list[Chunk]:
    all_chunks: list[Chunk] = []
    for doc in documents:
        chunks = chunk_text(
            source_id=doc.source_id,
            doc_type=doc.doc_type,
            url=doc.url,
            title=doc.title,
            post_body=doc.post_body,
            comments=doc.comments,
            sections=doc.sections,
        )
        print(f"  {doc.source_id}: {len(chunks)} chunks")
        all_chunks.extend(chunks)
    return all_chunks


def chunks_to_json(chunks: list[Chunk]) -> list[dict]:
    return [
        {
            "id": f"{c.source_id}_{c.chunk_index}",
            "text": c.text,
            "metadata": c.metadata,
        }
        for c in chunks
    ]


def print_sample_cleaned(documents, source_id: str | None) -> None:
    target = documents[0]
    if source_id:
        target = next(d for d in documents if d.source_id == source_id)
    print("\n" + "=" * 72)
    print(f"CLEANED SAMPLE: {target.source_id} ({target.doc_type})")
    print("=" * 72)
    preview = target.cleaned_text[:2500]
    print(preview)
    if len(target.cleaned_text) > 2500:
        print("\n... [truncated for display] ...")
    print("=" * 72 + "\n")


def print_sample_chunks(chunks: list[Chunk], count: int = 5) -> None:
    sample = random.sample(chunks, min(count, len(chunks)))
    for i, chunk in enumerate(sample, 1):
        print("\n" + "=" * 72)
        print(f"CHUNK SAMPLE {i}/{count} — {chunk.source_id} ({chunk.item_kind})")
        print("=" * 72)
        print(chunk.text)
        print(f"\n(length: {len(chunk.text)} characters)")
    print("\n" + "=" * 72)


def validate_chunks(chunks: list[Chunk]) -> None:
    issues = []
    for chunk in chunks:
        if not chunk.text.strip():
            issues.append(f"Empty chunk: {chunk.source_id} #{chunk.chunk_index}")
        if "<div" in chunk.text or "&#" in chunk.text:
            issues.append(f"HTML artifact in {chunk.source_id} #{chunk.chunk_index}")
        if len(chunk.text) < 50:
            issues.append(f"Very short chunk: {chunk.source_id} #{chunk.chunk_index}")
    if issues:
        print("CHUNK VALIDATION ISSUES:")
        for issue in issues[:20]:
            print(f"  - {issue}")
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more")
    else:
        print("Chunk validation: no empty chunks or HTML artifacts detected.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 3 document pipeline")
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Use existing raw/cleaned files on disk",
    )
    parser.add_argument(
        "--sample-cleaned",
        metavar="SOURCE_ID",
        nargs="?",
        const="reddit_04",
        help="Print one cleaned document (default: reddit_04)",
    )
    parser.add_argument(
        "--inspect-only",
        action="store_true",
        help="Only print 5 sample chunks from existing chunks.json",
    )
    args = parser.parse_args()

    if args.inspect_only:
        if not CHUNKS_PATH.exists():
            print("No chunks.json found. Run the full pipeline first.")
            return 1
        data = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
        print(f"Loaded {len(data)} chunks from {CHUNKS_PATH}")
        sample = random.sample(data, min(5, len(data)))
        for i, item in enumerate(sample, 1):
            print("\n" + "=" * 72)
            print(f"CHUNK SAMPLE {i}/5 — {item['metadata'].get('source_id')}")
            print("=" * 72)
            print(item["text"])
        return 0

    if args.skip_ingest:
        print("Loading cleaned documents from disk...")
        documents = load_cleaned_from_disk()
    else:
        print("Ingesting all sources...")
        documents = ingest_all()

    if args.sample_cleaned is not None:
        print_sample_cleaned(documents, args.sample_cleaned)

    print("\nChunking documents...")
    chunks = documents_to_chunks(documents)
    total = len(chunks)
    print(f"\nTotal chunks: {total}")

    by_source: dict[str, int] = {}
    for c in chunks:
        by_source[c.source_id] = by_source.get(c.source_id, 0) + 1
    print("\nChunks per source:")
    for sid in sorted(by_source):
        print(f"  {sid}: {by_source[sid]}")

    if total < 50:
        print("\nWARNING: Fewer than 50 chunks — chunks may be too large.")
    elif total > 2000:
        print("\nWARNING: More than 2000 chunks — chunks may be too small.")
    else:
        print("\nChunk count is in a healthy range (50–2000).")

    validate_chunks(chunks)

    CHUNKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHUNKS_PATH.write_text(
        json.dumps(chunks_to_json(chunks), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nSaved chunks to {CHUNKS_PATH}")

    random.seed(42)
    print_sample_chunks(chunks, count=5)
    return 0


if __name__ == "__main__":
    sys.exit(main())
