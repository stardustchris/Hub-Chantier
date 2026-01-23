"""DTOs pour les dossiers."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class DossierDTO:
    """DTO représentant un dossier."""

    id: int
    chantier_id: int
    nom: str
    type_dossier: str
    niveau_acces: str
    parent_id: Optional[int]
    ordre: int
    chemin_complet: str
    nombre_documents: int
    nombre_sous_dossiers: int
    created_at: datetime


@dataclass
class DossierCreateDTO:
    """DTO pour la création d'un dossier."""

    chantier_id: int
    nom: str
    type_dossier: str = "custom"
    niveau_acces: str = "compagnon"
    parent_id: Optional[int] = None


@dataclass
class DossierUpdateDTO:
    """DTO pour la mise à jour d'un dossier."""

    nom: Optional[str] = None
    niveau_acces: Optional[str] = None
    parent_id: Optional[int] = None


@dataclass
class DossierTreeDTO:
    """DTO représentant un dossier avec ses enfants (arborescence)."""

    id: int
    chantier_id: int
    nom: str
    type_dossier: str
    niveau_acces: str
    parent_id: Optional[int]
    ordre: int
    chemin_complet: str
    nombre_documents: int
    children: List["DossierTreeDTO"]


@dataclass
class ArborescenceDTO:
    """DTO pour l'arborescence complète d'un chantier."""

    chantier_id: int
    dossiers: List[DossierTreeDTO]
    total_documents: int
    total_taille: int
