"""Use case pour récupérer les consentements RGPD d'un utilisateur."""

from typing import Optional

from ...domain.repositories import UserRepository


class GetConsentsUseCase:
    """
    Récupère les consentements RGPD d'un utilisateur.

    Conformité RGPD Article 7 - Conditions applicables au consentement.
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialise le use case.

        Args:
            user_repository: Repository des utilisateurs.
        """
        self.user_repository = user_repository

    def execute(self, user_id: int) -> dict:
        """
        Récupère les consentements RGPD d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur.

        Returns:
            Dictionnaire avec les consentements et métadonnées.

        Raises:
            ValueError: Si l'utilisateur n'existe pas.
        """
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"Utilisateur avec ID {user_id} non trouvé")

        # Retourner les consentements avec métadonnées RGPD
        return {
            "geolocation": user.consent_geolocation if hasattr(user, 'consent_geolocation') else False,
            "notifications": user.consent_notifications if hasattr(user, 'consent_notifications') else False,
            "analytics": user.consent_analytics if hasattr(user, 'consent_analytics') else False,
            "timestamp": user.consent_timestamp.isoformat() if hasattr(user, 'consent_timestamp') and user.consent_timestamp else None,
            "ip_address": user.consent_ip_address if hasattr(user, 'consent_ip_address') else None,
            "user_agent": user.consent_user_agent if hasattr(user, 'consent_user_agent') else None,
        }
