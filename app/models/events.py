
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional, List
from app.models.messages import Message
from bson import ObjectId


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
    message_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    status: bool = True

    @field_validator('id', mode='before')
    def validate_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
