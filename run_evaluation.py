"""Run evaluation + grounding checks (Milestone 5)."""

from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from query import ask
from test_retrieval import EVALUATION_QUERIES

OUT_OF_DOMAIN_QUERY = "What is the best NYU dining hall for pizza?"


def run_query(label: str, query: str) -> None:
    print("\n" + "=" * 80)
    print(f"{label}: {query}")
    print("=" * 80)
    try:
        result = ask(query)
    except Exception as exc:
        print(f"FAILED: {exc}")
        return

    print(f"\nDeclined: {result['declined']}")
    print("\nANSWER:")
    print(result["answer"])
    print("\nSOURCES (programmatic):")
    for s in result["sources"]:
        print(f"  • {s}")


def main() -> int:
    for i, query in enumerate(EVALUATION_QUERIES, 1):
        run_query(f"EVAL {i}", query)

    run_query("OUT-OF-DOMAIN (should decline)", OUT_OF_DOMAIN_QUERY)
    print("\n" + "=" * 80)
    print("Done. Verify out-of-domain answer refuses to guess.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
