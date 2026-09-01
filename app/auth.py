import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from functools import lru_cache
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError, PyJWKClientError

from app.config import settings

_PROJECT_ROLES_CLAIM = "urn:zitadel:iam:org:project:roles"
_PROJECT_ROLES_CLAIM_PREFIX = "urn:zitadel:iam:org:project:"


@lru_cache(maxsize=1)
def _get_jwks_client() -> PyJWKClient:
    return PyJWKClient(settings.ZITADEL_JWKS_URI, cache_keys=True)


bearer_scheme = HTTPBearer(auto_error=False)


def verify_token(token: str) -> dict:
    try:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.ZITADEL_ISSUER,
            audience=settings.ZITADEL_AUDIENCE,
        )
    except (InvalidTokenError, PyJWKClientError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def _claim_role_keys(raw) -> list[str]:
    if isinstance(raw, dict):
        return [key for key in raw.keys() if isinstance(key, str) and key]
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, str) and item]
    if isinstance(raw, str):
        return [raw]
    return []


def extract_roles(claims: dict) -> set[str]:
    roles: set[str] = set()

    for key in claims:
        if not isinstance(key, str):
            continue
        if key == _PROJECT_ROLES_CLAIM or key.startswith(_PROJECT_ROLES_CLAIM_PREFIX):
            roles.update(_claim_role_keys(claims[key]))

    return roles


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return verify_token(credentials.credentials)


def require_role():
    required_roles = set(settings.ZITADEL_REQUIRED_ROLE)

    def dependency(claims: dict = Depends(get_current_user)) -> dict:
        if required_roles and not required_roles.issubset(extract_roles(claims)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role(s): {', '.join(sorted(required_roles))}",
            )
        return claims

    return dependency
