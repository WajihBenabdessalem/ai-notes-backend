"""Recherche par similarité cosinus, implémentée sans dépendance externe (pas de FAISS/Chroma) —
volontairement, pour démontrer la mécanique sous-jacente d'une recherche vectorielle."""

import math


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def rank_by_similarity(
    query_embedding: list[float], candidates: list[tuple[str, list[float]]], top_k: int
) -> list[tuple[str, float]]:
    """Trie une liste de (id, embedding) par similarité décroissante avec la requête."""
    scored = [(item_id, cosine_similarity(query_embedding, emb)) for item_id, emb in candidates]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:top_k]
