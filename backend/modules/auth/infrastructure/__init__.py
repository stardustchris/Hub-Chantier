"""Infrastructure Layer du module auth.

Ce module contient les implémentations techniques :
- Persistence (SQLAlchemy models et repositories)
- Web (routes FastAPI et dépendances)

RÈGLE : Cette couche dépend de toutes les autres.
"""

from .persistence import UserModel, Base, SQLAlchemyUserRepository

# NE PAS importer router ici pour eviter de charger jose/cryptography
# quand seul persistence est necessaire (ex: tests unitaires).
# Le router est importe directement via:
#   from modules.auth.infrastructure.web import router

__all__ = [
    "UserModel",
    "Base",
    "SQLAlchemyUserRepository",
]
