from fastapi import APIRouter, Query
from typing import Optional, Dict, Any
from app.services.message_service import MessageRepository

message_repo = MessageRepository()

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/messages/stats/minute")
async def get_message_stats_by_minute(
    minutes_back: int = 60,
    event_id: Optional[str] = None
):
    repo = MessageRepository()
    data = await repo.get_messages_count_by_minute(minutes_back, event_id)
    return {"data": data}