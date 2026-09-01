from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.auth import require_role
from app.database import get_db
from app.schemas.links import LinkCreate, LinkResponse, LinkUpdate
from app.schemas.clicks import LinkStats
from app.services.links_services import LinksServices

router = APIRouter(prefix="/links", tags=["links"])

auth_dependency = Depends(require_role())


@router.post("/", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
def create_short_link(link_data: LinkCreate, db: Session = Depends(get_db)):
    service = LinksServices(db)
    return service.create_link(link_data)


@router.get("/", response_model=list[LinkResponse], dependencies=[auth_dependency])
def list_all_links(db: Session = Depends(get_db)):
    service = LinksServices(db)
    return service.list_links()


@router.get("/{slug}", response_model=LinkResponse, dependencies=[auth_dependency])
def get_link(slug: str, db: Session = Depends(get_db)):
    service = LinksServices(db)
    return service.get_by_slug(slug)


@router.patch("/{slug}", response_model=LinkResponse, dependencies=[auth_dependency])
def update_link(slug: str, link_data: LinkUpdate, db: Session = Depends(get_db)):
    service = LinksServices(db)
    return service.update_link(slug, link_data)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[auth_dependency])
def delete_link(slug: str, db: Session = Depends(get_db)):
    service = LinksServices(db)
    service.delete_link(slug)


@router.get("/{slug}/stats", response_model=LinkStats, dependencies=[auth_dependency])
def get_link_stats(
    slug: str,
    days: int | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    db: Session = Depends(get_db),
):
    service = LinksServices(db)
    return service.get_stats(slug, days=days, start=start, end=end)
