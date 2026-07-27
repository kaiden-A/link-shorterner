from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.requests import Request
import secrets
import string

from app.models.links import Link
from app.models.clicks import Click
from app.schemas.links import LinkCreate
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

    def get_stats(self, slug: str) -> dict:
        link = self.db.query(Link).filter(Link.slug == slug).first()
        if not link:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Slug '{slug}' not found")

        clicks = self.db.query(Click).filter(Click.link_slug == slug).all()
        total = len(clicks)

        by_source: dict[str, int] = {}
        for click in clicks:
            key = click.source or "direct"
            by_source[key] = by_source.get(key, 0) + 1

        return {"total_clicks": total, "by_source": by_source}