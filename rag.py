import chromadb
import logging
from fastapi import HTTPException
from groq import Groq
from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("docs")
groq_client = Groq()

DOCUMENTS = [
    "FastAPI is a modern Python web framework for building APIs. It uses type hints for validation.",
    "ChromaDB is a vector database that stores embeddings and supports similarity search.",
    "RAG stands for Retrieval Augmented Generation. It grounds LLM responses in real documents.",
    "Embeddings are numerical representations of text. Similar texts have similar embeddings.",
    "Docker is a platform for packing applications into containers for consistent deployment.",
    "PostgreSQL is a relational database. It supports ACID transcations and complex queries.",
]

def ingest():
    current_count = collection.count()
    
    if current_count > 0:
        print(f"Skipping ingestion: Collection already has {current_count} documents.")
        return
    
    print("Ingesting new documents...")
    embeddings = embedding_model.encode(DOCUMENTS).tolist()
    collection.upsert(
        documents=DOCUMENTS,
        embeddings=embeddings,
        ids=[f"doc_{i}" for i in range(len(DOCUMENTS))]
    )
    
def retrieve(query: str, n_results: int = 2) -> list[str]:
    query_text = str(query)
    query_embedding = embedding_model.encode([query_text]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    docs = results.get("documents")
    if docs is not None and len(docs) > 0:
        return docs[0]
    
    return []

def ask(question: str) -> tuple[str, list[str]]:
    try:
        chunks = retrieve(question, n_results=2)
    
        if not chunks:
            return "I don't have any documents related to that question.", []
    
        context = "\n".join(chunks)
    
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=256,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. Answer the user's question "
                        "using only the context provided. If the answer is not in "
                        "the context, say 'I don't have that information'."
                    )
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}"
                }
            ]
        )
        answer = response.choices[0].message.content or "No response generated."
        return answer, chunks
    except Exception as e:
        logger.error(f"RAG ask failed: {e}")
        raise HTTPException(status_code=502, detail="LLM Service unavailable")
    
def ingest_documents(documents: list[str]) -> int:
    try:
        embeddings = embedding_model.encode(documents).tolist()
        ids = [f"doc_{collection.count() + i}" for i in range(len(documents))]
        collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids
        )
        return len(documents)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail="Ingestion failed")