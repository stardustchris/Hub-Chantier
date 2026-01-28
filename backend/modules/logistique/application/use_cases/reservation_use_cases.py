"""Use Cases pour la gestion des réservations.

LOG-07: Demande de réservation - Depuis mobile ou web
LOG-08: Sélection chantier - Association obligatoire au projet
LOG-09: Sélection créneau - Date + heure début / heure fin
LOG-11: Workflow validation - Demande → Chef valide → Confirmée
LOG-13-15: Notifications
LOG-16: Motif de refus
LOG-17: Conflit de réservation
LOG-18: Historique par ressource
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict

from ..ports.event_bus import EventBus

from ...domain.entities import Reservation
from ...domain.entities.reservation import (
    ReservationConflitError,
    TransitionStatutInvalideError,
)
from ...domain.repositories import RessourceRepository, ReservationRepository
from ...domain.value_objects import StatutReservation
from ....auth.domain.repositories import UserRepository
from ....auth.domain.entities import User
from ...domain.events import (
    ReservationCreatedEvent,
    ReservationValideeEvent,
    ReservationRefuseeEvent,
    ReservationAnnuleeEvent,
    ReservationConflitEvent,
)
from ..dtos import (
    ReservationCreateDTO,
    ReservationUpdateDTO,
    ReservationDTO,
    ReservationListDTO,
    PlanningRessourceDTO,
)
from .ressource_use_cases import RessourceNotFoundError


class ReservationNotFoundError(Exception):
    """Erreur levée quand une réservation n'est pas trouvée."""

    def __init__(self, reservation_id: int):
        self.reservation_id = reservation_id
        super().__init__(f"Réservation {reservation_id} non trouvée")


class RessourceInactiveError(Exception):
    """Erreur levée quand on essaie de réserver une ressource inactive."""

    def __init__(self, ressource_id: int):
        self.ressource_id = ressource_id
        super().__init__(f"La ressource {ressource_id} n'est pas disponible")


class CreateReservationUseCase:
    """Use case pour créer une réservation.

    LOG-07: Demande de réservation
    LOG-08: Sélection chantier obligatoire
    LOG-09: Sélection créneau
    LOG-17: Détection des conflits
    """

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        ressource_repository: RessourceRepository,
        event_bus: EventBus,
    ):
        self._reservation_repository = reservation_repository
        self._ressource_repository = ressource_repository
        self._event_bus = event_bus

    def execute(self, dto: ReservationCreateDTO, demandeur_id: int) -> ReservationDTO:
        """Crée une nouvelle réservation.

        Args:
            dto: Les données de la réservation
            demandeur_id: L'ID de l'utilisateur demandeur

        Returns:
            Le DTO de la réservation créée

        Raises:
            RessourceNotFoundError: Si la ressource n'existe pas
            RessourceInactiveError: Si la ressource est inactive
            ReservationConflitError: S'il y a un conflit de créneau
        """
        # Vérifier que la ressource existe et est active
        ressource = self._ressource_repository.find_by_id(dto.ressource_id)
        if not ressource:
            raise RessourceNotFoundError(dto.ressource_id)
        if not ressource.peut_etre_reservee():
            raise RessourceInactiveError(dto.ressource_id)

        # Créer l'entité
        reservation = Reservation(
            ressource_id=dto.ressource_id,
            chantier_id=dto.chantier_id,
            demandeur_id=demandeur_id,
            date_reservation=dto.date_reservation,
            heure_debut=dto.heure_debut,
            heure_fin=dto.heure_fin,
            commentaire=dto.commentaire,
            statut=StatutReservation.EN_ATTENTE,
            created_at=datetime.utcnow(),
        )

        # Vérifier les conflits (LOG-17)
        conflits = self._reservation_repository.find_conflits(reservation)
        if conflits:
            self._event_bus.publish(
                ReservationConflitEvent(
                    nouvelle_reservation_id=None,
                    ressource_id=dto.ressource_id,
                    date_reservation=dto.date_reservation,
                    reservations_en_conflit=tuple(c.id for c in conflits),
                )
            )
            raise ReservationConflitError(
                dto.ressource_id,
                dto.date_reservation,
                reservation.plage_horaire,
            )

        # Si la ressource ne requiert pas de validation, valider directement
        if not ressource.validation_requise:
            reservation.statut = StatutReservation.VALIDEE
            reservation.validated_at = datetime.utcnow()

        # Persister
        reservation = self._reservation_repository.save(reservation)

        # Publier l'event (LOG-13: Notification au valideur)
        self._event_bus.publish(
            ReservationCreatedEvent(
                reservation_id=reservation.id,
                ressource_id=ressource.id,
                ressource_nom=ressource.nom,
                chantier_id=dto.chantier_id,
                demandeur_id=demandeur_id,
                date_reservation=dto.date_reservation,
                heure_debut=dto.heure_debut,
                heure_fin=dto.heure_fin,
                validation_requise=ressource.validation_requise,
            )
        )

        return ReservationDTO.from_entity(
            reservation,
            ressource_nom=ressource.nom,
            ressource_code=ressource.code,
            ressource_couleur=ressource.couleur,
        )


