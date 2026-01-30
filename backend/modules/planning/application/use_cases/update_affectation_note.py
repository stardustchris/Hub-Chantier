"""Use Case: Mettre a jour la note d'une affectation (PLN-25 pour Chef de Chantier)."""

from typing import Optional

from ...domain.entities import Affectation
from ...domain.repositories import AffectationRepository
from ...domain.events import AffectationUpdatedEvent
from ..ports import EventBus
from .exceptions import AffectationNotFoundError


class UpdateAffectationNoteUseCase:
    """
    Met a jour uniquement la note d'une affectation.

    Ce use case est specifiquement concu pour permettre aux Chefs de Chantier
    d'ajouter ou modifier des notes sur les affectations de leurs chantiers,
    sans pouvoir modifier les autres attributs (PLN-25, matrice des droits section 5.5).

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

    def execute(
        self,
        affectation_id: int,
        note: Optional[str],
        modified_by: int,
    ) -> Affectation:
        """
        Met a jour la note d'une affectation.

        Args:
            affectation_id: ID de l'affectation a modifier.
            note: Nouvelle note (None pour supprimer).
            modified_by: ID de l'utilisateur qui modifie.

        Returns:
            L'affectation mise a jour.

        Raises:
            AffectationNotFoundError: Si l'affectation n'existe pas.

        Example:
            >>> result = use_case.execute(
            ...     affectation_id=42,
            ...     note="Apporter outils specifiques",
            ...     modified_by=3
            ... )
        """
        # Recuperer l'affectation
        affectation = self.affectation_repo.find_by_id(affectation_id)
        if not affectation:
            raise AffectationNotFoundError(affectation_id)

        # Recuperer l'ancienne note pour l'evenement
        old_note = affectation.note

        # Mettre a jour la note
        if note is None or note.strip() == "":
            affectation.supprimer_note()
        else:
            affectation.ajouter_note(note)

        # Sauvegarder
        affectation = self.affectation_repo.save(affectation)

        # Publier l'evenement si la note a change
        if self.event_bus and old_note != affectation.note:
            event = AffectationUpdatedEvent(
                affectation_id=affectation.id,
                utilisateur_id=affectation.utilisateur_id,
                chantier_id=affectation.chantier_id,
                changes={"note": {"old": old_note, "new": affectation.note}},
                updated_by=modified_by,
            )
            self.event_bus.publish(event)

        return affectation
