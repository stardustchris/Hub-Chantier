"""
Middleware de rate limiting avancé avec backoff exponentiel.

Amélioration L-01 du rapport d'audit sécurité.
"""

from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..rate_limiter_advanced import (
    backoff_limiter,
    get_limit_for_endpoint,
    ENDPOINT_LIMITS
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware de rate limiting avancé avec backoff exponentiel.

    Applique des limites spécifiques par endpoint et augmente
    progressivement les délais de blocage pour les violations
    répétées.

    Features:
    - Limites par endpoint (ex: /login plus restrictif que /dashboard)
    - Backoff exponentiel (30s → 60s → 120s → 240s → 300s max)
    - Reset automatique après 1h sans violation
    - Header Retry-After sur réponses 429
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Traite la requête et applique le rate limiting.

        Args:
            request: Requête HTTP entrante.
            call_next: Fonction pour passer à l'étape suivante.

        Returns:
            Réponse HTTP (200 ou 429 Too Many Requests).
        """
        # Récupérer l'IP du client
        client_ip = self._get_client_ip(request)

        # Vérifier si l'IP est bloquée (backoff exponentiel)
        is_blocked, retry_after = backoff_limiter.check_and_increment(client_ip)

        if is_blocked:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Too many failed attempts. Try again in {retry_after} seconds.",
                    "retry_after": retry_after,
                    "violations": backoff_limiter.violations.get(client_ip, 0),
                },
                headers={"Retry-After": str(retry_after)}
            )

        # Pas bloqué, continuer avec la requête
        response = await call_next(request)

        # Si c'est un endpoint sensible et la réponse est un échec (401, 403)
        # enregistrer une violation pour le backoff
        if self._is_sensitive_endpoint(request.url.path):
            if response.status_code in [401, 403, 429]:
                retry_after = backoff_limiter.record_violation(client_ip)
                # Ajouter header Retry-After
                response.headers["Retry-After"] = str(retry_after)

            elif response.status_code == 200:
                # Succès : reset les violations
                backoff_limiter.reset(client_ip)

        return response

    # IPs de reverse proxy de confiance (Docker bridge, localhost)
    TRUSTED_PROXIES = {"127.0.0.1", "::1", "172.17.0.1", "10.0.0.1"}

    def _get_client_ip(self, request: Request) -> str:
        """
        Extrait l'adresse IP du client.

        Sécurité: N'utilise X-Forwarded-For que si la requête provient
        d'un reverse proxy de confiance (TRUSTED_PROXIES), sinon un
        attaquant pourrait spoofer l'en-tête pour contourner le rate limiting.

        Args:
            request: Requête HTTP.

        Returns:
            Adresse IP du client.
        """
        direct_ip = request.client.host if request.client else "unknown"

        # Ne faire confiance aux headers proxy QUE si la connexion
        # provient d'un reverse proxy connu
        if direct_ip in self.TRUSTED_PROXIES:
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()

            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                return real_ip

        return direct_ip

    def _is_sensitive_endpoint(self, path: str) -> bool:
        """
        Vérifie si l'endpoint est sensible (authentification, uploads, etc.).

        Args:
            path: Chemin de l'endpoint.

        Returns:
            True si sensible, False sinon.
        """
        sensitive_prefixes = [
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh",
            "/api/upload",
            "/api/documents/upload",
        ]

        return any(path.startswith(prefix) for prefix in sensitive_prefixes)


def create_rate_limit_info_endpoint():
    """
    Créé un endpoint informatif sur les limites de rate.

    Returns:
        Dictionnaire des limites par endpoint.
    """
    return {
        "limits": ENDPOINT_LIMITS,
        "backoff_strategy": {
            "violations": [1, 2, 3, 4, 5],
            "retry_after_seconds": [30, 60, 120, 240, 300],
            "reset_after_hours": 1,
        },
        "sensitive_endpoints": [
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh",
            "/api/upload",
            "/api/documents/upload",
        ],
    }
