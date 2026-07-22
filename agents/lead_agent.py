import json
from ai.gemini_client import chat
from database.leads import save_lead


def _extract_info(user_msg: str, history: list[dict] = None) -> dict:
    history_text = ""
    if history:
        recent = history[-6:]
        history_text = "\n".join([f"{m['role']}: {m['text'][:150]}" for m in recent])

    prompt = f"""Extract customer details from this message. Look at conversation history for context.

Return JSON only: {{"name": "string", "mobile": "string", "city": "string", "budget": number, "scheme": "string", "is_complete": boolean}}

Rules:
- If user provides name and mobile, set is_complete to true
- If fields are missing, set them to empty string or 0
- Look at history to find scheme value if user is responding to a recommendation

Message: {user_msg}"""
    response = chat(prompt)
    try:
        return json.loads(response)
    except Exception:
        return {"name": "", "mobile": "", "city": "", "budget": 0, "scheme": "", "is_complete": False}


def handle(user_msg: str, history: list[dict] = None) -> str:
    data = _extract_info(user_msg, history)

    if data.get("is_complete") or (data.get("name") and data.get("mobile")):
        lead_id = save_lead({
            "name": data["name"],
            "mobile": data["mobile"],
            "city": data.get("city", ""),
            "budget": data.get("budget", 0),
            "interested_scheme": data.get("scheme", ""),
        })
        return (
            f"Thank you {data['name']}! Your details have been saved.\n\n"
            f"Our team will contact you soon at {data['mobile']}."
        )

    return (
        "I'd love to help you get started! Please share:\n\n"
        "1. **Your name**\n"
        "2. **Mobile number**\n"
        "3. **City**\n\n"
        "This helps our team reach out to you with the best scheme options."
    )
