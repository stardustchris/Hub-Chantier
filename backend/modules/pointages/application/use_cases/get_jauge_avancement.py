"""Use Case: Obtenir la jauge d'avancement (FDH-14)."""

from datetime import date, timedelta
from typing import Optional

from ...domain.repositories import PointageRepository
from ..dtos import JaugeAvancementDTO


class GetJaugeAvancementUseCase:
    """
    Calcule la jauge d'avancement planifié vs réalisé.

    Implémente FDH-14: Jauge d'avancement (Comparaison planifié vs réalisé).
    """

    def __init__(self, pointage_repo: PointageRepository):
        """
        Initialise le use case.

        Args:
            pointage_repo: Repository des pointages.
        """
        self.pointage_repo = pointage_repo

    def execute(
        self,
        utilisateur_id: int,
        semaine_debut: date,
        heures_planifiees: Optional[float] = None,
    ) -> JaugeAvancementDTO:
        """
        Calcule l'avancement pour un utilisateur sur une semaine.

        Args:
            utilisateur_id: ID de l'utilisateur.
            semaine_debut: Date du lundi de la semaine.
            heures_planifiees: Heures planifiées (si non fourni, utilise 35h par défaut).

        Returns:
            DTO avec la jauge d'avancement.
        """
        # Assure que c'est un lundi
        if semaine_debut.weekday() != 0:
            days_since_monday = semaine_debut.weekday()
            semaine_debut = semaine_debut - timedelta(days=days_since_monday)

        # Heures planifiées par défaut (35h hebdo standard BTP)
        if heures_planifiees is None:
            heures_planifiees = 35.0

        # Récupère les pointages de la semaine
        pointages = self.pointage_repo.find_by_utilisateur_and_semaine(
            utilisateur_id=utilisateur_id,
            semaine_debut=semaine_debut,
        )

        # Calcule les heures réalisées
        total_minutes = sum(p.total_heures.total_minutes for p in pointages)
        heures_realisees = total_minutes / 60.0

        # Calcule le taux de complétion
        taux_completion = 0.0
        if heures_planifiees > 0:
            taux_completion = (heures_realisees / heures_planifiees) * 100

        # Détermine le statut
        if taux_completion >= 110:
            status = "en_avance"
        elif taux_completion >= 90:
            status = "normal"
        else:
            status = "en_retard"

        iso_cal = semaine_debut.isocalendar()

        return JaugeAvancementDTO(
            utilisateur_id=utilisateur_id,
            semaine=f"Semaine {iso_cal[1]} - {iso_cal[0]}",
            heures_planifiees=heures_planifiees,
            heures_realisees=round(heures_realisees, 2),
            taux_completion=round(taux_completion, 1),
            status=status,
        )
