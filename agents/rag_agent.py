from config.settings import FOREMAN_COMMISSION_RATE
from ai.embeddings import get_embedding
from ai.vector_store import search
from ai.gemini_client import chat


def handle(user_msg: str) -> str:
    msg = user_msg.lower()

    if any(w in msg for w in ["commission", "rate", "foreman"]):
        return f"The foreman commission rate is {FOREMAN_COMMISSION_RATE}% of the chit value."

    query_vector = get_embedding(user_msg)
    results = search(query_vector, limit=5)

    context_parts = []
    for r in results:
        section = r.payload.get("section_title", "")
        category = r.payload.get("category", "")
        tags = r.payload.get("tags", [])
        text = r.payload["text"]

        if section:
            context_parts.append(f"[{section}] ({category})\n{text}")
        else:
            context_parts.append(text)

    context = "\n\n".join(context_parts)

    prompt = f"""You are a friendly chit fund adviser. Answer the user question using the information below.

RULES:
- NEVER return any numerical values like amounts, percentages, or calculations
- NEVER say "5%", "₹5,00,000", "35%" or any specific numbers
- ONLY explain concepts, processes, rules, and benefits in words
- If user asks about specific amounts, say "Please ask me to calculate that for you"
- Keep answers short and friendly

Information:
{context}

Question: {user_msg}

Answer:"""

    return chat(prompt)