class UpdateReservationUseCase:
    """Use case pour mettre à jour une réservation."""

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        ressource_repository: RessourceRepository,
    ):
        self._reservation_repository = reservation_repository
        self._ressource_repository = ressource_repository

    def execute(
        self, reservation_id: int, dto: ReservationUpdateDTO, user_id: int
    ) -> ReservationDTO:
        """Met à jour une réservation.

        Seules les réservations en attente peuvent être modifiées.
        """
        reservation = self._reservation_repository.find_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundError(reservation_id)

        if not reservation.est_en_attente:
            raise ValueError("Seules les réservations en attente peuvent être modifiées")

        # Appliquer les modifications
        if dto.date_reservation is not None:
            reservation.date_reservation = dto.date_reservation
        if dto.heure_debut is not None:
            reservation.heure_debut = dto.heure_debut
        if dto.heure_fin is not None:
            reservation.heure_fin = dto.heure_fin
        if dto.commentaire is not None:
            reservation.commentaire = dto.commentaire

        reservation.updated_at = datetime.utcnow()

        # Vérifier les conflits avec les nouvelles valeurs
        conflits = self._reservation_repository.find_conflits(reservation)
        if conflits:
            raise ReservationConflitError(
                reservation.ressource_id,
                reservation.date_reservation,
                reservation.plage_horaire,
            )

        reservation = self._reservation_repository.save(reservation)

        # Enrichir avec les infos ressource
        ressource = self._ressource_repository.find_by_id(reservation.ressource_id)

        return ReservationDTO.from_entity(
            reservation,
            ressource_nom=ressource.nom if ressource else None,
            ressource_code=ressource.code if ressource else None,
            ressource_couleur=ressource.couleur if ressource else None,
        )


class ValiderReservationUseCase:
    """Use case pour valider une réservation.

    LOG-11: Workflow validation - Chef valide → Confirmée 🟢
    LOG-14: Notification décision - Push au demandeur
    """

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        ressource_repository: RessourceRepository,
        event_bus: EventBus,
    ):
        self._reservation_repository = reservation_repository
        self._ressource_repository = ressource_repository
        self._event_bus = event_bus

    def execute(self, reservation_id: int, valideur_id: int) -> ReservationDTO:
        """Valide une réservation.

        Args:
            reservation_id: L'ID de la réservation
            valideur_id: L'ID du valideur (chef/conducteur)

        Returns:
            Le DTO de la réservation validée

        Raises:
            ReservationNotFoundError: Si la réservation n'existe pas
            TransitionStatutInvalideError: Si la transition n'est pas autorisée
        """
        reservation = self._reservation_repository.find_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundError(reservation_id)

        # Appliquer la validation (lève une exception si invalide)
        reservation.valider(valideur_id)

        reservation = self._reservation_repository.save(reservation)

        # Récupérer les infos ressource pour l'event
        ressource = self._ressource_repository.find_by_id(reservation.ressource_id)

        # Publier l'event (LOG-14)
        self._event_bus.publish(
            ReservationValideeEvent(
                reservation_id=reservation.id,
                ressource_id=reservation.ressource_id,
                ressource_nom=ressource.nom if ressource else "",
                demandeur_id=reservation.demandeur_id,
                valideur_id=valideur_id,
                date_reservation=reservation.date_reservation,
            )
        )

        return ReservationDTO.from_entity(
            reservation,
            ressource_nom=ressource.nom if ressource else None,
            ressource_code=ressource.code if ressource else None,
            ressource_couleur=ressource.couleur if ressource else None,
        )


