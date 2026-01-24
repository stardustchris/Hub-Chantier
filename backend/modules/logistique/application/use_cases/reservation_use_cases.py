"""Use cases pour la gestion des reservations.

CDC Section 11 - LOG-07 a LOG-18.
"""
from datetime import date, timedelta
from typing import Optional, List, Callable

from ..dtos import (
    CreateReservationDTO,
    ValidateReservationDTO,
    RefuseReservationDTO,
    ReservationFiltersDTO,
    ReservationDTO,
    ReservationListDTO,
    RessourceDTO,
    PlanningRessourceDTO,
    ConflitReservationDTO,
)
from ...domain.entities import Reservation
from ...domain.value_objects import StatutReservation
from ...domain.repositories import ReservationRepository, RessourceRepository


class ReservationNotFoundError(Exception):
    """Exception levee quand une reservation n'existe pas."""
    pass


class RessourceNotFoundError(Exception):
    """Exception levee quand une ressource n'existe pas."""
    pass


class ConflitReservationError(Exception):
    """Exception levee en cas de conflit de reservation (LOG-17)."""
    def __init__(self, message: str, conflits: List[ReservationDTO]):
        super().__init__(message)
        self.conflits = conflits


class AccessDeniedError(Exception):
    """Exception levee pour acces refuse."""
    pass


class InvalidStatusTransitionError(Exception):
    """Exception levee pour transition de statut invalide."""
    pass


# Type pour la resolution de noms
UserNameResolver = Callable[[int], Optional[str]]
ChantierNameResolver = Callable[[int], Optional[str]]


class CreateReservationUseCase:
    """Use case pour creer une reservation (LOG-07).

    Workflow LOG-11:
    - Si validation_requise sur la ressource: statut = EN_ATTENTE
    - Sinon: statut = VALIDEE directement
    """

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        ressource_repository: RessourceRepository,
    ):
        self._reservation_repo = reservation_repository
        self._ressource_repo = ressource_repository

    def execute(self, dto: CreateReservationDTO) -> ReservationDTO:
        """Execute le use case.

        Args:
            dto: Donnees de creation.

        Returns:
            La reservation creee.

        Raises:
            RessourceNotFoundError: Si la ressource n'existe pas.
            ConflitReservationError: Si conflit avec une autre reservation (LOG-17).
        """
        # Verifier que la ressource existe
        ressource = self._ressource_repo.find_by_id(dto.ressource_id)
        if not ressource:
            raise RessourceNotFoundError(f"Ressource {dto.ressource_id} non trouvee")

        # Verifier les conflits (LOG-17)
        conflits = self._reservation_repo.find_conflits(
            ressource_id=dto.ressource_id,
            date_debut=dto.date_debut,
            date_fin=dto.date_fin,
            heure_debut=dto.heure_debut,
            heure_fin=dto.heure_fin,
        )
        if conflits:
            raise ConflitReservationError(
                f"Conflit avec {len(conflits)} reservation(s) existante(s)",
                [ReservationDTO.from_entity(c) for c in conflits],
            )

        # Determiner le statut initial (LOG-11)
        statut_initial = (
            StatutReservation.EN_ATTENTE
            if ressource.validation_requise
            else StatutReservation.VALIDEE
        )

        reservation = Reservation(
            ressource_id=dto.ressource_id,
            chantier_id=dto.chantier_id,
            demandeur_id=dto.demandeur_id,
            date_debut=dto.date_debut,
            date_fin=dto.date_fin,
            heure_debut=dto.heure_debut,
            heure_fin=dto.heure_fin,
            note=dto.note,
            statut=statut_initial,
        )

        saved = self._reservation_repo.save(reservation)
        return ReservationDTO.from_entity(saved)


class GetReservationUseCase:
    """Use case pour obtenir une reservation."""

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        get_user_name: Optional[UserNameResolver] = None,
        get_chantier_name: Optional[ChantierNameResolver] = None,
    ):
        self._repo = reservation_repository
        self._get_user_name = get_user_name
        self._get_chantier_name = get_chantier_name

    def execute(self, reservation_id: int) -> ReservationDTO:
        """Execute le use case.

        Args:
            reservation_id: ID de la reservation.

        Returns:
            La reservation.

        Raises:
            ReservationNotFoundError: Si la reservation n'existe pas.
        """
        reservation = self._repo.find_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundError(
                f"Reservation {reservation_id} non trouvee"
            )

        # Enrichissement optionnel
        demandeur_nom = None
        valideur_nom = None
        chantier_nom = None

        if self._get_user_name:
            demandeur_nom = self._get_user_name(reservation.demandeur_id)
            if reservation.valideur_id:
                valideur_nom = self._get_user_name(reservation.valideur_id)

        if self._get_chantier_name:
            chantier_nom = self._get_chantier_name(reservation.chantier_id)

        return ReservationDTO.from_entity(
            reservation,
            demandeur_nom=demandeur_nom,
            valideur_nom=valideur_nom,
            chantier_nom=chantier_nom,
        )


