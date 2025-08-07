from app.services.repository_service import BaseRepository
from app.database.mongodb import get_messages_collection
from app.models.messages import Message
from bson import ObjectId

class MessageRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_messages_collection(), Message)
    

    def update_message_event_reference(
        self, 
        message_id: str, 
        event_id: str
    ):
        self.collection.find_one_and_update(
            {"_id": ObjectId(message_id)},
            {
                "$set": {
                    "event_id": ObjectId(event_id)
                }
            }
        )