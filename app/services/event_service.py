from app.services.repository_service import BaseRepository
from app.database.mongodb import get_events_collection
from app.models.events import Event
from app.models.events import HostData
from app.models.messages import Message
from datetime import datetime, timezone
from typing import Optional

class EventRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_events_collection(), Event)
    
    async def upsert(self,host_data: HostData, message_data: Message) -> Event:
        status = True
        message_data.text = message_data.text.strip()
        message = message_data.text
        if "SOLVED" in message_data.text:
            status = False
            message = message_data.text.replace("SOLVED","").strip()

        name = await self.identifier_event(host_data.model, message_data.text)
        if not name:
            name = message

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
        else:
            # Создаем новое событие
            new_event = Event(
                **host_data.model_dump(),
                name=name,
                messages=[message_data],
                status=status
            )
            updated_event = self.collection.insert_one(new_event.model_dump())
            updated_event = self.collection.find_one({"_id": updated_event.inserted_id})

        return Event(**updated_event)
    
    async def identifier_event(self, model: str, text: str) -> Optional[str]:
        return None
        '''
            TODO
        '''