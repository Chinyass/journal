from app.services.repository_service import BaseRepository
from app.database.mongodb import get_messages_collection
from app.models.messages import Message


class MessageRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_messages_collection(), Message)
    