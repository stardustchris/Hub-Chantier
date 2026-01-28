"""Repository Implementation SQLAlchemyAPIKeyRepository - Persistence clés API."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session

from ...domain.entities.api_key import APIKey
from ...domain.repositories.api_key_repository import APIKeyRepository
from .api_key_model import APIKeyModel


class SQLAlchemyAPIKeyRepository(APIKeyRepository):
    """
    Implémentation SQLAlchemy du repository APIKeyRepository.

    Gère la persistence des clés API en base de données PostgreSQL.

    Attributes:
        session: Session SQLAlchemy pour les requêtes DB
    """

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy (injection de dépendance)
        """
        self.session = session

    def find_by_hash(self, key_hash: str) -> Optional[APIKey]:
        """
        Recherche une clé API par son hash.

        Utilisé pour l'authentification (très fréquent, doit être rapide).
        Index unique sur key_hash garantit performance O(1).

        Args:
            key_hash: Hash SHA256 du secret (64 caractères hex)

        Returns:
            APIKey si trouvé, None sinon
        """
        model = (
            self.session.query(APIKeyModel)
            .filter(APIKeyModel.key_hash == key_hash)
            .first()
        )

        return self._to_entity(model) if model else None

    def find_by_user(
        self, user_id: int, include_revoked: bool = False
    ) -> List[APIKey]:
        """
        Liste toutes les clés d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            include_revoked: Inclure les clés révoquées (défaut: False)

        Returns:
            Liste des clés API (peut être vide)
        """
        query = self.session.query(APIKeyModel).filter(
            APIKeyModel.user_id == user_id
        )

        if not include_revoked:
            query = query.filter(APIKeyModel.is_active == True)

        models = query.order_by(APIKeyModel.created_at.desc()).all()

        return [self._to_entity(model) for model in models]

    def find_by_id(self, api_key_id: UUID) -> Optional[APIKey]:
        """
        Recherche une clé API par son ID.

        Args:
            api_key_id: UUID de la clé

        Returns:
            APIKey si trouvé, None sinon
        """
        model = (
            self.session.query(APIKeyModel)
            .filter(APIKeyModel.id == api_key_id)
            .first()
        )

        return self._to_entity(model) if model else None

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
        # Vérifier si la clé existe déjà
        existing_model = (
            self.session.query(APIKeyModel)
            .filter(APIKeyModel.id == api_key.id)
            .first()
        )

        if existing_model:
            # Mise à jour
            self._update_model_from_entity(existing_model, api_key)
        else:
            # Création
            existing_model = self._to_model(api_key)
            self.session.add(existing_model)

        self.session.commit()
        self.session.refresh(existing_model)

        return self._to_entity(existing_model)

    def delete(self, api_key_id: UUID) -> bool:
        """
        Supprime physiquement une clé API.

        Note: La révocation (is_active=False) est préférable pour l'audit.

        Args:
            api_key_id: UUID de la clé à supprimer

        Returns:
            True si supprimé, False si non trouvé
        """
        model = (
            self.session.query(APIKeyModel)
            .filter(APIKeyModel.id == api_key_id)
            .first()
        )

        if not model:
            return False

        self.session.delete(model)
        self.session.commit()

        return True

    def find_expired_keys(self) -> List[APIKey]:
        """
        Trouve toutes les clés expirées.

        Utilisé pour le cleanup automatique des clés expirées.

        Returns:
            Liste des clés expirées
        """
        now = datetime.utcnow()

        models = (
            self.session.query(APIKeyModel)
            .filter(
                APIKeyModel.expires_at != None,
                APIKeyModel.expires_at < now,
                APIKeyModel.is_active == True,
            )
            .all()
        )

        return [self._to_entity(model) for model in models]

    # --- Mappers Model <-> Entity ---

    def _to_entity(self, model: APIKeyModel) -> APIKey:
        """
        Convertit un Model SQLAlchemy en Entity Domain.

        Args:
            model: APIKeyModel (infrastructure)

        Returns:
            APIKey entity (domain)
        """
        return APIKey(
            id=model.id,
            key_hash=model.key_hash,
            key_prefix=model.key_prefix,
            user_id=model.user_id,
            nom=model.nom,
            description=model.description,
            scopes=model.scopes or [],
            rate_limit_per_hour=model.rate_limit_per_hour,
            is_active=model.is_active,
            last_used_at=model.last_used_at,
            expires_at=model.expires_at,
            created_at=model.created_at,
        )

    def _to_model(self, entity: APIKey) -> APIKeyModel:
        """
        Convertit une Entity Domain en Model SQLAlchemy.

        Args:
            entity: APIKey entity (domain)

        Returns:
            APIKeyModel (infrastructure)
        """
        return APIKeyModel(
            id=entity.id,
            key_hash=entity.key_hash,
            key_prefix=entity.key_prefix,
            user_id=entity.user_id,
            nom=entity.nom,
            description=entity.description,
            scopes=entity.scopes,
            rate_limit_per_hour=entity.rate_limit_per_hour,
            is_active=entity.is_active,
            last_used_at=entity.last_used_at,
            expires_at=entity.expires_at,
            created_at=entity.created_at,
        )

    def _update_model_from_entity(
        self, model: APIKeyModel, entity: APIKey
    ) -> None:
        """
        Met à jour un Model SQLAlchemy depuis une Entity.

        Args:
            model: APIKeyModel à mettre à jour
            entity: APIKey source
        """
        model.key_hash = entity.key_hash
        model.key_prefix = entity.key_prefix
        model.user_id = entity.user_id
        model.nom = entity.nom
        model.description = entity.description
        model.scopes = entity.scopes
        model.rate_limit_per_hour = entity.rate_limit_per_hour
        model.is_active = entity.is_active
        model.last_used_at = entity.last_used_at
        model.expires_at = entity.expires_at