class RefuserReservationUseCase:
    """Use case pour refuser une réservation.

    LOG-14: Notification décision
    LOG-16: Motif de refus
    """

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        ressource_repository: RessourceRepository,
        event_bus: EventBus,
    ):
        self._reservation_repository = reservation_repository
        self._ressource_repository = ressource_repository
        self._event_bus = event_bus

    def execute(
        self, reservation_id: int, valideur_id: int, motif: Optional[str] = None
    ) -> ReservationDTO:
        """Refuse une réservation.

        Args:
            reservation_id: L'ID de la réservation
            valideur_id: L'ID du valideur
            motif: Le motif de refus (optionnel, LOG-16)

        Returns:
            Le DTO de la réservation refusée

        Raises:
            ReservationNotFoundError: Si la réservation n'existe pas
            TransitionStatutInvalideError: Si la transition n'est pas autorisée
        """
        reservation = self._reservation_repository.find_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundError(reservation_id)

        reservation.refuser(valideur_id, motif)

        reservation = self._reservation_repository.save(reservation)

        ressource = self._ressource_repository.find_by_id(reservation.ressource_id)

        self._event_bus.publish(
            ReservationRefuseeEvent(
                reservation_id=reservation.id,
                ressource_id=reservation.ressource_id,
                ressource_nom=ressource.nom if ressource else "",
                demandeur_id=reservation.demandeur_id,
                valideur_id=valideur_id,
                date_reservation=reservation.date_reservation,
                motif=motif,
            )
        )

        return ReservationDTO.from_entity(
            reservation,
            ressource_nom=ressource.nom if ressource else None,
            ressource_code=ressource.code if ressource else None,
            ressource_couleur=ressource.couleur if ressource else None,
        )


class AnnulerReservationUseCase:
    """Use case pour annuler une réservation."""

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        event_bus: EventBus,
    ):
        self._reservation_repository = reservation_repository
        self._event_bus = event_bus

    def execute(self, reservation_id: int, user_id: int) -> ReservationDTO:
        """Annule une réservation.

        Args:
            reservation_id: L'ID de la réservation
            user_id: L'ID de l'utilisateur qui annule

        Returns:
            Le DTO de la réservation annulée
        """
        reservation = self._reservation_repository.find_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundError(reservation_id)

        reservation.annuler()

        reservation = self._reservation_repository.save(reservation)

        self._event_bus.publish(
            ReservationAnnuleeEvent(
                reservation_id=reservation.id,
                ressource_id=reservation.ressource_id,
                demandeur_id=reservation.demandeur_id,
                date_reservation=reservation.date_reservation,
            )
        )

        return ReservationDTO.from_entity(reservation)


class GetReservationUseCase:
    """Use case pour récupérer une réservation."""

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        ressource_repository: RessourceRepository,
    ):
        self._reservation_repository = reservation_repository
        self._ressource_repository = ressource_repository

    def execute(self, reservation_id: int) -> ReservationDTO:
        """Récupère une réservation par son ID."""
        reservation = self._reservation_repository.find_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundError(reservation_id)

        ressource = self._ressource_repository.find_by_id(reservation.ressource_id)

        return ReservationDTO.from_entity(
            reservation,
            ressource_nom=ressource.nom if ressource else None,
            ressource_code=ressource.code if ressource else None,
            ressource_couleur=ressource.couleur if ressource else None,
        )


