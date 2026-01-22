"""Use Case DeplacerAffectation - Déplacement d'une affectation (Drag & Drop)."""

from datetime import date, datetime
from typing import Optional, Callable

from ...domain.repositories import AffectationRepository
from ...domain.events import AffectationUpdatedEvent
from ..dtos import DeplacerAffectationDTO, AffectationDTO
from .get_affectation import AffectationNotFoundError


class DeplacerAffectationUseCase:
    """
    Cas d'utilisation : Déplacement d'une affectation (PLN-27: Drag & Drop).

    Permet de déplacer une affectation vers une autre date et/ou un autre chantier.

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

    def execute(self, dto: DeplacerAffectationDTO, moved_by: Optional[int] = None) -> AffectationDTO:
        """
        Déplace une affectation vers une nouvelle date/chantier.

        Args:
            dto: Données de déplacement.
            moved_by: ID de l'utilisateur qui déplace.

        Returns:
            AffectationDTO contenant l'affectation déplacée.

        Raises:
            AffectationNotFoundError: Si l'affectation n'existe pas.
        """
        # Récupérer l'affectation existante
        affectation = self.affectation_repo.find_by_id(dto.affectation_id)
        if not affectation:
            raise AffectationNotFoundError(dto.affectation_id)

        # Parser la nouvelle date
        nouvelle_date = date.fromisoformat(dto.nouvelle_date)

        # Utiliser la méthode de l'entité pour déplacer
        affectation_deplacee = affectation.deplacer(
            nouvelle_date=nouvelle_date,
            nouveau_chantier_id=dto.nouveau_chantier_id,
        )

        # Sauvegarder
        affectation_deplacee = self.affectation_repo.save(affectation_deplacee)

        # Publier l'événement
        if self.event_publisher:
            event = AffectationUpdatedEvent(
                affectation_id=affectation_deplacee.id,
                utilisateur_id=affectation_deplacee.utilisateur_id,
                chantier_id=affectation_deplacee.chantier_id,
                date_affectation=affectation_deplacee.date_affectation,
                updated_by=moved_by,
            )
            self.event_publisher(event)

        return AffectationDTO.from_entity(affectation_deplacee)
