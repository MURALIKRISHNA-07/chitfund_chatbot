import math
import re
from collections import Counter

from google import genai
from config.settings import GEMINI_API_KEY, GEMINI_EMBEDDING_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)


def get_embedding(text: str) -> list[float]:
    result = client.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        contents=text,
    )
    return result.embeddings[0].values


def get_embeddings(texts: list[str]) -> list[list[float]]:
    result = client.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        contents=texts,
    )
    return [e.values for e in result.embeddings]


def get_sparse_embedding(text: str) -> dict:
    tokens = re.findall(r'\b\w+\b', text.lower())
    counts = Counter(tokens)
    total = len(tokens) if tokens else 1

    indices = {}
    for i, (token, count) in enumerate(counts.most_common(100)):
        idx = abs(hash(token)) % 30000
        while idx in indices:
            idx = (idx + 1) % 30000
        indices[idx] = count / total

    return {
        "indices": list(indices.keys()),
        "values": list(indices.values()),
    }
