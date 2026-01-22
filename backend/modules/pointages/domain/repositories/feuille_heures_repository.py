"""Interface FeuilleHeuresRepository - Abstraction pour la persistence des feuilles d'heures."""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from datetime import date

from ..entities import FeuilleHeures
from ..value_objects import StatutPointage


class FeuilleHeuresRepository(ABC):
    """
    Interface abstraite pour la persistence des feuilles d'heures.

    Cette interface définit le contrat pour l'accès aux données de feuilles.
    L'implémentation concrète se trouve dans la couche Infrastructure.
    """

    @abstractmethod
    def find_by_id(self, feuille_id: int) -> Optional[FeuilleHeures]:
        """
        Trouve une feuille d'heures par son ID.

        Args:
            feuille_id: L'identifiant unique de la feuille.

        Returns:
            La feuille trouvée ou None.
        """
        pass

    @abstractmethod
    def save(self, feuille: FeuilleHeures) -> FeuilleHeures:
        """
        Persiste une feuille d'heures (création ou mise à jour).

        Args:
            feuille: La feuille à sauvegarder.

        Returns:
            La feuille sauvegardée (avec ID si création).
        """
        pass

    @abstractmethod
    def delete(self, feuille_id: int) -> bool:
        """
        Supprime une feuille d'heures.

        Args:
            feuille_id: L'identifiant de la feuille à supprimer.

        Returns:
            True si supprimée, False si non trouvée.
        """
        pass

    @abstractmethod
    def find_by_utilisateur_and_semaine(
        self, utilisateur_id: int, semaine_debut: date
    ) -> Optional[FeuilleHeures]:
        """
        Trouve la feuille d'un utilisateur pour une semaine donnée.

        Args:
            utilisateur_id: ID de l'utilisateur.
            semaine_debut: Date du lundi de la semaine.

        Returns:
            La feuille trouvée ou None.
        """
        pass

    @abstractmethod
    def find_by_utilisateur_and_week_number(
        self, utilisateur_id: int, annee: int, numero_semaine: int
    ) -> Optional[FeuilleHeures]:
        """
        Trouve la feuille d'un utilisateur par numéro de semaine.

        Args:
            utilisateur_id: ID de l'utilisateur.
            annee: L'année.
            numero_semaine: Le numéro de semaine (1-53).

        Returns:
            La feuille trouvée ou None.
        """
        pass

    @abstractmethod
    def find_by_utilisateur(
        self,
        utilisateur_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[FeuilleHeures], int]:
        """
        Trouve toutes les feuilles d'un utilisateur.

        Args:
            utilisateur_id: ID de l'utilisateur.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Tuple (liste des feuilles, total count).
        """
        pass

    @abstractmethod
    def find_by_semaine(
        self,
        semaine_debut: date,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[FeuilleHeures], int]:
        """
        Trouve toutes les feuilles pour une semaine donnée.

        Args:
            semaine_debut: Date du lundi de la semaine.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Tuple (liste des feuilles, total count).
        """
        pass

    @abstractmethod
    def find_by_statut(
        self,
        statut: StatutPointage,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[FeuilleHeures], int]:
        """
        Trouve les feuilles par statut global.

        Args:
            statut: Le statut à filtrer.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Tuple (liste des feuilles, total count).
        """
        pass

    @abstractmethod
    def search(
        self,
        utilisateur_id: Optional[int] = None,
        annee: Optional[int] = None,
        numero_semaine: Optional[int] = None,
        statut: Optional[StatutPointage] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[FeuilleHeures], int]:
        """
        Recherche des feuilles d'heures avec filtres multiples.

        Args:
            utilisateur_id: Filtrer par utilisateur (optionnel).
            annee: Filtrer par année (optionnel).
            numero_semaine: Filtrer par semaine (optionnel).
            statut: Filtrer par statut (optionnel).
            date_debut: Date de début de période (optionnel).
            date_fin: Date de fin de période (optionnel).
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Tuple (liste des feuilles, total count).
        """
        pass

    @abstractmethod
    def get_or_create(
        self, utilisateur_id: int, semaine_debut: date
    ) -> Tuple[FeuilleHeures, bool]:
        """
        Récupère ou crée une feuille pour un utilisateur/semaine.

        Args:
            utilisateur_id: ID de l'utilisateur.
            semaine_debut: Date du lundi de la semaine.

        Returns:
            Tuple (feuille, created) où created est True si nouvelle.
        """
        pass

    @abstractmethod
    def count_by_periode(
        self, date_debut: date, date_fin: date, statut: Optional[StatutPointage] = None
    ) -> int:
        """
        Compte les feuilles sur une période.

        Args:
            date_debut: Date de début.
            date_fin: Date de fin.
            statut: Filtrer par statut (optionnel).

        Returns:
            Nombre de feuilles.
        """
        pass
