from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.links_services import LinksServices

router = APIRouter(tags=["redirect"])


@router.get("/{slug}")
def redirect_to_destination(slug: str, db: Session = Depends(get_db)):
    """Look up a slug, increment clicks, and redirect to the original URL."""
    service = LinksServices(db)
    link = service.get_by_slug(slug)
        
    return {
        "destination_url" : link.destination_url
    }