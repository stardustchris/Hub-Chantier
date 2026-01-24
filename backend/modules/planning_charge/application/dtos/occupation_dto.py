"""DTOs pour les details d'occupation (PDC-17)."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class TypeOccupationDTO:
    """DTO pour l'occupation par type de metier."""

    type_metier: str
    type_metier_label: str
    type_metier_couleur: str
    planifie_heures: float
    besoin_heures: float
    capacite_heures: float
    taux_occupation: float
    taux_couleur: str
    alerte: bool


@dataclass
class OccupationDetailsDTO:
    """
    DTO pour les details d'occupation par type (PDC-17).

    Modal affichant le taux d'occupation par type/metier
    avec code couleur pour une semaine donnee.
    """

    semaine_code: str
    semaine_label: str

    # Occupation globale
    taux_global: float
    taux_global_couleur: str
    alerte_globale: bool

    # Occupation par type de metier
    types: List[TypeOccupationDTO] = field(default_factory=list)

    # Totaux
    planifie_total: float = 0.0
    besoin_total: float = 0.0
    capacite_totale: float = 0.0

    # Indicateurs (PDC-14, PDC-15)
    a_recruter: int = 0
    a_placer: int = 0
