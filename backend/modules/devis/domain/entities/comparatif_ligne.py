"""Entite ComparatifLigne - Detail ligne a ligne d'un comparatif de devis.

DEV-08: Variantes et revisions - Ecart par ligne entre deux versions.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from ..value_objects.type_ecart import TypeEcart


@dataclass
class ComparatifLigne:
    """Represente un ecart sur une ligne entre deux versions d'un devis.

    Le matching entre lignes source et cible se fait par :
    1. article_id (cle prioritaire si disponible)
    2. (lot_titre, designation) sinon

    Les ecarts sont calcules sur quantite, prix unitaire, montant HT
    et debourse sec.
    """

    id: Optional[int] = None
    comparatif_id: int = 0
    type_ecart: TypeEcart = TypeEcart.IDENTIQUE

    # Identification de la ligne
    lot_titre: str = ""
    designation: str = ""
    article_id: Optional[int] = None

    # Valeurs source (version ancienne)
    source_quantite: Optional[Decimal] = None
    source_prix_unitaire: Optional[Decimal] = None
    source_montant_ht: Optional[Decimal] = None
    source_debourse_sec: Optional[Decimal] = None

    # Valeurs cible (version nouvelle)
    cible_quantite: Optional[Decimal] = None
    cible_prix_unitaire: Optional[Decimal] = None
    cible_montant_ht: Optional[Decimal] = None
    cible_debourse_sec: Optional[Decimal] = None

    # Ecarts calcules
    ecart_quantite: Optional[Decimal] = None
    ecart_prix_unitaire: Optional[Decimal] = None
    ecart_montant_ht: Optional[Decimal] = None
    ecart_debourse_sec: Optional[Decimal] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if self.comparatif_id <= 0:
            raise ValueError("L'ID du comparatif est obligatoire")
        if not self.designation or not self.designation.strip():
            raise ValueError("La designation de la ligne est obligatoire")

    @property
    def pourcentage_ecart_montant(self) -> Optional[Decimal]:
        """Pourcentage d'ecart du montant HT.

        Returns:
            Le pourcentage d'ecart ou None si non calculable.
        """
        if (
            self.source_montant_ht is not None
            and self.source_montant_ht != Decimal("0")
            and self.ecart_montant_ht is not None
        ):
            return (self.ecart_montant_ht / self.source_montant_ht) * Decimal("100")
        return None

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        result = {
            "id": self.id,
            "comparatif_id": self.comparatif_id,
            "type_ecart": self.type_ecart.value,
            "lot_titre": self.lot_titre,
            "designation": self.designation,
            "article_id": self.article_id,
            "source_quantite": str(self.source_quantite) if self.source_quantite is not None else None,
            "source_prix_unitaire": str(self.source_prix_unitaire) if self.source_prix_unitaire is not None else None,
            "source_montant_ht": str(self.source_montant_ht) if self.source_montant_ht is not None else None,
            "source_debourse_sec": str(self.source_debourse_sec) if self.source_debourse_sec is not None else None,
            "cible_quantite": str(self.cible_quantite) if self.cible_quantite is not None else None,
            "cible_prix_unitaire": str(self.cible_prix_unitaire) if self.cible_prix_unitaire is not None else None,
            "cible_montant_ht": str(self.cible_montant_ht) if self.cible_montant_ht is not None else None,
            "cible_debourse_sec": str(self.cible_debourse_sec) if self.cible_debourse_sec is not None else None,
            "ecart_quantite": str(self.ecart_quantite) if self.ecart_quantite is not None else None,
            "ecart_prix_unitaire": str(self.ecart_prix_unitaire) if self.ecart_prix_unitaire is not None else None,
            "ecart_montant_ht": str(self.ecart_montant_ht) if self.ecart_montant_ht is not None else None,
            "ecart_debourse_sec": str(self.ecart_debourse_sec) if self.ecart_debourse_sec is not None else None,
            "pourcentage_ecart_montant": str(self.pourcentage_ecart_montant) if self.pourcentage_ecart_montant is not None else None,
        }
        return result
