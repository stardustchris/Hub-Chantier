"""Infrastructure web du module Shared."""

from .audit_routes import router as audit_router
from .dependencies import get_audit_service

__all__ = ["audit_router", "get_audit_service"]
