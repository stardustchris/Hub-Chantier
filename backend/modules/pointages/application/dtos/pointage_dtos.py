"""DTOs pour les pointages."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal


@dataclass
class CreatePointageDTO:
    """DTO pour la création d'un pointage."""

    utilisateur_id: int
    chantier_id: int
    date_pointage: date
    heures_normales: str  # Format HH:MM
    heures_supplementaires: str = "00:00"  # Format HH:MM
    commentaire: Optional[str] = None
    affectation_id: Optional[int] = None  # Lien planning (FDH-10)


@dataclass
class UpdatePointageDTO:
    """DTO pour la mise à jour d'un pointage."""

    pointage_id: int
    heures_normales: Optional[str] = None  # Format HH:MM
    heures_supplementaires: Optional[str] = None  # Format HH:MM
    commentaire: Optional[str] = None


@dataclass
class SignPointageDTO:
    """DTO pour la signature d'un pointage (FDH-12)."""

    pointage_id: int
    signature: str  # Signature électronique (base64 ou hash)


@dataclass
class ValidatePointageDTO:
    """DTO pour la validation d'un pointage."""

    pointage_id: int
    validateur_id: int


@dataclass
class RejectPointageDTO:
    """DTO pour le rejet d'un pointage."""

    pointage_id: int
    validateur_id: int
    motif: str


@dataclass
class BulkCreatePointageDTO:
    """DTO pour création en masse depuis le planning (FDH-10)."""

    utilisateur_id: int
    semaine_debut: date
    affectations: List["AffectationSourceDTO"]


@dataclass
class AffectationSourceDTO:
    """DTO représentant une affectation source pour création de pointage."""

    affectation_id: int
    chantier_id: int
    date_affectation: date
    heures_prevues: str  # Format HH:MM


@dataclass
class PointageDTO:
    """DTO de sortie pour un pointage."""

    id: int
    utilisateur_id: int
    chantier_id: int
    date_pointage: date
    heures_normales: str
    heures_supplementaires: str
    total_heures: str
    total_heures_decimal: float
    statut: str
    commentaire: Optional[str]
    signature_utilisateur: Optional[str]
    signature_date: Optional[datetime]
    validateur_id: Optional[int]
    validation_date: Optional[datetime]
    motif_rejet: Optional[str]
    affectation_id: Optional[int]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    # Données enrichies
    utilisateur_nom: Optional[str] = None
    chantier_nom: Optional[str] = None
    chantier_couleur: Optional[str] = None


@dataclass
class PointageListDTO:
    """DTO pour une liste paginée de pointages."""

    items: List[PointageDTO]
    total: int
    page: int
    page_size: int
    total_pages: int


@dataclass
class PointageSearchDTO:
    """DTO pour la recherche de pointages (FDH-04)."""

    utilisateur_id: Optional[int] = None
    chantier_id: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    page: int = 1
    page_size: int = 50


@dataclass
class CreateVariablePaieDTO:
    """DTO pour la création d'une variable de paie (FDH-13)."""

    pointage_id: int
    type_variable: str
    valeur: Decimal
    date_application: date
    commentaire: Optional[str] = None


@dataclass
class VariablePaieDTO:
    """DTO de sortie pour une variable de paie."""

    id: int
    pointage_id: int
    type_variable: str
    type_variable_libelle: str
    valeur: str  # Decimal sérialisé
    date_application: date
    commentaire: Optional[str]
    created_at: datetime
