def chunk_text(
    text: str,
    chunk_size: int = 200,
    overlap: int = 40
) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start: end])
        chunks.append(chunk)
        start += chunk_size - overlap
        
    return [c for c in chunks if len(c.strip()) > 50]

def load_and_chunk(filepath: str, chunk_size: int = 200, overlap: int = 40):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
        
    text = " ".join(text.split())
    return chunk_text(text, chunk_size, overlap)

if __name__ == "__main__":
    chunks = load_and_chunk("sample_doc.txt")
    print(f"Total chunks: {len(chunks)}\n")
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1} ---")
        print(chunk)
        print()