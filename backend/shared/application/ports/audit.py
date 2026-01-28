"""Port AuditPort - Interface pour le service d'audit RGPD."""

from abc import ABC, abstractmethod
from typing import Optional


class AuditPort(ABC):
    """
    Interface abstraite pour le service d'audit et traçabilité RGPD.

    L'implémentation concrète se trouve dans shared.infrastructure.audit.
    Permet de tracer les actions sensibles (exports PDF, accès données, etc.)
    pour conformité RGPD Article 30 (registre des activités de traitement).

    Note:
        L'Application ne connaît pas l'implémentation concrète (AuditService).
        Cette interface permet l'inversion de dépendance (Clean Architecture).

    Example:
        >>> audit_port.log_pdf_exported(
        ...     chantier_id=1,
        ...     user_id=2,
        ...     chantier_nom="Chantier A",
        ...     include_completed=True,
        ...     ip_address="192.168.1.1",
        ...     user_agent="Mozilla/5.0...",
        ... )
    """

    @abstractmethod
    def log_pdf_exported(
        self,
        chantier_id: int,
        user_id: int,
        chantier_nom: str,
        include_completed: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """
        Trace l'export PDF d'un chantier (RGPD Art. 30).

        Args:
            chantier_id: ID du chantier exporté.
            user_id: ID de l'utilisateur ayant effectué l'export.
            chantier_nom: Nom du chantier (pour contexte).
            include_completed: Inclut les tâches terminées dans l'export.
            ip_address: Adresse IP de l'utilisateur (optionnel).
            user_agent: User-Agent du navigateur/client (optionnel).

        Example:
            >>> audit_port.log_pdf_exported(
            ...     chantier_id=123,
            ...     user_id=456,
            ...     chantier_nom="Rénovation Immeuble A",
            ...     include_completed=True,
            ...     ip_address="203.0.113.42",
            ...     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            ... )
        """
        pass

    @abstractmethod
    def log_data_accessed(
        self,
        user_id: int,
        resource_type: str,
        resource_id: int,
        action: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """
        Trace l'accès à une ressource sensible (RGPD Art. 30).

        Args:
            user_id: ID de l'utilisateur ayant accédé à la ressource.
            resource_type: Type de ressource (ex: "feuille_heures", "formulaire").
            resource_id: ID de la ressource.
            action: Action effectuée (ex: "read", "export", "delete").
            ip_address: Adresse IP de l'utilisateur (optionnel).
            user_agent: User-Agent du navigateur/client (optionnel).

        Example:
            >>> audit_port.log_data_accessed(
            ...     user_id=456,
            ...     resource_type="feuille_heures",
            ...     resource_id=789,
            ...     action="export",
            ...     ip_address="203.0.113.42",
            ... )
        """
        pass

    @abstractmethod
    def log_user_deleted(
        self,
        user_id: int,
        deleted_by: int,
        reason: str,
        ip_address: Optional[str] = None,
    ) -> None:
        """
        Trace la suppression d'un utilisateur (RGPD Art. 17 - Droit à l'oubli).

        Args:
            user_id: ID de l'utilisateur supprimé.
            deleted_by: ID de l'administrateur ayant effectué la suppression.
            reason: Raison de la suppression.
            ip_address: Adresse IP de l'administrateur (optionnel).

        Example:
            >>> audit_port.log_user_deleted(
            ...     user_id=123,
            ...     deleted_by=1,
            ...     reason="Demande de suppression RGPD Article 17",
            ...     ip_address="203.0.113.42",
            ... )
        """
        pass
