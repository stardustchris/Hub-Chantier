"""Interface PasswordService - Abstraction pour le hashing de mots de passe."""

from abc import ABC, abstractmethod

from ..value_objects import PasswordHash


class PasswordService(ABC):
    """
    Interface abstraite pour le hashing et la vérification des mots de passe.

    L'implémentation concrète (bcrypt, argon2, etc.) se trouve dans Adapters.

    Note:
        Le Domain ne connaît pas l'algorithme de hashing utilisé.
    """

    @abstractmethod
    def hash(self, plain_password: str) -> PasswordHash:
        """
        Hash un mot de passe en clair.

        Args:
            plain_password: Le mot de passe en clair.

        Returns:
            Le hash du mot de passe encapsulé dans un PasswordHash.

        Raises:
            ValueError: Si le mot de passe est trop faible.
        """
        pass

    @abstractmethod
    def verify(self, plain_password: str, password_hash: PasswordHash) -> bool:
        """
        Vérifie un mot de passe contre son hash.

        Args:
            plain_password: Le mot de passe en clair à vérifier.
            password_hash: Le hash stocké.

        Returns:
            True si le mot de passe correspond.
        """
        pass

    def validate_strength(self, plain_password: str) -> bool:
        """
        Vérifie la force d'un mot de passe.

        Règles par défaut (peuvent être surchargées) :
        - Minimum 8 caractères
        - Au moins une majuscule
        - Au moins une minuscule
        - Au moins un chiffre

        Args:
            plain_password: Le mot de passe à valider.

        Returns:
            True si le mot de passe est assez fort.
        """
        if len(plain_password) < 8:
            return False
        if not any(c.isupper() for c in plain_password):
            return False
        if not any(c.islower() for c in plain_password):
            return False
        if not any(c.isdigit() for c in plain_password):
            return False
        return True
