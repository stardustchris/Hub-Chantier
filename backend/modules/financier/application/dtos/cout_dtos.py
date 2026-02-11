"""DTOs pour le suivi des couts (main-d'oeuvre et materiel).

FIN-09: Suivi couts main-d'oeuvre.
FIN-10: Suivi couts materiel.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class CoutEmployeDTO:
    """DTO pour le cout d'un employe sur un chantier."""

    user_id: int
    nom: str
    prenom: str
    heures_validees: str
    taux_horaire: str
    taux_horaire_charge: str
    cout_total: str


@dataclass
class CoutMaterielDTO:
    """DTO pour le cout d'une ressource materiel sur un chantier."""

    ressource_id: int
    nom: str
    code: str
    jours_reservation: int
    tarif_journalier: str
    cout_total: str


@dataclass
class CoutMainOeuvreSummaryDTO:
    """DTO resume des couts main-d'oeuvre d'un chantier."""

    chantier_id: int
    total_heures: str
    cout_total: str
    details: List[CoutEmployeDTO] = field(default_factory=list)


@dataclass
class CoutMaterielSummaryDTO:
    """DTO resume des couts materiel d'un chantier."""

    chantier_id: int
    cout_total: str
    details: List[CoutMaterielDTO] = field(default_factory=list)
