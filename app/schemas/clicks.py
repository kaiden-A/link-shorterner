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


class DailyClicks(BaseModel):
    date: str
    clicks: int


class LinkStats(BaseModel):
    total_clicks: int
    by_source: dict[str, int]
    by_device: dict[str, int]
    by_browser: dict[str, int]
    by_os: dict[str, int]
    daily_clicks: list[DailyClicks]