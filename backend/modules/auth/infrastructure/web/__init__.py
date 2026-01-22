"""Web (routes FastAPI) du module auth."""

from .auth_routes import router, users_router
from .dependencies import (
    get_auth_controller,
    get_current_user_id,
    get_token_service,
    get_user_repository,
)

__all__ = [
    "router",
    "users_router",
    "get_auth_controller",
    "get_current_user_id",
    "get_token_service",
    "get_user_repository",
]
