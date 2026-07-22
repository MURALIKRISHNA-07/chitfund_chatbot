from database.mongodb import db

collection = db["users"]


def create_user(data: dict) -> str:
    result = collection.insert_one(data)
    return str(result.inserted_id)


def get_user(user_id: str) -> dict | None:
    from bson import ObjectId
    return collection.find_one({"_id": ObjectId(user_id)})


def update_user(user_id: str, data: dict) -> bool:
    from bson import ObjectId
    result = collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})
    return result.modified_count > 0


def find_user_by_mobile(mobile: str) -> dict | None:
    return collection.find_one({"mobile": mobile})
