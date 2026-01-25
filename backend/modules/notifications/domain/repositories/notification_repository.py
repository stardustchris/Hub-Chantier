"""Interface NotificationRepository."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import Notification
from ..value_objects import NotificationType


class NotificationRepository(ABC):
    """
    Interface abstraite pour la persistence des notifications.

    L'implementation concrete se trouve dans la couche Infrastructure.
    """

    @abstractmethod
    def find_by_id(self, notification_id: int) -> Optional[Notification]:
        """Trouve une notification par son ID."""
        pass

    @abstractmethod
    def find_by_user(
        self,
        user_id: int,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Notification]:
        """
        Recupere les notifications d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur.
            unread_only: Si True, retourne uniquement les non lues.
            skip: Nombre d'elements a sauter (pagination).
            limit: Nombre maximum d'elements a retourner.

        Returns:
            Liste des notifications triees par date decroissante.
        """
        pass

    @abstractmethod
    def count_unread(self, user_id: int) -> int:
        """Compte les notifications non lues d'un utilisateur."""
        pass

    @abstractmethod
    def save(self, notification: Notification) -> Notification:
        """Persiste une notification (creation ou mise a jour)."""
        pass

    @abstractmethod
    def save_many(self, notifications: List[Notification]) -> List[Notification]:
        """Persiste plusieurs notifications en une transaction."""
        pass

    @abstractmethod
    def delete(self, notification_id: int) -> bool:
        """Supprime une notification. Retourne True si supprimee."""
        pass

    @abstractmethod
    def delete_all_for_user(self, user_id: int) -> int:
        """Supprime toutes les notifications d'un utilisateur. Retourne le nombre."""
        pass

    @abstractmethod
    def mark_all_as_read(self, user_id: int) -> int:
        """Marque toutes les notifications d'un utilisateur comme lues. Retourne le nombre."""
        pass

    @abstractmethod
    def find_by_type(
        self,
        user_id: int,
        notification_type: NotificationType,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Notification]:
        """Recupere les notifications d'un type specifique pour un utilisateur."""
        pass
