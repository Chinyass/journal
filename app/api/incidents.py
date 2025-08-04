from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any, List
from app.services.incident_service import upsert_incident, get_incidents, get_total_incidents_count
from app.models.incident import Incident


router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.post("/", response_model=Incident)
async def create_incident(incident: Incident):
    return await upsert_incident(incident.model_dump())
   

@router.get("/", response_model=Dict[str, Any])
async def list_incidents(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, le=100),
    latest: Optional[bool] = False,
    first_sort_key: Optional[str] = Query(None),
    first_sort_order: Optional[str] = Query(None),
    second_sort_key: Optional[str] = Query(None),
    second_sort_order: Optional[str] = Query(None),
    host_search: Optional[str] = Query(None),
    name_search: Optional[str] = Query(None),
    incident_search: Optional[str] = Query(None)
):
    incidents = get_incidents(
        page=page,
        per_page=per_page,
        latest=latest,
        first_sort_key=first_sort_key,
        first_sort_order=first_sort_order,
        second_sort_key=second_sort_key,
        second_sort_order=second_sort_order,
        host_filter=host_search,
        name_filter=name_search,
        incident_filter=incident_search
    )
    
    total = get_total_incidents_count(
        host_filter=host_search,
        name_filter=name_search,
        incident_filter=incident_search
    )
    
    return {
        "items": incidents,
        "total": total
    }