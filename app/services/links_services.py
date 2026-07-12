from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import secrets
import string

from app.models.links import Link
from app.schemas.links import LinkCreate


class LinksServices:

    def __init__(self, db: Session):
        self.db = db

    def _generate_unique_slug(self, length: int = 6) -> str:
        """Generate a random unique slug."""
        characters = string.ascii_letters + string.digits

        while True:
            new_slug = "".join(secrets.choice(characters) for _ in range(length)).lower()
            slug_exists = self.db.query(Link).filter(Link.slug == new_slug).first()
            if not slug_exists:
                return new_slug

    def create_link(self, link_data: LinkCreate) -> Link:

        slug = self._generate_unique_slug()

        if slug:
            existing = self.db.query(Link).filter(Link.slug == slug).first()
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Slug '{slug}' already exists")
        

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

        link.clicks += 1
        self.db.commit()
        return link