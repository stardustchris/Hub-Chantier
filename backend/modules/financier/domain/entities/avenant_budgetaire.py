"""Entité AvenantBudgetaire - Représente un avenant au budget d'un chantier.

FIN-04: Avenants budgétaires - Modifications du budget initial.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class AvenantBudgetaire:
    """Représente un avenant budgétaire rattaché à un budget.

    Un avenant permet de modifier le montant budgétaire d'un chantier,
    à la hausse ou à la baisse. Le montant peut être négatif pour une
    réduction de budget. Numérotation automatique AVN-YYYY-NN par budget.
    """

    id: Optional[int] = None
    budget_id: int = 0
    numero: str = ""
    motif: str = ""
    montant_ht: Decimal = Decimal("0")
    impact_description: Optional[str] = None
    statut: str = "brouillon"
    created_by: Optional[int] = None
    validated_by: Optional[int] = None
    validated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # H10: Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation à la création.

        Raises:
            ValueError: Si budget_id <= 0, motif vide ou numero vide.
        """
        if self.budget_id <= 0:
            raise ValueError("L'ID du budget est obligatoire")
        if not self.motif or not self.motif.strip():
            raise ValueError("Le motif de l'avenant est obligatoire")
        if not self.numero or not self.numero.strip():
            raise ValueError("Le numéro de l'avenant est obligatoire")

    def valider(self, validated_by: int) -> None:
        """Valide l'avenant budgétaire.

        Change le statut en 'valide' et enregistre le valideur.

        Args:
            validated_by: ID de l'utilisateur qui valide.

        Raises:
            ValueError: Si l'avenant est déjà validé.
        """
        if self.statut == "valide":
            raise ValueError("L'avenant est déjà validé")
        self.statut = "valide"
        self.validated_by = validated_by
        self.validated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @property
    def est_supprime(self) -> bool:
        """Vérifie si l'avenant a été supprimé (soft delete)."""
        return self.deleted_at is not None

    @property
    def est_valide(self) -> bool:
        """Vérifie si l'avenant est validé."""
        return self.statut == "valide"

    def to_dict(self) -> dict:
        """Convertit l'entité en dictionnaire."""
        return {
            "id": self.id,
            "budget_id": self.budget_id,
            "numero": self.numero,
            "motif": self.motif,
            "montant_ht": str(self.montant_ht),
            "impact_description": self.impact_description,
            "statut": self.statut,
            "created_by": self.created_by,
            "validated_by": self.validated_by,
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
