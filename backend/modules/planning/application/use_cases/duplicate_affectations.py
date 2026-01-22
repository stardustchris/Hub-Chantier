"""Use Case DuplicateAffectations - Duplication d'affectations."""

from datetime import timedelta
from typing import List, Optional

from ...domain.entities import Affectation
from ...domain.repositories import AffectationRepository
from ...domain.events import AffectationBulkCreatedEvent
from ..dtos import DuplicateAffectationsDTO
from ..ports import EventBus
from .exceptions import AffectationConflictError, NoAffectationsToDuplicateError


class DuplicateAffectationsUseCase:
    """
    Cas d'utilisation : Duplication d'affectations.

    Copie les affectations d'un utilisateur d'une periode source
    vers une periode cible en conservant la structure relative des jours.

    Selon CDC Section 5 - Planning Operationnel (PLN-13, PLN-14).

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
        dto: DuplicateAffectationsDTO,
        created_by: int,
    ) -> List[Affectation]:
        """
        Execute la duplication d'affectations.

        Recupere les affectations de la periode source et les duplique
        vers la periode cible avec un decalage de jours.

        Args:
            dto: Les donnees de duplication.
            created_by: ID de l'utilisateur qui cree les duplications.

        Returns:
            Liste des nouvelles affectations creees.

        Raises:
            NoAffectationsToDuplicateError: Si aucune affectation source.
            AffectationConflictError: Si conflit sur une date cible.

        Example:
            >>> affectations = use_case.execute(dto, created_by=1)
            >>> print(f"Duplique {len(affectations)} affectation(s)")
        """
        # Recuperer les affectations source
        source_affectations = self.affectation_repo.find_by_utilisateur(
            dto.utilisateur_id,
            dto.source_date_debut,
            dto.source_date_fin,
        )

        if not source_affectations:
            raise NoAffectationsToDuplicateError(dto.utilisateur_id)

        # Calculer le decalage de jours
        days_offset = dto.days_offset

        # Verifier les conflits pour toutes les dates cibles
        for affectation in source_affectations:
            target_date = affectation.date + timedelta(days=days_offset)
            if self.affectation_repo.exists_for_utilisateur_and_date(
                dto.utilisateur_id, target_date
            ):
                raise AffectationConflictError(dto.utilisateur_id, target_date)

        # Dupliquer les affectations
        new_affectations = []
        for affectation in source_affectations:
            target_date = affectation.date + timedelta(days=days_offset)

            # Utiliser la methode dupliquer de l'entite
            new_affectation = affectation.dupliquer(target_date)

            # Changer le createur
            new_affectation = Affectation(
                utilisateur_id=new_affectation.utilisateur_id,
                chantier_id=new_affectation.chantier_id,
                date=new_affectation.date,
                heure_debut=new_affectation.heure_debut,
                heure_fin=new_affectation.heure_fin,
                note=new_affectation.note,
                type_affectation=new_affectation.type_affectation,
                jours_recurrence=new_affectation.jours_recurrence,
                created_by=created_by,
            )

            # Sauvegarder
            new_affectation = self.affectation_repo.save(new_affectation)
            new_affectations.append(new_affectation)

        # Publier l'evenement bulk
        if self.event_bus and new_affectations:
            # Determiner le chantier majoritaire pour l'evenement
            chantier_ids = [a.chantier_id for a in new_affectations]
            most_common_chantier = max(set(chantier_ids), key=chantier_ids.count)

            target_dates = [a.date for a in new_affectations]

            event = AffectationBulkCreatedEvent(
                affectation_ids=tuple(a.id for a in new_affectations),
                utilisateur_id=dto.utilisateur_id,
                chantier_id=most_common_chantier,
                date_debut=min(target_dates),
                date_fin=max(target_dates),
                created_by=created_by,
                count=len(new_affectations),
            )
            self.event_bus.publish(event)

        return new_affectations
