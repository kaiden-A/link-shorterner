from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):

    DATABASE_URL: str
    ZITADEL_ISSUER: str
    ZITADEL_JWKS_URI: str
    ZITADEL_AUDIENCE: str
    ZITADEL_REQUIRED_ROLE: Annotated[list[str], NoDecode] = ["member"]

    @field_validator("ZITADEL_REQUIRED_ROLE", mode="before")
    @classmethod
    def _parse_roles(cls, value):
        if isinstance(value, list):
            return value

        cleaned = value.strip()
        if cleaned.startswith("[") and cleaned.endswith("]"):
            cleaned = cleaned[1:-1]

        return [
            part.strip().strip('"').strip("'")
            for part in cleaned.split(",")
            if part.strip()
        ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf8",
        extra="ignore"
    )

settings = Settings()
