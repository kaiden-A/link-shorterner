from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.links import LinkCreate, LinkResponse
from app.services.links_services import LinksServices

router = APIRouter(prefix="/links", tags=["links"])


@router.post("/", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
def create_short_link(link_data: LinkCreate, db: Session = Depends(get_db)):
    service = LinksServices(db)
    return service.create_link(link_data)


@router.get("/", response_model=list[LinkResponse])
def list_all_links(db: Session = Depends(get_db)):
    service = LinksServices(db)
    return service.list_links()