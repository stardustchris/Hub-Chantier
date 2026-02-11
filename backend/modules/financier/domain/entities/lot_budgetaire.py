"""Entité LotBudgetaire - Représente un lot du budget prévisionnel.

FIN-02: Décomposition en lots - Structure arborescente du budget.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from shared.domain.calcul_financier import arrondir_montant
from ..value_objects import UniteMesure


@dataclass
class LotBudgetaire:
    """Représente un lot budgétaire d'un chantier ou d'un devis.

    Un lot budgétaire est une ligne du devis/budget prévisionnel
    avec une quantité prévue et un prix unitaire. Les lots peuvent
    être hiérarchiques (parent_lot_id).

    Phase Devis (commerciale):
        - devis_id est renseigné
        - budget_id est None
        - Les champs déboursés détaillés sont utilisés
        - marge_pct et prix_vente_ht sont calculés

    Phase Chantier:
        - budget_id est renseigné
        - devis_id est None
        - Les champs déboursés sont optionnels
    """

    id: Optional[int] = None
    budget_id: Optional[int] = None
    devis_id: Optional[UUID] = None
    code_lot: str = ""
    libelle: str = ""
    unite: UniteMesure = UniteMesure.U
    quantite_prevue: Decimal = Decimal("0")
    prix_unitaire_ht: Decimal = Decimal("0")
    parent_lot_id: Optional[int] = None
    ordre: int = 0

    # Champs déboursés détaillés (phase devis)
    debourse_main_oeuvre: Optional[Decimal] = None
    debourse_materiaux: Optional[Decimal] = None
    debourse_sous_traitance: Optional[Decimal] = None
    debourse_materiel: Optional[Decimal] = None
    debourse_divers: Optional[Decimal] = None

    # Marge (phase devis)
    marge_pct: Optional[Decimal] = None
    prix_vente_ht: Optional[Decimal] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    # H10: Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation à la création."""
        if not self.code_lot or not self.code_lot.strip():
            raise ValueError("Le code du lot est obligatoire")
        if not self.libelle or not self.libelle.strip():
            raise ValueError("Le libellé du lot est obligatoire")
        if self.quantite_prevue < Decimal("0"):
            raise ValueError("La quantité prévue ne peut pas être négative")
        if self.prix_unitaire_ht < Decimal("0"):
            raise ValueError("Le prix unitaire HT ne peut pas être négatif")

        # Validation XOR: devis_id et budget_id sont mutuellement exclusifs
        if self.devis_id is not None and self.budget_id is not None:
            raise ValueError(
                "Un lot ne peut être lié à la fois à un devis et à un budget. "
                "Utilisez devis_id pour la phase commerciale ou budget_id pour la phase chantier."
            )
        if self.devis_id is None and self.budget_id is None:
            raise ValueError(
                "Un lot doit être lié soit à un devis (phase commerciale) "
                "soit à un budget (phase chantier)."
            )

        # Validation des déboursés (doivent être >= 0 s'ils sont renseignés)
        for field_name in [
            "debourse_main_oeuvre",
            "debourse_materiaux",
            "debourse_sous_traitance",
            "debourse_materiel",
            "debourse_divers",
        ]:
            value = getattr(self, field_name)
            if value is not None and value < Decimal("0"):
                raise ValueError(f"{field_name} ne peut pas être négatif")

        # Validation marge_pct
        if self.marge_pct is not None:
            if self.marge_pct < Decimal("0"):
                raise ValueError("Le pourcentage de marge ne peut pas être négatif")

        # Validation prix_vente_ht
        if self.prix_vente_ht is not None and self.prix_vente_ht < Decimal("0"):
            raise ValueError("Le prix de vente HT ne peut pas être négatif")

    @property
    def total_prevu_ht(self) -> Decimal:
        """Montant total prévu HT = quantité * prix unitaire."""
        return arrondir_montant(self.quantite_prevue * self.prix_unitaire_ht)

    @property
    def debourse_sec_total(self) -> Decimal:
        """Calcule le total des déboursés secs (somme de tous les déboursés).

        Returns:
            Somme des déboursés (main d'oeuvre, matériaux, sous-traitance,
            matériel, divers). Retourne 0 si aucun déboursé n'est renseigné.
        """
        total = Decimal("0")
        for field_name in [
            "debourse_main_oeuvre",
            "debourse_materiaux",
            "debourse_sous_traitance",
            "debourse_materiel",
            "debourse_divers",
        ]:
            value = getattr(self, field_name)
            if value is not None:
                total += value
        return total

    @property
    def prix_vente_calcule_ht(self) -> Optional[Decimal]:
        """Calcule le prix de vente HT en appliquant la marge au déboursé sec total.

        Returns:
            Prix de vente HT = debourse_sec_total * (1 + marge_pct / 100).
            Retourne None si marge_pct n'est pas renseigné ou si debourse_sec_total = 0.
        """
        if self.marge_pct is None:
            return None
        debourse = self.debourse_sec_total
        if debourse == Decimal("0"):
            return None
        return arrondir_montant(debourse * (Decimal("1") + self.marge_pct / Decimal("100")))

    @property
    def est_en_phase_devis(self) -> bool:
        """Vérifie si le lot est en phase devis (commerciale)."""
        return self.devis_id is not None

    @property
    def est_supprime(self) -> bool:
        """Vérifie si le lot a été supprimé (soft delete)."""
        return self.deleted_at is not None

    def supprimer(self, deleted_by: int) -> None:
        """Marque le lot comme supprimé (soft delete).

        Args:
            deleted_by: ID de l'utilisateur qui supprime.
        """
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    def to_dict(self) -> dict:
        """Convertit l'entité en dictionnaire."""
        result = {
            "id": self.id,
            "budget_id": self.budget_id,
            "devis_id": str(self.devis_id) if self.devis_id else None,
            "code_lot": self.code_lot,
            "libelle": self.libelle,
            "unite": self.unite.value,
            "quantite_prevue": str(self.quantite_prevue),
            "prix_unitaire_ht": str(self.prix_unitaire_ht),
            "total_prevu_ht": str(self.total_prevu_ht),
            "parent_lot_id": self.parent_lot_id,
            "ordre": self.ordre,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }

        # Ajouter les champs de phase devis si renseignés
        if self.est_en_phase_devis:
            result.update(
                {
                    "debourse_main_oeuvre": (
                        str(self.debourse_main_oeuvre) if self.debourse_main_oeuvre is not None else None
                    ),
                    "debourse_materiaux": (
                        str(self.debourse_materiaux) if self.debourse_materiaux is not None else None
                    ),
                    "debourse_sous_traitance": (
                        str(self.debourse_sous_traitance) if self.debourse_sous_traitance is not None else None
                    ),
                    "debourse_materiel": (
                        str(self.debourse_materiel) if self.debourse_materiel is not None else None
                    ),
                    "debourse_divers": (
                        str(self.debourse_divers) if self.debourse_divers is not None else None
                    ),
                    "debourse_sec_total": str(self.debourse_sec_total),
                    "marge_pct": str(self.marge_pct) if self.marge_pct is not None else None,
                    "prix_vente_ht": str(self.prix_vente_ht) if self.prix_vente_ht is not None else None,
                    "prix_vente_calcule_ht": (
                        str(self.prix_vente_calcule_ht) if self.prix_vente_calcule_ht is not None else None
                    ),
                }
            )

        return result
