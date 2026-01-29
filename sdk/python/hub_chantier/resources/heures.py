"""Ressource Feuilles d'Heures."""

from typing import List, Dict, Any
from .base import BaseResource


class Heures(BaseResource):
    """Gestion des feuilles d'heures."""

    def list(self, date_debut: str, date_fin: str) -> List[Dict[str, Any]]:
        """
        Liste les feuilles d'heures sur une période.

        Args:
            date_debut: Date de début (ISO 8601)
            date_fin: Date de fin (ISO 8601)

        Returns:
            Liste de feuilles d'heures
        """
        params: Dict[str, str] = {"date_debut": date_debut, "date_fin": date_fin}
        return self.client._request("GET", "/api/feuilles-heures", params=params)  # type: ignore

    def create(
        self, utilisateur_id: int, chantier_id: int, date: str, heures: float
    ) -> Dict[str, Any]:
        """
        Crée une feuille d'heures.

        Args:
            utilisateur_id: ID utilisateur
            chantier_id: ID chantier
            date: Date (ISO 8601)
            heures: Nombre d'heures

        Returns:
            Feuille d'heures créée
        """
        data: Dict[str, Any] = {
            "utilisateur_id": utilisateur_id,
            "chantier_id": chantier_id,
            "date": date,
            "heures_normales": heures,
        }
        return self.client._request("POST", "/api/feuilles-heures", json=data)
