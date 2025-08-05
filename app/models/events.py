
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, List
from app.models.messages import Message

class HostData(BaseModel):
    ip: Optional[str] = None
    hostname: Optional[str] = None
    role: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    services: List[str] = Field(default_factory=list)

# Модель для Event
class Event(HostData):
    id: Optional[str] = Field(None, alias="_id")
    name: Optional[str] = None

    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    status: bool = True

    class Config:
        allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "name": "Network Issue",
                "message_ids": ["607f1f77bcf86cd799439012"]
            }
        }

