"""Service applicatif pour la gestion de l'audit trail."""

from datetime import datetime
from typing import List, Optional, Any

from ...domain.entities.audit_entry import AuditEntry
from ...domain.repositories.audit_repository import AuditRepository
from ..dtos.audit_dtos import (
    LogAuditEntryDTO,
    AuditEntryDTO,
    GetHistoryDTO,
    GetUserActionsDTO,
    GetRecentEntriesDTO,
    SearchAuditDTO,
    AuditHistoryResponseDTO,
)


class AuditServiceError(Exception):
    """Exception de base pour le service d'audit."""

    def __init__(self, message: str = "Erreur du service d'audit"):
        self.message = message
        super().__init__(self.message)


class AuditService:
    """
    Service applicatif pour la gestion de l'audit trail.

    Ce service orchestre la logique métier de l'audit et coordonne
    les interactions avec le repository.

    Attributes:
        repository: Repository pour accéder aux données d'audit.
    """

    def __init__(self, repository: AuditRepository):
        """
        Initialise le service d'audit.

        Args:
            repository: Repository d'audit (interface).
        """
        self.repository = repository

    def log(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        author_id: int,
        author_name: str,
        field_name: Optional[str] = None,
        old_value: Any = None,
        new_value: Any = None,
        motif: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> AuditEntryDTO:
        """
        Enregistre une entrée d'audit.

        Cette méthode est le point d'entrée principal pour créer des entrées d'audit
        depuis les autres modules de l'application.

        Args:
            entity_type: Type de l'entité (ex: "devis", "lot_budgetaire").
            entity_id: ID de l'entité (string pour support UUID et int).
            action: Action effectuée (ex: "created", "updated", "deleted").
            author_id: ID de l'utilisateur auteur.
            author_name: Nom complet de l'utilisateur.
            field_name: Nom du champ modifié (optionnel).
            old_value: Valeur avant modification (optionnel).
            new_value: Valeur après modification (optionnel).
            motif: Raison de la modification (optionnel).
            metadata: Métadonnées additionnelles (optionnel).

        Returns:
            AuditEntryDTO de l'entrée créée.

        Raises:
            AuditServiceError: Si l'enregistrement échoue.

        Example:
            >>> service.log(
            ...     entity_type="devis",
            ...     entity_id="123",
            ...     action="updated",
            ...     author_id=1,
            ...     author_name="Jean Dupont",
            ...     field_name="montant_ht",
            ...     old_value=10000.00,
            ...     new_value=12000.00,
            ...     motif="Révision suite à modification du client",
            ... )
        """
        try:
            # Créer l'entité AuditEntry
            entry = AuditEntry(
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                author_id=author_id,
                author_name=author_name,
                field_name=field_name,
                old_value=AuditEntry.serialize_value(old_value) if old_value is not None else None,
                new_value=AuditEntry.serialize_value(new_value) if new_value is not None else None,
                motif=motif,
                metadata=metadata,
            )

            # Persister via le repository
            saved_entry = self.repository.save(entry)

            # Retourner le DTO
            return AuditEntryDTO.from_entity(saved_entry)

        except ValueError as e:
            raise AuditServiceError(f"Données d'audit invalides : {str(e)}")
        except Exception as e:
            raise AuditServiceError(f"Erreur lors de l'enregistrement de l'audit : {str(e)}")

    def log_creation(
        self,
        entity_type: str,
        entity_id: str,
        author_id: int,
        author_name: str,
        new_value: Any = None,
        motif: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> AuditEntryDTO:
        """
        Enregistre la création d'une entité.

        Helper method pour simplifier l'enregistrement des créations.

        Args:
            entity_type: Type de l'entité créée.
            entity_id: ID de l'entité créée.
            author_id: ID de l'utilisateur.
            author_name: Nom de l'utilisateur.
            new_value: Valeur initiale de l'entité (optionnel).
            motif: Raison de la création (optionnel).
            metadata: Métadonnées additionnelles (optionnel).

        Returns:
            AuditEntryDTO de l'entrée créée.
        """
        entry = AuditEntry.create_for_creation(
            entity_type=entity_type,
            entity_id=entity_id,
            author_id=author_id,
            author_name=author_name,
            new_value=new_value,
            motif=motif,
            metadata=metadata,
        )

        saved_entry = self.repository.save(entry)
        return AuditEntryDTO.from_entity(saved_entry)

    def log_update(
        self,
        entity_type: str,
        entity_id: str,
        field_name: str,
        old_value: Any,
        new_value: Any,
        author_id: int,
        author_name: str,
        motif: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> AuditEntryDTO:
        """
        Enregistre la mise à jour d'un champ.

        Helper method pour simplifier l'enregistrement des modifications.

        Args:
            entity_type: Type de l'entité modifiée.
            entity_id: ID de l'entité modifiée.
            field_name: Nom du champ modifié.
            old_value: Valeur avant modification.
            new_value: Valeur après modification.
            author_id: ID de l'utilisateur.
            author_name: Nom de l'utilisateur.
            motif: Raison de la modification (optionnel).
            metadata: Métadonnées additionnelles (optionnel).

        Returns:
            AuditEntryDTO de l'entrée créée.
        """
        entry = AuditEntry.create_for_update(
            entity_type=entity_type,
            entity_id=entity_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            author_id=author_id,
            author_name=author_name,
            motif=motif,
            metadata=metadata,
        )

        saved_entry = self.repository.save(entry)
        return AuditEntryDTO.from_entity(saved_entry)

    def log_deletion(
        self,
        entity_type: str,
        entity_id: str,
        author_id: int,
        author_name: str,
        old_value: Any = None,
        motif: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> AuditEntryDTO:
        """
        Enregistre la suppression d'une entité.

        Helper method pour simplifier l'enregistrement des suppressions.

        Args:
            entity_type: Type de l'entité supprimée.
            entity_id: ID de l'entité supprimée.
            author_id: ID de l'utilisateur.
            author_name: Nom de l'utilisateur.
            old_value: Valeur avant suppression (optionnel).
            motif: Raison de la suppression (optionnel).
            metadata: Métadonnées additionnelles (optionnel).

        Returns:
            AuditEntryDTO de l'entrée créée.
        """
        entry = AuditEntry.create_for_deletion(
            entity_type=entity_type,
            entity_id=entity_id,
            author_id=author_id,
            author_name=author_name,
            old_value=old_value,
            motif=motif,
            metadata=metadata,
        )

        saved_entry = self.repository.save(entry)
        return AuditEntryDTO.from_entity(saved_entry)

    def log_status_change(
        self,
        entity_type: str,
        entity_id: str,
        old_status: str,
        new_status: str,
        author_id: int,
        author_name: str,
        motif: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> AuditEntryDTO:
        """
        Enregistre un changement de statut.

        Helper method pour simplifier l'enregistrement des changements de statut.

        Args:
            entity_type: Type de l'entité modifiée.
            entity_id: ID de l'entité modifiée.
            old_status: Statut avant changement.
            new_status: Statut après changement.
            author_id: ID de l'utilisateur.
            author_name: Nom de l'utilisateur.
            motif: Raison du changement (optionnel).
            metadata: Métadonnées additionnelles (optionnel).

        Returns:
            AuditEntryDTO de l'entrée créée.
        """
        entry = AuditEntry.create_for_status_change(
            entity_type=entity_type,
            entity_id=entity_id,
            old_status=old_status,
            new_status=new_status,
            author_id=author_id,
            author_name=author_name,
            motif=motif,
            metadata=metadata,
        )

        saved_entry = self.repository.save(entry)
        return AuditEntryDTO.from_entity(saved_entry)

    def get_history(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> AuditHistoryResponseDTO:
        """
        Récupère l'historique d'une entité.

        Args:
            entity_type: Type de l'entité.
            entity_id: ID de l'entité.
            limit: Nombre maximum d'entrées à retourner.
            offset: Décalage pour pagination.

        Returns:
            AuditHistoryResponseDTO contenant les entrées d'audit.

        Example:
            >>> response = service.get_history(
            ...     entity_type="devis",
            ...     entity_id="123",
            ...     limit=20,
            ... )
            >>> print(f"Total: {response.total}, Entries: {len(response.entries)}")
        """
        entries = self.repository.get_history(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit,
            offset=offset,
        )

        total = self.repository.count_entries(
            entity_type=entity_type,
            entity_id=entity_id,
        )

        entry_dtos = [AuditEntryDTO.from_entity(entry) for entry in entries]

        return AuditHistoryResponseDTO(
            entries=entry_dtos,
            total=total,
            limit=limit,
            offset=offset,
        )

    def get_user_actions(
        self,
        author_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        entity_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEntryDTO]:
        """
        Récupère les actions d'un utilisateur.

        Args:
            author_id: ID de l'utilisateur.
            start_date: Date de début (optionnel).
            end_date: Date de fin (optionnel).
            entity_type: Filtrer par type d'entité (optionnel).
            limit: Nombre maximum d'entrées à retourner.
            offset: Décalage pour pagination.

        Returns:
            Liste des AuditEntryDTO.
        """
        entries = self.repository.get_user_actions(
            author_id=author_id,
            start_date=start_date,
            end_date=end_date,
            entity_type=entity_type,
            limit=limit,
            offset=offset,
        )

        return [AuditEntryDTO.from_entity(entry) for entry in entries]

    def get_recent_entries(
        self,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 50,
    ) -> List[AuditEntryDTO]:
        """
        Récupère les entrées d'audit récentes.

        Args:
            entity_type: Filtrer par type d'entité (optionnel).
            action: Filtrer par type d'action (optionnel).
            limit: Nombre maximum d'entrées à retourner.

        Returns:
            Liste des AuditEntryDTO.
        """
        entries = self.repository.get_recent_entries(
            entity_type=entity_type,
            action=action,
            limit=limit,
        )

        return [AuditEntryDTO.from_entity(entry) for entry in entries]

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
    ) -> AuditHistoryResponseDTO:
        """
        Recherche avancée dans les entrées d'audit.

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
            AuditHistoryResponseDTO contenant les résultats.
        """
        entries, total = self.repository.search(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            author_id=author_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

        entry_dtos = [AuditEntryDTO.from_entity(entry) for entry in entries]

        return AuditHistoryResponseDTO(
            entries=entry_dtos,
            total=total,
            limit=limit,
            offset=offset,
        )
