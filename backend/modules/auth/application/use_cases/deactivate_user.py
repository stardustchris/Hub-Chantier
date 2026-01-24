"""Use Case DeactivateUser - Desactivation/Activation d'un utilisateur."""

from typing import Callable, Optional

from ...domain.repositories import UserRepository
from ...domain.events import UserDeactivatedEvent, UserActivatedEvent
from ..dtos import UserDTO


class UserNotFoundError(Exception):
    """Exception levée quand l'utilisateur n'est pas trouvé."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.message = f"Utilisateur {user_id} non trouvé"
        super().__init__(self.message)


class DeactivateUserUseCase:
    """
    Cas d'utilisation : Désactivation d'un utilisateur (USR-10).

    Permet de désactiver un compte utilisateur sans supprimer ses données historiques.
    La révocation est instantanée.

    Attributes:
        user_repo: Repository pour accéder aux utilisateurs.
        event_publisher: Fonction pour publier les events (optionnel).
    """

    def __init__(
        self,
        user_repo: UserRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            user_repo: Repository utilisateurs (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.user_repo = user_repo
        self.event_publisher = event_publisher

    def execute(self, user_id: int) -> UserDTO:
        """
        Désactive un utilisateur.

        Args:
            user_id: ID de l'utilisateur à désactiver.

        Returns:
            UserDTO de l'utilisateur désactivé.

        Raises:
            UserNotFoundError: Si l'utilisateur n'existe pas.
        """
        # Récupérer l'utilisateur
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Désactiver
        user.deactivate()

        # Sauvegarder
        user = self.user_repo.save(user)

        # Publier l'event
        if self.event_publisher:
            event = UserDeactivatedEvent(
                user_id=user.id,
                email=str(user.email),
            )
            self.event_publisher(event)

        return UserDTO.from_entity(user)


class ActivateUserUseCase:
    """
    Cas d'utilisation : Réactivation d'un utilisateur.

    Permet de réactiver un compte utilisateur précédemment désactivé.

    Attributes:
        user_repo: Repository pour accéder aux utilisateurs.
        event_publisher: Fonction pour publier les events (optionnel).
    """

    def __init__(
        self,
        user_repo: UserRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            user_repo: Repository utilisateurs (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.user_repo = user_repo
        self.event_publisher = event_publisher

    def execute(self, user_id: int) -> UserDTO:
        """
        Active un utilisateur.

        Args:
            user_id: ID de l'utilisateur à activer.

        Returns:
            UserDTO de l'utilisateur activé.

        Raises:
            UserNotFoundError: Si l'utilisateur n'existe pas.
        """
        # Récupérer l'utilisateur
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Activer
        user.activate()

        # Sauvegarder
        user = self.user_repo.save(user)

        # Publier l'event
        if self.event_publisher:
            event = UserActivatedEvent(
                user_id=user.id,
                email=str(user.email),
            )
            self.event_publisher(event)

        return UserDTO.from_entity(user)
