
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, List

# Модель для Event
class Event(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    message_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    class Config:
        allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "name": "Network Issue",
                "message_ids": ["607f1f77bcf86cd799439012"]
            }
        }