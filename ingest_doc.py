import httpx
from chunker import load_and_chunk

chunks = load_and_chunk("sample_doc.txt")
print(f"Ingesting {len(chunks)} chunks...")

response = httpx.post(
    "http://localhost:8000/ingest",
    json={"documents": chunks}
)

print(response.json())