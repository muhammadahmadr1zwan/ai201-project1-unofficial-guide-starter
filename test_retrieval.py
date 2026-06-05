"""Test retrieval with evaluation-plan queries (Milestone 4 checkpoint)."""

from __future__ import annotations

import sys
import textwrap

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from retrieve import DEFAULT_TOP_K, get_relevant_chunks

EVALUATION_QUERIES = [
    "How much do NYU students usually pay for off-campus rent?",
    "Which neighborhoods do NYU students mention as realistic on a budget?",
    "How early should I start looking for an apartment before fall semester?",
    "Is living off campus cheaper or better than dorming?",
    "Where do NYU students look for roommates, sublets, or apartments?",
]


def print_results(query: str, k: int = DEFAULT_TOP_K) -> None:
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    results = get_relevant_chunks(query, k=k)
    if not results:
        print("No results returned.")
        return

    for rank, hit in enumerate(results, 1):
        meta = hit.metadata
        preview = textwrap.shorten(
            hit.text.replace("\n", " "),
            width=400,
            placeholder="...",
        )
        print(f"\n--- Rank {rank} | distance: {hit.distance:.4f} ---")
        print(f"source: {meta.get('source_id')} ({meta.get('doc_type')})")
        print(f"title:  {meta.get('title', '')[:70]}")
        print(f"url:    {meta.get('url', '')[:70]}")
        print(preview)

    best = results[0].distance
    if best < 0.5:
        print(f"\nTop distance {best:.4f} — strong match (< 0.5).")
    else:
        print(f"\nTop distance {best:.4f} — weak match (>= 0.5); review chunking/cleaning.")


def main() -> int:
    print(f"Testing retrieval with top-k={DEFAULT_TOP_K}")
    for query in EVALUATION_QUERIES:
        print_results(query)
    print("\n" + "=" * 80)
    print("Retrieval test complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
