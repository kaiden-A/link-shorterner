from pydantic import BaseModel, HttpUrl

class LinkCreate(BaseModel):
    slug: str
    destination_url: HttpUrl

class LinkResponse(BaseModel):
    slug: str
    destination_url: str
    clicks: int

    class Config:
        from_attributes = True