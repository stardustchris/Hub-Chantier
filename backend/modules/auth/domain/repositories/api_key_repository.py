"""Repository Interface APIKeyRepository - Abstraction persistence clés API."""

from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from ..entities.api_key import APIKey


class APIKeyRepository(ABC):
    """
    Interface abstraite pour la persistence des clés API.

    Définit les opérations de persistence sans dépendre de l'implémentation
    (SQLAlchemy, MongoDB, etc). Suit le principe d'Inversion de Dépendance.
    """

    @abstractmethod
    def find_by_hash(self, key_hash: str) -> Optional[APIKey]:
        """
        Recherche une clé API par son hash.

        Utilisé pour l'authentification (très fréquent, doit être rapide).

        Args:
            key_hash: Hash SHA256 du secret (64 caractères hex)

        Returns:
            APIKey si trouvé, None sinon
        """
        pass

    @abstractmethod
    def find_by_user(self, user_id: int, include_revoked: bool = False) -> List[APIKey]:
        """
        Liste toutes les clés d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            include_revoked: Inclure les clés révoquées (défaut: False)

        Returns:
            Liste des clés API (peut être vide)
        """
        pass

    @abstractmethod
    def find_by_id(self, api_key_id: UUID) -> Optional[APIKey]:
        """
        Recherche une clé API par son ID.

        Args:
            api_key_id: UUID de la clé

        Returns:
            APIKey si trouvé, None sinon
        """
        pass

    @abstractmethod
    def save(self, api_key: APIKey) -> APIKey:
        """
        Sauvegarde ou met à jour une clé API.

        Args:
            api_key: Entity APIKey à sauvegarder

        Returns:
            APIKey sauvegardé (avec ID si création)

        Raises:
            Exception si erreur de persistence
        """
        pass

    @abstractmethod
    def delete(self, api_key_id: UUID) -> bool:
        """
        Supprime physiquement une clé API.

        Note: La révocation (is_active=False) est préférable pour l'audit.

        Args:
            api_key_id: UUID de la clé à supprimer

        Returns:
            True si supprimé, False si non trouvé
        """
        pass

    @abstractmethod
    def find_expired_keys(self) -> List[APIKey]:
        """
        Trouve toutes les clés expirées.

        Utilisé pour le cleanup automatique des clés expirées.

        Returns:
            Liste des clés expirées
        """
        pass
