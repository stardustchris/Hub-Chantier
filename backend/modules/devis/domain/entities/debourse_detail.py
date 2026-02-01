"""Entite DebourseDetail - Sous-details par ligne de devis.

DEV-05: Detail debourses avances - Breakdown par ligne :
main d'oeuvre, materiaux, sous-traitance, materiel, deplacement.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..value_objects import TypeDebourse


@dataclass
class DebourseDetail:
    """Represente un detail de debourse sur une ligne de devis.

    Chaque ligne de devis peut avoir plusieurs debourses detailles
    qui decomposent le cout en categories (MOE, materiaux, etc.).
    Le total des debourses d'une ligne constitue le debourse sec de la ligne.

    Pour la MOE, les champs metier et taux_horaire permettent
    de detailler le calcul (heures x taux horaire par metier).
    """

    id: Optional[int] = None
    ligne_devis_id: int = 0
    type_debourse: TypeDebourse = TypeDebourse.MATERIAUX
    libelle: str = ""
    quantite: Decimal = Decimal("0")
    prix_unitaire: Decimal = Decimal("0")
    # Champs specifiques MOE
    metier: Optional[str] = None
    taux_horaire: Optional[Decimal] = None
    # Montant calcule
    total: Decimal = Decimal("0")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if self.ligne_devis_id <= 0:
            raise ValueError("L'ID de la ligne de devis est obligatoire")
        if not self.libelle or not self.libelle.strip():
            raise ValueError("Le libelle du debourse est obligatoire")
        if self.quantite < Decimal("0"):
            raise ValueError("La quantite ne peut pas etre negative")
        if self.prix_unitaire < Decimal("0"):
            raise ValueError("Le prix unitaire ne peut pas etre negatif")
        if self.taux_horaire is not None and self.taux_horaire < Decimal("0"):
            raise ValueError("Le taux horaire ne peut pas etre negatif")

    @property
    def montant_calcule(self) -> Decimal:
        """Montant calcule = quantite * prix unitaire."""
        return self.quantite * self.prix_unitaire

    @property
    def est_moe(self) -> bool:
        """Verifie si ce debourse est de type main d'oeuvre."""
        return self.type_debourse == TypeDebourse.MOE

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        result = {
            "id": self.id,
            "ligne_devis_id": self.ligne_devis_id,
            "type_debourse": self.type_debourse.value,
            "libelle": self.libelle,
            "quantite": str(self.quantite),
            "prix_unitaire": str(self.prix_unitaire),
            "total": str(self.total),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if self.est_moe:
            result["metier"] = self.metier
            result["taux_horaire"] = str(self.taux_horaire) if self.taux_horaire is not None else None
        return result
