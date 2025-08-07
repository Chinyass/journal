from fastapi import APIRouter, Query
from typing import Optional, Dict, Any
from app.services.event_service import EventRepository

event_repo = EventRepository()

router = APIRouter(prefix="/events", tags=["events"])

'''
@router.post("/", response_model=Incident)
async def create_incident(incident: Incident):
    return await upsert_incident(incident.model_dump())
'''

@router.get("/", response_model=list)
async def list_events(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, le=100)
):
    events = await event_repo.get_list()

    return events