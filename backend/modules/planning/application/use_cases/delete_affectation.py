"""Use Case DeleteAffectation - Suppression d'une affectation."""

from typing import Optional

from ...domain.repositories import AffectationRepository
from ...domain.events import AffectationDeletedEvent
from ..ports import EventBus
from .exceptions import AffectationNotFoundError


class DeleteAffectationUseCase:
    """
    Cas d'utilisation : Suppression d'une affectation.

    Supprime une affectation existante et publie un evenement.

    Selon CDC Section 5 - Planning Operationnel (PLN-09).

    Attributes:
        affectation_repo: Repository pour acceder aux affectations.
        event_bus: Bus d'evenements pour publier les domain events.
    """

    def __init__(
        self,
        affectation_repo: AffectationRepository,
        event_bus: Optional[EventBus] = None,
    ):
        """
        Initialise le use case.

        Args:
            affectation_repo: Repository affectations (interface).
            event_bus: Bus d'evenements (optionnel).
        """
        self.affectation_repo = affectation_repo
        self.event_bus = event_bus

    def execute(self, affectation_id: int, deleted_by: int) -> bool:
        """
        Execute la suppression d'une affectation.

        Args:
            affectation_id: ID de l'affectation a supprimer.
            deleted_by: ID de l'utilisateur qui supprime l'affectation.

        Returns:
            True si l'affectation a ete supprimee.

        Raises:
            AffectationNotFoundError: Si l'affectation n'existe pas.

        Example:
            >>> success = use_case.execute(1, deleted_by=2)
            >>> print("Supprimee" if success else "Echec")
        """
        # Recuperer l'affectation pour les donnees de l'evenement
        affectation = self.affectation_repo.find_by_id(affectation_id)
        if not affectation:
            raise AffectationNotFoundError(affectation_id)

        # Sauvegarder les infos avant suppression pour l'evenement
        utilisateur_id = affectation.utilisateur_id
        chantier_id = affectation.chantier_id
        date_affectation = affectation.date

        # Supprimer
        success = self.affectation_repo.delete(affectation_id)

        # Publier l'evenement
        if self.event_bus and success:
            event = AffectationDeletedEvent(
                affectation_id=affectation_id,
                utilisateur_id=utilisateur_id,
                chantier_id=chantier_id,
                date=date_affectation,
                deleted_by=deleted_by,
            )
            self.event_bus.publish(event)

        return success
