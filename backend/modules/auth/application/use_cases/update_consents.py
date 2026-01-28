"""Use case pour mettre à jour les consentements RGPD d'un utilisateur."""

from datetime import datetime
from typing import Optional

from ...domain.repositories import UserRepository


class UpdateConsentsUseCase:
    """
    Met à jour les consentements RGPD d'un utilisateur.

    Conformité RGPD Article 7 - Conditions applicables au consentement.
    Enregistre le consentement avec contexte (timestamp, IP, user agent).
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialise le use case.

        Args:
            user_repository: Repository des utilisateurs.
        """
        self.user_repository = user_repository

    def execute(
        self,
        user_id: int,
        geolocation: Optional[bool] = None,
        notifications: Optional[bool] = None,
        analytics: Optional[bool] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> dict:
        """
        Met à jour les consentements RGPD d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur.
            geolocation: Consentement géolocalisation (None = pas de changement).
            notifications: Consentement notifications (None = pas de changement).
            analytics: Consentement analytics (None = pas de changement).
            ip_address: Adresse IP du client (pour audit RGPD).
            user_agent: User agent du navigateur (pour audit RGPD).

        Returns:
            Dictionnaire avec les consentements mis à jour.

        Raises:
            ValueError: Si l'utilisateur n'existe pas.
        """
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"Utilisateur avec ID {user_id} non trouvé")

        # Note: UserModel est retourné directement par le repository
        # car il n'y a pas d'entité User avec logique métier pour les consentements
        # C'est une mise à jour simple de champs, pas de règles métier complexes

        # Mettre à jour les consentements (seulement si fournis)
        if geolocation is not None:
            user.consent_geolocation = geolocation
        if notifications is not None:
            user.consent_notifications = notifications
        if analytics is not None:
            user.consent_analytics = analytics

        # Mettre à jour les métadonnées RGPD
        user.consent_timestamp = datetime.now()
        user.consent_ip_address = ip_address
        user.consent_user_agent = user_agent

        # Sauvegarder
        self.user_repository.save(user)

        # Retourner les consentements mis à jour
        return {
            "geolocation": user.consent_geolocation,
            "notifications": user.consent_notifications,
            "analytics": user.consent_analytics,
            "timestamp": user.consent_timestamp.isoformat() if user.consent_timestamp else None,
            "ip_address": user.consent_ip_address,
            "user_agent": user.consent_user_agent,
        }
