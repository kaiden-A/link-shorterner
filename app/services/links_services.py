from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.requests import Request
from sqlalchemy import func
import secrets
import string
from datetime import datetime, timedelta, timezone

from app.models.links import Link
from app.models.clicks import Click
from app.schemas.links import LinkCreate, LinkUpdate
from app.services.classifier import classify_source, parse_user_agent


class LinksServices:

    def __init__(self, db: Session):
        self.db = db

    def _generate_unique_slug(self, length: int = 6) -> str:
        characters = string.ascii_letters + string.digits

        while True:
            new_slug = "".join(secrets.choice(characters) for _ in range(length)).lower()
            slug_exists = self.db.query(Link).filter(Link.slug == new_slug).first()
            if not slug_exists:
                return new_slug

    def create_link(self, link_data: LinkCreate) -> Link:

        slug = link_data.slug

        if slug:
            existing = self.db.query(Link).filter(Link.slug == slug).first()
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Slug '{slug}' already exists")
        else:
            slug = self._generate_unique_slug()

        link = Link(slug=slug, destination_url=str(link_data.destination_url))

        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)

        return link

    def list_links(self) -> list[Link]:
        return self.db.query(Link).all()

    def update_link(self, slug: str, link_data: LinkUpdate) -> Link:
        link = self.get_by_slug(slug)
        old_slug = link.slug

        new_slug = link_data.slug or link.slug

        if new_slug != old_slug:
            existing = self.db.query(Link).filter(Link.slug == new_slug).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Slug '{new_slug}' already exists",
                )

            link.slug = new_slug
            self.db.flush()
            self.db.query(Click).filter(Click.link_slug == old_slug).update(
                {Click.link_slug: new_slug}
            )

        if link_data.destination_url is not None:
            link.destination_url = str(link_data.destination_url)

        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link

    def delete_link(self, slug: str) -> None:
        link = self.get_by_slug(slug)

        self.db.query(Click).filter(Click.link_slug == slug).delete()
        self.db.delete(link)
        self.db.commit()

    def get_by_slug(self, slug: str) -> Link:
        link = self.db.query(Link).filter(Link.slug == slug).first()
        if not link:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Slug '{slug}' not found")
        return link

    def log_click(
        self,
        slug: str,
        referer: str | None = None,
        utm_source: str | None = None,
        request: Request | None = None,
    ) -> Click:
        source = classify_source(referer, utm_source)

        ip_address = None
        user_agent = None
        device_type = None
        browser = None
        os = None

        if request:
            user_agent = request.headers.get("user-agent")
            ip_address = request.client.host if request.client else None
            forwarded = request.headers.get("x-forwarded-for")
            if forwarded:
                ip_address = forwarded.split(",")[0].strip()
            device_type, browser, os = parse_user_agent(user_agent)

        click = Click(
            link_slug=slug,
            referer=referer,
            source=source,
            utm_source=utm_source,
            user_agent=user_agent,
            device_type=device_type,
            browser=browser,
            os=os,
            ip_address=ip_address,
        )

        link = self.db.query(Link).filter(Link.slug == slug).first()
        if link:
            link.clicks += 1

        self.db.add(click)
        self.db.commit()
        self.db.refresh(click)
        return click

    def get_stats(
        self,
        slug: str,
        days: int | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> dict:
        link = self.db.query(Link).filter(Link.slug == slug).first()
        if not link:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Slug '{slug}' not found")

        query = self.db.query(Click).filter(Click.link_slug == slug)
        if start:
            query = query.filter(Click.timestamp >= start)
        if end:
            query = query.filter(Click.timestamp <= end)
        elif start is None and days is not None:
            cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
            query = query.filter(Click.timestamp >= cutoff)

        total = query.count()

        def counts_by(field, none_label: str) -> dict[str, int]:
            rows = query.with_entities(field, func.count()).group_by(field).all()
            return {str(key) if key is not None else none_label: count for key, count in rows}

        day = func.date_trunc("day", Click.timestamp)
        daily_rows = (
            query.with_entities(day, func.count())
            .group_by(day)
            .order_by(day)
            .all()
        )
        daily_clicks = [
            {"date": day_value.date().isoformat(), "clicks": count}
            for day_value, count in daily_rows
        ]

        return {
            "total_clicks": total,
            "by_source": counts_by(Click.source, "direct"),
            "by_device": counts_by(Click.device_type, "unknown"),
            "by_browser": counts_by(Click.browser, "unknown"),
            "by_os": counts_by(Click.os, "unknown"),
            "daily_clicks": daily_clicks,
        }