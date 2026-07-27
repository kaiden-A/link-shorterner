from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.links_services import LinksServices

router = APIRouter(tags=["redirect"])


@router.get("/r/{slug}")
def redirect_to_destination(
    slug: str,
    request: Request,
    referer: str | None = Query(default=None),
    utm_source: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = LinksServices(db)
    link = service.get_by_slug(slug)

    service.log_click(
        slug=slug,
        referer=referer,
        utm_source=utm_source,
        request=request,
    )

    return {
        "destination_url": link.destination_url,
    }