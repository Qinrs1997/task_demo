from fastapi import Header

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError


async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Simple API key check for this interview demo."""
    if x_api_key != get_settings().API_KEY:
        raise AuthenticationError("Invalid or missing API key")
