"""Web layer du module pointages - Routes FastAPI."""

from .routes import router
from .macro_paie_routes import router as macro_paie_router
from .paie_externe_routes import router as paie_externe_router

__all__ = ["router", "macro_paie_router", "paie_externe_router"]
