"""Interface AffectationRepository - Abstraction pour la persistence des affectations."""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List

from ..entities import Affectation


class AffectationRepository(ABC):
    """
    Interface abstraite pour la persistence des affectations.

    Cette interface definit le contrat pour l'acces aux donnees d'affectation.
    L'implementation concrete se trouve dans la couche Infrastructure.

    Selon CDC Section 5 - Planning Operationnel (PLN-01 a PLN-28).

    Note:
        Le Domain ne connait pas l'implementation (SQLAlchemy, etc.).
    """

    @abstractmethod
    def save(self, affectation: Affectation) -> Affectation:
        """
        Persiste une affectation (creation ou mise a jour).

        Si l'affectation a un ID, c'est une mise a jour.
        Sinon, c'est une creation et l'ID sera attribue.

        Args:
            affectation: L'affectation a sauvegarder.

        Returns:
            L'affectation sauvegardee (avec ID si creation).
        """
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Affectation]:
        """
        Trouve une affectation par son ID.

        Args:
            id: L'identifiant unique de l'affectation.

        Returns:
            L'affectation trouvee ou None.
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
        Trouve les affectations d'un utilisateur sur une periode.

        Utilise pour afficher le planning d'un utilisateur (PLN-01).

        Args:
            utilisateur_id: L'ID de l'utilisateur.
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Liste des affectations de l'utilisateur sur la periode.
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
        Trouve les affectations pour un chantier sur une periode.

        Utilise pour voir qui est affecte a un chantier (PLN-02).

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Liste des affectations pour ce chantier sur la periode.
        """
        pass

    @abstractmethod
    def find_by_date_range(
        self,
        date_debut: date,
        date_fin: date,
    ) -> List[Affectation]:
        """
        Trouve toutes les affectations sur une periode.

        Utilise pour la vue globale du planning (PLN-03).

        Args:
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Liste de toutes les affectations sur la periode.
        """
        pass

    @abstractmethod
    def find_by_utilisateur_and_date(
        self,
        utilisateur_id: int,
        date_affectation: date,
    ) -> List[Affectation]:
        """
        Trouve les affectations d'un utilisateur pour une date specifique.

        Args:
            utilisateur_id: L'ID de l'utilisateur.
            date_affectation: La date recherchee.

        Returns:
            Liste des affectations (peut etre multiple si multi-chantiers).
        """
        pass

    @abstractmethod
    def find_by_chantier_and_date(
        self,
        chantier_id: int,
        date_affectation: date,
    ) -> List[Affectation]:
        """
        Trouve les affectations pour un chantier a une date specifique.

        Args:
            chantier_id: L'ID du chantier.
            date_affectation: La date recherchee.

        Returns:
            Liste des utilisateurs affectes ce jour-la.
        """
        pass

    @abstractmethod
    def find_non_planifies(
        self,
        date_debut: date,
        date_fin: date,
    ) -> List[int]:
        """
        Trouve les utilisateurs sans affectation sur une periode.

        Utilise pour identifier les utilisateurs disponibles (PLN-10).

        Args:
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Liste des IDs utilisateurs sans affectation sur cette periode.
        """
        pass

    @abstractmethod
    def find_utilisateurs_disponibles(
        self,
        date_cible: date,
    ) -> List[int]:
        """
        Trouve les utilisateurs disponibles pour une date donnee.

        Args:
            date_cible: La date pour laquelle chercher les disponibilites.

        Returns:
            Liste des IDs utilisateurs disponibles ce jour-la.
        """
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """
        Supprime une affectation.

        Args:
            id: L'identifiant de l'affectation a supprimer.

        Returns:
            True si supprimee, False si non trouvee.
        """
        pass

    @abstractmethod
    def delete_by_utilisateur_and_date_range(
        self,
        utilisateur_id: int,
        date_debut: date,
        date_fin: date,
    ) -> int:
        """
        Supprime les affectations d'un utilisateur sur une periode.

        Utilise pour la suppression en masse (ex: conges, depart).

        Args:
            utilisateur_id: L'ID de l'utilisateur.
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Nombre d'affectations supprimees.
        """
        pass

    @abstractmethod
    def delete_by_chantier_and_date_range(
        self,
        chantier_id: int,
        date_debut: date,
        date_fin: date,
    ) -> int:
        """
        Supprime les affectations d'un chantier sur une periode.

        Utilise quand un chantier est ferme ou annule.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Nombre d'affectations supprimees.
        """
        pass

    @abstractmethod
    def count_by_utilisateur(
        self,
        utilisateur_id: int,
        date_debut: date,
        date_fin: date,
    ) -> int:
        """
        Compte les affectations d'un utilisateur sur une periode.

        Args:
            utilisateur_id: L'ID de l'utilisateur.
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Nombre d'affectations.
        """
        pass

    @abstractmethod
    def count_by_chantier(
        self,
        chantier_id: int,
        date_debut: date,
        date_fin: date,
    ) -> int:
        """
        Compte les affectations pour un chantier sur une periode.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Nombre d'affectations.
        """
        pass

    @abstractmethod
    def exists_for_utilisateur_and_date(
        self,
        utilisateur_id: int,
        date_affectation: date,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """
        Verifie si un utilisateur a deja une affectation pour une date.

        Utilise pour detecter les conflits (PLN-12).

        Args:
            utilisateur_id: L'ID de l'utilisateur.
            date_affectation: La date a verifier.
            exclude_id: ID d'affectation a exclure (pour les mises a jour).

        Returns:
            True si une affectation existe deja.
        """
        pass

    @abstractmethod
    def find_recurrentes_actives(
        self,
        utilisateur_id: Optional[int] = None,
        chantier_id: Optional[int] = None,
    ) -> List[Affectation]:
        """
        Trouve les affectations recurrentes actives.

        Args:
            utilisateur_id: Filtrer par utilisateur (optionnel).
            chantier_id: Filtrer par chantier (optionnel).

        Returns:
            Liste des affectations recurrentes.
        """
        pass
