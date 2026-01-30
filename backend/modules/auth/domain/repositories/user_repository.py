"""Interface UserRepository - Abstraction pour la persistence des utilisateurs."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import User
from ..value_objects import Email, Role, TypeUtilisateur


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
    def find_by_code(self, code_utilisateur: str) -> Optional[User]:
        """
        Trouve un utilisateur par son code/matricule.

        Args:
            code_utilisateur: Le code utilisateur (matricule).

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
    def count(self) -> int:
        """
        Compte le nombre total d'utilisateurs.

        Returns:
            Nombre total d'utilisateurs.
        """
        pass

    @abstractmethod
    def find_by_role(self, role: Role, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Trouve les utilisateurs par rôle.

        Args:
            role: Le rôle à filtrer.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des utilisateurs avec ce rôle.
        """
        pass

    @abstractmethod
    def find_by_type(
        self, type_utilisateur: TypeUtilisateur, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Trouve les utilisateurs par type (employé/sous-traitant).

        Args:
            type_utilisateur: Le type à filtrer.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des utilisateurs de ce type.
        """
        pass

    @abstractmethod
    def find_active(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Trouve les utilisateurs actifs.

        Args:
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des utilisateurs actifs.
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

    @abstractmethod
    def exists_by_code(self, code_utilisateur: str) -> bool:
        """
        Vérifie si un code utilisateur est déjà utilisé.

        Args:
            code_utilisateur: Le code à vérifier.

        Returns:
            True si le code existe déjà.
        """
        pass

    @abstractmethod
    def search(
        self,
        query: Optional[str] = None,
        role: Optional[Role] = None,
        type_utilisateur: Optional[TypeUtilisateur] = None,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[User], int]:
        """
        Recherche des utilisateurs avec filtres multiples.

        Args:
            query: Texte à rechercher dans nom, prénom, email.
            role: Filtrer par rôle (optionnel).
            type_utilisateur: Filtrer par type (optionnel).
            active_only: Filtrer les actifs uniquement.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Tuple (liste des utilisateurs, total count).
        """
        pass

    @abstractmethod
    def find_by_password_reset_token(self, token: str) -> Optional[User]:
        """
        Trouve un utilisateur par son token de réinitialisation de mot de passe.

        Args:
            token: Le token de réinitialisation.

        Returns:
            L'utilisateur trouvé ou None.
        """
        pass

    @abstractmethod
    def find_by_invitation_token(self, token: str) -> Optional[User]:
        """
        Trouve un utilisateur par son token d'invitation.

        Args:
            token: Le token d'invitation.

        Returns:
            L'utilisateur trouvé ou None.
        """
        pass

    @abstractmethod
    def find_by_email_verification_token(self, token: str) -> Optional[User]:
        """
        Trouve un utilisateur par son token de vérification d'email.

        Args:
            token: Le token de vérification.

        Returns:
            L'utilisateur trouvé ou None.
        """
        pass
