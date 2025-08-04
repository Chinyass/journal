from datetime import datetime
from typing import List, Dict, Optional
from pymongo import ReturnDocument
from app.database.mongodb import get_incidents_collection
from app.models.incident import Incident

from app.websocket.manager import manager

from pymongo import DESCENDING, ASCENDING

async def upsert_incident(incident_data: Dict) -> Incident:
    collection = get_incidents_collection()

    result = collection.find_one_and_update(
        {"host": incident_data["host"], "message": incident_data["message"]},
        {
            "$inc": {"count": 1},
            "$set": {
                "last_updated": datetime.now(),
                "location": incident_data.get("location", ""),
                "hostname": incident_data["hostname"]
            }
        },
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    
    if result:
        # Convert MongoDB document to dict and handle _id
        incident_dict = dict(result)
        if "_id" in incident_dict:
            incident_dict["id"] = str(incident_dict["_id"])
            del incident_dict["_id"]
    
    new_incident = Incident(**incident_dict)
    
    # Use model_dump() with datetime handling
    incident_data = new_incident.model_dump()
    # Convert datetime to ISO format string
    if 'last_updated' in incident_data and incident_data['last_updated']:
        incident_data['last_updated'] = incident_data['last_updated'].isoformat()
    
    await manager.broadcast({
        "type": "incident_update",
        "data": incident_data
    })

    return new_incident

def get_incidents(
    page: int = 1,
    per_page: int = 10,
    latest: bool = False,
    first_sort_key: Optional[str] = None,
    first_sort_order: Optional[str] = None,
    second_sort_key: Optional[str] = None,
    second_sort_order: Optional[str] = None,
    host_filter: Optional[str] = None,
    name_filter: Optional[str] = None,
    incident_filter: Optional[str] = None

) -> List[Incident]:
    collection = get_incidents_collection()
    skip = (page - 1) * per_page
    cursor = collection.find()

    # Создаем query для фильтрации
    query = {}
    
    if host_filter:
        query["host"] = {"$regex": f"^{host_filter}$", "$options": "i"}  # Точное совпадение с учетом регистра
    
    if name_filter:
        query["hostname"] = {"$regex": f"^{name_filter}$", "$options": "i"}
    
    if incident_filter:
        query["message"] = {"$regex": incident_filter, "$options": "i"}  # Частичное совпадение
    
    cursor = collection.find(query)

    # Сначала применяем сортировку (если есть)
    sort_spec = []
    
    if latest:
        sort_spec.append(("last_updated", DESCENDING))
    
    if first_sort_key and first_sort_order:
        order = ASCENDING if first_sort_order == 'asc' else DESCENDING
        sort_spec.append((first_sort_key, order))
    
    if second_sort_key and second_sort_order:
        order = ASCENDING if second_sort_order == 'asc' else DESCENDING
        sort_spec.append((second_sort_key, order))
    
    if sort_spec:
        cursor = cursor.sort(sort_spec)
    
    # Затем применяем пагинацию
    if not latest:
        cursor = cursor.skip(skip)
    cursor = cursor.limit(per_page)
    
    result = []
    for incident in cursor:
        incident_dict = dict(incident)
        if "_id" in incident_dict:
            incident_dict["id"] = str(incident_dict["_id"])
            del incident_dict["_id"]
        result.append(Incident(**incident_dict))
        
    return result

def get_total_incidents_count(
        host_filter: Optional[str] = None,
        name_filter: Optional[str] = None,
        incident_filter: Optional[str] = None
) -> int:
    collection = get_incidents_collection()
    query = {}
    
    if host_filter:
        query["host"] = {"$regex": f"^{host_filter}$", "$options": "i"}
    
    if name_filter:
        query["hostname"] = {"$regex": f"^{name_filter}$", "$options": "i"}
    
    if incident_filter:
        query["message"] = {"$regex": incident_filter, "$options": "i"}
                            
    return collection.count_documents(query)