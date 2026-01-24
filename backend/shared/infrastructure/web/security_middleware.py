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

        # Politique de securite du contenu
        # Autorise uniquement les ressources du meme domaine + inline styles pour React
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Pour React dev
            "style-src 'self' 'unsafe-inline'; "  # Pour styles inline
            "img-src 'self' data: blob: https:; "  # Images locales + data URIs + externes
            "font-src 'self' data:; "  # Fonts locales
            "connect-src 'self' ws: wss:; "  # API + WebSocket pour HMR
            "frame-ancestors 'none'; "  # Empeche embedding
            "form-action 'self'; "  # Formulaires vers meme domaine
            "base-uri 'self'"  # Empeche injection de base href
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
