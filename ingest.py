"""Download, save, and clean project source documents."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import requests

from clean import clean_reddit_item, html_to_sections, sections_to_plaintext
from sources import SOURCES, Source

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "documents" / "raw"
CLEANED_DIR = ROOT / "documents" / "cleaned"
MANUAL_DIR = ROOT / "documents" / "manual"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
PULLPUSH_SUBMISSION = "https://api.pullpush.io/reddit/search/submission/"
PULLPUSH_COMMENT = "https://api.pullpush.io/reddit/search/comment/"


@dataclass
class CleanedDocument:
    source_id: str
    doc_type: str
    url: str
    title: str
    cleaned_text: str
    post_body: str = ""
    comments: list[str] = field(default_factory=list)
    sections: list[tuple[str, list[str]]] = field(default_factory=list)


def _session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    return session


def _save_raw(source: Source, payload: str | dict, suffix: str) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{source.source_id}.{suffix}"
    if isinstance(payload, dict):
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        path.write_text(payload, encoding="utf-8")
    return path


def _save_cleaned(source: Source, text: str) -> Path:
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    path = CLEANED_DIR / f"{source.source_id}.txt"
    path.write_text(text, encoding="utf-8")
    return path


def fetch_reddit_thread(session: requests.Session, source: Source) -> dict:
    assert source.reddit_id
    raw_path = RAW_DIR / f"{source.source_id}.json"
    if raw_path.exists():
        return json.loads(raw_path.read_text(encoding="utf-8"))

    submission_resp = session.get(
        PULLPUSH_SUBMISSION,
        params={"ids": source.reddit_id},
        timeout=60,
    )
    submission_resp.raise_for_status()
    submissions = submission_resp.json().get("data", [])

    comments: list[dict] = []
    size = 100
    before = None
    while True:
        params: dict = {"link_id": source.reddit_id, "size": size, "sort": "asc"}
        if before:
            params["before"] = before
        comment_resp = session.get(PULLPUSH_COMMENT, params=params, timeout=60)
        comment_resp.raise_for_status()
        batch = comment_resp.json().get("data", [])
        if not batch:
            break
        comments.extend(batch)
        if len(batch) < size:
            break
        before = batch[-1]["created_utc"]
        time.sleep(0.3)

    payload = {"submission": submissions, "comments": comments}
    _save_raw(source, payload, "json")
    time.sleep(0.5)
    return payload


def fetch_official_page(session: requests.Session, source: Source) -> str:
    raw_path = RAW_DIR / f"{source.source_id}.html"
    if raw_path.exists():
        return raw_path.read_text(encoding="utf-8")

    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = session.get(source.url, timeout=60)
            response.raise_for_status()
            html_content = response.text
            _save_raw(source, html_content, "html")
            time.sleep(0.5)
            return html_content
        except requests.RequestException as exc:
            last_error = exc
            time.sleep(2 * (attempt + 1))
    raise last_error  # type: ignore[misc]


def clean_reddit_payload(source: Source, payload: dict) -> CleanedDocument:
    submissions = payload.get("submission", [])
    post_title = source.title
    post_body = ""
    if submissions:
        post = submissions[0]
        post_title = post.get("title") or post_title
        post_body = clean_reddit_item(post.get("author"), post.get("selftext", "")) or ""

    comments: list[str] = []
    for item in payload.get("comments", []):
        cleaned = clean_reddit_item(item.get("author"), item.get("body", ""))
        if cleaned:
            comments.append(cleaned)

    lines = [f"# {post_title}", f"URL: {source.url}", ""]
    if post_body:
        lines.extend(["## Post", post_body, ""])
    lines.append("## Comments")
    for i, comment in enumerate(comments, 1):
        lines.append(f"### Comment {i}")
        lines.append(comment)
        lines.append("")

    cleaned_text = "\n".join(lines).strip()
    _save_cleaned(source, cleaned_text)
    return CleanedDocument(
        source_id=source.source_id,
        doc_type="reddit",
        url=source.url,
        title=post_title,
        cleaned_text=cleaned_text,
        post_body=post_body,
        comments=comments,
    )


def _markdown_to_sections(markdown_text: str) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    current_heading = "Introduction"
    current_paragraphs: list[str] = []

    for line in markdown_text.splitlines():
        line = line.strip()
        if not line or line.startswith("URL:"):
            continue
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            if current_paragraphs:
                sections.append((current_heading, current_paragraphs))
            current_heading = line[3:].strip()
            current_paragraphs = []
        else:
            current_paragraphs.append(line)

    if current_paragraphs:
        sections.append((current_heading, current_paragraphs))
    return sections


def load_manual_official(source: Source) -> CleanedDocument | None:
    manual_path = MANUAL_DIR / f"{source.source_id}.md"
    if not manual_path.exists():
        return None
    markdown_text = manual_path.read_text(encoding="utf-8")
    sections = _markdown_to_sections(markdown_text)
    cleaned_text = sections_to_plaintext(sections)
    _save_cleaned(source, cleaned_text)
    _save_raw(source, markdown_text, "md")
    return CleanedDocument(
        source_id=source.source_id,
        doc_type="official",
        url=source.url,
        title=source.title,
        cleaned_text=cleaned_text,
        sections=sections,
    )


def clean_official_html(source: Source, html_content: str) -> CleanedDocument:
    sections = html_to_sections(html_content)
    cleaned_text = sections_to_plaintext(sections)
    _save_cleaned(source, cleaned_text)
    return CleanedDocument(
        source_id=source.source_id,
        doc_type="official",
        url=source.url,
        title=source.title,
        cleaned_text=cleaned_text,
        sections=sections,
    )


def ingest_source(session: requests.Session, source: Source) -> CleanedDocument:
    if source.doc_type == "reddit":
        payload = fetch_reddit_thread(session, source)
        return clean_reddit_payload(source, payload)
    if source.doc_type == "official":
        try:
            html_content = fetch_official_page(session, source)
            return clean_official_html(source, html_content)
        except requests.RequestException:
            manual = load_manual_official(source)
            if manual:
                print(f"  -> used manual fallback for {source.source_id}")
                return manual
            raise
    raise ValueError(f"Unknown doc_type: {source.doc_type}")


def ingest_all(sources: list[Source] | None = None) -> list[CleanedDocument]:
    sources = sources or SOURCES
    session = _session()
    documents: list[CleanedDocument] = []
    for source in sources:
        print(f"Ingesting {source.source_id}: {source.title[:60]}...")
        doc = ingest_source(session, source)
        print(f"  -> cleaned {len(doc.cleaned_text):,} chars")
        documents.append(doc)
    return documents


def load_cleaned_from_disk(sources: list[Source] | None = None) -> list[CleanedDocument]:
    """Reload cleaned documents from disk (for chunk-only runs)."""
    sources = sources or SOURCES
    documents: list[CleanedDocument] = []
    for source in sources:
        cleaned_path = CLEANED_DIR / f"{source.source_id}.txt"
        raw_json = RAW_DIR / f"{source.source_id}.json"
        if source.doc_type == "reddit" and raw_json.exists():
            payload = json.loads(raw_json.read_text(encoding="utf-8"))
            documents.append(clean_reddit_payload(source, payload))
        elif cleaned_path.exists():
            text = cleaned_path.read_text(encoding="utf-8")
            if source.doc_type == "official":
                html_path = RAW_DIR / f"{source.source_id}.html"
                sections = (
                    html_to_sections(html_path.read_text(encoding="utf-8"))
                    if html_path.exists()
                    else [("Introduction", [text])]
                )
                documents.append(
                    CleanedDocument(
                        source_id=source.source_id,
                        doc_type=source.doc_type,
                        url=source.url,
                        title=source.title,
                        cleaned_text=text,
                        sections=sections,
                    )
                )
            else:
                documents.append(
                    CleanedDocument(
                        source_id=source.source_id,
                        doc_type=source.doc_type,
                        url=source.url,
                        title=source.title,
                        cleaned_text=text,
                    )
                )
    return documents
