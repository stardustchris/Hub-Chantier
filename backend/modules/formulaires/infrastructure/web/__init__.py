"""Web layer du module Formulaires."""

from .formulaire_routes import router, templates_router
from .dependencies import get_formulaire_controller, get_current_user_id

__all__ = [
    "router",
    "templates_router",
    "get_formulaire_controller",
    "get_current_user_id",
]
