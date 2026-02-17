"""Use case pour accepter une invitation."""

from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects import PasswordHash
from ...domain.exceptions import InvalidInvitationTokenError, WeakPasswordError
from ...domain.services.password_service import PasswordService


class AcceptInvitationUseCase:
    """
    Use case pour accepter une invitation et activer un compte.

    Valide le token d'invitation et permet à l'utilisateur de définir son mot de passe.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordService,
    ) -> None:
        """
        Initialise le use case.

        Args:
            user_repository: Repository des utilisateurs.
            password_hasher: Service de hachage de mot de passe.
        """
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, token: str, password: str) -> None:
        """
        Accepte une invitation et active le compte.

        Args:
            token: Token d'invitation.
            password: Mot de passe choisi par l'utilisateur.

        Raises:
            InvalidInvitationTokenError: Si le token est invalide ou expiré.
            WeakPasswordError: Si le mot de passe est trop faible.
        """
        # Rechercher l'utilisateur par token d'invitation
        user = self.user_repository.find_by_invitation_token(token)

        if not user:
            raise InvalidInvitationTokenError("Token d'invitation invalide ou expiré")

        # Vérifier que le token n'a pas expiré
        if not user.is_invitation_token_valid():
            raise InvalidInvitationTokenError("Token d'invitation expiré")

        # Valider la force du mot de passe
        self._validate_password_strength(password)

        # Hasher le mot de passe
        password_hash_str = self.password_hasher.hash(password)
        password_hash = PasswordHash(password_hash_str)

        # Accepter l'invitation (active le compte et invalide le token)
        user.accept_invitation(password_hash)

        # Sauvegarder les modifications
        self.user_repository.save(user)

    def _validate_password_strength(self, password: str) -> None:
        """
        Valide la force du mot de passe.

        Args:
            password: Mot de passe à valider.

        Raises:
            WeakPasswordError: Si le mot de passe est trop faible.
        """
        if len(password) < 8:
            raise WeakPasswordError("Le mot de passe doit contenir au moins 8 caractères")

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        if not (has_upper and has_lower and has_digit):
            raise WeakPasswordError(
                "Le mot de passe doit contenir au moins une majuscule, "
                "une minuscule et un chiffre"
            )
