from app.services.repository_service import BaseRepository
from app.database.mongodb import get_events_collection
from app.models.events import Event
from app.models.events import HostData
from app.models.messages import Message
from datetime import datetime, timezone
from typing import Optional, Tuple
from bson import ObjectId
from app.services.message_service import MessageRepository

import logging

logger = logging.getLogger(__name__)

class EventRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_events_collection(), Event)
    
    async def upsert(self,host_data: HostData, message_data: Message) -> Event:
        try:
            # Process message text and determine status
            status, processed_text = self._process_message_text(message_data.text)

            # Determine event name
            name = await self._identify_event(host_data.model, processed_text)

            # Find existing event
            existing_event = await self._find_existing_event(host_data.ip, name)

            if existing_event:
                updated_event = await self._update_existing_event(
                    existing_event["_id"], 
                    message_data.id, 
                    status
                )
                
            else:
                updated_event = await self._create_new_event(
                    host_data, 
                    name, 
                    message_data.id, 
                    status
                )

            return Event(**updated_event)
        
        except Exception as e:
            logger.error(f"Error in upsert event: {str(e)}")
            raise
    

    async def _identify_event(self, model: str, text: str) -> str:
        """Identify and return event name based on model and message text"""
        # TODO: Implement more sophisticated event identification logic
        return text[:100]
    

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
    
    async def _create_new_event(
        self, 
        host_data: HostData, 
        name: str, 
        message_id: str, 
        status: bool
    ) -> dict:
        """Create a new event document"""
        new_event = Event(
            **host_data.model_dump(),
            name=name,
            message_ids=[str(message_id)],
            status=status
        )
        insert_result = self.collection.insert_one(new_event.model_dump(by_alias=True))
        self.update_message_event_reference(message_id, str(insert_result.id))
        return self.collection.find_one({"_id": insert_result.inserted_id})
    
    async def _update_existing_event(
        self, 
        event_id: ObjectId, 
        message_id: str, 
        status: bool
    ) -> dict:
        """Update existing event with new message and status"""
        return self.collection.find_one_and_update(
            {"_id": event_id},
            {
                "$addToSet": {"message_ids": str(message_id)},
                "$set": {
                    "updated_at": datetime.now(timezone.utc),
                    "status": status
                }
            },
            return_document=True
        )

    async def update_message_event_reference(
        self, 
        message_id: str, 
        event_id: str 
    ) -> None:
        """
        Обновляет ссылку на событие в сообщении.
        """
        message_repo = MessageRepository()
        await message_repo.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": {"event_id": event_id}}
        )