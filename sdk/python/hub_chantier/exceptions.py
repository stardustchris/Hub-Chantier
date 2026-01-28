"""Exceptions custom du SDK Hub Chantier."""


class HubChantierError(Exception):
    """Exception de base pour le SDK Hub Chantier."""

    pass


class APIError(HubChantierError):
    """Erreur API générique."""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        """
        Initialize API error.

        Args:
            message: Message d'erreur
            status_code: Code HTTP de la réponse
            response: Réponse JSON complète
        """
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class AuthenticationError(HubChantierError):
    """Erreur d'authentification (401)."""

    pass


class RateLimitError(HubChantierError):
    """Rate limit dépassé (429)."""

    def __init__(self, message: str, reset_at: str = None):
        """
        Initialize rate limit error.

        Args:
            message: Message d'erreur
            reset_at: Timestamp ISO 8601 du reset du rate limit
        """
        super().__init__(message)
        self.reset_at = reset_at
