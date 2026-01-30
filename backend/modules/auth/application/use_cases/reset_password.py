"""Use case pour réinitialiser le mot de passe avec un token."""

from datetime import datetime

from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects import PasswordHash
from ...domain.exceptions import (
    InvalidResetTokenError,
    UserNotFoundError,
    WeakPasswordError,
)
from shared.infrastructure.password_hasher import PasswordHasher


class ResetPasswordUseCase:
    """
    Use case pour réinitialiser le mot de passe via un token.

    Valide le token et met à jour le mot de passe.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        """
        Initialise le use case.

        Args:
            user_repository: Repository des utilisateurs.
            password_hasher: Service de hachage de mot de passe.
        """
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, token: str, new_password: str) -> None:
        """
        Réinitialise le mot de passe avec un token.

        Args:
            token: Token de réinitialisation.
            new_password: Nouveau mot de passe en clair.

        Raises:
            InvalidResetTokenError: Si le token est invalide ou expiré.
            WeakPasswordError: Si le mot de passe est trop faible.
        """
        # Rechercher l'utilisateur par token de réinitialisation
        user = self.user_repository.find_by_password_reset_token(token)

        if not user:
            raise InvalidResetTokenError("Token de réinitialisation invalide ou expiré")

        # Vérifier que le token n'a pas expiré
        if not user.is_password_reset_token_valid():
            raise InvalidResetTokenError("Token de réinitialisation expiré")

        # Valider la force du nouveau mot de passe
        self._validate_password_strength(new_password)

        # Hasher le nouveau mot de passe
        password_hash_str = self.password_hasher.hash(new_password)
        password_hash = PasswordHash(password_hash_str)

        # Mettre à jour le mot de passe (cela invalide le token automatiquement)
        user.update_password(password_hash)

        # Réinitialiser les tentatives de connexion échouées
        user.reset_failed_login_attempts()

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
