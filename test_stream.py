import httpx

with httpx.stream(
    "POST",
    "http://localhost:8000/ask/stream",
    json={"question": "What is FastAPI?"},
    timeout=30
) as response:
    for text in response.iter_text():
        print(text, end="", flush=True)
print()