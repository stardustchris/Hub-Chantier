"""Events du module Documents."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class DocumentEvent:
    """Classe de base pour les événements document."""

    document_id: int
    chantier_id: int
    timestamp: datetime


@dataclass(frozen=True)
class DocumentUploaded(DocumentEvent):
    """Événement émis lors de l'upload d'un document."""

    nom: str
    dossier_id: int
    uploaded_by: int
    taille: int


@dataclass(frozen=True)
class DocumentDeleted(DocumentEvent):
    """Événement émis lors de la suppression d'un document."""

    nom: str
    deleted_by: int


@dataclass(frozen=True)
class DocumentMoved(DocumentEvent):
    """Événement émis lors du déplacement d'un document."""

    ancien_dossier_id: int
    nouveau_dossier_id: int
    moved_by: int


@dataclass(frozen=True)
class DocumentRenamed(DocumentEvent):
    """Événement émis lors du renommage d'un document."""

    ancien_nom: str
    nouveau_nom: str
    renamed_by: int


@dataclass(frozen=True)
class DossierEvent:
    """Classe de base pour les événements dossier."""

    dossier_id: int
    chantier_id: int
    timestamp: datetime


@dataclass(frozen=True)
class DossierCreated(DossierEvent):
    """Événement émis lors de la création d'un dossier."""

    nom: str
    parent_id: Optional[int]
    created_by: int


@dataclass(frozen=True)
class DossierDeleted(DossierEvent):
    """Événement émis lors de la suppression d'un dossier."""

    nom: str
    deleted_by: int


@dataclass(frozen=True)
class AutorisationEvent:
    """Classe de base pour les événements autorisation."""

    autorisation_id: int
    timestamp: datetime


@dataclass(frozen=True)
class AutorisationAccordee(AutorisationEvent):
    """Événement émis lors de l'accord d'une autorisation."""

    user_id: int
    cible_type: str  # "dossier" ou "document"
    cible_id: int
    accorde_par: int


@dataclass(frozen=True)
class AutorisationRevoquee(AutorisationEvent):
    """Événement émis lors de la révocation d'une autorisation."""

    user_id: int
    cible_type: str
    cible_id: int
    revoque_par: int