class ListReservationsUseCase:
    """Use case pour lister les reservations."""

    def __init__(self, reservation_repository: ReservationRepository):
        self._repo = reservation_repository

    def execute(self, filters: ReservationFiltersDTO) -> ReservationListDTO:
        """Execute le use case.

        Args:
            filters: Criteres de filtrage.

        Returns:
            Liste paginee des reservations.
        """
        reservations = self._repo.find_all(
            ressource_id=filters.ressource_id,
            chantier_id=filters.chantier_id,
            demandeur_id=filters.demandeur_id,
            statut=filters.statut,
            date_debut=filters.date_debut,
            date_fin=filters.date_fin,
            skip=filters.skip,
            limit=filters.limit,
        )
        total = self._repo.count(
            ressource_id=filters.ressource_id,
            chantier_id=filters.chantier_id,
            demandeur_id=filters.demandeur_id,
            statut=filters.statut,
            date_debut=filters.date_debut,
            date_fin=filters.date_fin,
        )

        return ReservationListDTO(
            reservations=[ReservationDTO.from_entity(r) for r in reservations],
            total=total,
            skip=filters.skip,
            limit=filters.limit,
        )


class ValidateReservationUseCase:
    """Use case pour valider une reservation (LOG-11)."""

    def __init__(self, reservation_repository: ReservationRepository):
        self._repo = reservation_repository

    def execute(
        self, dto: ValidateReservationDTO, user_role: str
    ) -> ReservationDTO:
        """Execute le use case.

        Args:
            dto: Donnees de validation.
            user_role: Role de l'utilisateur.

        Returns:
            La reservation validee.

        Raises:
            AccessDeniedError: Si l'utilisateur n'a pas les droits.
            ReservationNotFoundError: Si la reservation n'existe pas.
            InvalidStatusTransitionError: Si le statut ne permet pas la validation.
        """
        if user_role not in ("admin", "conducteur", "chef_chantier"):
            raise AccessDeniedError(
                "Seuls les chefs et conducteurs peuvent valider des reservations"
            )

        reservation = self._repo.find_by_id(dto.reservation_id)
        if not reservation:
            raise ReservationNotFoundError(
                f"Reservation {dto.reservation_id} non trouvee"
            )

        try:
            reservation.valider(dto.valideur_id)
        except ValueError as e:
            raise InvalidStatusTransitionError(str(e))

        saved = self._repo.save(reservation)
        return ReservationDTO.from_entity(saved)


class RefuseReservationUseCase:
    """Use case pour refuser une reservation (LOG-11, LOG-16)."""

    def __init__(self, reservation_repository: ReservationRepository):
        self._repo = reservation_repository

    def execute(self, dto: RefuseReservationDTO, user_role: str) -> ReservationDTO:
        """Execute le use case.

        Args:
            dto: Donnees de refus.
            user_role: Role de l'utilisateur.

        Returns:
            La reservation refusee.

        Raises:
            AccessDeniedError: Si l'utilisateur n'a pas les droits.
            ReservationNotFoundError: Si la reservation n'existe pas.
            InvalidStatusTransitionError: Si le statut ne permet pas le refus.
        """
        if user_role not in ("admin", "conducteur", "chef_chantier"):
            raise AccessDeniedError(
                "Seuls les chefs et conducteurs peuvent refuser des reservations"
            )

        reservation = self._repo.find_by_id(dto.reservation_id)
        if not reservation:
            raise ReservationNotFoundError(
                f"Reservation {dto.reservation_id} non trouvee"
            )

        try:
            reservation.refuser(dto.valideur_id, dto.motif)
        except ValueError as e:
            raise InvalidStatusTransitionError(str(e))

        saved = self._repo.save(reservation)
        return ReservationDTO.from_entity(saved)


