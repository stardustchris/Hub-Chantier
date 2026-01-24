"""Interface du repository pour les réservations.

LOG-03: Planning par ressource - Vue calendrier hebdomadaire 7 jours
LOG-17: Conflit de réservation - Détection des chevauchements
LOG-18: Historique par ressource - Journal complet des réservations
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from ..entities import Reservation
from ..value_objects import StatutReservation


class ReservationRepository(ABC):
    """Interface abstraite pour la persistence des réservations."""

    @abstractmethod
    def save(self, reservation: Reservation) -> Reservation:
        """Persiste une réservation (création ou mise à jour).

        Args:
            reservation: La réservation à persister

        Returns:
            La réservation avec son ID attribué
        """
        pass

    @abstractmethod
    def find_by_id(self, reservation_id: int) -> Optional[Reservation]:
        """Recherche une réservation par son ID.

        Args:
            reservation_id: L'ID de la réservation

        Returns:
            La réservation ou None si non trouvée
        """
        pass

    @abstractmethod
    def find_by_ressource_and_date_range(
        self,
        ressource_id: int,
        date_debut: date,
        date_fin: date,
        statuts: Optional[List[StatutReservation]] = None,
    ) -> List[Reservation]:
        """Liste les réservations d'une ressource sur une période.

        LOG-03: Planning par ressource - Vue calendrier hebdomadaire

        Args:
            ressource_id: L'ID de la ressource
            date_debut: Date de début de la période
            date_fin: Date de fin de la période
            statuts: Filtrer par statuts (optionnel)

        Returns:
            Liste des réservations
        """
        pass

    @abstractmethod
    def find_by_chantier(
        self,
        chantier_id: int,
        statuts: Optional[List[StatutReservation]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Reservation]:
        """Liste les réservations d'un chantier.

        Args:
            chantier_id: L'ID du chantier
            statuts: Filtrer par statuts (optionnel)
            limit: Nombre maximum de résultats
            offset: Décalage pour pagination

        Returns:
            Liste des réservations
        """
        pass

    @abstractmethod
    def find_by_demandeur(
        self,
        demandeur_id: int,
        statuts: Optional[List[StatutReservation]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Reservation]:
        """Liste les réservations d'un demandeur.

        Args:
            demandeur_id: L'ID du demandeur
            statuts: Filtrer par statuts (optionnel)
            limit: Nombre maximum de résultats
            offset: Décalage pour pagination

        Returns:
            Liste des réservations
        """
        pass

    @abstractmethod
    def find_en_attente_validation(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Reservation]:
        """Liste les réservations en attente de validation.

        LOG-11: Workflow validation - Liste des demandes à valider

        Returns:
            Liste des réservations en attente
        """
        pass

    @abstractmethod
    def find_conflits(self, reservation: Reservation) -> List[Reservation]:
        """Recherche les réservations en conflit avec une nouvelle.

        LOG-17: Conflit de réservation - Alerte si créneau déjà occupé

        Args:
            reservation: La réservation à vérifier

        Returns:
            Liste des réservations en conflit
        """
        pass

    @abstractmethod
    def find_a_rappeler_demain(self) -> List[Reservation]:
        """Liste les réservations pour demain (pour rappel J-1).

        LOG-15: Rappel J-1 - Notification veille de réservation

        Returns:
            Liste des réservations pour demain
        """
        pass

    @abstractmethod
    def find_historique_ressource(
        self,
        ressource_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Reservation]:
        """Retourne l'historique des réservations d'une ressource.

        LOG-18: Historique par ressource - Journal complet

        Args:
            ressource_id: L'ID de la ressource
            limit: Nombre maximum de résultats
            offset: Décalage pour pagination

        Returns:
            Liste des réservations (toutes, y compris passées)
        """
        pass

    @abstractmethod
    def count_by_ressource(
        self,
        ressource_id: int,
        statuts: Optional[List[StatutReservation]] = None,
    ) -> int:
        """Compte les réservations d'une ressource.

        Args:
            ressource_id: L'ID de la ressource
            statuts: Filtrer par statuts (optionnel)

        Returns:
            Le nombre de réservations
        """
        pass

    @abstractmethod
    def count_en_attente(self) -> int:
        """Compte le nombre total de réservations en attente (H11).

        Returns:
            Le nombre de réservations en attente
        """
        pass

    @abstractmethod
    def delete(self, reservation_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime une réservation (soft delete - H10).

        Args:
            reservation_id: L'ID de la réservation à supprimer
            deleted_by: L'ID de l'utilisateur qui supprime (optionnel)

        Returns:
            True si supprimée, False si non trouvée
        """
        pass
