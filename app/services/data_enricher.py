from app.services.netbox_service import NetboxService
from app.services.message_service import MessageRepository
from app.models.messages import Message


class DataEnricher:
    def __init__(self):        
        self.netbox = NetboxService()
        self.message_repo = MessageRepository()

    async def enriche(self, data):
        netbox_data = await self.get_data_from_netbox(data["ip"])
        netbox_data["text"] = data["message"]
        netbox_data["ip"] = data["ip"]
        print(netbox_data)
        message_data = Message(**netbox_data)
        message = await self.message_repo.create_message(message_data)
        print(message)
        
    async def get_data_from_netbox(self,ip: str):
        
        data = {
            "name" : None,
            "model" : None,
            "role" : None,
            "location": None,
            "services": []
        }

        try:
            netbox_device = self.netbox.nb.dcim.devices.get(primary_ip4=f"{ip}/24")

            if not netbox_device:
                return data
            
            data["name"] = netbox_device.name
            
            #get model
            if netbox_device.device_type.model != "unknown":
                data["model"] = netbox_device.device_type.model
            
            #get role
            if netbox_device.role.name != "unknown":
                data["role"] = netbox_device.role.name

            #get location
            if netbox_device.site.name != "unknown":
                data["location"] = netbox_device.site.name
            
        except Exception as e:
            if 'code 400' in str(e):
                '''
                    TODO
                '''
                pass
        
        return data