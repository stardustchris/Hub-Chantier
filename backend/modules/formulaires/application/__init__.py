"""Application layer du module Formulaires."""

from .use_cases import (
    CreateTemplateUseCase,
    UpdateTemplateUseCase,
    DeleteTemplateUseCase,
    GetTemplateUseCase,
    ListTemplatesUseCase,
    CreateFormulaireUseCase,
    UpdateFormulaireUseCase,
    SubmitFormulaireUseCase,
    GetFormulaireUseCase,
    ListFormulairesUseCase,
    GetFormulaireHistoryUseCase,
    ExportFormulairePDFUseCase,
)
from .dtos import (
    TemplateFormulaireDTO,
    ChampTemplateDTO,
    CreateTemplateDTO,
    UpdateTemplateDTO,
    FormulaireRempliDTO,
    ChampRempliDTO,
    PhotoFormulaireDTO,
    CreateFormulaireDTO,
    UpdateFormulaireDTO,
    SubmitFormulaireDTO,
)

__all__ = [
    # Use Cases
    "CreateTemplateUseCase",
    "UpdateTemplateUseCase",
    "DeleteTemplateUseCase",
    "GetTemplateUseCase",
    "ListTemplatesUseCase",
    "CreateFormulaireUseCase",
    "UpdateFormulaireUseCase",
    "SubmitFormulaireUseCase",
    "GetFormulaireUseCase",
    "ListFormulairesUseCase",
    "GetFormulaireHistoryUseCase",
    "ExportFormulairePDFUseCase",
    # DTOs
    "TemplateFormulaireDTO",
    "ChampTemplateDTO",
    "CreateTemplateDTO",
    "UpdateTemplateDTO",
    "FormulaireRempliDTO",
    "ChampRempliDTO",
    "PhotoFormulaireDTO",
    "CreateFormulaireDTO",
    "UpdateFormulaireDTO",
    "SubmitFormulaireDTO",
]
