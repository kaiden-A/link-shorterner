from pydantic import BaseModel
from datetime import datetime


class ClickResponse(BaseModel):
    id: int
    link_slug: str
    timestamp: datetime
    referer: str | None
    source: str | None
    utm_source: str | None
    user_agent: str | None
    device_type: str | None
    browser: str | None
    os: str | None
    ip_address: str | None

    class Config:
        from_attributes = True


class LinkStats(BaseModel):
    total_clicks: int
    by_source: dict[str, int]