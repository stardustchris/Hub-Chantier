"""Use Case: Corriger un pointage rejeté."""

from typing import Optional

from ...domain.entities import Pointage
from ...domain.repositories import PointageRepository
from ...domain.value_objects import PeriodePaie
from ..dtos import PointageDTO
from ..ports import EventBus, NullEventBus


class CorrectPointageUseCase:
    """
    Repasse un pointage REJETÉ en BROUILLON pour correction.

    Selon le workflow § 5.5 (Rejet et correction), après un rejet,
    le compagnon peut reprendre son pointage pour le corriger.

    Le pointage passe de REJETÉ → BROUILLON et peut être modifié,
    re-signé et re-soumis.
    """

    def __init__(
        self,
        pointage_repo: PointageRepository,
        event_bus: Optional[EventBus] = None,
    ):
        """
        Initialise le use case.

        Args:
            pointage_repo: Repository des pointages.
            event_bus: Bus d'événements (optionnel).
        """
        self.pointage_repo = pointage_repo
        self.event_bus = event_bus or NullEventBus()

    def execute(self, pointage_id: int) -> PointageDTO:
        """
        Exécute la correction d'un pointage rejeté.

        Args:
            pointage_id: ID du pointage à corriger.

        Returns:
            Le DTO du pointage remis en brouillon.

        Raises:
            ValueError: Si le pointage n'existe pas, n'est pas REJETÉ,
                       ou si la période de paie est verrouillée.
        """
        # Récupère le pointage
        pointage = self.pointage_repo.find_by_id(pointage_id)
        if not pointage:
            raise ValueError(f"Pointage {pointage_id} non trouvé")

        # Vérifie le verrouillage mensuel (CRITIQUE GAP-FDH-002)
        if PeriodePaie.is_locked(pointage.date_pointage):
            raise ValueError(
                "La période de paie est verrouillée. "
                "Impossible de corriger un pointage après la clôture mensuelle."
            )

        # Corrige le pointage (REJETE → BROUILLON)
        # La méthode corriger() de l'entité vérifie que le statut est REJETÉ
        pointage.corriger()

        # Persiste
        pointage = self.pointage_repo.save(pointage)

        # Pas d'événement publié pour la correction
        # (action interne au workflow, pas d'impact sur d'autres modules)

        return self._to_dto(pointage)

    def _to_dto(self, pointage: Pointage) -> PointageDTO:
        """
        Convertit l'entité Pointage en DTO.

        Args:
            pointage: L'entité Pointage.

        Returns:
            Le DTO correspondant.
        """
        return PointageDTO(
            id=pointage.id,
            utilisateur_id=pointage.utilisateur_id,
            chantier_id=pointage.chantier_id,
            date_pointage=pointage.date_pointage,
            heures_normales=str(pointage.heures_normales),
            heures_supplementaires=str(pointage.heures_supplementaires),
            total_heures=str(pointage.total_heures),
            total_heures_decimal=pointage.total_heures_decimal,
            statut=pointage.statut.value,
            commentaire=pointage.commentaire,
            signature_utilisateur=pointage.signature_utilisateur,
            signature_date=pointage.signature_date,
            validateur_id=pointage.validateur_id,
            validation_date=pointage.validation_date,
            motif_rejet=pointage.motif_rejet,
            affectation_id=pointage.affectation_id,
            created_by=pointage.created_by,
            created_at=pointage.created_at,
            updated_at=pointage.updated_at,
            utilisateur_nom=pointage.utilisateur_nom,
            chantier_nom=pointage.chantier_nom,
            chantier_couleur=pointage.chantier_couleur,
        )
