"""Interface AutorisationRepository - Abstraction pour la persistance des autorisations."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import AutorisationDocument, TypeAutorisation


class AutorisationRepository(ABC):
    """
    Interface abstraite pour la persistance des autorisations nominatives.

    Cette interface définit le contrat pour l'accès aux autorisations.
    L'implémentation concrète se trouve dans la couche Infrastructure.
    """

    @abstractmethod
    def find_by_id(self, autorisation_id: int) -> Optional[AutorisationDocument]:
        """
        Trouve une autorisation par son ID.

        Args:
            autorisation_id: L'identifiant unique de l'autorisation.

        Returns:
            L'autorisation trouvée ou None.
        """
        pass

    @abstractmethod
    def save(self, autorisation: AutorisationDocument) -> AutorisationDocument:
        """
        Persiste une autorisation (création ou mise à jour).

        Args:
            autorisation: L'autorisation à sauvegarder.

        Returns:
            L'autorisation sauvegardée (avec ID si création).
        """
        pass

    @abstractmethod
    def delete(self, autorisation_id: int) -> bool:
        """
        Supprime une autorisation.

        Args:
            autorisation_id: L'identifiant de l'autorisation à supprimer.

        Returns:
            True si supprimée, False si non trouvée.
        """
        pass

    @abstractmethod
    def find_by_dossier(self, dossier_id: int) -> List[AutorisationDocument]:
        """
        Récupère les autorisations d'un dossier.

        Args:
            dossier_id: ID du dossier.

        Returns:
            Liste des autorisations.
        """
        pass

    @abstractmethod
    def find_by_document(self, document_id: int) -> List[AutorisationDocument]:
        """
        Récupère les autorisations d'un document.

        Args:
            document_id: ID du document.

        Returns:
            Liste des autorisations.
        """
        pass

    @abstractmethod
    def find_by_user(self, user_id: int) -> List[AutorisationDocument]:
        """
        Récupère toutes les autorisations d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur.

        Returns:
            Liste des autorisations.
        """
        pass

    @abstractmethod
    def find_user_ids_for_dossier(self, dossier_id: int) -> List[int]:
        """
        Récupère les IDs des utilisateurs autorisés sur un dossier.

        Args:
            dossier_id: ID du dossier.

        Returns:
            Liste des user IDs.
        """
        pass

    @abstractmethod
    def find_user_ids_for_document(self, document_id: int) -> List[int]:
        """
        Récupère les IDs des utilisateurs autorisés sur un document.

        Args:
            document_id: ID du document.

        Returns:
            Liste des user IDs.
        """
        pass

    @abstractmethod
    def exists(
        self,
        user_id: int,
        dossier_id: Optional[int] = None,
        document_id: Optional[int] = None,
    ) -> bool:
        """
        Vérifie si une autorisation existe déjà.

        Args:
            user_id: ID de l'utilisateur.
            dossier_id: ID du dossier (optionnel).
            document_id: ID du document (optionnel).

        Returns:
            True si l'autorisation existe.
        """
        pass

    @abstractmethod
    def delete_by_dossier(self, dossier_id: int) -> int:
        """
        Supprime toutes les autorisations d'un dossier.

        Args:
            dossier_id: ID du dossier.

        Returns:
            Nombre d'autorisations supprimées.
        """
        pass

    @abstractmethod
    def delete_by_document(self, document_id: int) -> int:
        """
        Supprime toutes les autorisations d'un document.

        Args:
            document_id: ID du document.

        Returns:
            Nombre d'autorisations supprimées.
        """
        pass

    @abstractmethod
    def delete_expired(self) -> int:
        """
        Supprime les autorisations expirées.

        Returns:
            Nombre d'autorisations supprimées.
        """
        pass
