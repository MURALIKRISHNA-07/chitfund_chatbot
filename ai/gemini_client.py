from google import genai
from config.settings import GEMINI_API_KEY, GEMINI_CHAT_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)


def chat(prompt: str, history: list[dict] = None) -> str:
    if history:
        chat_session = client.chats.create(model=GEMINI_CHAT_MODEL)
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            chat_session.messages.append({"role": role, "parts": [msg["text"]]})
        response = chat_session.send_message(prompt)
        return response.text

    response = client.models.generate_content(
        model=GEMINI_CHAT_MODEL,
        contents=prompt,
    )
    return response.text
