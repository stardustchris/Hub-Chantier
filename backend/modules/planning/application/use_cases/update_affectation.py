"""Use Case UpdateAffectation - Mise à jour d'une affectation."""

from datetime import date, time, datetime
from typing import Optional, Callable

from ...domain.entities import Affectation
from ...domain.repositories import AffectationRepository
from ...domain.value_objects import CreneauHoraire
from ...domain.events import AffectationUpdatedEvent
from ..dtos import UpdateAffectationDTO, AffectationDTO
from .get_affectation import AffectationNotFoundError


class UpdateAffectationUseCase:
    """
    Cas d'utilisation : Mise à jour d'une affectation existante.

    Permet de modifier les propriétés d'une affectation.

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

    def execute(self, dto: UpdateAffectationDTO, updated_by: Optional[int] = None) -> AffectationDTO:
        """
        Met à jour une affectation.

        Args:
            dto: Données de mise à jour.
            updated_by: ID de l'utilisateur qui modifie.

        Returns:
            AffectationDTO contenant l'affectation mise à jour.

        Raises:
            AffectationNotFoundError: Si l'affectation n'existe pas.
        """
        # Récupérer l'affectation existante
        affectation = self.affectation_repo.find_by_id(dto.affectation_id)
        if not affectation:
            raise AffectationNotFoundError(dto.affectation_id)

        # Construire la nouvelle affectation avec les valeurs modifiées
        new_chantier_id = dto.chantier_id or affectation.chantier_id
        new_date = (
            date.fromisoformat(dto.date_affectation)
            if dto.date_affectation
            else affectation.date_affectation
        )

        # Construire le nouveau créneau si modifié
        new_creneau = affectation.creneau
        if dto.heure_debut is not None or dto.heure_fin is not None:
            heure_debut = None
            heure_fin = None

            if dto.heure_debut:
                heure_debut = self._parse_time(dto.heure_debut, "heure_debut")
            elif affectation.creneau and affectation.creneau.heure_debut:
                heure_debut = affectation.creneau.heure_debut

            if dto.heure_fin:
                heure_fin = self._parse_time(dto.heure_fin, "heure_fin")
            elif affectation.creneau and affectation.creneau.heure_fin:
                heure_fin = affectation.creneau.heure_fin

            if heure_debut or heure_fin:
                new_creneau = CreneauHoraire(heure_debut=heure_debut, heure_fin=heure_fin)

        # Construire la nouvelle affectation
        updated_affectation = Affectation(
            id=affectation.id,
            utilisateur_id=affectation.utilisateur_id,
            chantier_id=new_chantier_id,
            date_affectation=new_date,
            creneau=new_creneau,
            note=dto.note if dto.note is not None else affectation.note,
            recurrence=affectation.recurrence,
            jours_recurrence=affectation.jours_recurrence,
            date_fin_recurrence=affectation.date_fin_recurrence,
            created_by=affectation.created_by,
            created_at=affectation.created_at,
            updated_at=datetime.now(),
        )

        # Sauvegarder
        updated_affectation = self.affectation_repo.save(updated_affectation)

        # Publier l'événement
        if self.event_publisher:
            event = AffectationUpdatedEvent(
                affectation_id=updated_affectation.id,
                utilisateur_id=updated_affectation.utilisateur_id,
                chantier_id=updated_affectation.chantier_id,
                date_affectation=updated_affectation.date_affectation,
                updated_by=updated_by,
            )
            self.event_publisher(event)

        return AffectationDTO.from_entity(updated_affectation)

    def _parse_time(self, time_str: str, field_name: str) -> time:
        """
        Parse une chaîne HH:MM en objet time.

        Args:
            time_str: Chaîne au format HH:MM.
            field_name: Nom du champ pour les messages d'erreur.

        Returns:
            Objet time correspondant.

        Raises:
            ValueError: Si le format est invalide.
        """
        if not time_str or ":" not in time_str:
            raise ValueError(f"{field_name} doit être au format HH:MM")
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError(f"{field_name} doit être au format HH:MM")
        try:
            return time(int(parts[0]), int(parts[1]))
        except (ValueError, TypeError) as e:
            raise ValueError(f"{field_name} invalide: {e}")
