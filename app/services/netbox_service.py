from app.config import settings
import pynetbox

class NetboxService:
    def __init__(self):
        self.nb = pynetbox.api(
            settings.NETBOX_URL,
            token=settings.NETBOX_TOKEN
        )
    

