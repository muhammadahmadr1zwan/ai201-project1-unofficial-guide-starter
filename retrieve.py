"""Embed chunks and retrieve top-k matches from ChromaDB."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import chromadb
from chromadb.errors import NotFoundError
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent
CHUNKS_PATH = ROOT / "data" / "chunks.json"
CHROMA_PATH = ROOT / "chroma_db"
COLLECTION_NAME = "nyu_off_campus_housing"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 5


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    distance: float
    metadata: dict[str, Any]


def load_chunks(path: Path = CHUNKS_PATH) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"No chunks at {path}. Run `python run_pipeline.py` first."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def get_embedding_model(model_name: str = EMBEDDING_MODEL) -> SentenceTransformer:
    return SentenceTransformer(model_name)


def get_chroma_collection(
    *,
    chroma_path: Path = CHROMA_PATH,
    collection_name: str = COLLECTION_NAME,
    reset: bool = False,
):
    chroma_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(chroma_path))
    if reset:
        try:
            client.delete_collection(collection_name)
        except (ValueError, NotFoundError):
            pass
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def _chunk_metadata(record: dict) -> dict[str, str | int | float]:
    meta = dict(record.get("metadata", {}))
    chunk_id = record["id"]
    source_id = str(meta.get("source_id", "unknown"))
    return {
        "chunk_id": chunk_id,
        "source_id": source_id,
        "source_file": f"{source_id}.txt",
        "doc_type": str(meta.get("doc_type", "")),
        "url": str(meta.get("url", "")),
        "title": str(meta.get("title", ""))[:500],
        "section": str(meta.get("section", meta.get("title", "")))[:500],
        "kind": str(meta.get("kind", "")),
        "chunk_index": int(chunk_id.rsplit("_", 1)[-1])
        if "_" in chunk_id
        else 0,
    }


def build_index(
    *,
    chunks_path: Path = CHUNKS_PATH,
    chroma_path: Path = CHROMA_PATH,
    reset: bool = True,
    model_name: str = EMBEDDING_MODEL,
) -> int:
    """Embed all chunks and store them in ChromaDB. Returns number of chunks indexed."""
    records = load_chunks(chunks_path)
    if not records:
        raise ValueError("chunks.json is empty")

    model = get_embedding_model(model_name)
    collection = get_chroma_collection(chroma_path=chroma_path, reset=reset)

    ids = [r["id"] for r in records]
    documents = [r["text"] for r in records]
    metadatas = [_chunk_metadata(r) for r in records]

    embeddings = model.encode(
        documents,
        show_progress_bar=True,
        batch_size=32,
    ).tolist()

    # Chroma has batch limits; add in batches
    batch_size = 100
    for start in range(0, len(ids), batch_size):
        end = start + batch_size
        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            embeddings=embeddings[start:end],
            metadatas=metadatas[start:end],
        )

    return len(ids)


def get_relevant_chunks(
    query: str,
    k: int = DEFAULT_TOP_K,
    *,
    chroma_path: Path = CHROMA_PATH,
    collection_name: str = COLLECTION_NAME,
    model_name: str = EMBEDDING_MODEL,
) -> list[RetrievedChunk]:
    """Return top-k chunks for a query with cosine distance scores (lower = better)."""
    model = get_embedding_model(model_name)
    collection = get_chroma_collection(
        chroma_path=chroma_path,
        collection_name=collection_name,
        reset=False,
    )

    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved: list[RetrievedChunk] = []
    if not results["ids"] or not results["ids"][0]:
        return retrieved

    for chunk_id, text, meta, distance in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved.append(
            RetrievedChunk(
                chunk_id=chunk_id,
                text=text,
                distance=float(distance),
                metadata=meta or {},
            )
        )
    return retrieved
