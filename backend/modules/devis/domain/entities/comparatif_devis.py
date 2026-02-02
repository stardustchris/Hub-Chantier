"""Entite ComparatifDevis - Comparaison globale entre deux versions de devis.

DEV-08: Variantes et revisions - Comparatif detaille automatique.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from .comparatif_ligne import ComparatifLigne


@dataclass
class ComparatifDevis:
    """Represente un comparatif global entre deux versions d'un devis.

    Contient les ecarts globaux (montants HT, marges) et la liste
    des ecarts ligne a ligne. Le comparatif est persiste pour consultation
    ulterieure sans recalcul.
    """

    id: Optional[int] = None
    devis_source_id: int = 0
    devis_cible_id: int = 0

    # Ecarts globaux
    ecart_montant_ht: Decimal = Decimal("0")
    ecart_montant_ttc: Decimal = Decimal("0")
    ecart_marge_pct: Decimal = Decimal("0")
    ecart_debourse_total: Decimal = Decimal("0")

    # Compteurs de lignes
    nb_lignes_ajoutees: int = 0
    nb_lignes_supprimees: int = 0
    nb_lignes_modifiees: int = 0
    nb_lignes_identiques: int = 0

    # Details ligne a ligne
    lignes: List[ComparatifLigne] = field(default_factory=list)

    # Metadonnees
    genere_par: Optional[int] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if self.devis_source_id <= 0:
            raise ValueError("L'ID du devis source est obligatoire")
        if self.devis_cible_id <= 0:
            raise ValueError("L'ID du devis cible est obligatoire")
        if self.devis_source_id == self.devis_cible_id:
            raise ValueError(
                "Le devis source et le devis cible doivent etre differents"
            )

    @property
    def nb_lignes_total(self) -> int:
        """Nombre total de lignes dans le comparatif."""
        return (
            self.nb_lignes_ajoutees
            + self.nb_lignes_supprimees
            + self.nb_lignes_modifiees
            + self.nb_lignes_identiques
        )

    @property
    def a_des_ecarts(self) -> bool:
        """Indique si le comparatif contient des ecarts significatifs."""
        return (
            self.nb_lignes_ajoutees > 0
            or self.nb_lignes_supprimees > 0
            or self.nb_lignes_modifiees > 0
        )

    @property
    def pourcentage_ecart_montant_ht(self) -> Optional[Decimal]:
        """Pourcentage d'ecart du montant HT par rapport a la source.

        Returns:
            Le pourcentage d'ecart ou None si la source est a zero.
        """
        # Le calcul sera fait dans le use case avec les montants reels
        return None

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "devis_source_id": self.devis_source_id,
            "devis_cible_id": self.devis_cible_id,
            "ecart_montant_ht": str(self.ecart_montant_ht),
            "ecart_montant_ttc": str(self.ecart_montant_ttc),
            "ecart_marge_pct": str(self.ecart_marge_pct),
            "ecart_debourse_total": str(self.ecart_debourse_total),
            "nb_lignes_ajoutees": self.nb_lignes_ajoutees,
            "nb_lignes_supprimees": self.nb_lignes_supprimees,
            "nb_lignes_modifiees": self.nb_lignes_modifiees,
            "nb_lignes_identiques": self.nb_lignes_identiques,
            "nb_lignes_total": self.nb_lignes_total,
            "a_des_ecarts": self.a_des_ecarts,
            "lignes": [l.to_dict() for l in self.lignes],
            "genere_par": self.genere_par,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
