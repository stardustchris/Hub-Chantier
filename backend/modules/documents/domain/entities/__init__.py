"""Entités du module Documents."""

from .document import Document, MAX_TAILLE_FICHIER, MAX_FICHIERS_UPLOAD
from .dossier import Dossier
from .autorisation import AutorisationDocument, TypeAutorisation

__all__ = [
    "Document",
    "Dossier",
    "AutorisationDocument",
    "TypeAutorisation",
    "MAX_TAILLE_FICHIER",
    "MAX_FICHIERS_UPLOAD",
]
