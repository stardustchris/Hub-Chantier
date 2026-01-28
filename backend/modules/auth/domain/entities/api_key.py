"""Domain Entity APIKey - Clé API pour authentification API publique v1."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID


@dataclass
class APIKey:
    """
    Entity Domain APIKey.

    Représente une clé API utilisée pour l'authentification de l'API publique v1.
    Le secret n'est jamais stocké en clair, uniquement son hash SHA256.

    Attributes:
        id: Identifiant unique UUID
        key_hash: Hash SHA256 du secret (64 caractères hex)
        key_prefix: Préfixe pour affichage (8 premiers caractères du secret)
        user_id: ID de l'utilisateur propriétaire
        nom: Nom descriptif de la clé
        description: Description détaillée (optionnel)
        scopes: Liste des permissions accordées (read, write, admin)
        rate_limit_per_hour: Limite de requêtes par heure
        is_active: Clé active ou révoquée
        last_used_at: Dernière utilisation (audit)
        expires_at: Date d'expiration (None = jamais)
        created_at: Date de création
    """

    id: UUID
    key_hash: str
    key_prefix: str
    user_id: int
    nom: str
    description: Optional[str]
    scopes: List[str]
    rate_limit_per_hour: int
    is_active: bool
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    def is_expired(self) -> bool:
        """
        Vérifie si la clé est expirée.

        Returns:
            True si expires_at est passé, False sinon (ou si pas d'expiration)
        """
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def can_perform(self, scope: str) -> bool:
        """
        Vérifie si la clé possède un scope donné.

        Supporte les wildcards (ex: 'chantiers:*' permet 'chantiers:read', 'chantiers:write').

        Args:
            scope: Scope à vérifier (ex: 'chantiers:read')

        Returns:
            True si la clé possède le scope, False sinon
        """
        if not self.is_active:
            return False

        if self.is_expired():
            return False

        for s in self.scopes:
            # Scope exact
            if s == scope:
                return True

            # Wildcard (ex: 'chantiers:*' permet tout sous chantiers)
            if s.endswith(':*') and scope.startswith(s[:-1]):
                return True

        return False

    def revoke(self) -> None:
        """
        Révoque la clé (désactivation).

        Méthode Domain pour assurer la logique métier.
        """
        self.is_active = False

    def update_last_used(self) -> None:
        """
        Met à jour la date de dernière utilisation.

        Utilisé pour l'audit et le suivi d'activité.
        """
        self.last_used_at = datetime.utcnow()

    def is_valid_for_auth(self) -> bool:
        """
        Vérifie si la clé peut être utilisée pour l'authentification.

        Returns:
            True si active ET non expirée, False sinon
        """
        return self.is_active and not self.is_expired()
