"""Entite FraisChantierDevis - Frais de chantier d'un devis.

DEV-25: Frais de chantier - Compte prorata, frais generaux, installations
de chantier avec repartition globale ou par lot.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from shared.domain.calcul_financier import calculer_ttc, arrondir_montant

from ..value_objects.type_frais_chantier import TypeFraisChantier
from ..value_objects.mode_repartition import ModeRepartition


class FraisChantierValidationError(Exception):
    """Erreur levee lors d'une validation metier sur un frais de chantier."""

    pass


@dataclass
class FraisChantierDevis:
    """Represente un frais de chantier associe a un devis.

    Les frais de chantier sont des couts supplementaires (compte prorata,
    frais generaux, installations) qui s'ajoutent aux lots du devis.
    Ils peuvent etre repartis globalement ou au prorata des lots.

    Attributes:
        id: Identifiant unique (None si non persiste).
        devis_id: ID du devis associe (FK).
        type_frais: Type de frais de chantier.
        libelle: Description du frais.
        montant_ht: Montant hors taxes.
        mode_repartition: Mode de repartition sur les lots.
        taux_tva: Taux de TVA applicable.
        ordre: Ordre d'affichage.
        lot_devis_id: ID du lot associe (nullable, pour affectation directe).
        created_at: Date de creation.
        updated_at: Date de derniere modification.
        created_by: ID de l'utilisateur createur.
        deleted_at: Date de suppression (soft delete).
        deleted_by: ID de l'utilisateur qui a supprime.
    """

    devis_id: int
    type_frais: TypeFraisChantier
    libelle: str
    montant_ht: Decimal

    # Attributs avec valeurs par defaut
    id: Optional[int] = None
    mode_repartition: ModeRepartition = ModeRepartition.GLOBAL
    taux_tva: Decimal = Decimal("20")
    ordre: int = 0
    lot_devis_id: Optional[int] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    # H10: Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        if self.devis_id <= 0:
            raise FraisChantierValidationError(
                "L'ID du devis est obligatoire"
            )
        if not self.libelle or not self.libelle.strip():
            raise FraisChantierValidationError(
                "Le libelle du frais de chantier est obligatoire"
            )
        if self.montant_ht < Decimal("0"):
            raise FraisChantierValidationError(
                "Le montant HT ne peut pas etre negatif"
            )
        if self.taux_tva < Decimal("0") or self.taux_tva > Decimal("100"):
            raise FraisChantierValidationError(
                "Le taux de TVA doit etre entre 0 et 100%"
            )

    @property
    def montant_ttc(self) -> Decimal:
        """Calcule le montant TTC du frais de chantier.

        Formule: HT + TVA arrondie (via calculer_ttc).

        Returns:
            Le montant TTC.
        """
        return calculer_ttc(self.montant_ht, self.taux_tva)

    @property
    def est_supprime(self) -> bool:
        """Verifie si le frais a ete supprime (soft delete)."""
        return self.deleted_at is not None

    def calculer_repartition_lot(
        self, lot_total_ht: Decimal, devis_total_ht: Decimal
    ) -> Decimal:
        """Calcule la part proratisee du frais pour un lot donne.

        Si le mode est GLOBAL, retourne le montant complet.
        Si le mode est PRORATA_LOTS, retourne montant_ht * (lot_total_ht / devis_total_ht).

        Args:
            lot_total_ht: Montant HT total du lot.
            devis_total_ht: Montant HT total du devis (somme de tous les lots).

        Returns:
            La part du frais attribuee au lot.
        """
        if self.mode_repartition == ModeRepartition.GLOBAL:
            return self.montant_ht

        # PRORATA_LOTS
        if devis_total_ht <= Decimal("0"):
            return Decimal("0")

        return arrondir_montant(self.montant_ht * (lot_total_ht / devis_total_ht))

    def supprimer(self, deleted_by: int) -> None:
        """Marque le frais comme supprime (soft delete).

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
            "type_frais": self.type_frais.value,
            "libelle": self.libelle,
            "montant_ht": str(self.montant_ht),
            "montant_ttc": str(self.montant_ttc),
            "mode_repartition": self.mode_repartition.value,
            "taux_tva": str(self.taux_tva),
            "ordre": self.ordre,
            "lot_devis_id": self.lot_devis_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID (entite)."""
        if not isinstance(other, FraisChantierDevis):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
