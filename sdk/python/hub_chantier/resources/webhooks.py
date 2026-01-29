"""Ressource Webhooks."""

from typing import List, Dict, Optional, Any
from .base import BaseResource


class Webhooks(BaseResource):
    """Gestion des webhooks."""

    def list(self) -> List[Dict[str, Any]]:
        """
        Liste tous les webhooks.

        Returns:
            Liste de webhooks
        """
        return self.client._request("GET", "/api/v1/webhooks")  # type: ignore

    def create(
        self, url: str, events: List[str], description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crée un nouveau webhook.

        Args:
            url: URL de callback (doit être HTTPS)
            events: Liste d'événements à écouter (ex: ["chantier.created"])
            description: Description optionnelle

        Returns:
            Webhook créé avec secret

        Example:
            >>> webhook = client.webhooks.create(
            ...     url="https://myapp.com/webhooks/hub-chantier",
            ...     events=["chantier.created", "affectation.created"],
            ...     description="Production webhook"
            ... )
            >>> secret = webhook['secret']  # À sauvegarder pour vérifier signatures
        """
        data: Dict[str, Any] = {"url": url, "events": events}
        if description:
            data["description"] = description

        return self.client._request("POST", "/api/v1/webhooks", json=data)

    def delete(self, webhook_id: str) -> None:
        """
        Supprime un webhook.

        Args:
            webhook_id: ID du webhook (UUID)
        """
        self.client._request("DELETE", f"/api/v1/webhooks/{webhook_id}")
