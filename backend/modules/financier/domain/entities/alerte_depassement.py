"""Entite AlerteDepassement - Represente une alerte de depassement budgetaire.

FIN-12: Alertes depassements - alertes automatiques lors du depassement
de seuils budgetaires.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class AlerteDepassement:
    """Represente une alerte de depassement budgetaire.

    Une alerte est creee automatiquement lorsqu'un seuil budgetaire est
    atteint. Elle peut etre acquittee par un utilisateur pour indiquer
    qu'elle a ete prise en compte.

    Attributes:
        id: Identifiant unique (None si non persiste).
        chantier_id: ID du chantier concerne.
        budget_id: ID du budget concerne.
        type_alerte: Type d'alerte (seuil_engage, seuil_realise, depassement_lot).
        message: Message descriptif de l'alerte.
        pourcentage_atteint: Pourcentage du budget atteint.
        seuil_configure: Seuil d'alerte configure.
        montant_budget_ht: Montant du budget HT.
        montant_atteint_ht: Montant atteint HT.
        est_acquittee: Indique si l'alerte a ete acquittee.
        acquittee_par: ID de l'utilisateur qui a acquitte.
        acquittee_at: Date d'acquittement.
        created_at: Date de creation.
    """

    id: Optional[int] = None
    chantier_id: int = 0
    budget_id: int = 0
    type_alerte: str = "seuil_engage"
    message: str = ""
    pourcentage_atteint: Decimal = Decimal("0")
    seuil_configure: Decimal = Decimal("0")
    montant_budget_ht: Decimal = Decimal("0")
    montant_atteint_ht: Decimal = Decimal("0")
    est_acquittee: bool = False
    acquittee_par: Optional[int] = None
    acquittee_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validation a la creation.

        Raises:
            ValueError: Si chantier_id <= 0 ou budget_id <= 0.
        """
        if self.chantier_id <= 0:
            raise ValueError("L'ID du chantier est obligatoire")
        if self.budget_id <= 0:
            raise ValueError("L'ID du budget est obligatoire")

    def acquitter(self, user_id: int) -> None:
        """Acquitte l'alerte.

        Args:
            user_id: ID de l'utilisateur qui acquitte.

        Raises:
            ValueError: Si l'alerte est deja acquittee.
        """
        if self.est_acquittee:
            raise ValueError("L'alerte est deja acquittee")
        self.est_acquittee = True
        self.acquittee_par = user_id
        self.acquittee_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "chantier_id": self.chantier_id,
            "budget_id": self.budget_id,
            "type_alerte": self.type_alerte,
            "message": self.message,
            "pourcentage_atteint": str(self.pourcentage_atteint),
            "seuil_configure": str(self.seuil_configure),
            "montant_budget_ht": str(self.montant_budget_ht),
            "montant_atteint_ht": str(self.montant_atteint_ht),
            "est_acquittee": self.est_acquittee,
            "acquittee_par": self.acquittee_par,
            "acquittee_at": (
                self.acquittee_at.isoformat() if self.acquittee_at else None
            ),
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
        }
