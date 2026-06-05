"""Chunking logic per planning.md hybrid strategy."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

REDDIT_MAX_CHARS = 500
REDDIT_OVERLAP_CHARS = 80
OFFICIAL_MAX_CHARS = 600
OFFICIAL_OVERLAP_CHARS = 100
MIN_BODY_CHARS = 20

SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    text: str
    source_id: str
    doc_type: str
    url: str
    title: str
    section: str = ""
    item_kind: str = ""  # post | comment | official
    chunk_index: int = 0
    metadata: dict = field(default_factory=dict)


def _split_with_overlap(text: str, max_chars: int, overlap: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    sentences = SENTENCE_BOUNDARY.split(text.strip())
    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        if not sentence:
            continue
        candidate = f"{current} {sentence}".strip() if current else sentence
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(sentence) <= max_chars:
            current = sentence
        else:
            # Hard split very long sentences
            start = 0
            while start < len(sentence):
                part = sentence[start : start + max_chars]
                chunks.append(part.strip())
                start += max_chars - overlap
            current = ""

    if current:
        chunks.append(current)

    if overlap <= 0 or len(chunks) < 2:
        return chunks

    overlapped: list[str] = [chunks[0]]
    for i in range(1, len(chunks)):
        prev = overlapped[-1]
        prefix = prev[-overlap:] if len(prev) > overlap else prev
        merged = f"{prefix} {chunks[i]}".strip()
        if len(merged) > max_chars:
            overlapped.append(chunks[i])
        else:
            overlapped.append(merged)
    return overlapped


def _format_reddit_chunk(
    *,
    url: str,
    title: str,
    body: str,
    kind: str,
) -> str:
    return (
        f"[Source: {url} | Type: reddit | Thread: {title} | Kind: {kind}]\n"
        f"{body}"
    )


def _format_official_chunk(*, url: str, title: str, heading: str, body: str) -> str:
    return (
        f"[Source: {url} | Type: official | Page: {title} | Section: {heading}]\n"
        f"{body}"
    )


def chunk_reddit_document(
    *,
    source_id: str,
    url: str,
    title: str,
    post_body: str,
    comments: list[str],
) -> list[Chunk]:
    chunks: list[Chunk] = []
    idx = 0

    items: list[tuple[str, str]] = []
    if post_body and len(post_body) >= MIN_BODY_CHARS:
        items.append(("post", post_body))
    for body in comments:
        if body and len(body) >= MIN_BODY_CHARS:
            items.append(("comment", body))

    for kind, body in items:
        segments = _split_with_overlap(body, REDDIT_MAX_CHARS, REDDIT_OVERLAP_CHARS)
        for segment in segments:
            segment = segment.strip()
            if len(segment) < MIN_BODY_CHARS:
                continue
            text = _format_reddit_chunk(url=url, title=title, body=segment, kind=kind)
            chunks.append(
                Chunk(
                    text=text,
                    source_id=source_id,
                    doc_type="reddit",
                    url=url,
                    title=title,
                    section=title,
                    item_kind=kind,
                    chunk_index=idx,
                    metadata={
                        "source_id": source_id,
                        "doc_type": "reddit",
                        "url": url,
                        "title": title,
                        "kind": kind,
                    },
                )
            )
            idx += 1
    return chunks


def chunk_official_document(
    *,
    source_id: str,
    url: str,
    title: str,
    sections: list[tuple[str, list[str]]],
) -> list[Chunk]:
    chunks: list[Chunk] = []
    idx = 0

    for heading, paragraphs in sections:
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if len(paragraph) < MIN_BODY_CHARS:
                continue

            segments = _split_with_overlap(
                paragraph, OFFICIAL_MAX_CHARS, OFFICIAL_OVERLAP_CHARS
            )
            for segment in segments:
                segment = segment.strip()
                if len(segment) < MIN_BODY_CHARS:
                    continue
                body = f"[{heading}]\n{segment}"
                text = _format_official_chunk(
                    url=url, title=title, heading=heading, body=body
                )
                chunks.append(
                    Chunk(
                        text=text,
                        source_id=source_id,
                        doc_type="official",
                        url=url,
                        title=title,
                        section=heading,
                        item_kind="official",
                        chunk_index=idx,
                        metadata={
                            "source_id": source_id,
                            "doc_type": "official",
                            "url": url,
                            "title": title,
                            "section": heading,
                        },
                    )
                )
                idx += 1
    return chunks


def chunk_text(
    *,
    source_id: str,
    doc_type: str,
    url: str,
    title: str,
    post_body: str = "",
    comments: list[str] | None = None,
    sections: list[tuple[str, list[str]]] | None = None,
) -> list[Chunk]:
    """Chunk a cleaned document according to its type."""
    if doc_type == "reddit":
        return chunk_reddit_document(
            source_id=source_id,
            url=url,
            title=title,
            post_body=post_body,
            comments=comments or [],
        )
    if doc_type == "official":
        return chunk_official_document(
            source_id=source_id,
            url=url,
            title=title,
            sections=sections or [],
        )
    raise ValueError(f"Unknown doc_type: {doc_type}")
