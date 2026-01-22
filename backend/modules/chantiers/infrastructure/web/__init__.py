"""Web infrastructure du module Chantiers."""

from .chantier_routes import router
from .dependencies import get_chantier_controller, get_chantier_repository

__all__ = [
    "router",
    "get_chantier_controller",
    "get_chantier_repository",
]
