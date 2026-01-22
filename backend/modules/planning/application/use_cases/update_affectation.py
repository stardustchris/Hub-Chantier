"""Use Case UpdateAffectation - Mise a jour d'une affectation."""

from typing import Optional, Dict, Any

from ...domain.entities import Affectation
from ...domain.repositories import AffectationRepository
from ...domain.value_objects import HeureAffectation
from ...domain.events import AffectationUpdatedEvent
from ..dtos import UpdateAffectationDTO
from ..ports import EventBus
from .exceptions import AffectationNotFoundError


class UpdateAffectationUseCase:
    """
    Cas d'utilisation : Mise a jour d'une affectation.

    Permet de modifier les horaires, la note ou le chantier d'une affectation.

    Selon CDC Section 5 - Planning Operationnel (PLN-07, PLN-08).

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
        dto: UpdateAffectationDTO,
        updated_by: int,
    ) -> Affectation:
        """
        Execute la mise a jour d'une affectation.

        Seuls les champs fournis dans le DTO seront mis a jour.

        Args:
            affectation_id: ID de l'affectation a mettre a jour.
            dto: Les donnees de mise a jour.
            updated_by: ID de l'utilisateur qui effectue la modification.

        Returns:
            L'affectation mise a jour.

        Raises:
            AffectationNotFoundError: Si l'affectation n'existe pas.
            ValueError: Si les donnees sont invalides.

        Example:
            >>> affectation = use_case.execute(1, dto, updated_by=2)
        """
        # Recuperer l'affectation
        affectation = self.affectation_repo.find_by_id(affectation_id)
        if not affectation:
            raise AffectationNotFoundError(affectation_id)

        # Tracker les modifications pour l'evenement
        changes: Dict[str, Any] = {}

        # Modifier les horaires si fournis
        if dto.heure_debut is not None or dto.heure_fin is not None:
            # Determiner les nouvelles valeurs
            new_heure_debut = (
                HeureAffectation.from_string(dto.heure_debut)
                if dto.heure_debut
                else affectation.heure_debut
            )
            new_heure_fin = (
                HeureAffectation.from_string(dto.heure_fin)
                if dto.heure_fin
                else affectation.heure_fin
            )

            # Appliquer les modifications
            affectation.modifier_horaires(new_heure_debut, new_heure_fin)

            if dto.heure_debut is not None:
                changes["heure_debut"] = dto.heure_debut
            if dto.heure_fin is not None:
                changes["heure_fin"] = dto.heure_fin

        # Modifier la note si fournie
        if dto.note is not None:
            if dto.note.strip():
                affectation.ajouter_note(dto.note)
            else:
                affectation.supprimer_note()
            changes["note"] = dto.note

        # Modifier le chantier si fourni
        if dto.chantier_id is not None:
            affectation.changer_chantier(dto.chantier_id)
            changes["chantier_id"] = dto.chantier_id

        # Sauvegarder
        affectation = self.affectation_repo.save(affectation)

        # Publier l'evenement si des modifications ont ete faites
        if self.event_bus and changes:
            event = AffectationUpdatedEvent(
                affectation_id=affectation.id,
                utilisateur_id=affectation.utilisateur_id,
                chantier_id=affectation.chantier_id,
                changes=changes,
                updated_by=updated_by,
            )
            self.event_bus.publish(event)

        return affectation
