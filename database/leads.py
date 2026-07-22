from database.mongodb import db

collection = db["leads"]


def save_lead(data: dict) -> str:
    data.setdefault("status", "new")
    result = collection.insert_one(data)
    return str(result.inserted_id)


def get_leads(status: str = None) -> list[dict]:
    query = {"status": status} if status else {}
    return list(collection.find(query))


def update_lead_status(lead_id: str, status: str) -> bool:
    from bson import ObjectId
    result = collection.update_one(
        {"_id": ObjectId(lead_id)}, {"$set": {"status": status}}
    )
    return result.modified_count > 0
