"""Interfaces Repository du module Documents."""

from .document_repository import DocumentRepository
from .dossier_repository import DossierRepository
from .autorisation_repository import AutorisationRepository

__all__ = [
    "DocumentRepository",
    "DossierRepository",
    "AutorisationRepository",
]
