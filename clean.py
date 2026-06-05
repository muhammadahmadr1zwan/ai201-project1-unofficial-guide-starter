"""Text cleaning utilities for ingested documents."""

from __future__ import annotations

import html
import re
from typing import Iterable

from bs4 import BeautifulSoup, Comment

# Boilerplate phrases common on NYU / Meet NYU pages
BOILERPLATE_PATTERNS = [
    r"skip to (main )?content",
    r"cookie (policy|preferences)",
    r"sign in",
    r"subscribe to our newsletter",
    r"share on (facebook|twitter|linkedin)",
    r"read more",
    r"all rights reserved",
    r"©\s*\d{4}",
]

BOILERPLATE_RE = re.compile("|".join(BOILERPLATE_PATTERNS), re.IGNORECASE)

REDDIT_NOISE_AUTHORS = {"automoderator", "modmail", "reddit", "bot"}
REDDIT_REMOVED = {"[deleted]", "[removed]", ""}


def normalize_whitespace(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_boilerplate_line(line: str) -> bool:
    line = line.strip()
    if not line or len(line) < 4:
        return True
    if BOILERPLATE_RE.search(line):
        return True
    if line.lower() in {"menu", "search", "close", "open", "back", "next", "previous"}:
        return True
    return False


def clean_reddit_body(body: str) -> str:
    body = normalize_whitespace(body)
    if body.lower() in REDDIT_REMOVED:
        return ""
    # Drop markdown link targets but keep link text
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    body = re.sub(r"https?://\S+", "", body).strip()
    return body


def clean_reddit_item(author: str | None, body: str) -> str | None:
    author = (author or "").strip().lower()
    if author in REDDIT_NOISE_AUTHORS:
        return None
    cleaned = clean_reddit_body(body)
    if len(cleaned) < 20:
        return None
    return cleaned


def html_to_sections(html_content: str) -> list[tuple[str, list[str]]]:
    """Extract (heading, paragraphs) sections from HTML."""
    soup = BeautifulSoup(html_content, "lxml")

    for tag in soup(["script", "style", "noscript", "svg", "iframe", "nav", "footer", "header"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    root = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", class_=re.compile(r"content|article|main", re.I))
        or soup.body
        or soup
    )

    sections: list[tuple[str, list[str]]] = []
    current_heading = "Introduction"
    current_paragraphs: list[str] = []

    def flush():
        nonlocal current_paragraphs
        kept = [p for p in current_paragraphs if p and not is_boilerplate_line(p)]
        if kept:
            sections.append((current_heading, kept))
        current_paragraphs = []

    for element in root.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        text = normalize_whitespace(element.get_text(" ", strip=True))
        if not text or is_boilerplate_line(text):
            continue
        if element.name in {"h1", "h2", "h3", "h4"}:
            flush()
            current_heading = text
        else:
            if len(text) >= 40:
                current_paragraphs.append(text)

    flush()
    return sections


def sections_to_plaintext(sections: Iterable[tuple[str, list[str]]]) -> str:
    parts: list[str] = []
    for heading, paragraphs in sections:
        parts.append(f"## {heading}")
        parts.extend(paragraphs)
        parts.append("")
    return "\n".join(parts).strip()
