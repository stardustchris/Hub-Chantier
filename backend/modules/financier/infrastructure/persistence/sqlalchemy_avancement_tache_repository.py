"""Implementation SQLAlchemy du repository AvancementTache.

FIN-03: Suivi croise avancement physique vs financier.
Utilise text() pour les requetes SQL brutes afin d'eviter les imports
cross-module (Clean Architecture).
"""

from decimal import Decimal
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from ...domain.repositories.avancement_tache_repository import AvancementTacheRepository
from ...domain.value_objects.avancement_tache import AvancementTache


class SQLAlchemyAvancementTacheRepository(AvancementTacheRepository):
    """Implementation SQLAlchemy du repository AvancementTache.

    Utilise des requetes SQL brutes (text()) pour interroger les tables
    taches et pointages sans importer les modeles d'autres modules.
    """

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def get_avancements_chantier(
        self, chantier_id: int
    ) -> List[AvancementTache]:
        """Recupere l'avancement de toutes les taches d'un chantier.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des avancements par tache.
        """
        query = text("""
            SELECT
                t.id as tache_id,
                t.titre,
                t.statut,
                t.heures_estimees,
                COALESCE(
                    (SELECT SUM(p.heures_normales_minutes + p.heures_supplementaires_minutes) / 60.0
                     FROM pointages p
                     WHERE p.tache_id = t.id AND p.statut = 'valide'),
                    0
                ) as heures_realisees,
                t.quantite_estimee,
                COALESCE(t.quantite_realisee, 0) as quantite_realisee,
                CASE
                    WHEN t.statut = 'terminee' THEN 100
                    WHEN t.heures_estimees IS NOT NULL AND t.heures_estimees > 0 THEN
                        LEAST(100, ROUND(
                            COALESCE(
                                (SELECT SUM(p.heures_normales_minutes + p.heures_supplementaires_minutes) / 60.0
                                 FROM pointages p
                                 WHERE p.tache_id = t.id AND p.statut = 'valide'),
                                0
                            ) * 100.0 / t.heures_estimees, 2
                        ))
                    WHEN t.quantite_estimee IS NOT NULL AND t.quantite_estimee > 0 THEN
                        LEAST(100, ROUND(
                            COALESCE(t.quantite_realisee, 0) * 100.0 / t.quantite_estimee, 2
                        ))
                    ELSE 0
                END as progression_pct
            FROM taches t
            WHERE t.chantier_id = :chantier_id
              AND t.deleted_at IS NULL
            ORDER BY t.id
        """)

        rows = self._session.execute(
            query, {"chantier_id": chantier_id}
        ).fetchall()

        return [self._row_to_avancement(row) for row in rows]

    def get_avancement_tache(
        self, tache_id: int
    ) -> Optional[AvancementTache]:
        """Recupere l'avancement d'une tache specifique.

        Args:
            tache_id: L'ID de la tache.

        Returns:
            L'avancement de la tache ou None si non trouvee.
        """
        query = text("""
            SELECT
                t.id as tache_id,
                t.titre,
                t.statut,
                t.heures_estimees,
                COALESCE(
                    (SELECT SUM(p.heures_normales_minutes + p.heures_supplementaires_minutes) / 60.0
                     FROM pointages p
                     WHERE p.tache_id = t.id AND p.statut = 'valide'),
                    0
                ) as heures_realisees,
                t.quantite_estimee,
                COALESCE(t.quantite_realisee, 0) as quantite_realisee,
                CASE
                    WHEN t.statut = 'terminee' THEN 100
                    WHEN t.heures_estimees IS NOT NULL AND t.heures_estimees > 0 THEN
                        LEAST(100, ROUND(
                            COALESCE(
                                (SELECT SUM(p.heures_normales_minutes + p.heures_supplementaires_minutes) / 60.0
                                 FROM pointages p
                                 WHERE p.tache_id = t.id AND p.statut = 'valide'),
                                0
                            ) * 100.0 / t.heures_estimees, 2
                        ))
                    WHEN t.quantite_estimee IS NOT NULL AND t.quantite_estimee > 0 THEN
                        LEAST(100, ROUND(
                            COALESCE(t.quantite_realisee, 0) * 100.0 / t.quantite_estimee, 2
                        ))
                    ELSE 0
                END as progression_pct
            FROM taches t
            WHERE t.id = :tache_id
              AND t.deleted_at IS NULL
        """)

        row = self._session.execute(
            query, {"tache_id": tache_id}
        ).fetchone()

        return self._row_to_avancement(row) if row else None

    def _row_to_avancement(self, row) -> AvancementTache:
        """Convertit une ligne SQL en value object AvancementTache.

        Args:
            row: La ligne SQL.

        Returns:
            Le value object AvancementTache.
        """
        return AvancementTache(
            tache_id=row.tache_id,
            titre=row.titre or "",
            statut=row.statut or "a_faire",
            heures_estimees=Decimal(str(row.heures_estimees)) if row.heures_estimees else None,
            heures_realisees=Decimal(str(row.heures_realisees or 0)),
            quantite_estimee=Decimal(str(row.quantite_estimee)) if row.quantite_estimee else None,
            quantite_realisee=Decimal(str(row.quantite_realisee or 0)),
            progression_pct=Decimal(str(row.progression_pct or 0)),
        )
