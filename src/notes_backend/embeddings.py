"""Calcul d'embeddings pour les notes, avec repli local déterministe si aucune clé API n'est
configurée (permet de faire tourner tout le pipeline — et les tests — hors ligne)."""

import hashlib
import math

from notes_backend.config import Settings


def _hash_embedding(text: str, dimensions: int = 256) -> list[float]:
    """Embedding de secours, déterministe mais dénué de sens sémantique réel.

    Utile pour développer/tester le pipeline de bout en bout sans clé API, mais ne remplace
    pas un vrai modèle d'embeddings en production (voir compute_embedding)."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values = [float(digest[i % len(digest)]) for i in range(dimensions)]
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


def compute_embedding(text: str, settings: Settings) -> list[float]:
    """Calcule l'embedding d'un texte via l'API OpenAI, avec repli déterministe si pas de clé."""
    if not settings.openai_api_key:
        return _hash_embedding(text)

    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.embeddings.create(model=settings.embedding_model, input=text)
    return response.data[0].embedding
