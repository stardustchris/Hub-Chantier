"""DTOs du module Formulaires."""

from .template_dto import (
    TemplateFormulaireDTO,
    ChampTemplateDTO,
    CreateTemplateDTO,
    UpdateTemplateDTO,
)
from .formulaire_dto import (
    FormulaireRempliDTO,
    ChampRempliDTO,
    PhotoFormulaireDTO,
    CreateFormulaireDTO,
    UpdateFormulaireDTO,
    SubmitFormulaireDTO,
)

__all__ = [
    # Template DTOs
    "TemplateFormulaireDTO",
    "ChampTemplateDTO",
    "CreateTemplateDTO",
    "UpdateTemplateDTO",
    # Formulaire DTOs
    "FormulaireRempliDTO",
    "ChampRempliDTO",
    "PhotoFormulaireDTO",
    "CreateFormulaireDTO",
    "UpdateFormulaireDTO",
    "SubmitFormulaireDTO",
]
