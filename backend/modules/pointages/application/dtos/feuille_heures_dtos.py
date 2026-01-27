"""DTOs pour les feuilles d'heures."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict


@dataclass
class CreateFeuilleHeuresDTO:
    """DTO pour la création d'une feuille d'heures."""

    utilisateur_id: int
    semaine_debut: date  # Doit être un lundi


@dataclass
class FeuilleHeuresDTO:
    """DTO de sortie pour une feuille d'heures."""

    id: int
    utilisateur_id: int
    semaine_debut: date
    semaine_fin: date
    annee: int
    numero_semaine: int
    label_semaine: str
    statut_global: str
    total_heures_normales: str
    total_heures_supplementaires: str
    total_heures: str
    total_heures_decimal: float
    commentaire_global: Optional[str]
    is_complete: bool
    is_all_validated: bool
    created_at: datetime
    updated_at: datetime
    # Données enrichies
    utilisateur_nom: Optional[str] = None
    pointages: List["PointageJourDTO"] = field(default_factory=list)
    variables_paie: List["VariablePaieSemaineDTO"] = field(default_factory=list)
    totaux_par_jour: Dict[str, str] = field(default_factory=dict)
    totaux_par_chantier: Dict[int, str] = field(default_factory=dict)


@dataclass
class PointageJourDTO:
    """DTO pour un pointage dans la vue semaine."""

    id: int
    chantier_id: int
    chantier_nom: str
    chantier_couleur: str
    date_pointage: date
    jour_semaine: str  # lundi, mardi, etc.
    heures_normales: str
    heures_supplementaires: str
    total_heures: str
    statut: str
    is_editable: bool


@dataclass
class VariablePaieSemaineDTO:
    """DTO pour une variable de paie dans la vue semaine."""

    type_variable: str
    type_variable_libelle: str
    total: str  # Total de la semaine


@dataclass
class FeuilleHeuresListDTO:
    """DTO pour une liste paginée de feuilles d'heures."""

    items: List[FeuilleHeuresDTO]
    total: int
    page: int
    page_size: int
    total_pages: int


@dataclass
class FeuilleHeuresSearchDTO:
    """DTO pour la recherche de feuilles d'heures."""

    utilisateur_id: Optional[int] = None
    annee: Optional[int] = None
    numero_semaine: Optional[int] = None
    statut: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    page: int = 1
    page_size: int = 10


@dataclass
class NavigationSemaineDTO:
    """DTO pour la navigation par semaine (FDH-02)."""

    semaine_courante: date
    semaine_precedente: date
    semaine_suivante: date
    numero_semaine: int
    annee: int
    label: str


@dataclass
class VueChantierDTO:
    """DTO pour la vue par chantier (FDH-01 onglet Chantiers)."""

    chantier_id: int
    chantier_nom: str
    chantier_couleur: str
    total_heures: str
    total_heures_decimal: float
    pointages_par_jour: Dict[str, List["PointageUtilisateurDTO"]]
    total_par_jour: Dict[str, str]


@dataclass
class PointageUtilisateurDTO:
    """DTO pour un pointage dans la vue chantier."""

    pointage_id: int
    utilisateur_id: int
    utilisateur_nom: str
    heures_normales: str
    heures_supplementaires: str
    total_heures: str
    statut: str


@dataclass
class VueCompagnonDTO:
    """DTO pour la vue par compagnon (FDH-01 onglet Compagnons)."""

    utilisateur_id: int
    utilisateur_nom: str
    total_heures: str
    total_heures_decimal: float
    chantiers: List["ChantierPointageDTO"]
    totaux_par_jour: Dict[str, str]


@dataclass
class PointageJourCompagnonDTO:
    """DTO pour un pointage dans la vue compagnon (par jour/chantier)."""

    id: int
    utilisateur_id: int
    chantier_id: int
    date_pointage: str
    heures_normales: str
    heures_supplementaires: str
    total_heures: str
    statut: str
    is_editable: bool
    commentaire: Optional[str] = None


@dataclass
class ChantierPointageDTO:
    """DTO pour les pointages d'un chantier dans la vue compagnon."""

    chantier_id: int
    chantier_nom: str
    chantier_couleur: str
    total_heures: str
    pointages_par_jour: Dict[str, List["PointageJourCompagnonDTO"]]


@dataclass
class ComparaisonEquipesDTO:
    """DTO pour la comparaison inter-équipes (FDH-15)."""

    semaine: str
    equipes: List["EquipeStatsDTO"]
    ecarts_detectes: List["EcartDTO"]


@dataclass
class EquipeStatsDTO:
    """DTO pour les stats d'une équipe."""

    chantier_id: int
    chantier_nom: str
    total_heures_planifiees: float
    total_heures_realisees: float
    taux_completion: float
    nombre_utilisateurs: int


@dataclass
class EcartDTO:
    """DTO pour un écart détecté."""

    type_ecart: str  # "surplus", "deficit"
    chantier_id: int
    chantier_nom: str
    heures_planifiees: float
    heures_realisees: float
    ecart_heures: float
    ecart_pourcentage: float


@dataclass
class JaugeAvancementDTO:
    """DTO pour la jauge d'avancement (FDH-14)."""

    utilisateur_id: int
    semaine: str
    heures_planifiees: float
    heures_realisees: float
    taux_completion: float
    status: str  # "en_avance", "normal", "en_retard"
