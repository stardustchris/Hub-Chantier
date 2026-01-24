"""Service d'audit pour tracer les actions sur les entités."""

from typing import Optional

from sqlalchemy.orm import Session

from .audit_model import AuditLog


class AuditService:
    """
    Service pour enregistrer les actions d'audit.

    Utilisation:
        audit = AuditService(db_session)
        audit.log_action(
            entity_type="chantier",
            entity_id=123,
            action="deleted",
            user_id=1,
            old_values={"statut": "ouvert"},
        )
    """

    def __init__(self, session: Session):
        """
        Initialise le service d'audit.

        Args:
            session: Session SQLAlchemy active.
        """
        self.session = session

    def log_action(
        self,
        entity_type: str,
        entity_id: int,
        action: str,
        user_id: Optional[int] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """
        Enregistre une action d'audit.

        Args:
            entity_type: Type d'entité (ex: "chantier", "user").
            entity_id: ID de l'entité concernée.
            action: Action effectuée (created, updated, deleted, etc.).
            user_id: ID de l'utilisateur ayant effectué l'action.
            old_values: Valeurs avant modification.
            new_values: Valeurs après modification.
            ip_address: Adresse IP de l'utilisateur.
            user_agent: User-Agent du navigateur/client.

        Returns:
            L'entrée AuditLog créée.
        """
        audit_log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.session.add(audit_log)
        self.session.commit()
        return audit_log

    def log_chantier_created(
        self,
        chantier_id: int,
        user_id: int,
        chantier_data: dict,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """
        Log la création d'un chantier.

        Args:
            chantier_id: ID du chantier créé.
            user_id: ID de l'utilisateur créateur.
            chantier_data: Données du chantier créé.
            ip_address: Adresse IP de l'utilisateur.

        Returns:
            L'entrée AuditLog créée.
        """
        return self.log_action(
            entity_type="chantier",
            entity_id=chantier_id,
            action="created",
            user_id=user_id,
            new_values={
                "nom": chantier_data.get("nom"),
                "code": chantier_data.get("code"),
                "statut": chantier_data.get("statut"),
            },
            ip_address=ip_address,
        )

    def log_chantier_deleted(
        self,
        chantier_id: int,
        user_id: int,
        chantier_data: dict,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """
        Log la suppression (soft delete) d'un chantier.

        Args:
            chantier_id: ID du chantier supprimé.
            user_id: ID de l'utilisateur.
            chantier_data: Données du chantier avant suppression.
            ip_address: Adresse IP de l'utilisateur.

        Returns:
            L'entrée AuditLog créée.
        """
        return self.log_action(
            entity_type="chantier",
            entity_id=chantier_id,
            action="deleted",
            user_id=user_id,
            old_values={
                "nom": chantier_data.get("nom"),
                "code": chantier_data.get("code"),
                "statut": chantier_data.get("statut"),
            },
            ip_address=ip_address,
        )

    def log_chantier_status_changed(
        self,
        chantier_id: int,
        user_id: int,
        old_status: str,
        new_status: str,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """
        Log un changement de statut d'un chantier.

        Args:
            chantier_id: ID du chantier.
            user_id: ID de l'utilisateur.
            old_status: Ancien statut.
            new_status: Nouveau statut.
            ip_address: Adresse IP de l'utilisateur.

        Returns:
            L'entrée AuditLog créée.
        """
        return self.log_action(
            entity_type="chantier",
            entity_id=chantier_id,
            action="status_changed",
            user_id=user_id,
            old_values={"statut": old_status},
            new_values={"statut": new_status},
            ip_address=ip_address,
        )

    def log_responsable_assigned(
        self,
        chantier_id: int,
        user_id: int,
        responsable_id: int,
        role_type: str,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """
        Log l'assignation d'un responsable à un chantier.

        Args:
            chantier_id: ID du chantier.
            user_id: ID de l'utilisateur effectuant l'action.
            responsable_id: ID du responsable assigné.
            role_type: Type de rôle ("conducteur" ou "chef_chantier").
            ip_address: Adresse IP de l'utilisateur.

        Returns:
            L'entrée AuditLog créée.
        """
        return self.log_action(
            entity_type="chantier",
            entity_id=chantier_id,
            action="responsable_assigned",
            user_id=user_id,
            new_values={
                "responsable_id": responsable_id,
                "role_type": role_type,
            },
            ip_address=ip_address,
        )

    def log_responsable_removed(
        self,
        chantier_id: int,
        user_id: int,
        responsable_id: int,
        role_type: str,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """
        Log le retrait d'un responsable d'un chantier.

        Args:
            chantier_id: ID du chantier.
            user_id: ID de l'utilisateur effectuant l'action.
            responsable_id: ID du responsable retiré.
            role_type: Type de rôle ("conducteur" ou "chef_chantier").
            ip_address: Adresse IP de l'utilisateur.

        Returns:
            L'entrée AuditLog créée.
        """
        return self.log_action(
            entity_type="chantier",
            entity_id=chantier_id,
            action="responsable_removed",
            user_id=user_id,
            old_values={
                "responsable_id": responsable_id,
                "role_type": role_type,
            },
            ip_address=ip_address,
        )
