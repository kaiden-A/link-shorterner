from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from contextlib import asyncio
from sqlalchemy.orm import Session

from app.database import engine, get_db, Base
from app.models.links import Link
from app.routers import links as links_router


app = FastAPI(title="Link Shortener", version="0.1.0")

app.include_router(links_router.router, prefix="/api/v1/link-shorterner")


@app.get("/{slug}" , prefix="/api/v1/link-shorterner")
def redirect_to_destination(slug: str, db: Session = Depends(get_db)):
    """Look up a slug and redirect to the original URL."""
    link = db.query(Link).filter(Link.slug == slug).first()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Slug '{slug}' not found",
        )

    link.clicks += 1
    db.commit()

    return {
        "destination_url" : link.destination_url
    }
