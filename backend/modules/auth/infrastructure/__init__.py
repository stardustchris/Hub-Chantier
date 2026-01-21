"""Infrastructure Layer du module auth.

Ce module contient les implémentations techniques :
- Persistence (SQLAlchemy models et repositories)
- Web (routes FastAPI et dépendances)

RÈGLE : Cette couche dépend de toutes les autres.
"""

from .persistence import UserModel, Base, SQLAlchemyUserRepository
from .web import router

__all__ = [
    "UserModel",
    "Base",
    "SQLAlchemyUserRepository",
    "router",
]
