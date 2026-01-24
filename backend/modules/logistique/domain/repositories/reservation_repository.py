"""Interface du repository pour les reservations.

Clean Architecture: Interface dans Domain, implementation dans Infrastructure.
"""
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from ..entities import Reservation
from ..value_objects import StatutReservation


class ReservationRepository(ABC):
    """
    Interface abstraite pour le repository des reservations.

    Cette interface est definie dans le Domain pour respecter
    la regle de dependance de la Clean Architecture.
    L'implementation concrete est dans Infrastructure.
    """

    @abstractmethod
    async def get_by_id(self, reservation_id: int) -> Optional[Reservation]:
        """
        Recupere une reservation par son ID.

        Args:
            reservation_id: L'ID de la reservation.

        Returns:
            La reservation ou None si non trouvee.
        """
        pass

    @abstractmethod
    async def list_by_ressource(
        self,
        ressource_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        statuts: Optional[list[StatutReservation]] = None,
    ) -> list[Reservation]:
        """
        Liste les reservations d'une ressource (LOG-03, LOG-18).

        Args:
            ressource_id: L'ID de la ressource.
            date_debut: Date de debut de la periode.
            date_fin: Date de fin de la periode.
            statuts: Filtrer par statuts.

        Returns:
            Liste des reservations.
        """
        pass

    @abstractmethod
    async def list_by_chantier(
        self,
        chantier_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        statuts: Optional[list[StatutReservation]] = None,
    ) -> list[Reservation]:
        """
        Liste les reservations d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode.
            date_fin: Date de fin de la periode.
            statuts: Filtrer par statuts.

        Returns:
            Liste des reservations.
        """
        pass

    @abstractmethod
    async def list_by_demandeur(
        self,
        demandeur_id: int,
        statuts: Optional[list[StatutReservation]] = None,
    ) -> list[Reservation]:
        """
        Liste les reservations d'un demandeur.

        Args:
            demandeur_id: L'ID du demandeur.
            statuts: Filtrer par statuts.

        Returns:
            Liste des reservations.
        """
        pass

    @abstractmethod
    async def list_pending_for_validator(
        self,
        valideur_id: int,
    ) -> list[Reservation]:
        """
        Liste les reservations en attente de validation pour un valideur.

        Args:
            valideur_id: L'ID du valideur (chef/conducteur).

        Returns:
            Liste des reservations en attente.
        """
        pass

    @abstractmethod
    async def save(self, reservation: Reservation) -> Reservation:
        """
        Sauvegarde une reservation (creation ou mise a jour).

        Args:
            reservation: La reservation a sauvegarder.

        Returns:
            La reservation sauvegardee avec son ID.
        """
        pass

    @abstractmethod
    async def delete(self, reservation_id: int) -> bool:
        """
        Supprime une reservation.

        Args:
            reservation_id: L'ID de la reservation.

        Returns:
            True si la suppression a reussi.
        """
        pass

    @abstractmethod
    async def find_conflicts(
        self,
        ressource_id: int,
        date_debut: date,
        date_fin: date,
        heure_debut: str,
        heure_fin: str,
        exclude_id: Optional[int] = None,
    ) -> list[Reservation]:
        """
        Trouve les reservations en conflit (LOG-17).

        Recherche les reservations actives (EN_ATTENTE ou VALIDEE) qui
        chevauchent le creneau demande.

        Args:
            ressource_id: L'ID de la ressource.
            date_debut: Date de debut du creneau.
            date_fin: Date de fin du creneau.
            heure_debut: Heure de debut (HH:MM).
            heure_fin: Heure de fin (HH:MM).
            exclude_id: ID de reservation a exclure (pour modification).

        Returns:
            Liste des reservations en conflit.
        """
        pass

    @abstractmethod
    async def add_historique(
        self,
        reservation_id: int,
        action: str,
        user_id: Optional[int] = None,
        details: Optional[dict] = None,
    ) -> None:
        """
        Ajoute une entree dans l'historique (LOG-18).

        Args:
            reservation_id: L'ID de la reservation.
            action: L'action effectuee (created, validated, refused, cancelled, modified).
            user_id: L'ID de l'utilisateur.
            details: Details supplementaires (JSON).
        """
        pass

    @abstractmethod
    async def get_historique(
        self,
        reservation_id: int,
    ) -> list[dict]:
        """
        Recupere l'historique d'une reservation (LOG-18).

        Args:
            reservation_id: L'ID de la reservation.

        Returns:
            Liste des entrees d'historique.
        """
        pass
