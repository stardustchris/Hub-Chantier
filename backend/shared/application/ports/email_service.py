"""Port EmailService - Interface abstraite pour l'envoi d'emails."""

from abc import ABC, abstractmethod
from typing import List, Optional


class EmailServicePort(ABC):
    """
    Interface abstraite pour le service d'envoi d'emails.

    L'implémentation concrète (SMTP, console, etc.) se trouve dans Infrastructure.
    """

    @abstractmethod
    def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> bool:
        """Envoie un email."""
        pass

    @abstractmethod
    def send_password_reset_email(
        self, to: str, token: str, user_name: str
    ) -> bool:
        """Envoie un email de réinitialisation de mot de passe."""
        pass

    @abstractmethod
    def send_invitation_email(
        self,
        to: str,
        token: str,
        user_name: str,
        inviter_name: str,
        role: str,
    ) -> bool:
        """Envoie un email d'invitation."""
        pass
