"""Web Layer du module Signalements."""

from .signalement_routes import router
from .dependencies import get_signalement_controller, get_current_user

__all__ = ["router", "get_signalement_controller", "get_current_user"]
