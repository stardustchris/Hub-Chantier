"""DTOs pour l'export des feuilles d'heures."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class FormatExport(Enum):
    """Formats d'export disponibles (FDH-03, FDH-17)."""

    CSV = "csv"
    XLSX = "xlsx"
    PDF = "pdf"
    ERP = "erp"  # Export vers ERP (Costructor, Graneet)


@dataclass
class ExportFeuilleHeuresDTO:
    """DTO pour la demande d'export."""

    format_export: FormatExport
    date_debut: date
    date_fin: date
    utilisateur_ids: Optional[List[int]] = None  # None = tous
    chantier_ids: Optional[List[int]] = None  # None = tous
    inclure_variables_paie: bool = True
    inclure_signatures: bool = False
    destination_erp: Optional[str] = None  # Pour export ERP


@dataclass
class ExportResultDTO:
    """DTO pour le résultat d'un export."""

    success: bool
    format_export: str
    filename: Optional[str] = None
    file_path: Optional[str] = None
    file_content: Optional[bytes] = None
    error_message: Optional[str] = None
    exported_at: datetime = field(default_factory=datetime.now)
    records_count: int = 0


@dataclass
class FeuilleRouteDTO:
    """DTO pour une feuille de route PDF (FDH-19)."""

    utilisateur_id: int
    utilisateur_nom: str
    semaine: str
    chantiers: List["ChantierRouteDTO"]
    total_heures: str
    signature: Optional[str] = None
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ChantierRouteDTO:
    """DTO pour un chantier dans la feuille de route."""

    chantier_id: int
    chantier_nom: str
    adresse: Optional[str]
    jours: List[str]  # Liste des jours travaillés
    heures_par_jour: dict  # {"lundi": "08:00", ...}
    total_heures: str


@dataclass
class ImportERPDTO:
    """DTO pour l'import depuis ERP (FDH-16)."""

    source_erp: str  # "costructor", "graneet"
    date_debut: date
    date_fin: date
    donnees: List["DonneeERPDTO"]


@dataclass
class DonneeERPDTO:
    """DTO pour une donnée importée de l'ERP."""

    code_utilisateur: str
    code_chantier: str
    date_pointage: date
    heures: str
    type_heures: str  # "normal", "supplementaire"
    variables_paie: Optional[dict] = None


@dataclass
class ImportResultDTO:
    """DTO pour le résultat d'un import ERP."""

    success: bool
    source_erp: str
    records_imported: int
    records_skipped: int
    records_errors: int
    error_details: List[str] = field(default_factory=list)
    imported_at: datetime = field(default_factory=datetime.now)


@dataclass
class MacroPaieDTO:
    """DTO pour une macro de paie (FDH-18)."""

    id: int
    nom: str
    description: str
    formule: str  # Expression de calcul
    variables_requises: List[str]
    active: bool


@dataclass
class CalculMacroPaieDTO:
    """DTO pour le calcul d'une macro de paie."""

    macro_id: int
    utilisateur_id: int
    date_debut: date
    date_fin: date


@dataclass
class ResultatMacroPaieDTO:
    """DTO pour le résultat d'un calcul de macro."""

    macro_nom: str
    utilisateur_id: int
    periode: str
    resultat: str  # Valeur calculée
    details: dict  # Détails du calcul
