"""Entite LigneDevis - Lignes de detail d'un lot de devis.

DEV-03: Creation devis structure - Lignes avec quantites et prix.
DEV-06: Gestion marges et coefficients - Marge par ligne (priorite 1).
DEV-04: Metres numeriques - Verrouillage des quantites issues de metres.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..value_objects import UniteArticle


@dataclass
class LigneDevis:
    """Represente une ligne de detail dans un lot de devis.

    Chaque ligne peut etre liee a un article de la bibliotheque (article_id)
    ou etre saisie librement. La ligne peut avoir une marge specifique
    (priorite maximale dans la hierarchie de marge).

    Le champ verrouille indique que la quantite provient d'un metre numerique
    et ne doit pas etre modifiee accidentellement (DEV-04).
    """

    id: Optional[int] = None
    lot_devis_id: int = 0
    article_id: Optional[int] = None
    libelle: str = ""
    unite: UniteArticle = UniteArticle.U
    quantite: Decimal = Decimal("0")
    prix_unitaire_ht: Decimal = Decimal("0")
    taux_marge_ligne: Optional[Decimal] = None
    ordre: int = 0
    verrouille: bool = False
    # Montants calcules
    total_ht: Decimal = Decimal("0")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    # H10: Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if self.lot_devis_id <= 0:
            raise ValueError("L'ID du lot de devis est obligatoire")
        if not self.libelle or not self.libelle.strip():
            raise ValueError("Le libelle de la ligne est obligatoire")
        if self.quantite < Decimal("0"):
            raise ValueError("La quantite ne peut pas etre negative")
        if self.prix_unitaire_ht < Decimal("0"):
            raise ValueError("Le prix unitaire HT ne peut pas etre negatif")
        if self.taux_marge_ligne is not None and self.taux_marge_ligne < Decimal("0"):
            raise ValueError("Le taux de marge de la ligne ne peut pas etre negatif")

    @property
    def montant_ht(self) -> Decimal:
        """Montant HT calcule = quantite * prix unitaire."""
        return self.quantite * self.prix_unitaire_ht

    @property
    def est_supprime(self) -> bool:
        """Verifie si la ligne a ete supprimee (soft delete)."""
        return self.deleted_at is not None

    def verrouiller(self) -> None:
        """Verrouille la quantite (issue d'un metre numerique)."""
        self.verrouille = True
        self.updated_at = datetime.utcnow()

    def deverrouiller(self) -> None:
        """Deverrouille la quantite."""
        self.verrouille = False
        self.updated_at = datetime.utcnow()

    def modifier_quantite(self, nouvelle_quantite: Decimal) -> None:
        """Modifie la quantite de la ligne.

        Args:
            nouvelle_quantite: Nouvelle quantite.

        Raises:
            ValueError: Si la ligne est verrouillee ou la quantite negative.
        """
        if self.verrouille:
            raise ValueError(
                "La quantite de cette ligne est verrouillee (metre numerique). "
                "Deverrouillez-la avant de la modifier."
            )
        if nouvelle_quantite < Decimal("0"):
            raise ValueError("La quantite ne peut pas etre negative")
        self.quantite = nouvelle_quantite
        self.total_ht = self.montant_ht
        self.updated_at = datetime.utcnow()

    def supprimer(self, deleted_by: int) -> None:
        """Marque la ligne comme supprimee (soft delete).

        Args:
            deleted_by: ID de l'utilisateur qui supprime.
        """
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "lot_devis_id": self.lot_devis_id,
            "article_id": self.article_id,
            "libelle": self.libelle,
            "unite": self.unite.value,
            "quantite": str(self.quantite),
            "prix_unitaire_ht": str(self.prix_unitaire_ht),
            "total_ht": str(self.total_ht),
            "taux_marge_ligne": str(self.taux_marge_ligne) if self.taux_marge_ligne is not None else None,
            "ordre": self.ordre,
            "verrouille": self.verrouille,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }
