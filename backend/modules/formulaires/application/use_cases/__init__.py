"""Use Cases du module Formulaires."""

from .create_template import CreateTemplateUseCase
from .update_template import UpdateTemplateUseCase
from .delete_template import DeleteTemplateUseCase
from .get_template import GetTemplateUseCase
from .list_templates import ListTemplatesUseCase
from .create_formulaire import CreateFormulaireUseCase
from .update_formulaire import UpdateFormulaireUseCase
from .submit_formulaire import SubmitFormulaireUseCase
from .get_formulaire import GetFormulaireUseCase
from .list_formulaires import ListFormulairesUseCase
from .get_formulaire_history import GetFormulaireHistoryUseCase
from .export_pdf import ExportFormulairePDFUseCase

__all__ = [
    # Template Use Cases
    "CreateTemplateUseCase",
    "UpdateTemplateUseCase",
    "DeleteTemplateUseCase",
    "GetTemplateUseCase",
    "ListTemplatesUseCase",
    # Formulaire Use Cases
    "CreateFormulaireUseCase",
    "UpdateFormulaireUseCase",
    "SubmitFormulaireUseCase",
    "GetFormulaireUseCase",
    "ListFormulairesUseCase",
    "GetFormulaireHistoryUseCase",
    "ExportFormulairePDFUseCase",
]
