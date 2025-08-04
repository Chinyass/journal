from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone



class Message(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    ip: Optional[str]
    name: Optional[str]
    role: Optional[str]
    model: Optional[str]
    location: Optional[str]
    services: List[str]
    text: str
