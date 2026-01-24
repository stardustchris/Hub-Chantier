"""Infrastructure web partagée entre modules."""

from .dependencies import (
    get_current_user_id,
    get_current_user_role,
    get_is_moderator,
    require_admin,
    require_conducteur_or_admin,
    require_chef_or_above,
    get_current_user_chantier_ids,
)

__all__ = [
    "get_current_user_id",
    "get_current_user_role",
    "get_is_moderator",
    "require_admin",
    "require_conducteur_or_admin",
    "require_chef_or_above",
    "get_current_user_chantier_ids",
]
