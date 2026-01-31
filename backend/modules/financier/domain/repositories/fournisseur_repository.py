"""Interface du repository pour les fournisseurs.

FIN-14: Répertoire fournisseurs - CRUD des fournisseurs.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import Fournisseur
from ..value_objects import TypeFournisseur


class FournisseurRepository(ABC):
    """Interface abstraite pour la persistence des fournisseurs."""

    @abstractmethod
    def save(self, fournisseur: Fournisseur) -> Fournisseur:
        """Persiste un fournisseur (création ou mise à jour).

        Args:
            fournisseur: Le fournisseur à persister.

        Returns:
            Le fournisseur avec son ID attribué.
        """
        pass

    @abstractmethod
    def find_by_id(self, fournisseur_id: int) -> Optional[Fournisseur]:
        """Recherche un fournisseur par son ID.

        Args:
            fournisseur_id: L'ID du fournisseur.

        Returns:
            Le fournisseur ou None si non trouvé.
        """
        pass

    @abstractmethod
    def find_by_siret(self, siret: str) -> Optional[Fournisseur]:
        """Recherche un fournisseur par son SIRET.

        Args:
            siret: Le numéro SIRET (14 chiffres).

        Returns:
            Le fournisseur ou None si non trouvé.
        """
        pass

    @abstractmethod
    def find_all(
        self,
        type: Optional[TypeFournisseur] = None,
        actif_seulement: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Fournisseur]:
        """Liste les fournisseurs avec filtres optionnels.

        Args:
            type: Filtrer par type de fournisseur.
            actif_seulement: Ne retourner que les fournisseurs actifs.
            limit: Nombre maximum de résultats.
            offset: Décalage pour pagination.

        Returns:
            Liste des fournisseurs correspondants.
        """
        pass

    @abstractmethod
    def count(
        self,
        type: Optional[TypeFournisseur] = None,
        actif_seulement: bool = True,
    ) -> int:
        """Compte le nombre de fournisseurs.

        Args:
            type: Filtrer par type de fournisseur.
            actif_seulement: Ne compter que les fournisseurs actifs.

        Returns:
            Le nombre de fournisseurs.
        """
        pass

    @abstractmethod
    def delete(self, fournisseur_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime un fournisseur (soft delete - H10).

        Args:
            fournisseur_id: L'ID du fournisseur à supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprimé, False si non trouvé.
        """
        pass
