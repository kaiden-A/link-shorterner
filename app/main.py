from fastapi import FastAPI

from app.database import engine, Base
from app.routers import links as links_router
from app.routers import redirect as redirect_router

app = FastAPI(title="Link Shortener", version="0.1.0")

# Mount both routers under the same prefix
app.include_router(links_router.router, prefix="/api/v1/link-shorterner")
app.include_router(redirect_router.router, prefix="/api/v1/link-shorterner")


@app.on_event("startup")
def on_startup():
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)