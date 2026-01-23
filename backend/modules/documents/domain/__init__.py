"""Domain layer du module Documents.

Ce module contient la logique métier pure sans dépendances externes.
"""

from .entities import Document, Dossier, AutorisationDocument, TypeAutorisation
from .value_objects import NiveauAcces, TypeDocument, DossierType
from .repositories import DocumentRepository, DossierRepository, AutorisationRepository
from .services import FileStorageService

__all__ = [
    # Entities
    "Document",
    "Dossier",
    "AutorisationDocument",
    "TypeAutorisation",
    # Value Objects
    "NiveauAcces",
    "TypeDocument",
    "DossierType",
    # Repositories
    "DocumentRepository",
    "DossierRepository",
    "AutorisationRepository",
    # Services
    "FileStorageService",
]
