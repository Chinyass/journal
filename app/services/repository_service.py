from typing import Optional, List, Type, TypeVar
from bson import ObjectId
from datetime import datetime, timezone
from pydantic import BaseModel
from pymongo.collection import Collection

T = TypeVar('T', bound=BaseModel)

class BaseRepository:
    def __init__(self, collection: Collection, model: Type[T]):
        self.collection = collection
        self.model = model
    
    async def create(self, item: T) -> T:
        item_dict = item.model_dump(by_alias=True, exclude={"id"})
        res = self.collection.insert_one(item_dict)
        item.id = str(res.inserted_id)
        return item

    async def get(self, id: str) -> Optional[T]:
        item_data = self.collection.find_one({"_id": ObjectId(id)})
        return self.model(**item_data) if item_data else None
    
    async def get_list(
            self,
            skip: int = 0,
            limit: int = 100,
            text_search: Optional[str] = None,
            **filters
    ) -> List[T]:
        query = {}

        if text_search:
            query["$text"] = {"$search": text_search}
        
        for field, value in filters.items():
            if value is not None:
                query[field] = value
        
        cursor = self.collection.find(query).skip(skip).limit(limit)
        return [self.model(**item) for item in cursor]
    
    async def update(self, id: str, update_data: dict) -> Optional[T]:
        update_data = {k: v for k, v in update_data.items() if v is not None}
        update_data.pop("id", None)
        update_data.pop("_id", None)
        update_data.pop("created_at", None)
        
        if not update_data:
            return None
        
        update_data["updated_at"] = datetime.now(timezone.utc)

        result = self.collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": update_data},
            return_document=True
        )
        return self.model(**result) if result else None
    
    async def delete(self, id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0