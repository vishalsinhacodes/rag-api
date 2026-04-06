# RAG API

A Retrieval Augmented Generation API that answers natural language questions against a private document store. Built with FastAPI, ChromaDB, and Llama 3.3 via Groq.

## Architecture

Incoming questions are embedded locally using a sentence-transformer model, then matched against stored document chunks in ChromaDB using vector similarity search. The top matching chunks are passed as context to Llama 3.3, which generates a grounded answer. Documents can be added at runtime via the `/ingest` endpoint without restarting the server.

Request → FastAPI → ChromaDB (retrieve chunks) → Groq/Llama (generate answer) → Response

## Endpoints

| Method | Endpoint | Description                               |
| ------ | -------- | ----------------------------------------- |
| GET    | /health  | Health check                              |
| POST   | /ask     | Ask a question against the document store |
| POST   | /ingest  | Add new documents to the vector store     |

## Setup

1. Clone the repo
   git clone https://github.com/vishalsinhacodes/rag-api.git
   cd rag-api

2. Create and activate a virtual environment
   python -m venv venv
   venv\Scripts\activate # Windows

3. Install dependencies
   pip install -r requirements.txt

4. Set your Groq API key
   set GROQ_API_KEY=your_key_here # Windows

5. Run the server
   uvicorn main:app --reload

API docs available at http://localhost:8000/docs

## Example Usage

Ask a question:
curl -X POST http://localhost:8000/ask \
 -H "Content-Type: application/json" \
 -d "{\"question\": \"What is ChromaDB?\"}"

Response:
{
"answer": "ChromaDB is a vector database that stores embeddings and supports similarity search.",
"sources": ["ChromaDB is a vector database..."]
}

Ingest a new document:
curl -X POST http://localhost:8000/ingest \
 -H "Content-Type: application/json" \
 -d "{\"documents\": [\"Redis is an in-memory data store used for caching.\"]}"

## Design Decisions

- **ChromaDB over Pinecone** — runs fully local with no account or API key required, making it easy for anyone to clone and run this project immediately
- **PersistentClient over in-memory** — vector store survives server restarts so ingested documents are not lost between deployments
- **upsert over add** — prevents duplicate ID errors if the server restarts and ingestion runs again against existing data
- **502 for LLM failures** — the API acts as a gateway to Groq; when the upstream provider fails, 502 Bad Gateway is semantically correct rather than a generic 500

## Tech Stack

- FastAPI — HTTP framework
- ChromaDB — vector database
- sentence-transformers — local embedding model (all-MiniLM-L6-v2)
- Groq — LLM inference (Llama 3.3 70B)
- Pydantic — request/response validation
