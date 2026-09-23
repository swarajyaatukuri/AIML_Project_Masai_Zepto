"""Local sentence-transformer embeddings and ChromaDB storage/retrieval."""

from __future__ import annotations

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "docs"
CHROMA_DIR = ROOT / "chroma_db"
COLLECTION_NAME = "zepto_policies"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def load_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def get_client():
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection():
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def read_documents() -> list[dict]:
    records = []
    for path in sorted(DOCS_DIR.glob("doc_*.txt")):
        records.append(
            {
                "id": path.stem,
                "document": path.read_text(encoding="utf-8").strip(),
                "source_file": path.name,
            }
        )
    if len(records) != 8:
        raise RuntimeError(f"Expected 8 policy documents, found {len(records)}")
    return records


def ingest() -> int:
    records = read_documents()
    model = load_model()
    collection = get_collection()
    embeddings = model.encode(
        [item["document"] for item in records],
        normalize_embeddings=True,
    ).tolist()

    ids = [item["id"] for item in records]
    documents = [item["document"] for item in records]
    metadatas = [{"source_file": item["source_file"]} for item in records]

    # Upsert makes the script safe to rerun without duplicating chunks.
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    return len(records)


def retrieve(query: str, top_k: int = 3) -> dict:
    model = load_model()
    collection = get_collection()
    query_embedding = model.encode([query], normalize_embeddings=True)[0].tolist()
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]
    ids = result.get("ids", [[]])[0]
    return {
        "documents": documents,
        "metadatas": metadatas,
        "distances": distances,
        "ids": ids,
    }
