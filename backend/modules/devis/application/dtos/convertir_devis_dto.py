"""DTOs pour la conversion devis -> chantier.

DEV-16: Conversion en chantier - Donnees d'entree et de sortie.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass
class ConvertirDevisOptionsDTO:
    """Options pour la conversion d'un devis en chantier.

    Attributes:
        notify_client: Envoyer une notification au client.
        notify_team: Envoyer une notification a l'equipe.
    """

    notify_client: bool = False
    notify_team: bool = True


@dataclass
class ConvertirDevisResultDTO:
    """Resultat de la conversion d'un devis en chantier.

    Attributes:
        chantier_id: ID du chantier cree.
        code_chantier: Code unique du chantier (ex: A042).
        budget_id: ID du budget cree.
        nb_lots_transferes: Nombre de lots budgetaires crees.
        montant_total_ht: Montant total HT du budget.
        devis_id: ID du devis source.
        devis_numero: Numero du devis source.
    """

    chantier_id: int
    code_chantier: str
    budget_id: int
    nb_lots_transferes: int
    montant_total_ht: Decimal
    devis_id: int
    devis_numero: str

    def to_dict(self) -> dict[str, Any]:
        """Convertit le DTO en dictionnaire."""
        return {
            "chantier_id": self.chantier_id,
            "code_chantier": self.code_chantier,
            "budget_id": self.budget_id,
            "nb_lots_transferes": self.nb_lots_transferes,
            "montant_total_ht": str(self.montant_total_ht),
            "devis_id": self.devis_id,
            "devis_numero": self.devis_numero,
        }
