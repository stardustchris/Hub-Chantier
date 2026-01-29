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

# NE PAS importer router ici au top-level pour eviter de charger
# toute la chaine infrastructure (jose -> cryptography) quand seul
# le domain est necessaire (ex: tests unitaires).
# Le router est importe directement dans main.py via:
#   from modules.auth.infrastructure.web import router


def __getattr__(name):
    """Import paresseux pour eviter le chargement de l'infrastructure au top-level."""
    if name == "router":
        from .infrastructure.web import router
        return router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
