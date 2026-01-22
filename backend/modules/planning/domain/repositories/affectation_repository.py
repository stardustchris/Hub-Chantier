"""Interface AffectationRepository - Abstraction pour la persistence des affectations."""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List, Tuple

from ..entities import Affectation


class AffectationRepository(ABC):
    """
    Interface abstraite pour la persistence des affectations.

    Cette interface définit le contrat pour l'accès aux données d'affectation.
    L'implémentation concrète se trouve dans la couche Infrastructure.

    Note:
        Le Domain ne connaît pas l'implémentation (SQLAlchemy, etc.).
    """

    @abstractmethod
    def find_by_id(self, affectation_id: int) -> Optional[Affectation]:
        """
        Trouve une affectation par son ID.

        Args:
            affectation_id: L'identifiant unique de l'affectation.

        Returns:
            L'affectation trouvée ou None.
        """
        pass

    @abstractmethod
    def save(self, affectation: Affectation) -> Affectation:
        """
        Persiste une affectation (création ou mise à jour).

        Args:
            affectation: L'affectation à sauvegarder.

        Returns:
            L'affectation sauvegardée (avec ID si création).
        """
        pass

    @abstractmethod
    def delete(self, affectation_id: int) -> bool:
        """
        Supprime une affectation.

        Args:
            affectation_id: L'identifiant de l'affectation à supprimer.

        Returns:
            True si supprimée, False si non trouvée.
        """
        pass

    @abstractmethod
    def find_by_utilisateur(
        self,
        utilisateur_id: int,
        date_debut: date,
        date_fin: date,
    ) -> List[Affectation]:
        """
        Trouve les affectations d'un utilisateur sur une période.

        Args:
            utilisateur_id: ID de l'utilisateur.
            date_debut: Date de début de la période.
            date_fin: Date de fin de la période.

        Returns:
            Liste des affectations de l'utilisateur.
        """
        pass

    @abstractmethod
    def find_by_chantier(
        self,
        chantier_id: int,
        date_debut: date,
        date_fin: date,
    ) -> List[Affectation]:
        """
        Trouve les affectations d'un chantier sur une période.

        Args:
            chantier_id: ID du chantier.
            date_debut: Date de début de la période.
            date_fin: Date de fin de la période.

        Returns:
            Liste des affectations du chantier.
        """
        pass

    @abstractmethod
    def find_by_date(self, date_affectation: date) -> List[Affectation]:
        """
        Trouve toutes les affectations pour une date donnée.

        Args:
            date_affectation: Date des affectations recherchées.

        Returns:
            Liste des affectations de ce jour.
        """
        pass

    @abstractmethod
    def find_by_periode(
        self,
        date_debut: date,
        date_fin: date,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Affectation], int]:
        """
        Trouve les affectations sur une période avec pagination.

        Args:
            date_debut: Date de début de la période.
            date_fin: Date de fin de la période.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum d'éléments à retourner.

        Returns:
            Tuple (liste des affectations, total count).
        """
        pass

    @abstractmethod
    def find_utilisateurs_non_planifies(self, date_affectation: date) -> List[int]:
        """
        Trouve les IDs des utilisateurs non planifiés pour une date (PLN-04, PLN-11).

        Args:
            date_affectation: Date à vérifier.

        Returns:
            Liste des IDs utilisateurs sans affectation ce jour.
        """
        pass

    @abstractmethod
    def count_by_utilisateur_and_date(
        self,
        utilisateur_id: int,
        date_affectation: date,
    ) -> int:
        """
        Compte les affectations d'un utilisateur pour une date (PLN-20: Multi-affectations).

        Args:
            utilisateur_id: ID de l'utilisateur.
            date_affectation: Date à vérifier.

        Returns:
            Nombre d'affectations.
        """
        pass

    @abstractmethod
    def exists_for_utilisateur_chantier_date(
        self,
        utilisateur_id: int,
        chantier_id: int,
        date_affectation: date,
    ) -> bool:
        """
        Vérifie si une affectation existe déjà pour cet utilisateur/chantier/date.

        Args:
            utilisateur_id: ID de l'utilisateur.
            chantier_id: ID du chantier.
            date_affectation: Date de l'affectation.

        Returns:
            True si une affectation existe déjà.
        """
        pass

    @abstractmethod
    def delete_by_utilisateur_and_periode(
        self,
        utilisateur_id: int,
        date_debut: date,
        date_fin: date,
    ) -> int:
        """
        Supprime les affectations d'un utilisateur sur une période.

        Args:
            utilisateur_id: ID de l'utilisateur.
            date_debut: Date de début.
            date_fin: Date de fin.

        Returns:
            Nombre d'affectations supprimées.
        """
        pass
