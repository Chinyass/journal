from app.database.mongodb import get_messages_collection


class MessageManager:
    def __init__(self):
        self.collection = get_messages_collection()
    

    def create_message(
                    self, 
                    ip, 
                    name, 
                    role, 
                    model,
                    location,
                    services 
                ):
        
        pass


    def get_messages(self):
        pass