"""Grounded answer generation with Groq over retrieved chunks."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from dotenv import load_dotenv
from groq import Groq

from retrieve import DEFAULT_TOP_K, RetrievedChunk, get_relevant_chunks

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"
# If the best retrieval match is weaker than this, skip the LLM (avoids guessing).
WEAK_RETRIEVAL_THRESHOLD = 0.52
INSUFFICIENT_MSG = (
    "I don't have enough information on that in my retrieved documents."
)

SYSTEM_PROMPT = """You are an NYU off-campus housing guide assistant.

CRITICAL: Answer the question using ONLY the information in the provided document chunks below.
- Do NOT use general knowledge about NYU, New York City, or college life unless it appears verbatim in the chunks.
- Every factual claim must be traceable to a [Source N] block. Cite [Source N] inline when you state a fact.
- If the chunks do not contain enough information to answer, respond with exactly: "I don't have enough information on that."
- Distinguish official (doc_type: official) NYU/Meet NYU guidance from reddit student anecdotes.
- When reddit comments disagree, report a range and note variability; never state one anecdote as universal truth.
- Do not invent prices, neighborhoods, websites, or policies.
- Keep answers concise (2–4 short paragraphs or a short bullet list)."""


@dataclass
class GroundedAnswer:
    query: str
    answer: str
    sources: list[str]
    chunks: list[RetrievedChunk]
    declined: bool = False


def _format_context(chunks: list[RetrievedChunk]) -> str:
    blocks: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.metadata
        blocks.append(
            f"[Source {i} | {meta.get('doc_type', 'unknown')} | "
            f"{meta.get('source_id', '')} | {meta.get('title', '')}]\n"
            f"URL: {meta.get('url', '')}\n"
            f"{chunk.text}"
        )
    return "\n\n---\n\n".join(blocks)


def _source_labels(chunks: list[RetrievedChunk]) -> list[str]:
    """Programmatic source list — not left to the LLM."""
    seen: set[str] = set()
    labels: list[str] = []
    for chunk in chunks:
        meta = chunk.metadata
        source_id = meta.get("source_id", "unknown")
        if source_id in seen:
            continue
        seen.add(source_id)
        doc_type = meta.get("doc_type", "unknown")
        title = meta.get("title", "Untitled")
        url = meta.get("url", "")
        file_name = meta.get("source_file", f"{source_id}.txt")
        labels.append(f"{file_name} ({doc_type}) — {title} — {url}")
    return labels


def _append_sources(answer: str, source_labels: list[str]) -> str:
    if not source_labels:
        return answer
    bullet_lines = "\n".join(f"• {label}" for label in source_labels)
    return f"{answer.rstrip()}\n\n---\n**Retrieved from:**\n{bullet_lines}"


def _looks_like_refusal(text: str) -> bool:
    lowered = text.lower()
    return (
        "don't have enough information" in lowered
        or "do not have enough information" in lowered
        or "insufficient" in lowered and "context" in lowered
    )


def generate_answer(
    query: str,
    *,
    k: int = DEFAULT_TOP_K,
    model: str = GROQ_MODEL,
) -> GroundedAnswer:
    """Retrieve top-k chunks and produce a grounded Groq response."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    chunks = get_relevant_chunks(query, k=k)
    source_labels = _source_labels(chunks)

    if not chunks:
        return GroundedAnswer(
            query=query,
            answer=INSUFFICIENT_MSG,
            sources=[],
            chunks=[],
            declined=True,
        )

    if chunks[0].distance > WEAK_RETRIEVAL_THRESHOLD:
        return GroundedAnswer(
            query=query,
            answer=INSUFFICIENT_MSG,
            sources=source_labels,
            chunks=chunks,
            declined=True,
        )

    context = _format_context(chunks)
    user_message = (
        f"Question: {query}\n\n"
        f"Document chunks ({len(chunks)}). "
        f"Answer ONLY from these — cite [Source N] for each fact:\n\n{context}"
    )

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
        max_tokens=1024,
    )

    llm_answer = (response.choices[0].message.content or "").strip()
    declined = _looks_like_refusal(llm_answer)

    if declined:
        final_answer = INSUFFICIENT_MSG
    else:
        # Strip any LLM-authored "sources" footer so attribution stays programmatic.
        final_answer = re.split(r"\n---\n\*\*Retrieved from", llm_answer, maxsplit=1)[0].strip()
        final_answer = _append_sources(final_answer, source_labels)

    return GroundedAnswer(
        query=query,
        answer=final_answer,
        sources=source_labels,
        chunks=chunks,
        declined=declined,
    )
