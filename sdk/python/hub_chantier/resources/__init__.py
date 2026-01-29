"""Resources for Hub Chantier API."""

from .base import BaseResource
from .chantiers import Chantiers
from .affectations import Affectations
from .heures import Heures
from .documents import Documents
from .webhooks import Webhooks

__all__ = [
    "BaseResource",
    "Chantiers",
    "Affectations",
    "Heures",
    "Documents",
    "Webhooks",
]
