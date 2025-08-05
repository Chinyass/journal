from app.models.messages import RawMessage
from app.services.data_enricher import DataEnricher
from app.services.message_service import MessageRepository
from app.services.event_service import EventRepository
from app.models.messages import Message
from app.models.events import Event, HostData


class JournalService:
    def __init__(self):
        self.data_enricher = DataEnricher()
        self.message_repo = MessageRepository()
        self.event_repo = EventRepository()

    async def handle(self, raw_message: RawMessage) -> Event:
        host_data = await self.get_host_data(raw_message)
        message = await self.create_message(raw_message)
        
        event = await self.create_event(host_data, message)
        
        print(event)
        
    
    async def get_host_data(self, raw_message: RawMessage) -> HostData:
        host_data: HostData = await self.data_enricher.enriche(raw_message)
        return host_data
    
    async def create_message(self, raw_message: RawMessage) -> Message:
        message_data = Message(text=raw_message.text)
        message: Message = await self.message_repo.create(message_data)
        return message
    
    async def create_event(self, host_data: HostData, message: Message) -> Event:
        event = await self.event_repo.upsert(host_data, message)
        return event

    async def analyze(self):
        pass
        '''
            TODO
        '''