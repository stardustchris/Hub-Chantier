"""Use Case DeleteTache - Suppression d'une tache."""

from typing import Optional, Callable

from ...domain.repositories import TacheRepository
from ...domain.events import TacheDeletedEvent


class DeleteTacheUseCase:
    """
    Cas d'utilisation : Suppression d'une tache et ses sous-taches.

    Attributes:
        tache_repo: Repository pour acceder aux taches.
        event_publisher: Fonction pour publier les events (optionnel).
    """

    def __init__(
        self,
        tache_repo: TacheRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            tache_repo: Repository taches (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.tache_repo = tache_repo
        self.event_publisher = event_publisher

    def execute(self, tache_id: int) -> bool:
        """
        Execute la suppression d'une tache.

        Args:
            tache_id: ID de la tache a supprimer.

        Returns:
            True si supprimee avec succes.

        Raises:
            TacheNotFoundError: Si la tache n'existe pas.
        """
        from .get_tache import TacheNotFoundError

        # Recuperer la tache pour avoir les infos avant suppression
        tache = self.tache_repo.find_by_id(tache_id)
        if not tache:
            raise TacheNotFoundError(tache_id)

        # Sauvegarder les infos pour l'event
        chantier_id = tache.chantier_id
        titre = tache.titre

        # Supprimer (supprime aussi les sous-taches)
        result = self.tache_repo.delete(tache_id)

        # Publier l'event
        if result and self.event_publisher:
            event = TacheDeletedEvent(
                tache_id=tache_id,
                chantier_id=chantier_id,
                titre=titre,
            )
            self.event_publisher(event)

        return result
