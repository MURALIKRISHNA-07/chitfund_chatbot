from logic.chit_calculator import (
    load_schemes,
    find_scheme,
    generate_chit_breakdown,
    compare_schemes,
    recommend_scheme,
)
from ai.embeddings import get_embedding
from ai.vector_store import search
from ai.gemini_client import chat
from config.settings import FOREMAN_COMMISSION_RATE


def find_scheme_by_budget(monthly_budget: int) -> list[dict]:
    return recommend_scheme(monthly_budget)


def find_scheme_by_value(value: int) -> dict | None:
    return find_scheme(value)


def calculate_profit(value: int, monthly: int, duration: int, members: int, commission_percent: float = None) -> dict:
    if commission_percent is None:
        commission_percent = FOREMAN_COMMISSION_RATE
    df, summary = generate_chit_breakdown(value, monthly, duration, members, commission_percent)
    return summary


def answer_from_pdf(question: str) -> str:
    query_vector = get_embedding(question)
    results = search(query_vector, limit=5)
    context = "\n\n".join([r.payload["text"] for r in results])

    prompt = f"""You are a chit fund expert. Answer the user question using ONLY the context below.
If the answer is not in the context, say you don't have that information.

Context:
{context}

Question: {question}

Answer:"""

    return chat(prompt)
