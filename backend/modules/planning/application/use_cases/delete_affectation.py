"""Use Case DeleteAffectation - Suppression d'une affectation."""

from typing import Optional, Callable

from ...domain.repositories import AffectationRepository
from ...domain.events import AffectationDeletedEvent
from .get_affectation import AffectationNotFoundError


class DeleteAffectationUseCase:
    """
    Cas d'utilisation : Suppression d'une affectation.

    Attributes:
        affectation_repo: Repository pour accéder aux affectations.
        event_publisher: Fonction pour publier les events (optionnel).
    """

    def __init__(
        self,
        affectation_repo: AffectationRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            affectation_repo: Repository affectations (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.affectation_repo = affectation_repo
        self.event_publisher = event_publisher

    def execute(self, affectation_id: int, deleted_by: Optional[int] = None) -> dict:
        """
        Supprime une affectation.

        Args:
            affectation_id: ID de l'affectation à supprimer.
            deleted_by: ID de l'utilisateur qui supprime.

        Returns:
            Dict avec confirmation de suppression.

        Raises:
            AffectationNotFoundError: Si l'affectation n'existe pas.
        """
        # Récupérer l'affectation pour les infos de l'événement
        affectation = self.affectation_repo.find_by_id(affectation_id)
        if not affectation:
            raise AffectationNotFoundError(affectation_id)

        # Supprimer
        deleted = self.affectation_repo.delete(affectation_id)

        if not deleted:
            raise AffectationNotFoundError(affectation_id)

        # Publier l'événement
        if self.event_publisher:
            event = AffectationDeletedEvent(
                affectation_id=affectation_id,
                utilisateur_id=affectation.utilisateur_id,
                chantier_id=affectation.chantier_id,
                date_affectation=affectation.date_affectation,
                deleted_by=deleted_by,
            )
            self.event_publisher(event)

        return {
            "deleted": True,
            "id": affectation_id,
        }
