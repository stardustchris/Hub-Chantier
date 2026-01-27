"""
Middleware de protection CSRF (Cross-Site Request Forgery).

Implémente une protection CSRF via tokens pour les requêtes mutables
(POST, PUT, PATCH, DELETE). Renforce la protection offerte par
Cookie SameSite=strict (M-01).
"""

import secrets
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Middleware de protection CSRF avec tokens.

    Génère un token CSRF unique par session et le valide sur toutes
    les requêtes mutables (POST, PUT, PATCH, DELETE).

    Exceptions:
    - /api/auth/login : Exempté (pas de token avant authentification)
    - /api/auth/register : Exempté (pas de token avant authentification)
    - GET, HEAD, OPTIONS : Exemptés (requêtes safe)
    """

    # Endpoints exemptés de la vérification CSRF
    EXEMPT_PATHS = {
        "/api/auth/login",
        "/api/auth/register",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
    }

    # Méthodes HTTP sûres (ne modifient pas l'état)
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Traite la requête et valide le token CSRF si nécessaire.

        Args:
            request: Requête HTTP entrante.
            call_next: Fonction pour passer à l'étape suivante.

        Returns:
            Réponse HTTP avec token CSRF dans les cookies.
        """
        # Vérifier si l'endpoint est exempté
        if self._is_exempt(request):
            return await call_next(request)

        # Vérifier si la méthode est sûre
        if request.method in self.SAFE_METHODS:
            response = await call_next(request)
            # Générer un nouveau token CSRF pour les requêtes GET
            self._set_csrf_cookie(response)
            return response

        # Requête mutable (POST, PUT, PATCH, DELETE) : valider le token
        csrf_token_header = request.headers.get("X-CSRF-Token")
        csrf_token_cookie = request.cookies.get("csrf_token")

        if not csrf_token_header or not csrf_token_cookie:
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "CSRF token missing. Include X-CSRF-Token header with value from csrf_token cookie."
                }
            )

        if not secrets.compare_digest(csrf_token_header, csrf_token_cookie):
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "CSRF token invalid. Token mismatch between header and cookie."
                }
            )

        # Token valide, traiter la requête
        response = await call_next(request)

        # Renouveler le token après chaque requête mutable
        self._set_csrf_cookie(response)

        return response

    def _is_exempt(self, request: Request) -> bool:
        """
        Vérifie si l'endpoint est exempté de la vérification CSRF.

        Args:
            request: Requête HTTP.

        Returns:
            True si l'endpoint est exempté, False sinon.
        """
        return request.url.path in self.EXEMPT_PATHS

    def _set_csrf_cookie(self, response: Response) -> None:
        """
        Génère et définit un nouveau token CSRF dans les cookies.

        Args:
            response: Réponse HTTP à modifier.
        """
        csrf_token = secrets.token_urlsafe(32)
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=False,  # Doit être accessible en JavaScript
            secure=True,     # HTTPS uniquement en production
            samesite="strict",  # Protection complémentaire
            max_age=3600,    # 1 heure
        )
