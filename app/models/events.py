
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, List



# Модель для Event
class Event(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    messages: List[str]
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    class Config:
        allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "name": "Network Issue",
                "messages": [
                    "Port down",
                    "Interface flapping",
                    "Link degraded"
                ]
            }
        }