"""Implementation SQLAlchemy du repository CoutMainOeuvre.

FIN-09: Suivi couts main-d'oeuvre - requetes sur les pointages valides.
Utilise text() pour les requetes SQL brutes afin d'eviter les imports
cross-module (Clean Architecture).
"""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from shared.domain.calcul_financier import COEFF_HEURES_SUP, COEFF_HEURES_SUP_2

from ...domain.repositories.cout_main_oeuvre_repository import (
    CoutMainOeuvreRepository,
)
from ...domain.value_objects.cout_employe import CoutEmploye


class SQLAlchemyCoutMainOeuvreRepository(CoutMainOeuvreRepository):
    """Implementation SQLAlchemy du repository CoutMainOeuvre.

    Utilise des requetes SQL brutes (text()) pour interroger les tables
    pointages et users sans importer les modeles d'autres modules.
    """

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def calculer_cout_chantier(
        self,
        chantier_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
    ) -> Decimal:
        """Calcule le cout total main-d'oeuvre d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (optionnel).
            date_fin: Date de fin de la periode (optionnel).

        Returns:
            Le cout total en Decimal.
        """
        # Art. L3121-36 Code du travail : 2 paliers heures sup par employe.
        # Palier 1 : 8 premieres heures sup (480 min) a +25% (COEFF_HEURES_SUP).
        # Palier 2 : au-dela a +50% (COEFF_HEURES_SUP_2).
        # Note : approximation sur la periode (pas par semaine). Pour un calcul
        # exact semaine par semaine, un module de paie serait necessaire.
        query = text("""
            SELECT COALESCE(SUM(emp_cost), 0) as cout_total
            FROM (
                SELECT
                    p.utilisateur_id,
                    (SUM(p.heures_normales_minutes) / 60::numeric
                        * COALESCE(u.taux_horaire, 0))
                    + (LEAST(SUM(p.heures_supplementaires_minutes), 480) / 60::numeric
                        * COALESCE(u.taux_horaire, 0) * :coeff_hs_1::numeric)
                    + (GREATEST(SUM(p.heures_supplementaires_minutes) - 480, 0) / 60::numeric
                        * COALESCE(u.taux_horaire, 0) * :coeff_hs_2::numeric)
                    as emp_cost
                FROM pointages p
                JOIN users u ON p.utilisateur_id = u.id
                WHERE p.chantier_id = :chantier_id
                  AND p.statut = 'valide'
                  AND (p.date_pointage >= :date_debut OR :date_debut IS NULL)
                  AND (p.date_pointage <= :date_fin OR :date_fin IS NULL)
                GROUP BY p.utilisateur_id, u.taux_horaire
            ) employee_costs
        """)

        result = self._session.execute(
            query,
            {
                "chantier_id": chantier_id,
                "date_debut": date_debut,
                "date_fin": date_fin,
                "coeff_hs_1": str(COEFF_HEURES_SUP),
                "coeff_hs_2": str(COEFF_HEURES_SUP_2),
            },
        ).scalar()

        return Decimal(str(result)) if result else Decimal("0")

    def calculer_cout_par_employe(
        self,
        chantier_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
    ) -> List[CoutEmploye]:
        """Calcule le cout main-d'oeuvre par employe.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (optionnel).
            date_fin: Date de fin de la periode (optionnel).

        Returns:
            Liste des couts par employe.
        """
        query = text("""
            SELECT p.utilisateur_id,
                   u.nom,
                   u.prenom,
                   SUM(p.heures_normales_minutes) as total_normales_minutes,
                   SUM(p.heures_supplementaires_minutes) as total_sup_minutes,
                   COALESCE(u.taux_horaire, 0) as taux_horaire
            FROM pointages p
            JOIN users u ON p.utilisateur_id = u.id
            WHERE p.chantier_id = :chantier_id
              AND p.statut = 'valide'
              AND (p.date_pointage >= :date_debut OR :date_debut IS NULL)
              AND (p.date_pointage <= :date_fin OR :date_fin IS NULL)
            GROUP BY p.utilisateur_id, u.nom, u.prenom, u.taux_horaire
            ORDER BY u.nom, u.prenom
        """)

        rows = self._session.execute(
            query,
            {
                "chantier_id": chantier_id,
                "date_debut": date_debut,
                "date_fin": date_fin,
            },
        ).fetchall()

        result = []
        for row in rows:
            normales_minutes = Decimal(str(row.total_normales_minutes or 0))
            sup_minutes = Decimal(str(row.total_sup_minutes or 0))
            heures_normales = normales_minutes / Decimal("60")
            heures_sup = sup_minutes / Decimal("60")
            heures = heures_normales + heures_sup
            taux = Decimal(str(row.taux_horaire or 0))

            # Palier heures sup (art. L3121-36 Code du travail)
            # - 8 premieres heures sup/semaine (36h-43h): +25% (COEFF_HEURES_SUP = 1.25)
            # - Au-dela de 43h/semaine: +50% (COEFF_HEURES_SUP_2 = 1.50)
            # Note: approximation - les totaux sont cumules sur la periode, pas par semaine.
            # Pour un calcul exact par semaine, un module de paie serait necessaire.
            seuil_palier1_min = Decimal("480")  # 8h * 60 = 480 min
            if sup_minutes <= seuil_palier1_min:
                cout_sup = (sup_minutes / Decimal("60")) * taux * COEFF_HEURES_SUP
            else:
                heures_palier1 = seuil_palier1_min / Decimal("60")
                heures_palier2 = (sup_minutes - seuil_palier1_min) / Decimal("60")
                cout_sup = (heures_palier1 * taux * COEFF_HEURES_SUP) + (heures_palier2 * taux * COEFF_HEURES_SUP_2)
            cout = (heures_normales * taux) + cout_sup

            result.append(
                CoutEmploye(
                    user_id=row.utilisateur_id,
                    nom=row.nom or "",
                    prenom=row.prenom or "",
                    heures_validees=heures.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                    taux_horaire=taux,
                    cout_total=cout.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                )
            )

        return result
