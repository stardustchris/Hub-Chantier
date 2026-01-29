"""SDK Python officiel pour Hub Chantier API."""

from .client import HubChantierClient
from .exceptions import HubChantierError, APIError, AuthenticationError, RateLimitError
from .webhooks import verify_webhook_signature

__version__ = "1.0.0"

__all__ = [
    "HubChantierClient",
    "HubChantierError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "verify_webhook_signature",
]
