# Module 3 — Support Assistant

## Required baseline

The graded path uses `MOCK_LLM` unset or `MOCK_LLM=1`. In that state there is no LLM-provider network call. Local Sentence Transformers embeddings and ChromaDB retrieval still run normally.

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python ingest.py
uvicorn main:app --host 127.0.0.1 --port 7860
```

The `all-MiniLM-L6-v2` model may need to be downloaded the first time it is used. After that, the model is cached locally by Sentence Transformers.

## Required sample calls in mock mode

Policy-style query:

```powershell
curl.exe -X POST http://127.0.0.1:7860/ask -H "Content-Type: application/json" -d "{\"query\":\"What is the delivery policy?\"}"
```

Expected shape:

```json
{
  "answer": "Based on the retrieved context: Zepto delivers grocery and household essentials...",
  "sources": ["doc_01", "doc_06", "doc_04"],
  "confidence": 1.0
}
```

The exact top-three source order can depend on embedding similarity, but the top result should contain delivery-policy text.

General query:

```powershell
curl.exe -X POST http://127.0.0.1:7860/ask -H "Content-Type: application/json" -d "{\"query\":\"What is 2 + 2?\"}"
```

Expected mock response:

```json
{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}
```

## RAG architecture

```text
                INGESTION
8 policy TXT files
       │
       ▼
per-document chunks
       │
       ▼
EMBEDDING
SentenceTransformer(all-MiniLM-L6-v2)
       │
       ▼
STORAGE
ChromaDB collection: zepto_policies
       │
       │ user query
       ▼
RETRIEVAL
retrieve() → cosine similarity → top 3 chunks
       │
       ▼
GENERATION
LangGraph retrieve_and_answer / direct_answer
       │
       ▼
Pydantic AnswerResponse
       │
       ▼
FastAPI POST /ask
```

`MOCK_LLM` affects the intent-generation and final-answer-generation steps only. In default mock mode, `classify_intent` uses the required keyword heuristic, `retrieve_and_answer` creates the required canned response from the most similar chunk, and `direct_answer` returns the fixed canned response. Embedding and Chroma retrieval are always real/local. When `MOCK_LLM=0`, the optional real-LLM branch uses the configured OpenAI-compatible endpoint and retries malformed JSON up to two additional times.

## Docker

```powershell
docker build -t zepto-support .
docker run --rm -p 7860:7860 zepto-support
```

The Dockerfile is designed for the required local/mock baseline. The container downloads the Sentence Transformers model on first use if it is not already cached inside the image.
