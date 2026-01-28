"""Use Case RevokeAPIKey - Révocation d'une clé API."""

from ...domain.repositories.api_key_repository import APIKeyRepository
from ..dtos.api_key_dtos import RevokeAPIKeyDTO


class APIKeyNotFoundError(Exception):
    """Erreur levée si la clé API n'est pas trouvée."""

    pass


class UnauthorizedRevokeError(Exception):
    """Erreur levée si l'utilisateur n'est pas propriétaire de la clé."""

    pass


class RevokeAPIKeyUseCase:
    """
    Use Case pour révoquer une clé API.

    La révocation désactive la clé (is_active=False) mais conserve l'historique
    pour l'audit. Suppression physique possible mais déconseillée.

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

    def execute(self, dto: RevokeAPIKeyDTO) -> None:
        """
        Révoque une clé API.

        Vérifie que l'utilisateur est bien propriétaire avant révocation.

        Args:
            dto: Données de révocation (api_key_id, user_id)

        Raises:
            APIKeyNotFoundError: Si clé non trouvée
            UnauthorizedRevokeError: Si user_id ne correspond pas au propriétaire
        """
        # 1. Récupérer la clé
        api_key = self.api_key_repo.find_by_id(dto.api_key_id)

        if not api_key:
            raise APIKeyNotFoundError(
                f"Clé API {dto.api_key_id} non trouvée"
            )

        # 2. Vérifier que l'utilisateur est propriétaire
        if api_key.user_id != dto.user_id:
            raise UnauthorizedRevokeError(
                f"L'utilisateur {dto.user_id} n'est pas propriétaire "
                f"de la clé {dto.api_key_id}"
            )

        # 3. Révoquer (logique métier dans l'entity)
        api_key.revoke()

        # 4. Sauvegarder
        self.api_key_repo.save(api_key)
