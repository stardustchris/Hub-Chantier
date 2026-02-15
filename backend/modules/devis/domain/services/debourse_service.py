"""Service de decomposition des debourses par ligne.

DEV-05: Detail debourses avances.
Calcul automatique du prix de revient par ligne a partir des debourses.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List

from ..entities.debourse_detail import DebourseDetail
from ..value_objects import TypeDebourse


@dataclass
class DecomposeDebourse:
    """Decomposition du debourse sec d'une ligne par type.

    DEV-05: Vue decomposee des couts directs d'une ligne de devis.
    Chaque ligne peut avoir des debourses de types differents
    (MOE, materiaux, sous-traitance, materiel, deplacement).

    Ce value object aggrege les debourses par type et calcule
    les totaux pour la vue interne du devis.
    """

    ligne_devis_id: int = 0
    total_moe: Decimal = Decimal("0")
    total_materiaux: Decimal = Decimal("0")
    total_sous_traitance: Decimal = Decimal("0")
    total_materiel: Decimal = Decimal("0")
    total_deplacement: Decimal = Decimal("0")
    details_par_type: Dict[str, List[dict]] = field(default_factory=dict)

    @property
    def debourse_sec(self) -> Decimal:
        """Calcule le debourse sec total (somme de tous les types)."""
        return (
            self.total_moe
            + self.total_materiaux
            + self.total_sous_traitance
            + self.total_materiel
            + self.total_deplacement
        )

    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour serialisation."""
        return {
            "ligne_devis_id": self.ligne_devis_id,
            "total_moe": str(self.total_moe),
            "total_materiaux": str(self.total_materiaux),
            "total_sous_traitance": str(self.total_sous_traitance),
            "total_materiel": str(self.total_materiel),
            "total_deplacement": str(self.total_deplacement),
            "debourse_sec": str(self.debourse_sec),
            "details_par_type": self.details_par_type,
        }


class DebourseService:
    """Service domain pour la decomposition des debourses.

    DEV-05: Calcule les totaux par type de debourse pour une ligne
    et fournit la vue decomposee du prix de revient.
    """

    @staticmethod
    def decomposer(
        ligne_devis_id: int,
        debourses: List[DebourseDetail],
    ) -> DecomposeDebourse:
        """Decompose les debourses d'une ligne par type.

        Args:
            ligne_devis_id: L'ID de la ligne de devis.
            debourses: Liste des debourses detailles de la ligne.

        Returns:
            DecomposeDebourse avec les totaux par type.
        """
        result = DecomposeDebourse(ligne_devis_id=ligne_devis_id)
        details: Dict[str, List[dict]] = {}

        for deb in debourses:
            montant = deb.quantite * deb.prix_unitaire
            type_key = deb.type_debourse.value

            # Accumuler par type
            if deb.type_debourse == TypeDebourse.MOE:
                result.total_moe += montant
            elif deb.type_debourse == TypeDebourse.MATERIAUX:
                result.total_materiaux += montant
            elif deb.type_debourse == TypeDebourse.SOUS_TRAITANCE:
                result.total_sous_traitance += montant
            elif deb.type_debourse == TypeDebourse.MATERIEL:
                result.total_materiel += montant
            elif deb.type_debourse == TypeDebourse.DEPLACEMENT:
                result.total_deplacement += montant

            # Collecter les details
            if type_key not in details:
                details[type_key] = []
            detail = {
                "id": deb.id,
                "libelle": deb.libelle,
                "quantite": str(deb.quantite),
                "prix_unitaire": str(deb.prix_unitaire),
                "montant": str(montant),
            }
            if deb.est_moe:
                detail["metier"] = deb.metier
                detail["taux_horaire"] = (
                    str(deb.taux_horaire) if deb.taux_horaire is not None else None
                )
            details[type_key].append(detail)

        result.details_par_type = details
        return result

    @staticmethod
    def calculer_debourse_sec(debourses: List[DebourseDetail]) -> Decimal:
        """Calcule le debourse sec total d'une liste de debourses.

        Args:
            debourses: Liste des debourses detailles.

        Returns:
            Le debourse sec (somme de tous les montants).
        """
        return sum(
            (deb.quantite * deb.prix_unitaire for deb in debourses),
            Decimal("0"),
        )
