from app.database.mongodb import get_messages_collection
from app.models.messages import Message
from typing import Optional, List
from bson import ObjectId
from datetime import datetime, timezone

class MessageRepository:
    def __init__(self):
        self.collection = get_messages_collection()
    

    async def create_message(self, message: Message ) -> Message:
        message_dict = message.model_dump(by_alias=True, exclude={"id"})
        res = self.collection.insert_one(message_dict)
        message.id = str(res.inserted_id)
       
        return message


    async def get_message(self, id: str) -> Optional[Message]:
        message_data = self.collection.find_one({"_id": ObjectId(id)})
        return Message(**message_data) if message_data else None
    
    async def get_messages(
            self,
            skip: int = 0,
            limit: int = 100,
            text_search: Optional[str] = None,
            **filters
                           
    ) -> List[Message]:
        query = {}

        if text_search:
            query["$text"] = {"$search": text_search}
        
        for field, value in filters.items():
            if value is not None:
                query[field] = value
        
        cursor = self.collection.find(query).skip(skip).limit(limit)

        return [ Message(**msg) for msg in cursor ]
    
    async def update_message(self, id: str, update_data: dict) -> Optional[Message]:
        # Удаляем None значения и поля, которые не должны обновляться
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

        return Message(**result) if result else None
    
    async def delete_message(self, id: str) -> bool:
        """Удаление сообщения"""
        result = self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
