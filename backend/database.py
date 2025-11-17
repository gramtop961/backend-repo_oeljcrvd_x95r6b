import os
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "appdb")

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_db() -> AsyncIOMotorDatabase:
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(DATABASE_URL)
        _db = _client[DATABASE_NAME]
    return _db


async def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    db = get_db()
    data = {**data, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
    result = await db[collection_name].insert_one(data)
    inserted = await db[collection_name].find_one({"_id": result.inserted_id})
    if inserted and "_id" in inserted:
        inserted["id"] = str(inserted.pop("_id"))
    return inserted or {}


async def get_documents(collection_name: str, filter_dict: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
    db = get_db()
    cur = db[collection_name].find(filter_dict or {}).limit(limit)
    docs: List[Dict[str, Any]] = []
    async for doc in cur:
        doc["id"] = str(doc.pop("_id"))
        docs.append(doc)
    return docs


async def get_document(collection_name: str, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = get_db()
    doc = await db[collection_name].find_one(filter_dict)
    if doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


async def update_document(collection_name: str, filter_dict: Dict[str, Any], update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = get_db()
    update["updated_at"] = datetime.utcnow()
    await db[collection_name].update_one(filter_dict, {"$set": update})
    return await get_document(collection_name, filter_dict)


async def delete_document(collection_name: str, filter_dict: Dict[str, Any]) -> bool:
    db = get_db()
    res = await db[collection_name].delete_one(filter_dict)
    return res.deleted_count > 0
