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
