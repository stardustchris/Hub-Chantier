"""Entite LotDevis - Lots et chapitres d'un devis.

DEV-03: Creation devis structure - Arborescence par lots/chapitres.
DEV-06: Gestion marges et coefficients - Marge par lot (priorite 2).
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class LotDevis:
    """Represente un lot ou chapitre dans un devis.

    Les lots forment une arborescence (parent_id pour sous-chapitres).
    Chaque lot peut avoir une marge specifique qui s'applique a toutes
    ses lignes (sauf si une ligne a sa propre marge).

    Hierarchie de marge : Ligne > Lot > Type debourse > Global.
    """

    id: Optional[int] = None
    devis_id: int = 0
    code_lot: str = ""
    libelle: str = ""
    ordre: int = 0
    taux_marge_lot: Optional[Decimal] = None
    parent_id: Optional[int] = None
    # Montants calcules (mis a jour par le service de calcul)
    montant_debourse_ht: Decimal = Decimal("0")
    montant_vente_ht: Decimal = Decimal("0")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    # H10: Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if self.devis_id <= 0:
            raise ValueError("L'ID du devis est obligatoire")
        if not self.code_lot or not self.code_lot.strip():
            raise ValueError("Le code du lot est obligatoire")
        if not self.libelle or not self.libelle.strip():
            raise ValueError("Le libelle du lot est obligatoire")
        if self.taux_marge_lot is not None and self.taux_marge_lot < Decimal("0"):
            raise ValueError("Le taux de marge du lot ne peut pas etre negatif")

    @property
    def est_sous_chapitre(self) -> bool:
        """Verifie si le lot est un sous-chapitre (a un parent)."""
        return self.parent_id is not None

    @property
    def est_supprime(self) -> bool:
        """Verifie si le lot a ete supprime (soft delete)."""
        return self.deleted_at is not None

    def supprimer(self, deleted_by: int) -> None:
        """Marque le lot comme supprime (soft delete).

        Args:
            deleted_by: ID de l'utilisateur qui supprime.
        """
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "devis_id": self.devis_id,
            "code_lot": self.code_lot,
            "libelle": self.libelle,
            "ordre": self.ordre,
            "taux_marge_lot": str(self.taux_marge_lot) if self.taux_marge_lot is not None else None,
            "parent_id": self.parent_id,
            "montant_debourse_ht": str(self.montant_debourse_ht),
            "montant_vente_ht": str(self.montant_vente_ht),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }
