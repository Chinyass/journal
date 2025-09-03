from app.services.repository_service import BaseRepository
from app.database.mongodb import get_events_collection
from app.models.events import Event
from app.models.events import HostData
from app.models.messages import Message
from datetime import datetime
from typing import Optional, Tuple, List
from bson import ObjectId
from app.services.message_service import MessageRepository
import logging
import traceback

logger = logging.getLogger(__name__)

class EventRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_events_collection(), Event)
    
    async def get_list(
        self,
        skip: int = 0,
        limit: int = 10,
        text_search: Optional[str] = None,
        service_filter: Optional[str] = None,
        **filters
    ) -> List[Event]:
        query = {}

        if text_search:
            query["$text"] = {"$search": text_search}
        
        if service_filter:
            query["services"] = {"$regex": service_filter, "$options": "i"}  # case-insensitive search
        
        for field, value in filters.items():
            if value is not None:
                query[field] = value
        
        cursor = self.collection.find(query).sort("updated_at", -1).skip(skip).limit(limit)
        return [self.model(**item) for item in cursor]
    
    async def get_count(
        self,
        text_search: Optional[str] = None,
        service_filter: Optional[str] = None,
        **filters
    ) -> int:
        query = {}
        
        if text_search:
            query["$text"] = {"$search": text_search}
        
        if service_filter:
            query["services"] = {"$regex": service_filter, "$options": "i"}
        
        for field, value in filters.items():
            if value is not None:
                query[field] = value
        
        return self.collection.count_documents(query)
    

    async def upsert(self, host_data: HostData, message_data: Message) -> Event:
        try:
            # Process message text and determine status
            status, processed_text = self._process_message_text(message_data.text)

            # Determine event name
            name = await self._identify_event(host_data.model, processed_text)

            # Find existing event
            existing_event = await self._find_existing_event(host_data.ip, name)
            
            event_data = None
            if existing_event:
                event_data = await self._update_existing_event(
                    host_data,
                    existing_event["_id"], 
                    status
                )
            else:
                event_data = await self._create_new_event(
                    host_data, 
                    name, 
                    message_data.id, 
                    status
                )

            return Event(**event_data)
        
        except Exception as e:
            logger.error(f"Error in upsert event:\n{traceback.format_exc()}")
            raise
    

    async def _identify_event(self, model: str, text: str) -> str:
        """Identify and return event name based on model and message text"""
        # TODO: Implement more sophisticated event identification logic
        return text[:300]
    

    def _process_message_text(self, text: str) -> Tuple[bool, str]:
        """Process message text and return status and cleaned text"""
        cleaned_text = text.strip()
        if "SOLVED" in cleaned_text:
            return False, cleaned_text.replace("SOLVED", "").strip()
        return True, cleaned_text

    async def _find_existing_event(self, ip: str, name: str) -> Optional[dict]:
        """Find existing event by IP and name"""
        return self.collection.find_one({
            "ip": ip,
            "name": name
        })
    
    async def _create_new_event(self, host_data: HostData, name: str, message_id: str, status: bool) -> dict:
        """Create a new event document"""

        event_data = {
            **host_data.model_dump(),
            "name": name,
            "status": status,
            "count_message": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Вставляем новый документ
        insert_result = self.collection.insert_one(event_data)
        
        # Получаем созданный документ
        created_event = self.collection.find_one({"_id": insert_result.inserted_id})
        # Обновляем ссылку на событие в сообщении
        await self.update_message_event_reference(message_id, str(insert_result.inserted_id))
        
        # Убедимся, что _id преобразован в строку
        if created_event and '_id' in created_event:
            created_event['_id'] = str(created_event['_id'])
        
        return created_event
    
    async def _update_existing_event(self, host_data: HostData, event_id, status: bool) -> dict:
        """Update existing event with new message and status"""

        # Убедимся, что event_id - ObjectId
        if not isinstance(event_id, ObjectId):
            event_id = ObjectId(event_id)
        
        # Получаем данные из host_data в виде словаря
        host_data_dict = host_data.model_dump()

        updated_event = self.collection.find_one_and_update(
            {"_id": event_id},
            {
                "$set": {
                    **host_data_dict,
                    "updated_at": datetime.now(),
                    "status": status
                },
                "$inc": {
                    "count_message": 1
                }
            },
            return_document=True
        )
        
        # Убедимся, что _id преобразован в строку
        if updated_event and '_id' in updated_event:
            updated_event['_id'] = str(updated_event['_id'])
        
        return updated_event

    async def update_message_event_reference(
        self, 
        message_id: str, 
        event_id: str 
    ) -> None:
        """
        Обновляет ссылку на событие в сообщении.
        """
        message_repo = MessageRepository()
        message_repo.update_message_event_reference(message_id, event_id )