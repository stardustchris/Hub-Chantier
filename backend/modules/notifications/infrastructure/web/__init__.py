"""Web layer du module notifications."""

from .routes import router
from .sse import router as sse_router

__all__ = ["router", "sse_router"]
