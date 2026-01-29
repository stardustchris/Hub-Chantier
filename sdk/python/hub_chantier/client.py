"""Client principal Hub Chantier API."""

import requests
from typing import Optional, Dict, Any
from .exceptions import APIError, AuthenticationError, RateLimitError


class HubChantierClient:
    """
    Client Hub Chantier API.

    Usage:
        >>> client = HubChantierClient(api_key="hbc_your_key")
        >>> chantiers = client.chantiers.list()
        >>> for chantier in chantiers:
        ...     print(chantier['nom'])

    Args:
        api_key: Clé API Hub Chantier (depuis Paramètres > Clés API)
        base_url: URL de base de l'API (par défaut: production)
        timeout: Timeout requêtes HTTP (secondes)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.hub-chantier.fr",
        timeout: int = 30,
    ):
        """
        Initialize Hub Chantier client.

        Args:
            api_key: Clé API (format: hbc_...)
            base_url: URL de base de l'API
            timeout: Timeout en secondes

        Raises:
            ValueError: Si api_key invalide
        """
        if not api_key:
            raise ValueError("api_key is required")

        if not api_key.startswith("hbc_"):
            raise ValueError("Invalid API key format (must start with 'hbc_')")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Initialiser ressources (lazy import pour éviter circular imports)
        from .resources import Chantiers, Affectations, Heures, Documents, Webhooks

        self.chantiers = Chantiers(self)
        self.affectations = Affectations(self)
        self.heures = Heures(self)
        self.documents = Documents(self)
        self.webhooks = Webhooks(self)

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Effectue une requête HTTP vers l'API.

        Args:
            method: Méthode HTTP (GET, POST, PUT, DELETE)
            path: Chemin endpoint (ex: '/v1/chantiers')
            params: Query parameters
            json: Body JSON

        Returns:
            Réponse JSON parsée

        Raises:
            AuthenticationError: Si API key invalide
            RateLimitError: Si rate limit dépassé
            APIError: Autre erreur API
        """
        url = f"{self.base_url}{path}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "hub-chantier-python/1.0.0",
        }

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                timeout=self.timeout,
            )

            # Gestion erreurs HTTP
            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired API key")

            elif response.status_code == 429:
                reset_at = response.headers.get("X-RateLimit-Reset")
                raise RateLimitError(
                    f"Rate limit exceeded. Resets at {reset_at}", reset_at=reset_at
                )

            elif response.status_code >= 400:
                error_detail = response.json().get("detail", "Unknown error")
                raise APIError(
                    f"API Error ({response.status_code}): {error_detail}",
                    status_code=response.status_code,
                    response=response.json(),
                )

            return response.json()

        except requests.RequestException as e:
            raise APIError(f"Network error: {e}")
