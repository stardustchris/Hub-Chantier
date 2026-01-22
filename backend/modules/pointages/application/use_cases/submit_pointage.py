"""Use Case: Soumettre un pointage pour validation."""

from typing import Optional

from ...domain.entities import Pointage
from ...domain.repositories import PointageRepository
from ...domain.events import PointageSubmittedEvent
from ..dtos import PointageDTO
from ..ports import EventBus, NullEventBus


class SubmitPointageUseCase:
    """
    Soumet un pointage pour validation.

    Le pointage passe du statut BROUILLON à SOUMIS.
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
        Exécute la soumission d'un pointage.

        Args:
            pointage_id: ID du pointage à soumettre.

        Returns:
            Le DTO du pointage soumis.

        Raises:
            ValueError: Si le pointage n'existe pas ou ne peut pas être soumis.
        """
        # Récupère le pointage
        pointage = self.pointage_repo.find_by_id(pointage_id)
        if not pointage:
            raise ValueError(f"Pointage {pointage_id} non trouvé")

        # Soumet le pointage
        pointage.soumettre()

        # Persiste
        pointage = self.pointage_repo.save(pointage)

        # Publie l'événement
        event = PointageSubmittedEvent(
            pointage_id=pointage.id,
            utilisateur_id=pointage.utilisateur_id,
            chantier_id=pointage.chantier_id,
            date_pointage=pointage.date_pointage,
        )
        self.event_bus.publish(event)

        return self._to_dto(pointage)

    def _to_dto(self, pointage: Pointage) -> PointageDTO:
        """Convertit l'entité en DTO."""
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
