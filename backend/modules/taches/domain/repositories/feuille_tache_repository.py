"""Interface FeuilleTacheRepository - Abstraction pour la persistence des feuilles."""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date

from ..entities import FeuilleTache
from ..entities.feuille_tache import StatutValidation


class FeuilleTacheRepository(ABC):
    """
    Interface abstraite pour la persistence des feuilles de taches.

    Cette interface definit le contrat pour l'acces aux declarations
    quotidiennes de travail (TAC-18, TAC-19).
    """

    @abstractmethod
    def find_by_id(self, feuille_id: int) -> Optional[FeuilleTache]:
        """
        Trouve une feuille par son ID.

        Args:
            feuille_id: L'identifiant unique de la feuille.

        Returns:
            La feuille trouvee ou None.
        """
        pass

    @abstractmethod
    def find_by_tache(
        self,
        tache_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FeuilleTache]:
        """
        Trouve les feuilles d'une tache.

        Args:
            tache_id: ID de la tache.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des feuilles de la tache.
        """
        pass

    @abstractmethod
    def find_by_utilisateur(
        self,
        utilisateur_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FeuilleTache]:
        """
        Trouve les feuilles d'un utilisateur.

        Args:
            utilisateur_id: ID de l'utilisateur.
            date_debut: Date de debut de periode.
            date_fin: Date de fin de periode.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des feuilles de l'utilisateur.
        """
        pass

    @abstractmethod
    def find_by_chantier(
        self,
        chantier_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        statut: Optional[StatutValidation] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FeuilleTache]:
        """
        Trouve les feuilles d'un chantier.

        Args:
            chantier_id: ID du chantier.
            date_debut: Date de debut de periode.
            date_fin: Date de fin de periode.
            statut: Filtrer par statut de validation.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des feuilles du chantier.
        """
        pass

    @abstractmethod
    def find_en_attente_validation(
        self,
        chantier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FeuilleTache]:
        """
        Trouve les feuilles en attente de validation (TAC-19).

        Args:
            chantier_id: Filtrer par chantier (optionnel).
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des feuilles en attente.
        """
        pass

    @abstractmethod
    def save(self, feuille: FeuilleTache) -> FeuilleTache:
        """
        Persiste une feuille (creation ou mise a jour).

        Args:
            feuille: La feuille a sauvegarder.

        Returns:
            La feuille sauvegardee (avec ID si creation).
        """
        pass

    @abstractmethod
    def delete(self, feuille_id: int) -> bool:
        """
        Supprime une feuille.

        Args:
            feuille_id: L'identifiant de la feuille a supprimer.

        Returns:
            True si supprimee, False si non trouvee.
        """
        pass

    @abstractmethod
    def count_by_tache(self, tache_id: int) -> int:
        """
        Compte les feuilles d'une tache.

        Args:
            tache_id: ID de la tache.

        Returns:
            Nombre de feuilles.
        """
        pass

    @abstractmethod
    def get_total_heures_tache(self, tache_id: int, validees_only: bool = True) -> float:
        """
        Calcule le total des heures pour une tache.

        Args:
            tache_id: ID de la tache.
            validees_only: Compter uniquement les feuilles validees.

        Returns:
            Total des heures.
        """
        pass

    @abstractmethod
    def get_total_quantite_tache(self, tache_id: int, validees_only: bool = True) -> float:
        """
        Calcule le total des quantites pour une tache.

        Args:
            tache_id: ID de la tache.
            validees_only: Compter uniquement les feuilles validees.

        Returns:
            Total des quantites.
        """
        pass

    @abstractmethod
    def exists_for_date(
        self,
        tache_id: int,
        utilisateur_id: int,
        date_travail: date,
    ) -> bool:
        """
        Verifie si une feuille existe pour cette combinaison.

        Args:
            tache_id: ID de la tache.
            utilisateur_id: ID de l'utilisateur.
            date_travail: Date du travail.

        Returns:
            True si existe.
        """
        pass
