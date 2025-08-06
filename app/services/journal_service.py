from app.models.messages import RawMessage
from app.services.data_enricher import DataEnricher
from app.services.message_service import MessageRepository
from app.services.event_service import EventRepository
from app.models.messages import Message
from app.models.events import Event, HostData
import logging

logger = logging.getLogger(__name__)

class JournalService:
    def __init__(self):
        self.data_enricher = DataEnricher()
        self.message_repo = MessageRepository()
        self.event_repo = EventRepository()

    async def handle(self, raw_message: RawMessage) -> Event:
        try:
            logger.info(f"Processing new message from {raw_message.ip}: {raw_message.text}")
            
            # Получаем данные о хосте
            host_data = await self.get_host_data(raw_message)
            logger.debug(f"Host data retrieved: {host_data}")
            
            # Создаем сообщение
            message = await self.create_message(raw_message)
            logger.debug(f"Message created: {message.id}")
            
            # Создаем или обновляем событие
            event = await self.create_event(host_data, message)
            logger.info(f"Event processed: {event.id if event.id else 'new'}")
            
            return event
            
        except Exception as e:
            logger.error(f"Failed to process message: {str(e)}")
            raise
    
    async def get_host_data(self, raw_message: RawMessage) -> HostData:
        try:
            host_data: HostData = await self.data_enricher.enriche(raw_message)
            return host_data
        except Exception as e:
            logger.error(f"Error enriching host data: {str(e)}")
            # Возвращаем минимальные данные, если обогащение не удалось
            return HostData(ip=raw_message.ip)

    async def create_message(self, raw_message: RawMessage) -> Message:
        try:
            message_data = Message(text=raw_message.text)
            message: Message = await self.message_repo.create(message_data)
            return message
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            raise

    async def create_event(self, host_data: HostData, message: Message) -> Event:
        try:
            event = await self.event_repo.upsert(host_data, message)
            return event
        except Exception as e:
            logger.error(f"Error creating/updating event: {str(e)}")
            raise

    async def analyze(self):
        pass
        '''
            TODO
        '''