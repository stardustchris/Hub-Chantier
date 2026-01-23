"""Interface ReponseRepository - Abstraction pour la persistance des réponses."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import Reponse


class ReponseRepository(ABC):
    """
    Interface abstraite pour la persistance des réponses aux signalements.

    Cette interface définit le contrat pour l'accès aux données réponses.
    L'implémentation concrète se trouve dans la couche Infrastructure.
    """

    @abstractmethod
    def find_by_id(self, reponse_id: int) -> Optional[Reponse]:
        """
        Trouve une réponse par son ID.

        Args:
            reponse_id: L'identifiant unique de la réponse.

        Returns:
            La réponse trouvée ou None.
        """
        pass

    @abstractmethod
    def save(self, reponse: Reponse) -> Reponse:
        """
        Persiste une réponse (création ou mise à jour).

        Args:
            reponse: La réponse à sauvegarder.

        Returns:
            La réponse sauvegardée (avec ID si création).
        """
        pass

    @abstractmethod
    def delete(self, reponse_id: int) -> bool:
        """
        Supprime une réponse.

        Args:
            reponse_id: L'identifiant de la réponse à supprimer.

        Returns:
            True si supprimée, False si non trouvée.
        """
        pass

    @abstractmethod
    def find_by_signalement(
        self,
        signalement_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Reponse]:
        """
        Récupère les réponses d'un signalement.

        Args:
            signalement_id: ID du signalement.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum d'éléments.

        Returns:
            Liste des réponses ordonnées par date de création.
        """
        pass

    @abstractmethod
    def find_by_auteur(
        self,
        auteur_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Reponse]:
        """
        Récupère les réponses d'un auteur.

        Args:
            auteur_id: ID de l'auteur.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum d'éléments.

        Returns:
            Liste des réponses.
        """
        pass

    @abstractmethod
    def count_by_signalement(self, signalement_id: int) -> int:
        """
        Compte le nombre de réponses d'un signalement.

        Args:
            signalement_id: ID du signalement.

        Returns:
            Nombre de réponses.
        """
        pass

    @abstractmethod
    def find_resolution(self, signalement_id: int) -> Optional[Reponse]:
        """
        Trouve la réponse marquée comme résolution.

        Args:
            signalement_id: ID du signalement.

        Returns:
            La réponse de résolution ou None.
        """
        pass

    @abstractmethod
    def delete_by_signalement(self, signalement_id: int) -> int:
        """
        Supprime toutes les réponses d'un signalement.

        Args:
            signalement_id: ID du signalement.

        Returns:
            Nombre de réponses supprimées.
        """
        pass
