"""Domain layer du module Formulaires."""

from .entities import (
    TemplateFormulaire,
    ChampTemplate,
    FormulaireRempli,
    ChampRempli,
    PhotoFormulaire,
)
from .value_objects import (
    TypeChamp,
    StatutFormulaire,
    CategorieFormulaire,
)
from .repositories import (
    TemplateFormulaireRepository,
    FormulaireRempliRepository,
)
from .events import (
    TemplateCreatedEvent,
    TemplateUpdatedEvent,
    TemplateDeletedEvent,
    FormulaireCreatedEvent,
    FormulaireSubmittedEvent,
    FormulaireValidatedEvent,
    FormulaireSignedEvent,
)

__all__ = [
    # Entities
    "TemplateFormulaire",
    "ChampTemplate",
    "FormulaireRempli",
    "ChampRempli",
    "PhotoFormulaire",
    # Value Objects
    "TypeChamp",
    "StatutFormulaire",
    "CategorieFormulaire",
    # Repositories
    "TemplateFormulaireRepository",
    "FormulaireRempliRepository",
    # Events
    "TemplateCreatedEvent",
    "TemplateUpdatedEvent",
    "TemplateDeletedEvent",
    "FormulaireCreatedEvent",
    "FormulaireSubmittedEvent",
    "FormulaireValidatedEvent",
    "FormulaireSignedEvent",
]
