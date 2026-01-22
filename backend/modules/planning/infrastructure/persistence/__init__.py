"""Persistence du module Planning.

Ce module contient les implementations concretes de la persistence:
- Modeles SQLAlchemy
- Repository implementations
"""

from .affectation_model import AffectationModel, Base
from .sqlalchemy_affectation_repository import SQLAlchemyAffectationRepository

__all__ = [
    "AffectationModel",
    "Base",
    "SQLAlchemyAffectationRepository",
]
