"""Classe de base pour les ressources API."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import HubChantierClient


class BaseResource:
    """Classe de base pour toutes les ressources API."""

    def __init__(self, client: "HubChantierClient"):
        """
        Initialize resource.

        Args:
            client: Instance du client Hub Chantier
        """
        self.client = client
