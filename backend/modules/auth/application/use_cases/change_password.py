"""Use case pour changer le mot de passe d'un utilisateur connecté."""

from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects import PasswordHash
from ...domain.exceptions import (
    UserNotFoundError,
    InvalidCredentialsError,
    WeakPasswordError,
)
from shared.infrastructure.password_hasher import PasswordHasher


class ChangePasswordUseCase:
    """
    Use case pour changer le mot de passe.

    Vérifie l'ancien mot de passe avant d'autoriser le changement.
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

    def execute(
        self,
        user_id: int,
        old_password: str,
        new_password: str,
    ) -> None:
        """
        Change le mot de passe d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur.
            old_password: Ancien mot de passe (pour vérification).
            new_password: Nouveau mot de passe.

        Raises:
            UserNotFoundError: Si l'utilisateur n'existe pas.
            InvalidCredentialsError: Si l'ancien mot de passe est incorrect.
            WeakPasswordError: Si le nouveau mot de passe est trop faible.
        """
        # Récupérer l'utilisateur
        user = self.user_repository.find_by_id(user_id)

        if not user:
            raise UserNotFoundError(f"Utilisateur {user_id} non trouvé")

        # Vérifier l'ancien mot de passe
        if not self.password_hasher.verify(old_password, user.password_hash.value):
            raise InvalidCredentialsError("Ancien mot de passe incorrect")

        # Vérifier que le nouveau mot de passe est différent de l'ancien
        if old_password == new_password:
            raise WeakPasswordError(
                "Le nouveau mot de passe doit être différent de l'ancien"
            )

        # Valider la force du nouveau mot de passe
        self._validate_password_strength(new_password)

        # Hasher le nouveau mot de passe
        new_password_hash_str = self.password_hasher.hash(new_password)
        new_password_hash = PasswordHash(new_password_hash_str)

        # Mettre à jour le mot de passe
        user.update_password(new_password_hash)

        # Réinitialiser les tentatives de connexion échouées (si existantes)
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
