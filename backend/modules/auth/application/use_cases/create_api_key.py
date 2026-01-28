"""Use Case CreateAPIKey - Création d'une clé API pour l'API publique v1."""

import secrets
import hashlib
from datetime import datetime, timedelta
from uuid import uuid4

from ...domain.entities.api_key import APIKey
from ...domain.repositories.api_key_repository import APIKeyRepository
from ..dtos.api_key_dtos import CreateAPIKeyDTO, APIKeyCreatedDTO


class CreateAPIKeyUseCase:
    """
    Use Case pour créer une nouvelle clé API.

    Génère un secret cryptographiquement sécurisé (hbc_xxxxx...),
    le hashe en SHA256, et ne stocke QUE le hash en base.

    Le secret est retourné UNE SEULE FOIS à l'utilisateur.

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

    def execute(self, dto: CreateAPIKeyDTO) -> APIKeyCreatedDTO:
        """
        Crée une nouvelle clé API.

        Process:
        1. Génère secret aléatoire (hbc_xxxxx...) avec secrets.token_urlsafe
        2. Calcule hash SHA256
        3. Crée entity APIKey avec hash
        4. Sauvegarde en DB
        5. Retourne secret (UNE FOIS) + infos clé

        Args:
            dto: Données de création (user_id, nom, scopes, etc.)

        Returns:
            APIKeyCreatedDTO avec secret (à afficher UNE fois)

        Raises:
            ValueError: Si scopes invalides
            Exception: Si erreur persistence
        """
        # 1. Générer secret cryptographiquement sécurisé (>128 bits)
        # token_urlsafe(32) génère 32 bytes = 256 bits = ~43 caractères base64
        random_part = secrets.token_urlsafe(32)
        secret = f"hbc_{random_part}"

        # 2. Calculer hash SHA256 (stocké en DB, jamais le secret)
        key_hash = hashlib.sha256(secret.encode('utf-8')).hexdigest()

        # 3. Extraire préfixe pour affichage (8 premiers caractères)
        key_prefix = secret[:8]

        # 4. Calculer date d'expiration
        expires_at = None
        if dto.expires_days:
            expires_at = datetime.utcnow() + timedelta(days=dto.expires_days)

        # 5. Valider scopes (si nécessaire)
        scopes = dto.scopes or ["read"]
        self._validate_scopes(scopes)

        # 6. Créer entity Domain
        api_key = APIKey(
            id=uuid4(),
            key_hash=key_hash,
            key_prefix=key_prefix,
            user_id=dto.user_id,
            nom=dto.nom,
            description=dto.description,
            scopes=scopes,
            rate_limit_per_hour=dto.rate_limit_per_hour,
            is_active=True,
            last_used_at=None,
            expires_at=expires_at,
            created_at=datetime.utcnow(),
        )

        # 7. Sauvegarder via repository
        saved_key = self.api_key_repo.save(api_key)

        # 8. Retourner DTO avec SECRET (une seule fois !)
        return APIKeyCreatedDTO(
            api_key=secret,  # CRITIQUE: Secret en clair, une fois seulement
            key_id=saved_key.id,
            key_prefix=saved_key.key_prefix,
            nom=saved_key.nom,
            created_at=saved_key.created_at,
            expires_at=saved_key.expires_at,
        )

    def _validate_scopes(self, scopes: list[str]) -> None:
        """
        Valide les scopes demandés.

        Args:
            scopes: Liste des scopes à valider

        Raises:
            ValueError: Si scope invalide
        """
        valid_scopes = {
            "read",
            "write",
            "admin",
            "chantiers:read",
            "chantiers:write",
            "planning:read",
            "planning:write",
            "documents:read",
            "documents:write",
            # Wildcards
            "chantiers:*",
            "planning:*",
            "documents:*",
        }

        for scope in scopes:
            if scope not in valid_scopes:
                raise ValueError(
                    f"Scope invalide: '{scope}'. "
                    f"Scopes valides: {', '.join(sorted(valid_scopes))}"
                )
