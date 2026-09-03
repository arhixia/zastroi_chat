from datetime import datetime
import uuid 

from pydantic import BaseModel

class WidgetMessageIn(BaseModel):
    site_id: uuid.UUID
    session_id: str
    visitor_id: str 
    message: str 
    current_page_url: str | None = None
    referrer: str | None = None
  
class WidgetMessageOut(BaseModel):
    conversation_id: uuid.UUID
    answer: str
    sources: list[str]


class LeadIn(BaseModel):
    site_id: str
    session_id: str
    name: str
    phone: str
    last_message: str | None = None

class LeadOut(BaseModel):
    id: uuid.UUID
    site_id: uuid.UUID
    site_name: str 
    name: str
    phone: str
    interest: dict
    created_at: datetime
    
    class Config:
        from_attributes = True
    