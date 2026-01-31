"""Implementation SQLAlchemy du repository CoutMateriel.

FIN-10: Suivi couts materiel - requetes sur les reservations validees.
Utilise text() pour les requetes SQL brutes afin d'eviter les imports
cross-module (Clean Architecture).
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from ...domain.repositories.cout_materiel_repository import (
    CoutMaterielRepository,
)
from ...domain.value_objects.cout_materiel import CoutMaterielItem


class SQLAlchemyCoutMaterielRepository(CoutMaterielRepository):
    """Implementation SQLAlchemy du repository CoutMateriel.

    Utilise des requetes SQL brutes (text()) pour interroger les tables
    reservations et ressources sans importer les modeles d'autres modules.
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
        """Calcule le cout total materiel d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (optionnel).
            date_fin: Date de fin de la periode (optionnel).

        Returns:
            Le cout total en Decimal.
        """
        query = text("""
            SELECT COALESCE(
                SUM(
                    sub.jours * COALESCE(sub.tarif_journalier, 0)
                ), 0
            ) as cout_total
            FROM (
                SELECT r.ressource_id,
                       COUNT(DISTINCT r.date_reservation) as jours,
                       res.tarif_journalier
                FROM reservations r
                JOIN ressources res ON r.ressource_id = res.id
                WHERE r.chantier_id = :chantier_id
                  AND r.statut = 'validee'
                  AND (r.date_reservation >= :date_debut OR :date_debut IS NULL)
                  AND (r.date_reservation <= :date_fin OR :date_fin IS NULL)
                GROUP BY r.ressource_id, res.tarif_journalier
            ) sub
        """)

        result = self._session.execute(
            query,
            {
                "chantier_id": chantier_id,
                "date_debut": date_debut,
                "date_fin": date_fin,
            },
        ).scalar()

        return Decimal(str(result)) if result else Decimal("0")

    def calculer_cout_par_ressource(
        self,
        chantier_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
    ) -> List[CoutMaterielItem]:
        """Calcule le cout materiel par ressource.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (optionnel).
            date_fin: Date de fin de la periode (optionnel).

        Returns:
            Liste des couts par ressource.
        """
        query = text("""
            SELECT r.ressource_id,
                   res.nom,
                   res.code,
                   COUNT(DISTINCT r.date_reservation) as jours,
                   COALESCE(res.tarif_journalier, 0) as tarif_journalier
            FROM reservations r
            JOIN ressources res ON r.ressource_id = res.id
            WHERE r.chantier_id = :chantier_id
              AND r.statut = 'validee'
              AND (r.date_reservation >= :date_debut OR :date_debut IS NULL)
              AND (r.date_reservation <= :date_fin OR :date_fin IS NULL)
            GROUP BY r.ressource_id, res.nom, res.code, res.tarif_journalier
            ORDER BY res.nom
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
            jours = int(row.jours or 0)
            tarif = Decimal(str(row.tarif_journalier or 0))
            cout = Decimal(str(jours)) * tarif

            result.append(
                CoutMaterielItem(
                    ressource_id=row.ressource_id,
                    nom=row.nom or "",
                    code=row.code or "",
                    jours_reservation=jours,
                    tarif_journalier=tarif,
                    cout_total=cout.quantize(Decimal("0.01")),
                )
            )

        return result
