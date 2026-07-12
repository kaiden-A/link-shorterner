from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.links import Link
from app.schemas.links import LinkCreate, LinkResponse

router = APIRouter(prefix="/links", tags=["links"])


@router.post("/", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
def create_short_link(link_data: LinkCreate, db: Session = Depends(get_db)):
    existing = db.query(Link).filter(Link.slug == link_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Slug '{link_data.slug}' already exists",
        )
    link = Link(slug=link_data.slug, destination_url=str(link_data.destination_url))
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.get("/", response_model=list[LinkResponse])
def list_all_links(db: Session = Depends(get_db)):
    links = db.query(Link).all()
    return links
