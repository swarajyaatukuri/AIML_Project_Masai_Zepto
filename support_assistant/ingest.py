"""Ingest the eight exact policy documents into the local ChromaDB collection."""

from __future__ import annotations

from vector_store import ingest


if __name__ == "__main__":
    count = ingest()
    print(f"Ingested/upserted {count} policy documents into ChromaDB.")
