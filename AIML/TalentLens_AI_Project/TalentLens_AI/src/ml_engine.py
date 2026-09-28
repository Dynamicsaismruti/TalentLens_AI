from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .config import EMBEDDING_MODEL

@lru_cache(maxsize=1)
def get_encoder() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)

def semantic_similarity(text_a: str, text_b: str) -> float:
    encoder = get_encoder()
    embeddings = encoder.encode([text_a, text_b], normalize_embeddings=True)
    return float(np.dot(embeddings[0], embeddings[1]))

def rank_chunks(query: str, chunks: list[str], top_k: int = 4) -> list[tuple[str, float]]:
    if not chunks:
        return []
    encoder = get_encoder()
    vectors = encoder.encode([query] + chunks, normalize_embeddings=True)
    scores = np.dot(vectors[1:], vectors[0])
    order = np.argsort(scores)[::-1][:top_k]
    return [(chunks[i], float(scores[i])) for i in order]

def combined_match_score(semantic_score: float, skill_coverage: float) -> float:
    # Semantic similarity captures meaning; skill coverage rewards explicit requirements.
    score = 0.70 * semantic_score + 0.30 * skill_coverage
    return max(0.0, min(1.0, score))
