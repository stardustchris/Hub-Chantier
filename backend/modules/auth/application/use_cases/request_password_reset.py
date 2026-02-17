"""Use case pour demander une réinitialisation de mot de passe."""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from ...domain.repositories.user_repository import UserRepository
from ...domain.exceptions import UserNotFoundError
from shared.application.ports.email_service import EmailServicePort


class RequestPasswordResetUseCase:
    """
    Use case pour demander une réinitialisation de mot de passe.

    Génère un token de réinitialisation et envoie un email.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        email_service: EmailServicePort,
    ) -> None:
        """
        Initialise le use case.

        Args:
            user_repository: Repository des utilisateurs.
            email_service: Service d'envoi d'emails.
        """
        self.user_repository = user_repository
        self.email_service = email_service

    def execute(self, email: str) -> bool:
        """
        Demande une réinitialisation de mot de passe.

        Args:
            email: Email de l'utilisateur.

        Returns:
            True si l'email a été envoyé (ou si l'utilisateur n'existe pas pour éviter l'énumération).

        Note:
            Pour des raisons de sécurité, retourne toujours True même si l'utilisateur n'existe pas.
            Cela évite l'énumération des comptes valides.
        """
        # Rechercher l'utilisateur par email
        user = self.user_repository.find_by_email(email)

        # Si l'utilisateur n'existe pas, on retourne True pour éviter l'énumération
        # mais on n'envoie pas d'email
        if not user:
            return True

        # Vérifier que le compte est actif
        if not user.is_active:
            # Compte désactivé : on ne permet pas la réinitialisation
            # mais on retourne True pour éviter l'énumération
            return True

        # Générer un token de réinitialisation sécurisé
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)

        # Enregistrer le token sur l'utilisateur
        user.set_password_reset_token(token, expires_at)
        self.user_repository.save(user)

        # Envoyer l'email de réinitialisation
        email_sent = self.email_service.send_password_reset_email(
            to=user.email.value,
            token=token,
            user_name=user.nom_complet,
        )

        return email_sent
