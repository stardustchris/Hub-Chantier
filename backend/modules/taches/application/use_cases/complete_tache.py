"""Use Case CompleteTache - Marquer une tache comme terminee (TAC-13)."""

from typing import Optional, Callable

from ...domain.repositories import TacheRepository
from ...domain.events import TacheTermineeEvent
from ..dtos import TacheDTO


class CompleteTacheUseCase:
    """
    Cas d'utilisation : Marquer une tache comme terminee.

    Selon CDC Section 13 - TAC-13: Statuts tache (A faire / Termine).

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

    def execute(self, tache_id: int, terminer: bool = True) -> TacheDTO:
        """
        Execute le changement de statut.

        Args:
            tache_id: ID de la tache.
            terminer: True pour terminer, False pour rouvrir.

        Returns:
            TacheDTO de la tache mise a jour.

        Raises:
            TacheNotFoundError: Si la tache n'existe pas.
        """
        from .get_tache import TacheNotFoundError

        # Recuperer la tache
        tache = self.tache_repo.find_by_id(tache_id)
        if not tache:
            raise TacheNotFoundError(tache_id)

        # Changer le statut
        if terminer:
            tache.terminer()
        else:
            tache.rouvrir()

        # Sauvegarder
        tache = self.tache_repo.save(tache)

        # Publier l'event si terminee
        if terminer and self.event_publisher:
            event = TacheTermineeEvent(
                tache_id=tache.id,
                chantier_id=tache.chantier_id,
                titre=tache.titre,
                heures_realisees=tache.heures_realisees,
                quantite_realisee=tache.quantite_realisee,
            )
            self.event_publisher(event)

        return TacheDTO.from_entity(tache)
