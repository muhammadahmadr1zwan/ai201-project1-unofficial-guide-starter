"""End-to-end RAG: retrieve → grounded generate → structured result."""

from __future__ import annotations

from generate import GroundedAnswer, generate_answer


def ask(question: str) -> dict:
    """
    Run the full pipeline for one question.

    Returns:
        answer: str — LLM response with programmatic source footer
        sources: list[str] — document labels used for retrieval
        declined: bool — True if the system refused to answer from context
    """
    result: GroundedAnswer = generate_answer(question.strip())
    return {
        "answer": result.answer,
        "sources": result.sources,
        "declined": result.declined,
    }
