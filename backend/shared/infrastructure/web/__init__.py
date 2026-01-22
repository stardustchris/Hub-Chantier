"""Infrastructure web partagée entre modules."""

from .dependencies import (
    get_current_user_id,
    get_current_user_role,
    get_is_moderator,
)

__all__ = [
    "get_current_user_id",
    "get_current_user_role",
    "get_is_moderator",
]
