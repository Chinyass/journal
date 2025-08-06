from app.services.repository_service import BaseRepository
from app.database.mongodb import get_events_collection
from app.models.events import Event
from app.models.events import HostData
from app.models.messages import Message
from datetime import datetime, timezone
from typing import Optional

import logging

logger = logging.getLogger(__name__)

class EventRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_events_collection(), Event)
    
    async def upsert(self,host_data: HostData, message_data: Message) -> Event:
        try:
            status = True
            message_text = message_data.text.strip()

            if "SOLVED" in message_data.text:
                status = False
                message_text = message_text.replace("SOLVED", "").strip()

            # Определяем имя события
            name = await self.identifier_event(host_data.model, message_data.text)
            if not name:
                name = message_text[:100]

            # Ищем существующее событие
            existing_event = self.collection.find_one({
                "ip": host_data.ip,
                "name": name
            })

            # Обновляем или создаем событие
            if existing_event:
                # Обновляем существующее событие
                updated_event = self.collection.find_one_and_update(
                    {"_id": existing_event["_id"]},
                    {
                        "$push": {"messages": message_data.model_dump()},  # Добавляем сообщение
                        "$set": {
                            "updated_at": datetime.now(timezone.utc),
                            "status": status  # Обновляем статус
                        }
                    },
                    return_document=True  # Возвращаем обновленный документ
                )
                logger.info(f"Updated existing event: {updated_event['_id']}")
            else:
                # Создаем новое событие
                new_event = Event(
                    **host_data.model_dump(),
                    name=name,
                    messages=[message_data],
                    status=status
                )
                insert_result = self.collection.insert_one(new_event.model_dump(by_alias=True))
                updated_event = self.collection.find_one({"_id": insert_result.inserted_id})
                
                logger.info(f"Created new event: {insert_result.inserted_id}")

            return Event(**updated_event)
        
        except Exception as e:
            logger.error(f"Error in upsert event: {str(e)}")
            raise
    
    async def identifier_event(self, model: str, text: str) -> Optional[str]:
        return None
        '''
            TODO
        '''