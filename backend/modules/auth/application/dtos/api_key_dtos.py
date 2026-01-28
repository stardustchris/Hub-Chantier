"""DTOs pour les Use Cases de gestion des clés API."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID


@dataclass
class CreateAPIKeyDTO:
    """
    DTO pour la création d'une clé API.

    Attributes:
        user_id: ID de l'utilisateur propriétaire
        nom: Nom descriptif de la clé
        description: Description détaillée (optionnel)
        scopes: Liste des permissions (défaut: ['read'])
        rate_limit_per_hour: Limite requêtes/heure (défaut: 1000)
        expires_days: Nombre de jours avant expiration (None = jamais)
    """

    user_id: int
    nom: str
    description: Optional[str] = None
    scopes: Optional[List[str]] = None
    rate_limit_per_hour: int = 1000
    expires_days: Optional[int] = 90


@dataclass
class APIKeyCreatedDTO:
    """
    DTO de retour après création d'une clé API.

    CRITIQUE: Le secret (api_key) n'est retourné qu'UNE SEULE FOIS.
    Il ne sera plus jamais accessible après cette réponse.

    Attributes:
        api_key: Secret complet (hbc_xxxxx...) - À AFFICHER UNE FOIS
        key_id: UUID de la clé créée
        key_prefix: Préfixe pour affichage futur (hbc_xxxx...)
        nom: Nom de la clé
        created_at: Date de création
        expires_at: Date d'expiration (None si jamais)
    """

    api_key: str  # SECRET - Une seule fois !
    key_id: UUID
    key_prefix: str
    nom: str
    created_at: datetime
    expires_at: Optional[datetime]


@dataclass
class APIKeyInfoDTO:
    """
    DTO pour l'affichage d'une clé API (sans secret).

    Utilisé pour lister les clés d'un utilisateur.

    Attributes:
        id: UUID de la clé
        key_prefix: Préfixe pour identification (hbc_xxxx...)
        nom: Nom descriptif
        description: Description détaillée
        scopes: Permissions accordées
        rate_limit_per_hour: Limite requêtes/heure
        is_active: Clé active ou révoquée
        last_used_at: Dernière utilisation
        expires_at: Date d'expiration
        created_at: Date de création
    """

    id: UUID
    key_prefix: str
    nom: str
    description: Optional[str]
    scopes: List[str]
    rate_limit_per_hour: int
    is_active: bool
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime


@dataclass
class RevokeAPIKeyDTO:
    """
    DTO pour révoquer une clé API.

    Attributes:
        api_key_id: UUID de la clé à révoquer
        user_id: ID de l'utilisateur (vérification propriété)
    """

    api_key_id: UUID
    user_id: int
