"""Interface DocumentRepository - Abstraction pour la persistance des documents."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import Document
from ..value_objects import TypeDocument


class DocumentRepository(ABC):
    """
    Interface abstraite pour la persistance des documents.

    Cette interface définit le contrat pour l'accès aux données documents.
    L'implémentation concrète se trouve dans la couche Infrastructure.
    """

    @abstractmethod
    def find_by_id(self, document_id: int) -> Optional[Document]:
        """
        Trouve un document par son ID.

        Args:
            document_id: L'identifiant unique du document.

        Returns:
            Le document trouvé ou None.
        """
        pass

    @abstractmethod
    def save(self, document: Document) -> Document:
        """
        Persiste un document (création ou mise à jour).

        Args:
            document: Le document à sauvegarder.

        Returns:
            Le document sauvegardé (avec ID si création).
        """
        pass

    @abstractmethod
    def delete(self, document_id: int) -> bool:
        """
        Supprime un document.

        Args:
            document_id: L'identifiant du document à supprimer.

        Returns:
            True si supprimé, False si non trouvé.
        """
        pass

    @abstractmethod
    def find_by_dossier(
        self, dossier_id: int, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """
        Récupère les documents d'un dossier.

        Args:
            dossier_id: ID du dossier.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum d'éléments.

        Returns:
            Liste des documents.
        """
        pass

    @abstractmethod
    def find_by_chantier(
        self, chantier_id: int, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """
        Récupère tous les documents d'un chantier.

        Args:
            chantier_id: ID du chantier.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum d'éléments.

        Returns:
            Liste des documents.
        """
        pass

    @abstractmethod
    def count_by_dossier(self, dossier_id: int) -> int:
        """
        Compte le nombre de documents dans un dossier.

        Args:
            dossier_id: ID du dossier.

        Returns:
            Nombre de documents.
        """
        pass

    @abstractmethod
    def count_by_chantier(self, chantier_id: int) -> int:
        """
        Compte le nombre total de documents d'un chantier.

        Args:
            chantier_id: ID du chantier.

        Returns:
            Nombre total de documents.
        """
        pass

    @abstractmethod
    def search(
        self,
        chantier_id: int,
        query: Optional[str] = None,
        type_document: Optional[TypeDocument] = None,
        dossier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Document], int]:
        """
        Recherche des documents avec filtres.

        Args:
            chantier_id: ID du chantier.
            query: Texte à rechercher dans le nom.
            type_document: Filtrer par type.
            dossier_id: Filtrer par dossier.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Tuple (liste des documents, total count).
        """
        pass

    @abstractmethod
    def exists_by_nom_in_dossier(self, nom: str, dossier_id: int) -> bool:
        """
        Vérifie si un document avec ce nom existe dans le dossier.

        Args:
            nom: Nom du document.
            dossier_id: ID du dossier.

        Returns:
            True si le nom existe déjà.
        """
        pass

    @abstractmethod
    def get_total_size_by_chantier(self, chantier_id: int) -> int:
        """
        Calcule la taille totale des documents d'un chantier.

        Args:
            chantier_id: ID du chantier.

        Returns:
            Taille totale en bytes.
        """
        pass
