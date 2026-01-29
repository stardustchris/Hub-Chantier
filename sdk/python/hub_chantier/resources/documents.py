"""Ressource Documents (GED)."""

from typing import List, Dict
from .base import BaseResource


class Documents(BaseResource):
    """Gestion des documents (GED)."""

    def list(self, chantier_id: int, dossier_id: int = None) -> List[Dict]:
        """
        Liste les documents d'un chantier.

        Args:
            chantier_id: ID du chantier
            dossier_id: ID du dossier (optionnel)

        Returns:
            Liste de documents
        """
        params = {"chantier_id": chantier_id}
        if dossier_id:
            params["dossier_id"] = dossier_id

        return self.client._request("GET", "/api/documents", params=params)

    def get(self, document_id: int) -> Dict:
        """
        Récupère un document.

        Args:
            document_id: ID du document

        Returns:
            Document
        """
        return self.client._request("GET", f"/api/documents/{document_id}")
