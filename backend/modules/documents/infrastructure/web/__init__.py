"""Web layer du module Documents."""

from .document_routes import router
from .dependencies import get_document_controller, get_current_user, get_file_storage

__all__ = [
    "router",
    "get_document_controller",
    "get_current_user",
    "get_file_storage",
]
