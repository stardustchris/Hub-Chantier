"""Ressource Chantiers."""

from typing import List, Dict, Optional
from .base import BaseResource


class Chantiers(BaseResource):
    """
    Gestion des chantiers.

    Usage:
        >>> chantiers = client.chantiers.list()
        >>> chantier = client.chantiers.create(nom="Villa Lyon", adresse="...")
        >>> chantier = client.chantiers.get(42)
        >>> client.chantiers.update(42, statut="en_cours")
        >>> client.chantiers.delete(42)
    """

    def list(
        self,
        status: Optional[str] = None,
        conducteur_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict]:
        """
        Liste tous les chantiers.

        Args:
            status: Filtrer par statut (ouvert, en_cours, receptionne, ferme)
            conducteur_id: Filtrer par conducteur
            limit: Nombre max de résultats (1-100)
            offset: Décalage pagination

        Returns:
            Liste de chantiers

        Example:
            >>> chantiers = client.chantiers.list(status="en_cours")
            >>> for chantier in chantiers:
            ...     print(chantier['nom'])
        """
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if conducteur_id:
            params["conducteur_id"] = conducteur_id

        response = self.client._request("GET", "/api/chantiers", params=params)
        return response.get("items", response)  # Handle both paginated and direct list

    def get(self, chantier_id: int) -> Dict:
        """
        Récupère un chantier.

        Args:
            chantier_id: ID du chantier

        Returns:
            Chantier

        Example:
            >>> chantier = client.chantiers.get(42)
            >>> print(chantier['nom'])
        """
        return self.client._request("GET", f"/api/chantiers/{chantier_id}")

    def create(
        self,
        nom: str,
        adresse: str,
        statut: str = "ouvert",
        date_debut: Optional[str] = None,
        conducteur_id: Optional[int] = None,
        **kwargs,
    ) -> Dict:
        """
        Crée un nouveau chantier.

        Args:
            nom: Nom du chantier (3-255 caractères)
            adresse: Adresse complète
            statut: Statut initial (défaut: ouvert)
            date_debut: Date début (ISO 8601, ex: "2026-01-30")
            conducteur_id: ID conducteur responsable
            **kwargs: Autres champs optionnels (code, couleur, description, etc.)

        Returns:
            Chantier créé

        Example:
            >>> chantier = client.chantiers.create(
            ...     nom="Villa Caluire",
            ...     adresse="12 Rue de la République, 69300 Caluire",
            ...     statut="ouvert",
            ...     couleur="#3B82F6"
            ... )
            >>> print(f"Chantier créé : {chantier['id']}")
        """
        data = {"nom": nom, "adresse": adresse, "statut": statut, **kwargs}
        if date_debut:
            data["date_debut_prevue"] = date_debut
        if conducteur_id:
            data["conducteur_id"] = conducteur_id

        return self.client._request("POST", "/api/chantiers", json=data)

    def update(self, chantier_id: int, **kwargs) -> Dict:
        """
        Modifie un chantier.

        Args:
            chantier_id: ID du chantier
            **kwargs: Champs à modifier (nom, adresse, statut, etc.)

        Returns:
            Chantier modifié

        Example:
            >>> chantier = client.chantiers.update(42, statut="en_cours")
            >>> print(chantier['statut'])
        """
        return self.client._request("PUT", f"/api/chantiers/{chantier_id}", json=kwargs)

    def delete(self, chantier_id: int) -> None:
        """
        Supprime un chantier.

        Args:
            chantier_id: ID du chantier

        Example:
            >>> client.chantiers.delete(42)
        """
        self.client._request("DELETE", f"/api/chantiers/{chantier_id}")