class CancelReservationUseCase:
    """Use case pour annuler une reservation."""

    def __init__(self, reservation_repository: ReservationRepository):
        self._repo = reservation_repository

    def execute(
        self, reservation_id: int, user_id: int
    ) -> ReservationDTO:
        """Execute le use case.

        Args:
            reservation_id: ID de la reservation.
            user_id: ID de l'utilisateur qui annule.

        Returns:
            La reservation annulee.

        Raises:
            ReservationNotFoundError: Si la reservation n'existe pas.
            AccessDeniedError: Si l'utilisateur n'est pas le demandeur.
            InvalidStatusTransitionError: Si le statut ne permet pas l'annulation.
        """
        reservation = self._repo.find_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundError(f"Reservation {reservation_id} non trouvee")

        # Seul le demandeur peut annuler
        if reservation.demandeur_id != user_id:
            raise AccessDeniedError(
                "Seul le demandeur peut annuler sa reservation"
            )

        try:
            reservation.annuler()
        except ValueError as e:
            raise InvalidStatusTransitionError(str(e))

        saved = self._repo.save(reservation)
        return ReservationDTO.from_entity(saved)


class GetPlanningRessourceUseCase:
    """Use case pour obtenir le planning d'une ressource (LOG-03)."""

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        ressource_repository: RessourceRepository,
    ):
        self._reservation_repo = reservation_repository
        self._ressource_repo = ressource_repository

    def execute(
        self, ressource_id: int, semaine_debut: date
    ) -> PlanningRessourceDTO:
        """Execute le use case.

        Args:
            ressource_id: ID de la ressource.
            semaine_debut: Date du lundi de la semaine.

        Returns:
            Le planning de la ressource pour la semaine.

        Raises:
            RessourceNotFoundError: Si la ressource n'existe pas.
        """
        ressource = self._ressource_repo.find_by_id(ressource_id)
        if not ressource:
            raise RessourceNotFoundError(f"Ressource {ressource_id} non trouvee")

        # Calculer la fin de semaine (dimanche)
        semaine_fin = semaine_debut + timedelta(days=6)

        # Recuperer les reservations de la semaine (validees et en attente)
        reservations = self._reservation_repo.find_all(
            ressource_id=ressource_id,
            date_debut=semaine_debut,
            date_fin=semaine_fin,
            statut=None,  # Toutes les reservations actives
            skip=0,
            limit=100,
        )

        # Filtrer pour exclure les refusees et annulees
        reservations_actives = [
            r for r in reservations
            if r.statut in (StatutReservation.EN_ATTENTE, StatutReservation.VALIDEE)
        ]

        return PlanningRessourceDTO(
            ressource=RessourceDTO.from_entity(ressource),
            reservations=[ReservationDTO.from_entity(r) for r in reservations_actives],
            semaine_debut=semaine_debut.isoformat(),
            semaine_fin=semaine_fin.isoformat(),
        )


class GetPendingReservationsUseCase:
    """Use case pour obtenir les reservations en attente de validation."""

    def __init__(self, reservation_repository: ReservationRepository):
        self._repo = reservation_repository

    def execute(
        self,
        ressource_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ReservationListDTO:
        """Execute le use case.

        Args:
            ressource_id: Filtrer par ressource (optionnel).
            skip: Offset de pagination.
            limit: Limite de pagination.

        Returns:
            Liste des reservations en attente.
        """
        reservations = self._repo.find_all(
            ressource_id=ressource_id,
            statut=StatutReservation.EN_ATTENTE.value,
            skip=skip,
            limit=limit,
        )
        total = self._repo.count(
            ressource_id=ressource_id,
            statut=StatutReservation.EN_ATTENTE.value,
        )

        return ReservationListDTO(
            reservations=[ReservationDTO.from_entity(r) for r in reservations],
            total=total,
            skip=skip,
            limit=limit,
        )


class CheckConflitsUseCase:
    """Use case pour verifier les conflits avant creation (LOG-17)."""

    def __init__(self, reservation_repository: ReservationRepository):
        self._repo = reservation_repository

    def execute(self, dto: CreateReservationDTO) -> Optional[ConflitReservationDTO]:
        """Execute le use case.

        Args:
            dto: Donnees de reservation a verifier.

        Returns:
            Les conflits trouves, ou None si pas de conflit.
        """
        conflits = self._repo.find_conflits(
            ressource_id=dto.ressource_id,
            date_debut=dto.date_debut,
            date_fin=dto.date_fin,
            heure_debut=dto.heure_debut,
            heure_fin=dto.heure_fin,
        )

        if not conflits:
            return None

        return ConflitReservationDTO(
            nouvelle_reservation=dto,
            reservations_en_conflit=[ReservationDTO.from_entity(c) for c in conflits],
            message=f"Conflit avec {len(conflits)} reservation(s) existante(s)",
        )
