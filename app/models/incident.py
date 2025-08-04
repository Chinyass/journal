from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Incident(BaseModel):
    id: Optional[str] = None  # No longer needs alias
    host: str
    hostname: str
    message: str
    location: str
    count: int = 1
    last_updated: datetime = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "685e77b69c5841ca018a4bbb",
                "host": "server1",
                "hostname": "server1.example.com",
                "message": "CPU overload",
                "location": "DC1",
                "count": 3,
                "last_updated": "2023-01-01T00:00:00"
            }
        }