from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Any
from app.services.message_service import MessageRepository
from datetime import datetime
from app.models.messages import MessageCountResponse

message_repo = MessageRepository()

router = APIRouter(prefix="/messages", tags=["events"])

@router.get("/", response_model=dict)
async def list_messages(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, le=100),
    status: Optional[bool] = None,
):
    total = await message_repo.get_count(status=status)
    events = await message_repo.get_list(
        skip=(page - 1) * per_page,
        limit=per_page,
        status=status,
    )
    
    return {
        "items": events,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

@router.get("/count-by-time/", response_model=List[MessageCountResponse])
async def get_messages_count_by_time(
    time_range: str = Query("1d", description="Time range (e.g. '1h', '2h', '1d')"),
    interval: str = Query("5m", description="Grouping interval (e.g. '1m', '5m', '15m')"),
    start_time: Optional[datetime] = Query(None, description="Custom start time"),
    end_time: Optional[datetime] = Query(None, description="Custom end time (default now)"),
    service: Optional[str] = Query(None, description="Service filter")
):
    """
    Get message counts grouped by time intervals.
    
    Examples:
    - Last 2 hours with 3-minute intervals: /count-by-time/?time_range=2h&interval=3m
    - Today with 5-minute intervals: /count-by-time/?time_range=1d&interval=5m
    - Custom range: /count-by-time/?start_time=2023-01-01T00:00:00&end_time=2023-01-02T00:00:00&interval=15m
    """
    try:
        results = await message_repo.get_messages_count_by_time(
            time_range=time_range,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            service=service
        )
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")