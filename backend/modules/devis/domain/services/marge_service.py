"""Service de resolution des marges multi-niveaux.

DEV-06: Gestion marges et coefficients.
Regle de priorite: ligne > lot > type debourse > global.

Ce service encapsule la logique metier de resolution de marge
pour etre reutilise par les use cases de calcul et de lecture.
"""

from decimal import Decimal
from typing import Dict, List, Optional

from ..entities.devis import Devis
from ..entities.debourse_detail import DebourseDetail
from ..value_objects import TypeDebourse


class MargeResolue:
    """Resultat de la resolution de marge avec tracabilite du niveau."""

    def __init__(self, taux: Decimal, niveau: str):
        """Initialise le resultat de resolution de marge.

        Args:
            taux: Le taux de marge resolu en pourcentage.
            niveau: Le niveau de la hierarchie qui a fourni la marge
                    ("ligne", "lot", "type_debourse", "global").
        """
        self.taux = taux
        self.niveau = niveau

    def __repr__(self) -> str:
        return f"MargeResolue(taux={self.taux}%, niveau='{self.niveau}')"


class MargeService:
    """Service domain pour la resolution des marges multi-niveaux.

    Implemente la regle de priorite DEV-06:
    1. Marge ligne (si definie) - priorite maximale
    2. Marge lot (si definie)
    3. Marge par type de debourse (si definie sur le devis)
    4. Marge globale du devis - priorite minimale
    """

    @staticmethod
    def resoudre_marge(
        ligne_marge: Optional[Decimal],
        lot_marge: Optional[Decimal],
        devis: Devis,
        debourses: Optional[List[DebourseDetail]] = None,
    ) -> MargeResolue:
        """Resout la marge applicable selon la hierarchie de priorite.

        Args:
            ligne_marge: Marge definie sur la ligne (None = non definie).
            lot_marge: Marge definie sur le lot (None = non definie).
            devis: Le devis contenant la marge globale et les marges par type.
            debourses: Les debourses de la ligne (pour determiner le type principal).

        Returns:
            MargeResolue avec le taux et le niveau de resolution.
        """
        # 1. Marge ligne (priorite 1)
        if ligne_marge is not None:
            return MargeResolue(taux=ligne_marge, niveau="ligne")

        # 2. Marge lot (priorite 2)
        if lot_marge is not None:
            return MargeResolue(taux=lot_marge, niveau="lot")

        # 3. Marge par type de debourse (priorite 3)
        if debourses:
            type_principal = MargeService._get_type_principal(debourses)
            marge_type = MargeService._get_marge_by_type(devis, type_principal)
            if marge_type is not None:
                return MargeResolue(taux=marge_type, niveau="type_debourse")

        # 4. Marge globale (priorite 4)
        return MargeResolue(taux=devis.taux_marge_global, niveau="global")

    @staticmethod
    def _get_type_principal(debourses: List[DebourseDetail]) -> Optional[TypeDebourse]:
        """Determine le type de debourse principal (le plus cher).

        Args:
            debourses: Liste des debourses de la ligne.

        Returns:
            Le type de debourse avec le montant le plus eleve, ou None.
        """
        if not debourses:
            return None

        type_totaux: Dict[TypeDebourse, Decimal] = {}
        for d in debourses:
            montant = d.quantite * d.prix_unitaire
            type_totaux[d.type_debourse] = (
                type_totaux.get(d.type_debourse, Decimal("0")) + montant
            )

        if type_totaux:
            return max(type_totaux, key=type_totaux.get)
        return None

    @staticmethod
    def _get_marge_by_type(
        devis: Devis, type_debourse: Optional[TypeDebourse]
    ) -> Optional[Decimal]:
        """Recupere la marge configuree pour un type de debourse sur le devis.

        Args:
            devis: Le devis contenant les marges par type.
            type_debourse: Le type de debourse.

        Returns:
            Le taux de marge configure ou None si non defini.
        """
        if type_debourse is None:
            return None
        mapping = {
            TypeDebourse.MOE: devis.taux_marge_moe,
            TypeDebourse.MATERIAUX: devis.taux_marge_materiaux,
            TypeDebourse.SOUS_TRAITANCE: devis.taux_marge_sous_traitance,
            TypeDebourse.MATERIEL: devis.taux_marge_materiel,
            TypeDebourse.DEPLACEMENT: devis.taux_marge_deplacement,
        }
        return mapping.get(type_debourse)

    @staticmethod
    def calculer_prix_revient(
        debourse_sec: Decimal,
        coefficient_frais_generaux: Decimal,
    ) -> Decimal:
        """Calcule le prix de revient a partir du debourse sec.

        Formule: Prix de revient = Debourse sec * (1 + coeff_fg / 100)

        Args:
            debourse_sec: Le debourse sec total.
            coefficient_frais_generaux: Le coefficient de frais generaux en %.

        Returns:
            Le prix de revient.
        """
        return debourse_sec * (Decimal("1") + coefficient_frais_generaux / Decimal("100"))

    @staticmethod
    def calculer_prix_vente_ht(
        prix_revient: Decimal,
        taux_marge: Decimal,
    ) -> Decimal:
        """Calcule le prix de vente HT a partir du prix de revient.

        Formule: Prix de vente HT = Prix de revient * (1 + taux_marge / 100)

        Args:
            prix_revient: Le prix de revient.
            taux_marge: Le taux de marge en %.

        Returns:
            Le prix de vente HT.
        """
        return prix_revient * (Decimal("1") + taux_marge / Decimal("100"))
