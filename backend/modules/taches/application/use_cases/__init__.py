"""Use Cases du module Taches."""

# Tache Use Cases
from .create_tache import CreateTacheUseCase, TacheAlreadyExistsError
from .update_tache import UpdateTacheUseCase
from .delete_tache import DeleteTacheUseCase
from .get_tache import GetTacheUseCase, TacheNotFoundError
from .list_taches import ListTachesUseCase
from .complete_tache import CompleteTacheUseCase
from .reorder_taches import ReorderTachesUseCase

# Template Use Cases
from .create_template import CreateTemplateUseCase, TemplateAlreadyExistsError
from .list_templates import ListTemplatesUseCase
from .import_template import ImportTemplateUseCase, TemplateNotFoundError

# Feuille Tache Use Cases
from .create_feuille_tache import CreateFeuilleTacheUseCase, FeuilleTacheAlreadyExistsError
from .validate_feuille_tache import ValidateFeuilleTacheUseCase, FeuilleTacheNotFoundError
from .list_feuilles_taches import ListFeuillesTachesUseCase

# Stats
from .get_tache_stats import GetTacheStatsUseCase

# Export PDF
from .export_pdf import ExportTachesPDFUseCase

__all__ = [
    # Tache Use Cases
    "CreateTacheUseCase",
    "UpdateTacheUseCase",
    "DeleteTacheUseCase",
    "GetTacheUseCase",
    "ListTachesUseCase",
    "CompleteTacheUseCase",
    "ReorderTachesUseCase",
    # Template Use Cases
    "CreateTemplateUseCase",
    "ListTemplatesUseCase",
    "ImportTemplateUseCase",
    # Feuille Tache Use Cases
    "CreateFeuilleTacheUseCase",
    "ValidateFeuilleTacheUseCase",
    "ListFeuillesTachesUseCase",
    # Stats
    "GetTacheStatsUseCase",
    # Export PDF
    "ExportTachesPDFUseCase",
    # Errors
    "TacheNotFoundError",
    "TacheAlreadyExistsError",
    "TemplateNotFoundError",
    "TemplateAlreadyExistsError",
    "FeuilleTacheNotFoundError",
    "FeuilleTacheAlreadyExistsError",
]
