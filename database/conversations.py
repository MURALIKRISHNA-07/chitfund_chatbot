from database.mongodb import db

collection = db["conversations"]


def save_conversation(user_id: str, messages: list[dict]) -> str:
    result = collection.insert_one({"user_id": user_id, "messages": messages})
    return str(result.inserted_id)


def get_conversations(user_id: str) -> list[dict]:
    return list(collection.find({"user_id": user_id}))


def append_message(user_id: str, role: str, text: str):
    collection.update_one(
        {"user_id": user_id},
        {"$push": {"messages": {"role": role, "text": text}}},
        upsert=True,
    )
