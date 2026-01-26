"""Use Case GetTacheStats - Statistiques des taches d'un chantier."""

from ...domain.repositories import TacheRepository
from ..dtos import TacheStatsDTO


class GetTacheStatsUseCase:
    """
    Cas d'utilisation : Obtenir les statistiques des taches.

    Selon CDC Section 13 - TAC-20: Code couleur avancement.

    Attributes:
        tache_repo: Repository pour les taches.
    """

    def __init__(self, tache_repo: TacheRepository):
        """
        Initialise le use case.

        Args:
            tache_repo: Repository taches (interface).
        """
        self.tache_repo = tache_repo

    def execute(self, chantier_id: int) -> TacheStatsDTO:
        """
        Calcule les statistiques des taches d'un chantier.

        Args:
            chantier_id: ID du chantier.

        Returns:
            TacheStatsDTO avec les statistiques.
        """
        stats = self.tache_repo.get_stats_chantier(chantier_id)

        # Calculer la progression globale
        heures_estimees = stats.get("heures_estimees_total", 0) or 0
        heures_realisees = stats.get("heures_realisees_total", 0) or 0
        total_taches = stats.get("total", 0) or 0
        taches_terminees = stats.get("terminees", 0) or 0

        progression_globale = 0.0
        if heures_realisees > 0 and heures_estimees > 0:
            # Progression basee sur les heures si des heures ont ete saisies
            progression_globale = min((heures_realisees / heures_estimees) * 100, 100.0)
        elif total_taches > 0:
            # Fallback: progression basee sur le nombre de taches terminees
            progression_globale = (taches_terminees / total_taches) * 100

        return TacheStatsDTO(
            chantier_id=chantier_id,
            total_taches=stats.get("total", 0),
            taches_terminees=stats.get("terminees", 0),
            taches_en_cours=stats.get("en_cours", 0),
            taches_en_retard=stats.get("en_retard", 0),
            heures_estimees_total=heures_estimees,
            heures_realisees_total=heures_realisees,
            progression_globale=progression_globale,
        )
