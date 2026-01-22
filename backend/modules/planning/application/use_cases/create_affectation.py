"""Use Case CreateAffectation - Creation d'une affectation."""

from datetime import date, timedelta
from typing import List, Optional

from ...domain.entities import Affectation
from ...domain.repositories import AffectationRepository
from ...domain.value_objects import HeureAffectation, TypeAffectation, JourSemaine
from ...domain.events import AffectationCreatedEvent, AffectationBulkCreatedEvent
from ..dtos import CreateAffectationDTO
from ..ports import EventBus
from .exceptions import AffectationConflictError, InvalidDateRangeError


class CreateAffectationUseCase:
    """
    Cas d'utilisation : Creation d'une affectation.

    Cree une ou plusieurs affectations selon le type (unique ou recurrente).
    Une affectation recurrente genere plusieurs affectations individuelles.

    Selon CDC Section 5 - Planning Operationnel (PLN-04 a PLN-09).

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

    def execute(self, dto: CreateAffectationDTO, created_by: int) -> List[Affectation]:
        """
        Execute la creation d'affectation(s).

        Pour une affectation unique, cree une seule affectation.
        Pour une affectation recurrente, cree plusieurs affectations
        jusqu'a la date de fin de recurrence.

        Args:
            dto: Les donnees de creation.
            created_by: ID de l'utilisateur qui cree l'affectation.

        Returns:
            Liste des affectations creees (une ou plusieurs).

        Raises:
            AffectationConflictError: Si une affectation existe deja.
            InvalidDateRangeError: Si la plage de dates est invalide.
            ValueError: Si les donnees sont invalides.

        Example:
            >>> affectations = use_case.execute(dto, created_by=1)
            >>> print(f"Cree {len(affectations)} affectation(s)")
        """
        # Convertir les heures si fournies
        heure_debut = None
        heure_fin = None

        if dto.heure_debut:
            heure_debut = HeureAffectation.from_string(dto.heure_debut)

        if dto.heure_fin:
            heure_fin = HeureAffectation.from_string(dto.heure_fin)

        # Determiner le type d'affectation
        type_affectation = TypeAffectation.from_string(dto.type_affectation)

        if type_affectation == TypeAffectation.UNIQUE:
            # Creer une affectation unique
            return self._create_unique(
                dto=dto,
                created_by=created_by,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
            )
        else:
            # Creer des affectations recurrentes
            return self._create_recurrentes(
                dto=dto,
                created_by=created_by,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
            )

    def _create_unique(
        self,
        dto: CreateAffectationDTO,
        created_by: int,
        heure_debut: Optional[HeureAffectation],
        heure_fin: Optional[HeureAffectation],
    ) -> List[Affectation]:
        """
        Cree une affectation unique.

        Args:
            dto: Les donnees de creation.
            created_by: ID du createur.
            heure_debut: Heure de debut (optionnel).
            heure_fin: Heure de fin (optionnel).

        Returns:
            Liste contenant l'affectation creee.
        """
        # Verifier qu'il n'y a pas de conflit
        if self.affectation_repo.exists_for_utilisateur_and_date(
            dto.utilisateur_id, dto.date
        ):
            raise AffectationConflictError(dto.utilisateur_id, dto.date)

        # Creer l'entite
        affectation = Affectation(
            utilisateur_id=dto.utilisateur_id,
            chantier_id=dto.chantier_id,
            date=dto.date,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            note=dto.note,
            type_affectation=TypeAffectation.UNIQUE,
            created_by=created_by,
        )

        # Sauvegarder
        affectation = self.affectation_repo.save(affectation)

        # Publier l'evenement
        if self.event_bus:
            event = AffectationCreatedEvent(
                affectation_id=affectation.id,
                utilisateur_id=affectation.utilisateur_id,
                chantier_id=affectation.chantier_id,
                date=affectation.date,
                created_by=created_by,
            )
            self.event_bus.publish(event)

        return [affectation]

    def _create_recurrentes(
        self,
        dto: CreateAffectationDTO,
        created_by: int,
        heure_debut: Optional[HeureAffectation],
        heure_fin: Optional[HeureAffectation],
    ) -> List[Affectation]:
        """
        Cree des affectations recurrentes.

        Genere une affectation pour chaque jour correspondant aux jours
        de recurrence, entre la date de debut et la date de fin.

        Args:
            dto: Les donnees de creation.
            created_by: ID du createur.
            heure_debut: Heure de debut (optionnel).
            heure_fin: Heure de fin (optionnel).

        Returns:
            Liste des affectations creees.
        """
        # Convertir les jours de recurrence
        jours_recurrence = [
            JourSemaine.from_int(jour) for jour in dto.jours_recurrence
        ]

        # Generer les dates
        dates_affectation = self._generate_recurrence_dates(
            date_debut=dto.date,
            date_fin=dto.date_fin_recurrence,
            jours=jours_recurrence,
        )

        if not dates_affectation:
            raise InvalidDateRangeError(
                "Aucune date ne correspond aux jours de recurrence specifies"
            )

        # Verifier les conflits pour toutes les dates
        for date_aff in dates_affectation:
            if self.affectation_repo.exists_for_utilisateur_and_date(
                dto.utilisateur_id, date_aff
            ):
                raise AffectationConflictError(dto.utilisateur_id, date_aff)

        # Creer les affectations
        affectations = []
        for date_aff in dates_affectation:
            affectation = Affectation(
                utilisateur_id=dto.utilisateur_id,
                chantier_id=dto.chantier_id,
                date=date_aff,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                note=dto.note,
                type_affectation=TypeAffectation.RECURRENTE,
                jours_recurrence=jours_recurrence,
                created_by=created_by,
            )
            affectation = self.affectation_repo.save(affectation)
            affectations.append(affectation)

        # Publier l'evenement bulk
        if self.event_bus and affectations:
            event = AffectationBulkCreatedEvent(
                affectation_ids=tuple(a.id for a in affectations),
                utilisateur_id=dto.utilisateur_id,
                chantier_id=dto.chantier_id,
                date_debut=dates_affectation[0],
                date_fin=dates_affectation[-1],
                created_by=created_by,
                count=len(affectations),
            )
            self.event_bus.publish(event)

        return affectations

    def _generate_recurrence_dates(
        self,
        date_debut: date,
        date_fin: date,
        jours: List[JourSemaine],
    ) -> List[date]:
        """
        Genere les dates pour une recurrence.

        Args:
            date_debut: Date de debut (incluse).
            date_fin: Date de fin (incluse).
            jours: Liste des jours de la semaine.

        Returns:
            Liste des dates correspondant aux jours specifies.
        """
        dates = []
        current_date = date_debut

        while current_date <= date_fin:
            # Verifier si le jour de la semaine correspond
            jour_semaine = JourSemaine.from_int(current_date.weekday())
            if jour_semaine in jours:
                dates.append(current_date)

            current_date += timedelta(days=1)

        return dates
