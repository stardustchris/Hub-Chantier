"""DTOs pour le planning de charge."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class PlanningChargeFiltersDTO:
    """DTO pour les filtres du planning de charge."""

    semaine_debut: str  # Format SXX-YYYY
    semaine_fin: str  # Format SXX-YYYY
    recherche: Optional[str] = None  # PDC-03: Recherche par nom de chantier
    mode_avance: bool = False  # PDC-04: Toggle mode avance
    unite: str = "heures"  # PDC-05: heures ou jours_homme


@dataclass
class CelluleChargeDTO:
    """DTO pour une cellule du tableau (planifie + besoin)."""

    planifie_heures: float = 0.0
    besoin_heures: float = 0.0
    besoin_non_couvert: float = 0.0  # max(besoin - planifie, 0)
    has_besoin: bool = False  # Pour PDC-10: cellules violettes

    @property
    def est_couvert(self) -> bool:
        """Indique si le besoin est entierement couvert."""
        return self.planifie_heures >= self.besoin_heures


@dataclass
class SemaineChargeDTO:
    """DTO pour une semaine dans le planning."""

    code: str  # SXX-YYYY
    label: str  # S30 - 2025
    cellule: CelluleChargeDTO = field(default_factory=CelluleChargeDTO)


@dataclass
class ChantierChargeDTO:
    """DTO pour un chantier dans le planning de charge."""

    id: int
    code: str  # Code chantier (ex: A001)
    nom: str
    couleur: str
    charge_totale: float  # PDC-08: Budget heures total
    semaines: List[SemaineChargeDTO] = field(default_factory=list)


@dataclass
class FooterChargeDTO:
    """DTO pour le footer repliable (PDC-11)."""

    semaine_code: str
    taux_occupation: float  # PDC-12: Pourcentage
    taux_couleur: str  # Code couleur hex
    taux_label: str  # Label du niveau
    alerte_surcharge: bool  # PDC-13: True si >= 100%
    a_recruter: int  # PDC-14: Nombre de personnes a embaucher
    a_placer: int  # PDC-15: Personnes disponibles


@dataclass
class PlanningChargeDTO:
    """DTO complet pour la vue planning de charge (PDC-01)."""

    # Metadonnees
    total_chantiers: int  # PDC-02: Compteur chantiers
    semaine_debut: str
    semaine_fin: str
    unite: str  # heures ou jours_homme

    # Colonnes semaines (PDC-07)
    semaines: List[str]  # Liste des codes semaine

    # Lignes chantiers
    chantiers: List[ChantierChargeDTO]

    # Footer (PDC-11)
    footer: List[FooterChargeDTO]

    # Stats globales
    capacite_totale: float
    planifie_total: float
    besoin_total: float
