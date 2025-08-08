from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone


class Message(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    
    text: str
    event_id: Optional[str] = None

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