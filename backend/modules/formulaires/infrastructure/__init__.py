"""Infrastructure layer du module Formulaires."""

from .persistence import (
    TemplateFormulaireModel,
    ChampTemplateModel,
    FormulaireRempliModel,
    ChampRempliModel,
    PhotoFormulaireModel,
    SQLAlchemyTemplateFormulaireRepository,
    SQLAlchemyFormulaireRempliRepository,
)
from .web import router, templates_router

__all__ = [
    # Models
    "TemplateFormulaireModel",
    "ChampTemplateModel",
    "FormulaireRempliModel",
    "ChampRempliModel",
    "PhotoFormulaireModel",
    # Repositories
    "SQLAlchemyTemplateFormulaireRepository",
    "SQLAlchemyFormulaireRempliRepository",
    # Routers
    "router",
    "templates_router",
]
