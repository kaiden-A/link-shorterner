from pydantic import BaseModel, HttpUrl
from datetime import datetime


class LinkCreate(BaseModel):
    destination_url: HttpUrl
    slug: str | None = None


class LinkUpdate(BaseModel):
    destination_url: HttpUrl | None = None
    slug: str | None = None

class LinkResponse(BaseModel):
    slug: str
    destination_url: str
    clicks: int
    created_at: datetime

    class Config:
        from_attributes = True