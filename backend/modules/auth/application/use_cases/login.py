"""Use Case Login - Authentification d'un utilisateur."""

from ...domain.repositories import UserRepository
from ...domain.services import PasswordService
from ...domain.value_objects import Email
from ...domain.events import UserLoggedInEvent
from ..ports import TokenService
from ..dtos import LoginDTO, AuthResponseDTO, UserDTO, TokenDTO


class InvalidCredentialsError(Exception):
    """Exception levée quand les identifiants sont invalides."""

    def __init__(self, message: str = "Email ou mot de passe incorrect"):
        self.message = message
        super().__init__(self.message)


class UserInactiveError(Exception):
    """Exception levée quand le compte est désactivé."""

    def __init__(self, message: str = "Ce compte a été désactivé"):
        self.message = message
        super().__init__(self.message)


class LoginUseCase:
    """
    Cas d'utilisation : Connexion d'un utilisateur.

    Vérifie les identifiants et retourne un token JWT si valides.

    Attributes:
        user_repo: Repository pour accéder aux utilisateurs.
        password_service: Service pour vérifier les mots de passe.
        token_service: Service pour générer les tokens.
        event_publisher: Fonction pour publier les events (optionnel).
    """

    def __init__(
        self,
        user_repo: UserRepository,
        password_service: PasswordService,
        token_service: TokenService,
        event_publisher: callable = None,
    ):
        """
        Initialise le use case.

        Args:
            user_repo: Repository utilisateurs (interface).
            password_service: Service de hash (interface).
            token_service: Service de tokens (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.user_repo = user_repo
        self.password_service = password_service
        self.token_service = token_service
        self.event_publisher = event_publisher

    def execute(self, dto: LoginDTO) -> AuthResponseDTO:
        """
        Exécute la connexion.

        Args:
            dto: Les données de connexion (email, password).

        Returns:
            AuthResponseDTO contenant le user et le token.

        Raises:
            InvalidCredentialsError: Si email ou mot de passe incorrect.
            UserInactiveError: Si le compte est désactivé.
        """
        # Valider l'email
        try:
            email = Email(dto.email)
        except ValueError:
            raise InvalidCredentialsError()

        # Chercher l'utilisateur
        user = self.user_repo.find_by_email(email)
        if not user:
            raise InvalidCredentialsError()

        # Vérifier que le compte est actif
        if not user.is_active:
            raise UserInactiveError()

        # Vérifier le mot de passe
        if not self.password_service.verify(dto.password, user.password_hash):
            raise InvalidCredentialsError()

        # Générer le token
        access_token = self.token_service.generate(user)

        # Publier l'event
        if self.event_publisher:
            event = UserLoggedInEvent(
                user_id=user.id,
                email=str(user.email),
            )
            self.event_publisher(event)

        # Retourner la réponse
        return AuthResponseDTO(
            user=UserDTO.from_entity(user),
            token=TokenDTO(access_token=access_token),
        )
