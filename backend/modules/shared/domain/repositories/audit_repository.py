"""Interface AuditRepository - Abstraction pour la persistence des entrées d'audit."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from ..entities.audit_entry import AuditEntry


class AuditRepository(ABC):
    """
    Interface abstraite pour la persistence des entrées d'audit.

    Cette interface définit le contrat pour l'accès aux données d'audit.
    L'implémentation concrète se trouve dans la couche Infrastructure.

    Note:
        Le Domain ne connaît pas l'implémentation (SQLAlchemy, etc.).
        Principe d'inversion de dépendance (Clean Architecture).
    """

    @abstractmethod
    def save(self, entry: AuditEntry) -> AuditEntry:
        """
        Persiste une entrée d'audit (append-only).

        Les entrées d'audit ne sont jamais modifiées ou supprimées après création
        (table append-only pour garantir l'intégrité de l'audit trail).

        Args:
            entry: L'entrée d'audit à sauvegarder.

        Returns:
            L'entrée d'audit sauvegardée (avec ID si création).

        Example:
            >>> entry = AuditEntry.create_for_creation(
            ...     entity_type="devis",
            ...     entity_id="550e8400-e29b-41d4-a716-446655440000",
            ...     author_id=1,
            ...     author_name="Jean Dupont",
            ... )
            >>> saved_entry = repository.save(entry)
        """
        pass

    @abstractmethod
    def find_by_id(self, entry_id: UUID) -> Optional[AuditEntry]:
        """
        Trouve une entrée d'audit par son ID.

        Args:
            entry_id: L'identifiant UUID de l'entrée.

        Returns:
            L'entrée d'audit trouvée ou None.
        """
        pass

    @abstractmethod
    def get_history(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[AuditEntry]:
        """
        Récupère l'historique d'une entité.

        Les résultats sont triés par timestamp décroissant (plus récent en premier).

        Args:
            entity_type: Type de l'entité (ex: "devis", "lot_budgetaire").
            entity_id: ID de l'entité (string pour support UUID et int).
            limit: Nombre maximum d'entrées à retourner (défaut: 50).
            offset: Décalage pour pagination (défaut: 0).

        Returns:
            Liste des entrées d'audit pour cette entité.

        Example:
            >>> history = repository.get_history(
            ...     entity_type="devis",
            ...     entity_id="550e8400-e29b-41d4-a716-446655440000",
            ...     limit=20,
            ... )
        """
        pass

    @abstractmethod
    def get_history_for_field(
        self,
        entity_type: str,
        entity_id: str,
        field_name: str,
        limit: int = 50,
    ) -> List[AuditEntry]:
        """
        Récupère l'historique d'un champ spécifique.

        Utile pour tracer l'évolution d'un champ particulier (ex: statut, montant).

        Args:
            entity_type: Type de l'entité.
            entity_id: ID de l'entité.
            field_name: Nom du champ.
            limit: Nombre maximum d'entrées à retourner.

        Returns:
            Liste des entrées d'audit pour ce champ.

        Example:
            >>> history = repository.get_history_for_field(
            ...     entity_type="devis",
            ...     entity_id="123",
            ...     field_name="status",
            ... )
        """
        pass

    @abstractmethod
    def get_user_actions(
        self,
        author_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        entity_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEntry]:
        """
        Récupère les actions d'un utilisateur.

        Utile pour l'audit des actions utilisateur et la conformité RGPD.

        Args:
            author_id: ID de l'utilisateur.
            start_date: Date de début (optionnel).
            end_date: Date de fin (optionnel).
            entity_type: Filtrer par type d'entité (optionnel).
            limit: Nombre maximum d'entrées à retourner.
            offset: Décalage pour pagination.

        Returns:
            Liste des entrées d'audit pour cet utilisateur.

        Example:
            >>> from datetime import datetime, timedelta
            >>> end = datetime.now()
            >>> start = end - timedelta(days=7)
            >>> actions = repository.get_user_actions(
            ...     author_id=1,
            ...     start_date=start,
            ...     end_date=end,
            ...     entity_type="devis",
            ... )
        """
        pass

    @abstractmethod
    def get_recent_entries(
        self,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 50,
    ) -> List[AuditEntry]:
        """
        Récupère les entrées d'audit récentes.

        Utile pour l'affichage d'un feed d'activité global.

        Args:
            entity_type: Filtrer par type d'entité (optionnel).
            action: Filtrer par type d'action (optionnel).
            limit: Nombre maximum d'entrées à retourner.

        Returns:
            Liste des entrées d'audit récentes.

        Example:
            >>> recent = repository.get_recent_entries(
            ...     entity_type="devis",
            ...     action="created",
            ...     limit=10,
            ... )
        """
        pass

    @abstractmethod
    def count_entries(
        self,
        entity_type: str,
        entity_id: str,
    ) -> int:
        """
        Compte le nombre d'entrées d'audit pour une entité.

        Args:
            entity_type: Type de l'entité.
            entity_id: ID de l'entité.

        Returns:
            Nombre d'entrées d'audit.
        """
        pass

    @abstractmethod
    def search(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        action: Optional[str] = None,
        author_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[AuditEntry], int]:
        """
        Recherche avancée dans les entrées d'audit.

        Permet de combiner plusieurs critères de recherche.

        Args:
            entity_type: Filtrer par type d'entité (optionnel).
            entity_id: Filtrer par ID d'entité (optionnel).
            action: Filtrer par type d'action (optionnel).
            author_id: Filtrer par auteur (optionnel).
            start_date: Date de début (optionnel).
            end_date: Date de fin (optionnel).
            limit: Nombre maximum d'entrées à retourner.
            offset: Décalage pour pagination.

        Returns:
            Tuple (liste des entrées, total count).

        Example:
            >>> entries, total = repository.search(
            ...     entity_type="devis",
            ...     action="updated",
            ...     author_id=1,
            ...     limit=20,
            ... )
        """
        pass
