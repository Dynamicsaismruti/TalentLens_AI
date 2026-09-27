import re
from .ml_engine import rank_chunks

def chunk_text(text: str, max_chars: int = 900) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\n", text) if p.strip()]
    chunks, current = [], ""
    for paragraph in paragraphs:
        if len(current) + len(paragraph) + 1 <= max_chars:
            current = (current + " " + paragraph).strip()
        else:
            if current:
                chunks.append(current)
            current = paragraph
    if current:
        chunks.append(current)
    return chunks

def retrieve_context(query: str, documents: list[str], top_k: int = 5) -> list[tuple[str, float]]:
    chunks = []
    for document in documents:
        chunks.extend(chunk_text(document))
    return rank_chunks(query, chunks, top_k=top_k)
