"""Module Auth - Authentification et gestion des utilisateurs.

Ce module suit Clean Architecture avec 4 layers :
- domain/      : Entités, Value Objects, Interfaces (PURE)
- application/ : Use Cases, DTOs, Ports
- adapters/    : Controllers, Providers
- infrastructure/ : SQLAlchemy, FastAPI

Usage:
    from modules.auth.infrastructure.web import router
    app.include_router(router, prefix="/api")
"""

from .infrastructure.web import router

__all__ = ["router"]
