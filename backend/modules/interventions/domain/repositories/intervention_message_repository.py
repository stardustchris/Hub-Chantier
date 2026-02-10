"""Interface du repository InterventionMessage."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import InterventionMessage, TypeMessage


class InterventionMessageRepository(ABC):
    """Interface abstraite pour le repository des messages d'intervention."""

    @abstractmethod
    async def save(self, message: InterventionMessage) -> InterventionMessage:
        """Sauvegarde un message.

        Args:
            message: Le message a sauvegarder.

        Returns:
            Le message avec son ID assigne.
        """
        pass

    @abstractmethod
    async def get_by_id(self, message_id: int) -> Optional[InterventionMessage]:
        """Recupere un message par son ID.

        Args:
            message_id: L'identifiant du message.

        Returns:
            Le message ou None si non trouve.
        """
        pass

    @abstractmethod
    async def list_by_intervention(
        self,
        intervention_id: int,
        type_message: Optional[TypeMessage] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[InterventionMessage]:
        """Liste les messages d'une intervention.

        INT-11: Fil d'actualite - Timeline actions, photos, commentaires

        Args:
            intervention_id: ID de l'intervention.
            type_message: Filtrer par type de message.
            include_deleted: Inclure les messages supprimes.
            limit: Nombre maximum de resultats.
            offset: Decalage pour la pagination.

        Returns:
            Liste des messages.
        """
        pass

    @abstractmethod
    async def list_by_interventions(
        self,
        intervention_ids: List[int],
        auteur_id: Optional[int] = None,
        limit: int = 500,
    ) -> List[InterventionMessage]:
        """Liste les messages de plusieurs interventions (batch).

        Utilisé par l'export RGPD pour éviter le N+1.

        Args:
            intervention_ids: Liste d'IDs d'interventions.
            auteur_id: Filtrer par auteur (optionnel).
            limit: Nombre maximum de résultats.

        Returns:
            Liste des messages.
        """
        pass

    @abstractmethod
    async def list_for_rapport(
        self,
        intervention_id: int,
    ) -> List[InterventionMessage]:
        """Liste les messages a inclure dans le rapport PDF.

        INT-15: Selection posts pour rapport

        Args:
            intervention_id: ID de l'intervention.

        Returns:
            Liste des messages avec inclure_rapport=True.
        """
        pass

    @abstractmethod
    async def count_by_intervention(
        self,
        intervention_id: int,
        include_deleted: bool = False,
    ) -> int:
        """Compte les messages d'une intervention.

        Args:
            intervention_id: ID de l'intervention.
            include_deleted: Inclure les messages supprimes.

        Returns:
            Nombre de messages.
        """
        pass

    @abstractmethod
    async def delete(self, message_id: int, deleted_by: int) -> bool:
        """Supprime un message (soft delete).

        Args:
            message_id: ID du message.
            deleted_by: ID de l'utilisateur qui supprime.

        Returns:
            True si supprime.
        """
        pass

    @abstractmethod
    async def toggle_inclure_rapport(
        self, message_id: int, inclure: bool
    ) -> bool:
        """Active/desactive l'inclusion dans le rapport.

        INT-15: Selection posts pour rapport

        Args:
            message_id: ID du message.
            inclure: True pour inclure, False pour exclure.

        Returns:
            True si modifie.
        """
        pass
