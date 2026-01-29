"""Ressource Affectations (Planning)."""

from typing import List, Dict, Optional, Any
from .base import BaseResource


class Affectations(BaseResource):
    """
    Gestion des affectations du planning.

    Usage:
        >>> affectations = client.affectations.list("2026-01-20", "2026-01-26")
        >>> affectation = client.affectations.create(
        ...     utilisateur_id=5,
        ...     chantier_id=42,
        ...     date="2026-01-30"
        ... )
    """

    def list(
        self, date_debut: str, date_fin: str, utilisateur_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Liste les affectations sur une période.

        Args:
            date_debut: Date de début (ISO 8601)
            date_fin: Date de fin (ISO 8601)
            utilisateur_ids: Filtrer par utilisateurs

        Returns:
            Liste d'affectations
        """
        params: Dict[str, Any] = {"date_debut": date_debut, "date_fin": date_fin}
        if utilisateur_ids:
            params["utilisateur_ids"] = ",".join(map(str, utilisateur_ids))

        return self.client._request("GET", "/api/affectations", params=params)  # type: ignore

    def create(
        self,
        utilisateur_id: int,
        chantier_id: int,
        date: str,
        heure_debut: Optional[str] = None,
        heure_fin: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Crée une nouvelle affectation.

        Args:
            utilisateur_id: ID de l'utilisateur
            chantier_id: ID du chantier
            date: Date (ISO 8601, ex: "2026-01-30")
            heure_debut: Heure de début (HH:MM)
            heure_fin: Heure de fin (HH:MM)
            **kwargs: note, type_affectation, etc.

        Returns:
            Affectation créée
        """
        data: Dict[str, Any] = {
            "utilisateur_id": utilisateur_id,
            "chantier_id": chantier_id,
            "date": date,
            **kwargs,
        }
        if heure_debut:
            data["heure_debut"] = heure_debut
        if heure_fin:
            data["heure_fin"] = heure_fin

        return self.client._request("POST", "/api/affectations", json=data)

    def update(self, affectation_id: int, **kwargs: Any) -> Dict[str, Any]:
        """Modifie une affectation."""
        return self.client._request(
            "PUT", f"/api/affectations/{affectation_id}", json=kwargs
        )

    def delete(self, affectation_id: int) -> None:
        """Supprime une affectation."""
        self.client._request("DELETE", f"/api/affectations/{affectation_id}")
