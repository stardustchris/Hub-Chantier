"""Web layer du module pointages - Routes FastAPI."""

from .routes import router
from .macro_paie_routes import router as macro_paie_router

__all__ = ["router", "macro_paie_router"]
