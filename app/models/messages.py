from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone


class Message(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    ip: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    services: List[str] = Field(default_factory=list)
    text: str

    class Config:
        allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "ip": "192.168.1.1",
                "name": "switch01",
                "role": "core",
                "model": "Cisco 3850",
                "location": "DC1-RackA",
                "services": ["IPTV", "INTERNET"],
                "text": "Interface Gig1/0/1 down"
            }
        }