from fastapi import FastAPI

from app.routers import links as links_router
from app.routers import redirect as redirect_router

app = FastAPI(title="Link Shortener", version="0.1.0", docs_url="/api/v1/link-shorterner/docs", openapi_url="/api/v1/link-shorterner/openapi.json")

# Mount both routers under the same prefix
app.include_router(links_router.router, prefix="/api/v1/link-shorterner")
app.include_router(redirect_router.router, prefix="/api/v1/link-shorterner")


