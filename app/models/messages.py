from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId

class Message(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    
    text: str
    event_id: Optional[str] = None

    @field_validator('id', 'event_id', mode='before')
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
    
    
    class Config:
        allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "text": "Interface Gig1/0/1 down"
            }
        }

class RawMessage(BaseModel):
    ip: str
    text: str

# Модель для ответа
class MessageCountResponse(BaseModel):
    timestamp: datetime
    count: int