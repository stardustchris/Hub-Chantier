"""DTOs pour le tableau de bord devis.

DEV-17: Tableau de bord devis - KPI pipeline commercial.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class KPIDevisDTO:
    """DTO pour les KPI du pipeline commercial."""

    nb_brouillon: int = 0
    nb_en_validation: int = 0
    nb_approuve: int = 0
    nb_envoye: int = 0
    nb_accepte: int = 0
    nb_refuse: int = 0
    nb_perdu: int = 0
    nb_expire: int = 0
    total_pipeline_ht: str = "0"
    total_accepte_ht: str = "0"
    taux_conversion: str = "0"
    nb_total: int = 0

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "nb_brouillon": self.nb_brouillon,
            "nb_en_validation": self.nb_en_validation,
            "nb_approuve": self.nb_approuve,
            "nb_envoye": self.nb_envoye,
            "nb_accepte": self.nb_accepte,
            "nb_refuse": self.nb_refuse,
            "nb_perdu": self.nb_perdu,
            "nb_expire": self.nb_expire,
            "total_pipeline_ht": self.total_pipeline_ht,
            "total_accepte_ht": self.total_accepte_ht,
            "taux_conversion": self.taux_conversion,
            "nb_total": self.nb_total,
        }


@dataclass
class DevisRecentDTO:
    """DTO pour un devis recent dans le dashboard."""

    id: int
    numero: str
    client_nom: str
    objet: str
    statut: str
    total_ht: str
    date_creation: str

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "numero": self.numero,
            "client_nom": self.client_nom,
            "objet": self.objet,
            "statut": self.statut,
            "total_ht": self.total_ht,
            "date_creation": self.date_creation,
        }


@dataclass
class DashboardDevisDTO:
    """DTO principal du tableau de bord devis.

    DEV-17: Agregation KPI, pipeline commercial, devis recents.
    """

    kpi: KPIDevisDTO
    derniers_devis: List[DevisRecentDTO] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "kpi": self.kpi.to_dict(),
            "derniers_devis": [d.to_dict() for d in self.derniers_devis],
        }
