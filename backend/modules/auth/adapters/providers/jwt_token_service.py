"""Implémentation JWTTokenService - Génération de tokens JWT."""

from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError

from ...domain.entities import User
from ...application.ports import TokenService, TokenPayload


class JWTTokenService(TokenService):
    """
    Implémentation du TokenService utilisant JWT (JSON Web Tokens).

    Utilise la bibliothèque python-jose pour la génération et validation.

    Attributes:
        secret_key: Clé secrète pour signer les tokens.
        algorithm: Algorithme de signature (défaut: HS256).
        expires_minutes: Durée de validité en minutes (défaut: 60).
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        expires_minutes: int = 60,
    ):
        """
        Initialise le service.

        Args:
            secret_key: Clé secrète pour la signature JWT.
            algorithm: Algorithme de signature.
            expires_minutes: Durée de validité du token.
        """
        if not secret_key or len(secret_key) < 32:
            raise ValueError("La clé secrète doit faire au moins 32 caractères")

        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expires_minutes = expires_minutes

    def generate(self, user: User) -> str:
        """
        Génère un token JWT pour un utilisateur.

        Args:
            user: L'utilisateur pour lequel générer le token.

        Returns:
            Le token JWT encodé.
        """
        expire = datetime.utcnow() + timedelta(minutes=self.expires_minutes)

        payload = {
            "sub": str(user.id),
            "email": str(user.email),
            "role": user.role.value,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify(self, token: str) -> Optional[TokenPayload]:
        """
        Vérifie et décode un token JWT.

        Args:
            token: Le token à vérifier.

        Returns:
            Le payload décodé ou None si invalide/expiré.
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )

            return TokenPayload(
                user_id=int(payload["sub"]),
                email=payload["email"],
                role=payload["role"],
                exp=payload["exp"],
            )
        except JWTError:
            return None

    def get_user_id(self, token: str) -> Optional[int]:
        """
        Extrait l'ID utilisateur d'un token.

        Args:
            token: Le token à décoder.

        Returns:
            L'ID utilisateur ou None si invalide.
        """
        payload = self.verify(token)
        return payload.user_id if payload else None
