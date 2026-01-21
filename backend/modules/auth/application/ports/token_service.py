"""Interface TokenService - Port pour la génération de tokens."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ...domain.entities import User


@dataclass(frozen=True)
class TokenPayload:
    """Payload décodé d'un token."""

    user_id: int
    email: str
    role: str
    exp: int  # Timestamp d'expiration


class TokenService(ABC):
    """
    Interface abstraite pour la génération et validation de tokens.

    L'implémentation concrète (JWT, etc.) se trouve dans Adapters.

    Note:
        L'Application ne connaît pas le format exact du token.
    """

    @abstractmethod
    def generate(self, user: User) -> str:
        """
        Génère un token d'accès pour un utilisateur.

        Args:
            user: L'utilisateur pour lequel générer le token.

        Returns:
            Le token sous forme de string.
        """
        pass

    @abstractmethod
    def verify(self, token: str) -> Optional[TokenPayload]:
        """
        Vérifie et décode un token.

        Args:
            token: Le token à vérifier.

        Returns:
            Le payload décodé ou None si invalide/expiré.
        """
        pass

    @abstractmethod
    def get_user_id(self, token: str) -> Optional[int]:
        """
        Extrait l'ID utilisateur d'un token.

        Args:
            token: Le token à décoder.

        Returns:
            L'ID utilisateur ou None si invalide.
        """
        pass
