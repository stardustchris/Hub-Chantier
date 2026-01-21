"""Interface UserRepository - Abstraction pour la persistence des utilisateurs."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import User
from ..value_objects import Email


class UserRepository(ABC):
    """
    Interface abstraite pour la persistence des utilisateurs.

    Cette interface définit le contrat pour l'accès aux données utilisateur.
    L'implémentation concrète se trouve dans la couche Infrastructure.

    Note:
        Le Domain ne connaît pas l'implémentation (SQLAlchemy, etc.).
    """

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """
        Trouve un utilisateur par son ID.

        Args:
            user_id: L'identifiant unique de l'utilisateur.

        Returns:
            L'utilisateur trouvé ou None.
        """
        pass

    @abstractmethod
    def find_by_email(self, email: Email) -> Optional[User]:
        """
        Trouve un utilisateur par son email.

        Args:
            email: L'adresse email à rechercher.

        Returns:
            L'utilisateur trouvé ou None.
        """
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        """
        Persiste un utilisateur (création ou mise à jour).

        Args:
            user: L'utilisateur à sauvegarder.

        Returns:
            L'utilisateur sauvegardé (avec ID si création).
        """
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """
        Supprime un utilisateur.

        Args:
            user_id: L'identifiant de l'utilisateur à supprimer.

        Returns:
            True si supprimé, False si non trouvé.
        """
        pass

    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Récupère tous les utilisateurs avec pagination.

        Args:
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum d'éléments à retourner.

        Returns:
            Liste des utilisateurs.
        """
        pass

    @abstractmethod
    def exists_by_email(self, email: Email) -> bool:
        """
        Vérifie si un email est déjà utilisé.

        Args:
            email: L'email à vérifier.

        Returns:
            True si l'email existe déjà.
        """
        pass
