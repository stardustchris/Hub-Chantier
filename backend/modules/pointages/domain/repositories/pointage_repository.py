"""Interface PointageRepository - Abstraction pour la persistence des pointages."""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from datetime import date

from ..entities import Pointage
from ..value_objects import StatutPointage


class PointageRepository(ABC):
    """
    Interface abstraite pour la persistence des pointages.

    Cette interface définit le contrat pour l'accès aux données de pointage.
    L'implémentation concrète se trouve dans la couche Infrastructure.
    """

    @abstractmethod
    def find_by_id(self, pointage_id: int) -> Optional[Pointage]:
        """
        Trouve un pointage par son ID.

        Args:
            pointage_id: L'identifiant unique du pointage.

        Returns:
            Le pointage trouvé ou None.
        """
        pass

    @abstractmethod
    def save(self, pointage: Pointage) -> Pointage:
        """
        Persiste un pointage (création ou mise à jour).

        Args:
            pointage: Le pointage à sauvegarder.

        Returns:
            Le pointage sauvegardé (avec ID si création).
        """
        pass

    @abstractmethod
    def delete(self, pointage_id: int) -> bool:
        """
        Supprime un pointage.

        Args:
            pointage_id: L'identifiant du pointage à supprimer.

        Returns:
            True si supprimé, False si non trouvé.
        """
        pass

    @abstractmethod
    def find_by_utilisateur_and_date(
        self, utilisateur_id: int, date_pointage: date
    ) -> List[Pointage]:
        """
        Trouve les pointages d'un utilisateur pour une date.

        Args:
            utilisateur_id: ID de l'utilisateur.
            date_pointage: La date de pointage.

        Returns:
            Liste des pointages du jour.
        """
        pass

    @abstractmethod
    def find_by_utilisateur_and_semaine(
        self, utilisateur_id: int, semaine_debut: date
    ) -> List[Pointage]:
        """
        Trouve les pointages d'un utilisateur pour une semaine.

        Args:
            utilisateur_id: ID de l'utilisateur.
            semaine_debut: Date du lundi de la semaine.

        Returns:
            Liste des pointages de la semaine.
        """
        pass

    @abstractmethod
    def find_by_chantier_and_date(
        self, chantier_id: int, date_pointage: date
    ) -> List[Pointage]:
        """
        Trouve les pointages d'un chantier pour une date.

        Args:
            chantier_id: ID du chantier.
            date_pointage: La date de pointage.

        Returns:
            Liste des pointages du jour pour ce chantier.
        """
        pass

    @abstractmethod
    def find_by_chantier_and_semaine(
        self, chantier_id: int, semaine_debut: date
    ) -> List[Pointage]:
        """
        Trouve les pointages d'un chantier pour une semaine.

        Args:
            chantier_id: ID du chantier.
            semaine_debut: Date du lundi de la semaine.

        Returns:
            Liste des pointages de la semaine pour ce chantier.
        """
        pass

    @abstractmethod
    def find_by_utilisateur_chantier_date(
        self, utilisateur_id: int, chantier_id: int, date_pointage: date
    ) -> Optional[Pointage]:
        """
        Trouve un pointage unique par utilisateur, chantier et date.

        Args:
            utilisateur_id: ID de l'utilisateur.
            chantier_id: ID du chantier.
            date_pointage: La date de pointage.

        Returns:
            Le pointage trouvé ou None.
        """
        pass

    @abstractmethod
    def find_by_affectation(self, affectation_id: int) -> Optional[Pointage]:
        """
        Trouve un pointage par son affectation source (FDH-10).

        Args:
            affectation_id: ID de l'affectation.

        Returns:
            Le pointage lié ou None.
        """
        pass

    @abstractmethod
    def find_pending_validation(
        self,
        validateur_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Pointage], int]:
        """
        Trouve les pointages en attente de validation.

        Args:
            validateur_id: Filtrer par validateur (optionnel).
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Tuple (liste des pointages, total count).
        """
        pass

    @abstractmethod
    def search(
        self,
        utilisateur_id: Optional[int] = None,
        chantier_id: Optional[int] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        statut: Optional[StatutPointage] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Pointage], int]:
        """
        Recherche des pointages avec filtres multiples.

        Args:
            utilisateur_id: Filtrer par utilisateur (optionnel).
            chantier_id: Filtrer par chantier (optionnel).
            date_debut: Date de début de période (optionnel).
            date_fin: Date de fin de période (optionnel).
            statut: Filtrer par statut (optionnel).
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Tuple (liste des pointages, total count).
        """
        pass

    @abstractmethod
    def count_by_utilisateur_semaine(
        self, utilisateur_id: int, semaine_debut: date
    ) -> int:
        """
        Compte les pointages d'un utilisateur pour une semaine.

        Args:
            utilisateur_id: ID de l'utilisateur.
            semaine_debut: Date du lundi de la semaine.

        Returns:
            Nombre de pointages.
        """
        pass

    @abstractmethod
    def bulk_save(self, pointages: List[Pointage]) -> List[Pointage]:
        """
        Sauvegarde plusieurs pointages en une seule transaction.

        Args:
            pointages: Liste des pointages à sauvegarder.

        Returns:
            Liste des pointages sauvegardés.
        """
        pass
