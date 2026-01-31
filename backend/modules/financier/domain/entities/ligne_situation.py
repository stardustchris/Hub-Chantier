"""Entite LigneSituation - Ligne d'avancement par lot budgetaire.

FIN-07: Situations de travaux - detail de l'avancement par lot.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class LigneSituation:
    """Represente une ligne de situation (avancement par lot budgetaire).

    Chaque ligne de situation correspond a un lot budgetaire et indique
    le pourcentage d'avancement constate. Les montants sont calcules
    automatiquement a partir du montant marche et du pourcentage.

    Attributes:
        id: Identifiant unique (None si non persiste).
        situation_id: ID de la situation de travaux parente.
        lot_budgetaire_id: ID du lot budgetaire concerne.
        pourcentage_avancement: Pourcentage d'avancement (0-100).
        montant_marche_ht: Montant total du marche HT pour ce lot.
        montant_cumule_precedent_ht: Montant cumule des situations precedentes HT.
        montant_periode_ht: Montant de la periode courante HT.
        montant_cumule_ht: Montant cumule total HT.
        created_at: Date de creation.
        updated_at: Date de derniere modification.
    """

    id: Optional[int] = None
    situation_id: int = 0
    lot_budgetaire_id: int = 0
    pourcentage_avancement: Decimal = Decimal("0")
    montant_marche_ht: Decimal = Decimal("0")
    montant_cumule_precedent_ht: Decimal = Decimal("0")
    montant_periode_ht: Decimal = Decimal("0")
    montant_cumule_ht: Decimal = Decimal("0")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validation a la creation.

        Raises:
            ValueError: Si situation_id <= 0, lot_budgetaire_id <= 0,
                        ou pourcentage_avancement hors bornes [0, 100].
        """
        if self.situation_id <= 0:
            raise ValueError("L'ID de la situation est obligatoire")
        if self.lot_budgetaire_id <= 0:
            raise ValueError("L'ID du lot budgetaire est obligatoire")
        if self.pourcentage_avancement < Decimal("0") or self.pourcentage_avancement > Decimal("100"):
            raise ValueError(
                "Le pourcentage d'avancement doit etre compris entre 0 et 100"
            )

    def calculer_montants(self) -> None:
        """Calcule les montants a partir du pourcentage d'avancement.

        montant_cumule_ht = montant_marche_ht * pourcentage_avancement / 100
        montant_periode_ht = montant_cumule_ht - montant_cumule_precedent_ht
        """
        self.montant_cumule_ht = (
            self.montant_marche_ht * self.pourcentage_avancement / Decimal("100")
        )
        self.montant_periode_ht = (
            self.montant_cumule_ht - self.montant_cumule_precedent_ht
        )

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "situation_id": self.situation_id,
            "lot_budgetaire_id": self.lot_budgetaire_id,
            "pourcentage_avancement": str(self.pourcentage_avancement),
            "montant_marche_ht": str(self.montant_marche_ht),
            "montant_cumule_precedent_ht": str(self.montant_cumule_precedent_ht),
            "montant_periode_ht": str(self.montant_periode_ht),
            "montant_cumule_ht": str(self.montant_cumule_ht),
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }
