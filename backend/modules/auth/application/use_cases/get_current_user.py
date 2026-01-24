"""Use Case GetCurrentUser - Récupération de l'utilisateur connecté."""


from ...domain.repositories import UserRepository
from ..ports import TokenService
from ..dtos import UserDTO


class InvalidTokenError(Exception):
    """Exception levée quand le token est invalide."""

    def __init__(self, message: str = "Token invalide ou expiré"):
        self.message = message
        super().__init__(self.message)


class UserNotFoundError(Exception):
    """Exception levée quand l'utilisateur n'existe pas."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.message = f"Utilisateur {user_id} non trouvé"
        super().__init__(self.message)


class GetCurrentUserUseCase:
    """
    Cas d'utilisation : Récupération de l'utilisateur connecté.

    Décode le token et retourne les informations de l'utilisateur.

    Attributes:
        user_repo: Repository pour accéder aux utilisateurs.
        token_service: Service pour décoder les tokens.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        token_service: TokenService,
    ):
        """
        Initialise le use case.

        Args:
            user_repo: Repository utilisateurs (interface).
            token_service: Service de tokens (interface).
        """
        self.user_repo = user_repo
        self.token_service = token_service

    def execute(self, token: str) -> UserDTO:
        """
        Récupère l'utilisateur à partir du token.

        Args:
            token: Le JWT token.

        Returns:
            UserDTO avec les informations de l'utilisateur.

        Raises:
            InvalidTokenError: Si le token est invalide ou expiré.
            UserNotFoundError: Si l'utilisateur n'existe plus.
        """
        # Décoder le token
        user_id = self.token_service.get_user_id(token)
        if user_id is None:
            raise InvalidTokenError()

        # Chercher l'utilisateur
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Vérifier que le compte est actif
        if not user.is_active:
            raise InvalidTokenError("Ce compte a été désactivé")

        return UserDTO.from_entity(user)

    def execute_from_id(self, user_id: int) -> UserDTO:
        """
        Récupère l'utilisateur à partir de son ID.

        Utile quand le token a déjà été validé par le middleware.

        Args:
            user_id: L'ID de l'utilisateur.

        Returns:
            UserDTO avec les informations de l'utilisateur.

        Raises:
            UserNotFoundError: Si l'utilisateur n'existe pas.
        """
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        return UserDTO.from_entity(user)
