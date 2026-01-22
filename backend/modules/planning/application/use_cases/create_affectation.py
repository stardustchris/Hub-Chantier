"""Use Case CreateAffectation - Création d'une nouvelle affectation."""

from datetime import date, time, datetime
from typing import Optional, Callable

from ...domain.entities import Affectation
from ...domain.repositories import AffectationRepository
from ...domain.value_objects import CreneauHoraire, TypeRecurrence
from ...domain.events import AffectationCreatedEvent
from ..dtos import CreateAffectationDTO, AffectationDTO


class AffectationAlreadyExistsError(Exception):
    """Exception levée quand l'affectation existe déjà."""

    def __init__(self, utilisateur_id: int, chantier_id: int, date_affectation: date):
        self.utilisateur_id = utilisateur_id
        self.chantier_id = chantier_id
        self.date_affectation = date_affectation
        self.message = (
            f"L'utilisateur {utilisateur_id} est déjà affecté au chantier "
            f"{chantier_id} le {date_affectation}"
        )
        super().__init__(self.message)


class InvalidCreneauError(Exception):
    """Exception levée quand le créneau horaire est invalide."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class CreateAffectationUseCase:
    """
    Cas d'utilisation : Création d'une nouvelle affectation.

    Crée une affectation d'un utilisateur à un chantier pour une date donnée.
    Selon CDC Section 5 - PLN-03, PLN-28.

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

    def execute(self, dto: CreateAffectationDTO, created_by: Optional[int] = None) -> AffectationDTO:
        """
        Exécute la création de l'affectation.

        Args:
            dto: Les données de création.
            created_by: ID de l'utilisateur qui crée l'affectation.

        Returns:
            AffectationDTO contenant l'affectation créée.

        Raises:
            AffectationAlreadyExistsError: Si l'affectation existe déjà.
            InvalidCreneauError: Si le créneau horaire est invalide.
            ValueError: Si les données sont invalides.
        """
        # Parser la date
        date_affectation = date.fromisoformat(dto.date_affectation)

        # Vérifier si l'affectation existe déjà
        if self.affectation_repo.exists_for_utilisateur_chantier_date(
            utilisateur_id=dto.utilisateur_id,
            chantier_id=dto.chantier_id,
            date_affectation=date_affectation,
        ):
            raise AffectationAlreadyExistsError(
                dto.utilisateur_id, dto.chantier_id, date_affectation
            )

        # Parser le créneau horaire
        creneau = None
        if dto.heure_debut or dto.heure_fin:
            try:
                heure_debut = None
                heure_fin = None
                if dto.heure_debut:
                    heure_debut = self._parse_time(dto.heure_debut, "heure_debut")
                if dto.heure_fin:
                    heure_fin = self._parse_time(dto.heure_fin, "heure_fin")
                creneau = CreneauHoraire(heure_debut=heure_debut, heure_fin=heure_fin)
            except ValueError as e:
                raise InvalidCreneauError(f"Créneau horaire invalide: {e}")

        # Parser la récurrence
        recurrence = TypeRecurrence.from_string(dto.recurrence)

        # Parser la date de fin de récurrence
        date_fin_recurrence = None
        if dto.date_fin_recurrence:
            date_fin_recurrence = date.fromisoformat(dto.date_fin_recurrence)

        # Créer l'entité
        affectation = Affectation(
            utilisateur_id=dto.utilisateur_id,
            chantier_id=dto.chantier_id,
            date_affectation=date_affectation,
            creneau=creneau,
            note=dto.note,
            recurrence=recurrence,
            jours_recurrence=list(dto.jours_recurrence),
            date_fin_recurrence=date_fin_recurrence,
            created_by=created_by,
            created_at=datetime.now(),
        )

        # Sauvegarder
        affectation = self.affectation_repo.save(affectation)

        # Publier l'événement
        if self.event_publisher:
            event = AffectationCreatedEvent(
                affectation_id=affectation.id,
                utilisateur_id=affectation.utilisateur_id,
                chantier_id=affectation.chantier_id,
                date_affectation=affectation.date_affectation,
                created_by=created_by,
            )
            self.event_publisher(event)

        return AffectationDTO.from_entity(affectation)

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
