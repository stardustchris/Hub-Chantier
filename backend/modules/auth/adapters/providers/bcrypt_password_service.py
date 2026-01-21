"""Implémentation BcryptPasswordService - Hash des mots de passe avec bcrypt."""

import bcrypt

from ...domain.services import PasswordService
from ...domain.value_objects import PasswordHash


class BcryptPasswordService(PasswordService):
    """
    Implémentation du PasswordService utilisant bcrypt.

    Bcrypt est un algorithme de hash sécurisé conçu pour les mots de passe.
    Il inclut automatiquement un salt et est résistant aux attaques par force brute.

    Attributes:
        rounds: Nombre de rounds pour le hashing (défaut: 12).
    """

    def __init__(self, rounds: int = 12):
        """
        Initialise le service.

        Args:
            rounds: Complexité du hash (plus élevé = plus lent mais plus sûr).
        """
        self.rounds = rounds

    def hash(self, plain_password: str) -> PasswordHash:
        """
        Hash un mot de passe avec bcrypt.

        Args:
            plain_password: Le mot de passe en clair.

        Returns:
            Le hash encapsulé dans un PasswordHash.

        Raises:
            ValueError: Si le mot de passe est trop faible.
        """
        if not self.validate_strength(plain_password):
            raise ValueError(
                "Le mot de passe doit contenir au moins 8 caractères, "
                "une majuscule, une minuscule et un chiffre"
            )

        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return PasswordHash(hashed.decode("utf-8"))

    def verify(self, plain_password: str, password_hash: PasswordHash) -> bool:
        """
        Vérifie un mot de passe contre son hash bcrypt.

        Args:
            plain_password: Le mot de passe en clair.
            password_hash: Le hash stocké.

        Returns:
            True si le mot de passe correspond.
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                password_hash.value.encode("utf-8"),
            )
        except Exception:
            return False