class GetPlanningRessourceUseCase:
    """Use case pour récupérer le planning d'une ressource.

    LOG-03: Planning par ressource - Vue calendrier hebdomadaire 7 jours
    LOG-04: Navigation semaine
    """

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        ressource_repository: RessourceRepository,
        user_repository: UserRepository,
    ):
        self._reservation_repository = reservation_repository
        self._ressource_repository = ressource_repository
        self._user_repository = user_repository

    def execute(
        self,
        ressource_id: int,
        date_debut: date,
        date_fin: Optional[date] = None,
    ) -> PlanningRessourceDTO:
        """Récupère le planning d'une ressource sur une période.

        Args:
            ressource_id: L'ID de la ressource
            date_debut: Date de début (lundi de la semaine par défaut)
            date_fin: Date de fin (dimanche de la semaine par défaut)

        Returns:
            Le planning avec les réservations enrichies (ressource + utilisateurs)
        """
        ressource = self._ressource_repository.find_by_id(ressource_id)
        if not ressource:
            raise RessourceNotFoundError(ressource_id)

        # Par défaut, afficher 7 jours
        if date_fin is None:
            date_fin = date_debut + timedelta(days=6)

        reservations = self._reservation_repository.find_by_ressource_and_date_range(
            ressource_id=ressource_id,
            date_debut=date_debut,
            date_fin=date_fin,
            statuts=[StatutReservation.EN_ATTENTE, StatutReservation.VALIDEE],
        )

        # Enrichir avec les infos utilisateurs (demandeurs et valideurs)
        users_cache: Dict[int, Optional[User]] = {}
        enriched_reservations = []

        for r in reservations:
            # Récupérer le demandeur
            if r.demandeur_id not in users_cache:
                users_cache[r.demandeur_id] = self._user_repository.find_by_id(r.demandeur_id)
            demandeur = users_cache[r.demandeur_id]
            demandeur_nom = f"{demandeur.prenom} {demandeur.nom}" if demandeur else None

            # Récupérer le valideur si présent
            valideur_nom = None
            if r.valideur_id:
                if r.valideur_id not in users_cache:
                    users_cache[r.valideur_id] = self._user_repository.find_by_id(r.valideur_id)
                valideur = users_cache[r.valideur_id]
                valideur_nom = f"{valideur.prenom} {valideur.nom}" if valideur else None

            enriched_reservations.append(
                ReservationDTO.from_entity(
                    r,
                    ressource_nom=ressource.nom,
                    ressource_code=ressource.code,
                    ressource_couleur=ressource.couleur,
                    demandeur_nom=demandeur_nom,
                    valideur_nom=valideur_nom,
                )
            )

        return PlanningRessourceDTO(
            ressource_id=ressource.id,
            ressource_nom=ressource.nom,
            ressource_code=ressource.code,
            ressource_couleur=ressource.couleur,
            date_debut=date_debut,
            date_fin=date_fin,
            reservations=enriched_reservations,
        )


class GetHistoriqueRessourceUseCase:
    """Use case pour récupérer l'historique d'une ressource.

    LOG-18: Historique par ressource - Journal complet des réservations
    """

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        ressource_repository: RessourceRepository,
    ):
        self._reservation_repository = reservation_repository
        self._ressource_repository = ressource_repository

    def execute(
        self,
        ressource_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> ReservationListDTO:
        """Récupère l'historique complet des réservations d'une ressource.

        Args:
            ressource_id: L'ID de la ressource
            limit: Nombre max de résultats
            offset: Décalage pour pagination

        Returns:
            Liste paginée des réservations
        """
        ressource = self._ressource_repository.find_by_id(ressource_id)
        if not ressource:
            raise RessourceNotFoundError(ressource_id)

        reservations = self._reservation_repository.find_historique_ressource(
            ressource_id=ressource_id,
            limit=limit,
            offset=offset,
        )
        total = self._reservation_repository.count_by_ressource(ressource_id)

        return ReservationListDTO(
            items=[
                ReservationDTO.from_entity(
                    r,
                    ressource_nom=ressource.nom,
                    ressource_code=ressource.code,
                    ressource_couleur=ressource.couleur,
                )
                for r in reservations
            ],
            total=total,
            limit=limit,
            offset=offset,
        )


class ListReservationsEnAttenteUseCase:
    """Use case pour lister les réservations en attente de validation.

    LOG-11: Liste des demandes à valider pour les chefs/conducteurs.
    """

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        ressource_repository: RessourceRepository,
    ):
        self._reservation_repository = reservation_repository
        self._ressource_repository = ressource_repository

    def execute(self, limit: int = 100, offset: int = 0) -> ReservationListDTO:
        """Liste les réservations en attente de validation.

        Returns:
            Liste paginée des réservations en attente
        """
        reservations = self._reservation_repository.find_en_attente_validation(
            limit=limit,
            offset=offset,
        )

        # Enrichir avec les infos ressources
        ressources_cache = {}
        items = []
        for r in reservations:
            if r.ressource_id not in ressources_cache:
                ressources_cache[r.ressource_id] = self._ressource_repository.find_by_id(
                    r.ressource_id
                )
            ressource = ressources_cache[r.ressource_id]
            items.append(
                ReservationDTO.from_entity(
                    r,
                    ressource_nom=ressource.nom if ressource else None,
                    ressource_code=ressource.code if ressource else None,
                    ressource_couleur=ressource.couleur if ressource else None,
                )
            )

        # H11: Use proper count instead of approximation
        total = self._reservation_repository.count_en_attente()

        return ReservationListDTO(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )
