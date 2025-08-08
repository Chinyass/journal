
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: bool = True
    count_message: int = 1

    @field_validator('id', mode='before')
    def validate_id(cls, v):
        if v is None:
            return None
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, dict):  # Обработка случая, когда приходит словарь
            if '_id' in v:
                return str(v['_id'])
            return str(v.get('id'))
        return str(v)
    
