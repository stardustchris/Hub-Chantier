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

from shared.domain.calcul_financier import COEFF_HEURES_SUP, COEFF_HEURES_SUP_2, COEFF_CHARGES_PATRONALES

from ...domain.repositories.cout_main_oeuvre_repository import (
    CoutMainOeuvreRepository,
)
from ...domain.repositories.configuration_entreprise_repository import (
    ConfigurationEntrepriseRepository,
)
from ...domain.value_objects.cout_employe import CoutEmploye


class SQLAlchemyCoutMainOeuvreRepository(CoutMainOeuvreRepository):
    """Implementation SQLAlchemy du repository CoutMainOeuvre.

    Utilise des requetes SQL brutes (text()) pour interroger les tables
    pointages et users sans importer les modeles d'autres modules.

    Les coefficients (charges patronales, heures sup) sont lus depuis
    ConfigurationEntreprise (BDD) si disponible, sinon fallback sur
    les constantes de calcul_financier.py.
    """

    def __init__(
        self,
        session: Session,
        config_repository: Optional[ConfigurationEntrepriseRepository] = None,
    ):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
            config_repository: Repository config entreprise pour coefficients (SSOT).
        """
        self._session = session
        self._config_repository = config_repository

    def _get_coefficients(self) -> tuple:
        """Recupere les coefficients MO depuis la config entreprise (SSOT).

        Returns:
            Tuple (coeff_charges, coeff_hs_1, coeff_hs_2).
        """
        coeff_charges = COEFF_CHARGES_PATRONALES
        coeff_hs_1 = COEFF_HEURES_SUP
        coeff_hs_2 = COEFF_HEURES_SUP_2

        if self._config_repository:
            from datetime import datetime
            config = self._config_repository.find_by_annee(datetime.now().year)
            if config:
                coeff_charges = config.coeff_charges_patronales
                coeff_hs_1 = config.coeff_heures_sup
                coeff_hs_2 = config.coeff_heures_sup_2

        return coeff_charges, coeff_hs_1, coeff_hs_2

    def calculer_cout_chantier(
        self,
        chantier_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
    ) -> Decimal:
        """Calcule le cout total main-d'oeuvre d'un chantier.

        Art. L3121-36 Code du travail : les heures sup se decompent PAR SEMAINE.
        - Palier 1 : 8 premieres heures sup/semaine (480 min) a +25%.
        - Palier 2 : au-dela de 43h/semaine a +50%.
        Le GROUP BY inclut date_trunc('week') pour un calcul conforme.

        Le coefficient de charges patronales (x1.45) est applique au taux horaire
        pour obtenir le cout employeur reel.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (optionnel).
            date_fin: Date de fin de la periode (optionnel).

        Returns:
            Le cout total en Decimal.
        """
        query = text("""
            SELECT COALESCE(SUM(week_cost), 0) as cout_total
            FROM (
                SELECT
                    p.utilisateur_id,
                    date_trunc('week', p.date_pointage) as semaine,
                    (SUM(p.heures_normales_minutes) / 60::numeric
                        * COALESCE(u.taux_horaire, 0) * CAST(:coeff_charges AS numeric))
                    + (LEAST(SUM(p.heures_supplementaires_minutes), 480) / 60::numeric
                        * COALESCE(u.taux_horaire, 0) * CAST(:coeff_charges AS numeric) * CAST(:coeff_hs_1 AS numeric))
                    + (GREATEST(SUM(p.heures_supplementaires_minutes) - 480, 0) / 60::numeric
                        * COALESCE(u.taux_horaire, 0) * CAST(:coeff_charges AS numeric) * CAST(:coeff_hs_2 AS numeric))
                    as week_cost
                FROM pointages p
                JOIN users u ON p.utilisateur_id = u.id
                WHERE p.chantier_id = :chantier_id
                  AND p.statut = 'valide'
                  AND (p.date_pointage >= :date_debut OR :date_debut IS NULL)
                  AND (p.date_pointage <= :date_fin OR :date_fin IS NULL)
                GROUP BY p.utilisateur_id, u.taux_horaire,
                         date_trunc('week', p.date_pointage)
            ) weekly_costs
        """)

        coeff_charges, coeff_hs_1, coeff_hs_2 = self._get_coefficients()

        result = self._session.execute(
            query,
            {
                "chantier_id": chantier_id,
                "date_debut": date_debut,
                "date_fin": date_fin,
                "coeff_charges": str(coeff_charges),
                "coeff_hs_1": str(coeff_hs_1),
                "coeff_hs_2": str(coeff_hs_2),
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

        Art. L3121-36 : calcul des heures sup par semaine puis agregation
        par employe pour le total. Chaque semaine a son propre seuil de
        480 min (8h) pour le palier 1.

        Le coefficient de charges patronales (x1.45) est applique au taux horaire
        pour obtenir le cout employeur reel.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (optionnel).
            date_fin: Date de fin de la periode (optionnel).

        Returns:
            Liste des couts par employe.
        """
        # Etape 1 : calculer le cout par employe par semaine (avec charges patronales)
        # Etape 2 : agreger par employe (SUM des couts hebdo)
        query = text("""
            SELECT
                utilisateur_id,
                nom,
                prenom,
                SUM(week_normales_min) as total_normales_minutes,
                SUM(week_sup_min) as total_sup_minutes,
                taux_horaire,
                SUM(week_cost) as cout_total
            FROM (
                SELECT
                    p.utilisateur_id,
                    u.nom,
                    u.prenom,
                    COALESCE(u.taux_horaire, 0) as taux_horaire,
                    date_trunc('week', p.date_pointage) as semaine,
                    SUM(p.heures_normales_minutes) as week_normales_min,
                    SUM(p.heures_supplementaires_minutes) as week_sup_min,
                    (SUM(p.heures_normales_minutes) / 60::numeric
                        * COALESCE(u.taux_horaire, 0) * CAST(:coeff_charges AS numeric))
                    + (LEAST(SUM(p.heures_supplementaires_minutes), 480) / 60::numeric
                        * COALESCE(u.taux_horaire, 0) * CAST(:coeff_charges AS numeric) * CAST(:coeff_hs_1 AS numeric))
                    + (GREATEST(SUM(p.heures_supplementaires_minutes) - 480, 0) / 60::numeric
                        * COALESCE(u.taux_horaire, 0) * CAST(:coeff_charges AS numeric) * CAST(:coeff_hs_2 AS numeric))
                    as week_cost
                FROM pointages p
                JOIN users u ON p.utilisateur_id = u.id
                WHERE p.chantier_id = :chantier_id
                  AND p.statut = 'valide'
                  AND (p.date_pointage >= :date_debut OR :date_debut IS NULL)
                  AND (p.date_pointage <= :date_fin OR :date_fin IS NULL)
                GROUP BY p.utilisateur_id, u.nom, u.prenom, u.taux_horaire,
                         date_trunc('week', p.date_pointage)
            ) weekly
            GROUP BY utilisateur_id, nom, prenom, taux_horaire
            ORDER BY nom, prenom
        """)

        coeff_charges, coeff_hs_1, coeff_hs_2 = self._get_coefficients()

        rows = self._session.execute(
            query,
            {
                "chantier_id": chantier_id,
                "date_debut": date_debut,
                "date_fin": date_fin,
                "coeff_charges": str(coeff_charges),
                "coeff_hs_1": str(coeff_hs_1),
                "coeff_hs_2": str(coeff_hs_2),
            },
        ).fetchall()

        result = []
        for row in rows:
            normales_minutes = Decimal(str(row.total_normales_minutes or 0))
            sup_minutes = Decimal(str(row.total_sup_minutes or 0))
            heures = (normales_minutes + sup_minutes) / Decimal("60")
            taux = Decimal(str(row.taux_horaire or 0))
            taux_charge = taux * coeff_charges
            cout = Decimal(str(row.cout_total or 0))

            result.append(
                CoutEmploye(
                    user_id=row.utilisateur_id,
                    nom=row.nom or "",
                    prenom=row.prenom or "",
                    heures_validees=heures.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                    taux_horaire=taux,
                    taux_horaire_charge=taux_charge.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                    cout_total=cout.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                )
            )

        return result
