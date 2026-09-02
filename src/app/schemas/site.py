import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    filename: str
    file_type: str 
    status: str
    uploaded_at: datetime

class SiteCreate(BaseModel):
    name: str
    domain: str
    allowed_origins: list[str] = []
    crawl_start_urls: list[str] = []
    crawl_excluded_urls: list[str] = []
    widget_logo_url: str | None = None
    widget_primary_color: str = "#2563eb"
    widget_bot_name: str = "Помощник"
    widget_welcome_message: str = "Здравствуйте! Чем могу помочь?"

class SiteUpdate(BaseModel):
    name: str | None = None
    domain: str | None = None
    allowed_origins: list[str] | None = None
    crawl_start_urls: list[str] | None = None
    crawl_excluded_urls: list[str] | None = None
    widget_logo_url: str | None = None
    widget_primary_color: str | None = None
    widget_bot_name: str | None = None
    widget_welcome_message: str | None = None
    is_active: bool | None = None

class SiteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    domain: str
    allowed_origins: list[str]
    crawl_start_urls: list[str]
    crawl_excluded_urls: list[str]
    widget_logo_url: str | None
    widget_primary_color: str
    widget_bot_name: str
    widget_welcome_message: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    documents: list[DocumentOut] = [] 


class WidgetSnippetOut(BaseModel):
    site_id: uuid.UUID
    snippet: str