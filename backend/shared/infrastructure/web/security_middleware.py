"""Middleware de securite HTTP.

Ajoute les en-tetes de securite recommandes par OWASP:
- X-Frame-Options: Protection contre le clickjacking
- X-Content-Type-Options: Empeche le MIME sniffing
- X-XSS-Protection: Protection XSS (legacy, pour anciens navigateurs)
- Strict-Transport-Security: Force HTTPS
- Content-Security-Policy: Politique de securite du contenu
- Referrer-Policy: Controle les informations de referrer
- Permissions-Policy: Controle les fonctionnalites du navigateur
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from ..config import settings


# CSP stricte pour production (pas de 'unsafe-inline' ni 'unsafe-eval')
CSP_PRODUCTION = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data: blob: https:; "
    "font-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "form-action 'self'; "
    "base-uri 'self'"
)

# CSP permissive pour developpement (React HMR, inline styles)
CSP_DEVELOPMENT = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: blob: https:; "
    "font-src 'self' data:; "
    "connect-src 'self' ws: wss:; "
    "frame-ancestors 'none'; "
    "form-action 'self'; "
    "base-uri 'self'"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware qui ajoute les en-tetes de securite HTTP a toutes les reponses.

    Ces en-tetes protegent contre diverses attaques courantes:
    - Clickjacking (X-Frame-Options)
    - MIME sniffing (X-Content-Type-Options)
    - XSS (X-XSS-Protection, CSP)
    - Downgrade attacks (HSTS)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Traite la requete et ajoute les en-tetes de securite a la reponse.

        Args:
            request: Requete entrante.
            call_next: Prochain handler dans la chaine.

        Returns:
            Response avec les en-tetes de securite ajoutes.
        """
        response: Response = await call_next(request)

        # Protection contre le clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Empeche le MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Protection XSS (pour anciens navigateurs)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Force HTTPS (1 an, inclut les sous-domaines)
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # Politique de securite du contenu (env-specific)
        # Production: CSP stricte sans unsafe-inline/eval
        # Developpement: CSP permissive pour React HMR
        response.headers["Content-Security-Policy"] = (
            CSP_DEVELOPMENT if settings.DEBUG else CSP_PRODUCTION
        )

        # Politique de referrer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Politique de permissions (desactive fonctionnalites non utilisees)
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(self), "  # Autorise geolocation pour localisation chantiers
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=(), "
            "usb=()"
        )

        # Empeche le cache sur les donnees sensibles (API)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"

        return response
