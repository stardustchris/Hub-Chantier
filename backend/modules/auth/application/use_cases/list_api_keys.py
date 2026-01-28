"""Use Case ListAPIKeys - Liste les clés API d'un utilisateur."""

from typing import List

from ...domain.repositories.api_key_repository import APIKeyRepository
from ...domain.entities.api_key import APIKey
from ..dtos.api_key_dtos import APIKeyInfoDTO


class ListAPIKeysUseCase:
    """
    Use Case pour lister les clés API d'un utilisateur.

    Retourne uniquement les informations publiques (pas de secret).
    Par défaut, n'inclut pas les clés révoquées.

    Attributes:
        api_key_repo: Repository pour persistence clés API
    """

    def __init__(self, api_key_repo: APIKeyRepository):
        """
        Initialise le use case.

        Args:
            api_key_repo: Repository APIKeyRepository (injection de dépendance)
        """
        self.api_key_repo = api_key_repo

    def execute(
        self, user_id: int, include_revoked: bool = False
    ) -> List[APIKeyInfoDTO]:
        """
        Liste toutes les clés API d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            include_revoked: Inclure les clés révoquées (défaut: False)

        Returns:
            Liste de APIKeyInfoDTO (sans secrets)
        """
        # Récupérer les clés depuis le repository
        api_keys = self.api_key_repo.find_by_user(
            user_id=user_id, include_revoked=include_revoked
        )

        # Convertir entities en DTOs (mapper)
        return [self._to_dto(key) for key in api_keys]

    def _to_dto(self, api_key: APIKey) -> APIKeyInfoDTO:
        """
        Convertit une entity APIKey en DTO pour affichage.

        Args:
            api_key: Entity Domain

        Returns:
            DTO sans secret
        """
        return APIKeyInfoDTO(
            id=api_key.id,
            key_prefix=api_key.key_prefix,
            nom=api_key.nom,
            description=api_key.description,
            scopes=api_key.scopes,
            rate_limit_per_hour=api_key.rate_limit_per_hour,
            is_active=api_key.is_active,
            last_used_at=api_key.last_used_at,
            expires_at=api_key.expires_at,
            created_at=api_key.created_at,
        )
