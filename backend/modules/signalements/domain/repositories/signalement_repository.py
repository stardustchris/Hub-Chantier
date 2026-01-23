"""Interface SignalementRepository - Abstraction pour la persistance des signalements."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Tuple

from ..entities import Signalement
from ..value_objects import Priorite, StatutSignalement


class SignalementRepository(ABC):
    """
    Interface abstraite pour la persistance des signalements.

    Cette interface définit le contrat pour l'accès aux données signalements.
    L'implémentation concrète se trouve dans la couche Infrastructure.
    """

    @abstractmethod
    def find_by_id(self, signalement_id: int) -> Optional[Signalement]:
        """
        Trouve un signalement par son ID.

        Args:
            signalement_id: L'identifiant unique du signalement.

        Returns:
            Le signalement trouvé ou None.
        """
        pass

    @abstractmethod
    def save(self, signalement: Signalement) -> Signalement:
        """
        Persiste un signalement (création ou mise à jour).

        Args:
            signalement: Le signalement à sauvegarder.

        Returns:
            Le signalement sauvegardé (avec ID si création).
        """
        pass

    @abstractmethod
    def delete(self, signalement_id: int) -> bool:
        """
        Supprime un signalement.

        Args:
            signalement_id: L'identifiant du signalement à supprimer.

        Returns:
            True si supprimé, False si non trouvé.
        """
        pass

    @abstractmethod
    def find_by_chantier(
        self,
        chantier_id: int,
        skip: int = 0,
        limit: int = 100,
        statut: Optional[StatutSignalement] = None,
        priorite: Optional[Priorite] = None,
    ) -> List[Signalement]:
        """
        Récupère les signalements d'un chantier.

        Args:
            chantier_id: ID du chantier.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum d'éléments.
            statut: Filtrer par statut (optionnel).
            priorite: Filtrer par priorité (optionnel).

        Returns:
            Liste des signalements.
        """
        pass

    @abstractmethod
    def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
        chantier_ids: Optional[List[int]] = None,
        statut: Optional[StatutSignalement] = None,
        priorite: Optional[Priorite] = None,
        date_debut: Optional[datetime] = None,
        date_fin: Optional[datetime] = None,
    ) -> Tuple[List[Signalement], int]:
        """
        Récupère tous les signalements avec filtres (vue globale admin/conducteur).

        Args:
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum d'éléments.
            chantier_ids: Liste des chantiers à inclure (None = tous).
            statut: Filtrer par statut (optionnel).
            priorite: Filtrer par priorité (optionnel).
            date_debut: Filtrer par date de création >= (optionnel).
            date_fin: Filtrer par date de création <= (optionnel).

        Returns:
            Tuple (liste des signalements, total count).
        """
        pass

    @abstractmethod
    def find_by_createur(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Signalement]:
        """
        Récupère les signalements créés par un utilisateur.

        Args:
            user_id: ID de l'utilisateur créateur.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum d'éléments.

        Returns:
            Liste des signalements.
        """
        pass

    @abstractmethod
    def find_assignes_a(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Signalement]:
        """
        Récupère les signalements assignés à un utilisateur.

        Args:
            user_id: ID de l'utilisateur assigné.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum d'éléments.

        Returns:
            Liste des signalements.
        """
        pass

    @abstractmethod
    def count_by_chantier(
        self,
        chantier_id: int,
        statut: Optional[StatutSignalement] = None,
    ) -> int:
        """
        Compte le nombre de signalements dans un chantier.

        Args:
            chantier_id: ID du chantier.
            statut: Filtrer par statut (optionnel).

        Returns:
            Nombre de signalements.
        """
        pass

    @abstractmethod
    def count_by_statut(self, chantier_id: Optional[int] = None) -> dict:
        """
        Compte les signalements par statut.

        Args:
            chantier_id: ID du chantier (optionnel, tous si None).

        Returns:
            Dict avec les comptages par statut.
        """
        pass

    @abstractmethod
    def count_by_priorite(self, chantier_id: Optional[int] = None) -> dict:
        """
        Compte les signalements par priorité.

        Args:
            chantier_id: ID du chantier (optionnel, tous si None).

        Returns:
            Dict avec les comptages par priorité.
        """
        pass

    @abstractmethod
    def find_en_retard(
        self,
        chantier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Signalement]:
        """
        Récupère les signalements en retard (SIG-16).

        Args:
            chantier_id: ID du chantier (optionnel, tous si None).
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum d'éléments.

        Returns:
            Liste des signalements en retard.
        """
        pass

    @abstractmethod
    def find_a_escalader(
        self,
        seuil_pourcentage: float = 50.0,
    ) -> List[Signalement]:
        """
        Récupère les signalements nécessitant une escalade (SIG-16, SIG-17).

        Args:
            seuil_pourcentage: Seuil en pourcentage du temps écoulé.

        Returns:
            Liste des signalements à escalader.
        """
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        chantier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Signalement], int]:
        """
        Recherche des signalements par texte (SIG-10).

        Args:
            query: Texte à rechercher dans titre/description.
            chantier_id: Filtrer par chantier (optionnel).
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Tuple (liste des signalements, total count).
        """
        pass

    @abstractmethod
    def get_statistiques(
        self,
        chantier_id: Optional[int] = None,
        date_debut: Optional[datetime] = None,
        date_fin: Optional[datetime] = None,
    ) -> dict:
        """
        Récupère les statistiques des signalements (SIG-18).

        Args:
            chantier_id: ID du chantier (optionnel, tous si None).
            date_debut: Date de début (optionnel).
            date_fin: Date de fin (optionnel).

        Returns:
            Dict avec les statistiques (total, par statut, par priorité, en retard, etc.).
        """
        pass
