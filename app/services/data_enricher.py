from app.services.netbox_service import NetboxService
from app.models.messages import RawMessage
from app.models.events import HostData

class DataEnricher:
    def __init__(self):        
        self.netbox = NetboxService()
        
    async def enriche(self, raw_message: RawMessage) -> HostData:
        enriched_data: HostData = await self.get_data_from_netbox(raw_message.ip)
        return enriched_data
    
    async def get_data_from_netbox(self,ip: str) -> HostData:
        
        data = {
            "ip" : ip,
            "hostname" : None,
            "model" : None,
            "role" : None,
            "location": None,
            "services": []
        }

        try:
            ipam_ip = self.netbox.nb.ipam.ip_addresses.get(address=ip)
            netbox_device = None
            if ipam_ip and ipam_ip.assigned_object:
                netbox_device = self.netbox.nb.dcim.devices.get(id=ipam_ip.assigned_object.device.id)

            if not netbox_device:
                return HostData(**data)
            
            data["hostname"] = netbox_device.name
            
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
        
        return HostData(**data)