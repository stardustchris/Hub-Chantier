"""Interface TacheRepository - Abstraction pour la persistence des taches."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import Tache
from ..value_objects import StatutTache


class TacheRepository(ABC):
    """
    Interface abstraite pour la persistence des taches.

    Cette interface definit le contrat pour l'acces aux donnees tache.
    L'implementation concrete se trouve dans la couche Infrastructure.
    """

    @abstractmethod
    def find_by_id(self, tache_id: int) -> Optional[Tache]:
        """
        Trouve une tache par son ID.

        Args:
            tache_id: L'identifiant unique de la tache.

        Returns:
            La tache trouvee ou None.
        """
        pass

    @abstractmethod
    def find_by_chantier(
        self,
        chantier_id: int,
        include_sous_taches: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Tache]:
        """
        Trouve les taches d'un chantier (TAC-01).

        Args:
            chantier_id: ID du chantier.
            include_sous_taches: Inclure les sous-taches.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des taches racines du chantier.
        """
        pass

    @abstractmethod
    def find_children(self, parent_id: int) -> List[Tache]:
        """
        Trouve les sous-taches d'une tache (TAC-02).

        Args:
            parent_id: ID de la tache parente.

        Returns:
            Liste des sous-taches.
        """
        pass

    @abstractmethod
    def save(self, tache: Tache) -> Tache:
        """
        Persiste une tache (creation ou mise a jour).

        Args:
            tache: La tache a sauvegarder.

        Returns:
            La tache sauvegardee (avec ID si creation).
        """
        pass

    @abstractmethod
    def delete(self, tache_id: int) -> bool:
        """
        Supprime une tache et ses sous-taches.

        Args:
            tache_id: L'identifiant de la tache a supprimer.

        Returns:
            True si supprimee, False si non trouvee.
        """
        pass

    @abstractmethod
    def count_by_chantier(self, chantier_id: int) -> int:
        """
        Compte le nombre de taches d'un chantier.

        Args:
            chantier_id: ID du chantier.

        Returns:
            Nombre total de taches.
        """
        pass

    @abstractmethod
    def search(
        self,
        chantier_id: int,
        query: Optional[str] = None,
        statut: Optional[StatutTache] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Tache], int]:
        """
        Recherche des taches avec filtres (TAC-14).

        Args:
            chantier_id: ID du chantier.
            query: Texte a rechercher dans le titre/description.
            statut: Filtrer par statut.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Tuple (liste des taches, total count).
        """
        pass

    @abstractmethod
    def reorder(self, tache_id: int, nouvel_ordre: int) -> None:
        """
        Reordonne une tache (TAC-15 - drag & drop).

        Args:
            tache_id: ID de la tache.
            nouvel_ordre: Nouvelle position.
        """
        pass

    @abstractmethod
    def find_by_template(self, template_id: int) -> List[Tache]:
        """
        Trouve les taches creees depuis un template.

        Args:
            template_id: ID du template source.

        Returns:
            Liste des taches.
        """
        pass

    @abstractmethod
    def get_stats_chantier(self, chantier_id: int) -> dict:
        """
        Obtient les statistiques des taches d'un chantier.

        Args:
            chantier_id: ID du chantier.

        Returns:
            Dictionnaire avec les stats (total, terminees, en_cours, etc.).
        """
        pass
