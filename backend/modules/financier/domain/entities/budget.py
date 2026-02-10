"""Entité Budget - Représente le budget global d'un chantier.

FIN-01: Budget prévisionnel - Enveloppe budgétaire par chantier.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Budget:
    """Représente le budget prévisionnel d'un chantier.

    Chaque chantier possède un budget avec un montant initial,
    des avenants éventuels, et des seuils d'alerte.
    """

    id: Optional[int] = None
    chantier_id: int = 0
    montant_initial_ht: Decimal = Decimal("0")
    montant_avenants_ht: Decimal = Decimal("0")
    retenue_garantie_pct: Decimal = Decimal("5")
    seuil_alerte_pct: Decimal = Decimal("90")
    seuil_validation_achat: Decimal = Decimal("5000")
    notes: Optional[str] = None
    devis_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    # H10: Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None
    # A5: Lock optimiste
    version: int = 1

    def __post_init__(self) -> None:
        """Validation à la création."""
        if self.chantier_id <= 0:
            raise ValueError("L'ID du chantier est obligatoire")
        if self.montant_initial_ht < Decimal("0"):
            raise ValueError("Le montant initial HT ne peut pas être négatif")
        if self.retenue_garantie_pct < Decimal("0") or self.retenue_garantie_pct > Decimal("5"):
            raise ValueError("La retenue de garantie doit être entre 0 et 5% (loi 71-584)")
        if self.seuil_alerte_pct < Decimal("0") or self.seuil_alerte_pct > Decimal("200"):
            raise ValueError("Le seuil d'alerte doit être entre 0 et 200%")
        if self.seuil_validation_achat < Decimal("0"):
            raise ValueError("Le seuil de validation achat ne peut pas être négatif")

    @property
    def montant_revise_ht(self) -> Decimal:
        """Montant révisé HT = initial + avenants."""
        return self.montant_initial_ht + self.montant_avenants_ht

    @property
    def est_supprime(self) -> bool:
        """Vérifie si le budget a été supprimé (soft delete)."""
        return self.deleted_at is not None

    def ajouter_avenant(self, montant: Decimal, motif: str) -> None:
        """Ajoute un avenant au budget.

        Args:
            montant: Montant de l'avenant (peut être négatif pour une réduction).
            motif: Justification de l'avenant.

        Raises:
            ValueError: Si le motif est vide ou si le budget révisé deviendrait négatif.
        """
        if not motif or not motif.strip():
            raise ValueError("Le motif de l'avenant est obligatoire")
        nouveau_revise = self.montant_initial_ht + self.montant_avenants_ht + montant
        if nouveau_revise < Decimal("0"):
            raise ValueError(
                f"Avenant de {montant} EUR refuse : le budget revise deviendrait "
                f"negatif ({nouveau_revise} EUR). Un budget ne peut pas etre negatif."
            )
        self.montant_avenants_ht += montant
        self.updated_at = datetime.utcnow()

    def modifier_retenue_garantie(self, pct: Decimal) -> None:
        """Modifie le pourcentage de retenue de garantie.

        Args:
            pct: Nouveau pourcentage (entre 0 et 5, loi 71-584).

        Raises:
            ValueError: Si le pourcentage est hors limites.
        """
        if pct < Decimal("0") or pct > Decimal("5"):
            raise ValueError("La retenue de garantie doit être entre 0 et 5% (loi 71-584)")
        self.retenue_garantie_pct = pct
        self.updated_at = datetime.utcnow()

    def necessite_validation_achat(self, montant: Decimal) -> bool:
        """Détermine si un achat nécessite une validation N+1.

        Args:
            montant: Montant HT de l'achat.

        Returns:
            True si le montant dépasse le seuil de validation.
        """
        return montant >= self.seuil_validation_achat

    def supprimer(self, deleted_by: int) -> None:
        """Marque le budget comme supprimé (soft delete).

        Args:
            deleted_by: ID de l'utilisateur qui supprime.
        """
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    def to_dict(self) -> dict:
        """Convertit l'entité en dictionnaire."""
        return {
            "id": self.id,
            "chantier_id": self.chantier_id,
            "montant_initial_ht": str(self.montant_initial_ht),
            "montant_avenants_ht": str(self.montant_avenants_ht),
            "montant_revise_ht": str(self.montant_revise_ht),
            "retenue_garantie_pct": str(self.retenue_garantie_pct),
            "seuil_alerte_pct": str(self.seuil_alerte_pct),
            "seuil_validation_achat": str(self.seuil_validation_achat),
            "notes": self.notes,
            "devis_id": self.devis_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }
