from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime, timezone
from app.database import Base

class Link(Base):
    __tablename__ = "links"

    slug = Column(String, primary_key=True, index=True)
    destination_url = Column(String, nullable=False)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))