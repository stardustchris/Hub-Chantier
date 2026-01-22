"""Use Case: Supprimer un pointage."""

from typing import Optional

from ...domain.repositories import PointageRepository
from ...domain.events import PointageDeletedEvent
from ..ports import EventBus, NullEventBus


class DeletePointageUseCase:
    """
    Supprime un pointage.

    Seuls les pointages en brouillon peuvent être supprimés.
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

    def execute(self, pointage_id: int, deleted_by: int) -> bool:
        """
        Exécute la suppression d'un pointage.

        Args:
            pointage_id: ID du pointage à supprimer.
            deleted_by: ID de l'utilisateur qui supprime.

        Returns:
            True si supprimé avec succès.

        Raises:
            ValueError: Si le pointage n'existe pas ou ne peut pas être supprimé.
        """
        # Récupère le pointage
        pointage = self.pointage_repo.find_by_id(pointage_id)
        if not pointage:
            raise ValueError(f"Pointage {pointage_id} non trouvé")

        # Vérifie qu'il est en brouillon
        if not pointage.is_editable:
            raise ValueError(
                f"Seuls les pointages en brouillon ou rejetés peuvent être supprimés "
                f"(statut actuel: {pointage.statut.value})"
            )

        # Supprime
        self.pointage_repo.delete(pointage_id)

        # Publie l'événement
        event = PointageDeletedEvent(
            pointage_id=pointage_id,
            utilisateur_id=pointage.utilisateur_id,
            chantier_id=pointage.chantier_id,
            date_pointage=pointage.date_pointage,
            deleted_by=deleted_by,
        )
        self.event_bus.publish(event)

        return True
