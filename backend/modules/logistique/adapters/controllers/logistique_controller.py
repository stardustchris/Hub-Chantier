"""Controller pour le module Logistique.

Orchestre les use cases et fournit une façade pour les opérations.
"""

from datetime import date
from typing import Optional

from ...domain.value_objects import CategorieRessource
from ...application.use_cases import (
    CreateRessourceUseCase,
    UpdateRessourceUseCase,
    DeleteRessourceUseCase,
    GetRessourceUseCase,
    ListRessourcesUseCase,
    CreateReservationUseCase,
    UpdateReservationUseCase,
    ValiderReservationUseCase,
    RefuserReservationUseCase,
    AnnulerReservationUseCase,
    GetReservationUseCase,
    GetPlanningRessourceUseCase,
    GetHistoriqueRessourceUseCase,
    ListReservationsEnAttenteUseCase,
)
from ...application.dtos import (
    RessourceCreateDTO,
    RessourceUpdateDTO,
    RessourceDTO,
    RessourceListDTO,
    ReservationCreateDTO,
    ReservationUpdateDTO,
    ReservationDTO,
    ReservationListDTO,
    PlanningRessourceDTO,
)


class LogistiqueController:
    """Controller façade pour le module Logistique."""

    def __init__(
        self,
        create_ressource: CreateRessourceUseCase,
        update_ressource: UpdateRessourceUseCase,
        delete_ressource: DeleteRessourceUseCase,
        get_ressource: GetRessourceUseCase,
        list_ressources: ListRessourcesUseCase,
        create_reservation: CreateReservationUseCase,
        update_reservation: UpdateReservationUseCase,
        valider_reservation: ValiderReservationUseCase,
        refuser_reservation: RefuserReservationUseCase,
        annuler_reservation: AnnulerReservationUseCase,
        get_reservation: GetReservationUseCase,
        get_planning: GetPlanningRessourceUseCase,
        get_historique: GetHistoriqueRessourceUseCase,
        list_en_attente: ListReservationsEnAttenteUseCase,
    ):
        self._create_ressource = create_ressource
        self._update_ressource = update_ressource
        self._delete_ressource = delete_ressource
        self._get_ressource = get_ressource
        self._list_ressources = list_ressources
        self._create_reservation = create_reservation
        self._update_reservation = update_reservation
        self._valider_reservation = valider_reservation
        self._refuser_reservation = refuser_reservation
        self._annuler_reservation = annuler_reservation
        self._get_reservation = get_reservation
        self._get_planning = get_planning
        self._get_historique = get_historique
        self._list_en_attente = list_en_attente

    # Ressources

    def create_ressource(
        self, dto: RessourceCreateDTO, created_by: int
    ) -> RessourceDTO:
        """Crée une ressource."""
        return self._create_ressource.execute(dto, created_by)

    def update_ressource(
        self, ressource_id: int, dto: RessourceUpdateDTO, updated_by: int
    ) -> RessourceDTO:
        """Met à jour une ressource."""
        return self._update_ressource.execute(ressource_id, dto, updated_by)

    def delete_ressource(self, ressource_id: int, deleted_by: int) -> bool:
        """Supprime une ressource."""
        return self._delete_ressource.execute(ressource_id, deleted_by)

    def get_ressource(self, ressource_id: int) -> RessourceDTO:
        """Récupère une ressource."""
        return self._get_ressource.execute(ressource_id)

    def list_ressources(
        self,
        categorie: Optional[CategorieRessource] = None,
        actif_seulement: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> RessourceListDTO:
        """Liste les ressources."""
        return self._list_ressources.execute(
            categorie=categorie,
            actif_seulement=actif_seulement,
            limit=limit,
            offset=offset,
        )

    # Réservations

    def create_reservation(
        self, dto: ReservationCreateDTO, demandeur_id: int
    ) -> ReservationDTO:
        """Crée une réservation."""
        return self._create_reservation.execute(dto, demandeur_id)

    def update_reservation(
        self, reservation_id: int, dto: ReservationUpdateDTO, user_id: int
    ) -> ReservationDTO:
        """Met à jour une réservation."""
        return self._update_reservation.execute(reservation_id, dto, user_id)

    def valider_reservation(
        self, reservation_id: int, valideur_id: int
    ) -> ReservationDTO:
        """Valide une réservation."""
        return self._valider_reservation.execute(reservation_id, valideur_id)

    def refuser_reservation(
        self, reservation_id: int, valideur_id: int, motif: Optional[str] = None
    ) -> ReservationDTO:
        """Refuse une réservation."""
        return self._refuser_reservation.execute(reservation_id, valideur_id, motif)

    def annuler_reservation(
        self, reservation_id: int, user_id: int
    ) -> ReservationDTO:
        """Annule une réservation."""
        return self._annuler_reservation.execute(reservation_id, user_id)

    def get_reservation(self, reservation_id: int) -> ReservationDTO:
        """Récupère une réservation."""
        return self._get_reservation.execute(reservation_id)

    def get_planning_ressource(
        self, ressource_id: int, date_debut: date, date_fin: Optional[date] = None
    ) -> PlanningRessourceDTO:
        """Récupère le planning d'une ressource."""
        return self._get_planning.execute(ressource_id, date_debut, date_fin)

    def get_historique_ressource(
        self, ressource_id: int, limit: int = 100, offset: int = 0
    ) -> ReservationListDTO:
        """Récupère l'historique d'une ressource."""
        return self._get_historique.execute(ressource_id, limit, offset)

    def list_reservations_en_attente(
        self, limit: int = 100, offset: int = 0
    ) -> ReservationListDTO:
        """Liste les réservations en attente."""
        return self._list_en_attente.execute(limit, offset)
