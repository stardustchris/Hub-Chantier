"""DTOs pour les documents."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class DocumentDTO:
    """DTO représentant un document."""

    id: int
    chantier_id: int
    dossier_id: int
    nom: str
    nom_original: str
    type_document: str
    taille: int
    taille_formatee: str
    mime_type: str
    uploaded_by: int
    uploaded_by_nom: Optional[str]
    uploaded_at: datetime
    description: Optional[str]
    version: int
    icone: str
    extension: str
    niveau_acces: Optional[str]


@dataclass
class DocumentCreateDTO:
    """DTO pour la création d'un document."""

    chantier_id: int
    dossier_id: int
    nom: str
    nom_original: str
    taille: int
    mime_type: str
    chemin_stockage: str
    uploaded_by: int
    description: Optional[str] = None
    niveau_acces: Optional[str] = None


@dataclass
class DocumentUpdateDTO:
    """DTO pour la mise à jour d'un document."""

    nom: Optional[str] = None
    description: Optional[str] = None
    dossier_id: Optional[int] = None
    niveau_acces: Optional[str] = None


@dataclass
class DocumentListDTO:
    """DTO pour la liste de documents avec pagination."""

    documents: List[DocumentDTO]
    total: int
    skip: int
    limit: int


@dataclass
class DocumentSearchDTO:
    """DTO pour la recherche de documents."""

    chantier_id: int
    query: Optional[str] = None
    type_document: Optional[str] = None
    dossier_id: Optional[int] = None
    skip: int = 0
    limit: int = 100
