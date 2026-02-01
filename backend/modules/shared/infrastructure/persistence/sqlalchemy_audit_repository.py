"""Implémentation SQLAlchemy du repository Audit."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import Session

from ...domain.entities.audit_entry import AuditEntry
from ...domain.repositories.audit_repository import AuditRepository
from .models import AuditLogModel


class SQLAlchemyAuditRepository(AuditRepository):
    """
    Implémentation SQLAlchemy du repository d'audit.

    Cette implémentation gère la persistence des entrées d'audit dans PostgreSQL
    avec optimisations pour les requêtes fréquentes (index, pagination, etc.).

    Attributes:
        _session: Session SQLAlchemy pour les opérations de base de données.
    """

    def __init__(self, session: Session):
        """
        Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: AuditLogModel) -> AuditEntry:
        """
        Convertit un modèle SQLAlchemy en entité AuditEntry.

        Args:
            model: Le modèle SQLAlchemy source.

        Returns:
            L'entité AuditEntry correspondante.
        """
        return AuditEntry(
            id=model.id,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            action=model.action,
            field_name=model.field_name,
            old_value=model.old_value,
            new_value=model.new_value,
            author_id=model.author_id,
            author_name=model.author_name,
            timestamp=model.timestamp,
            motif=model.motif,
            metadata=model.metadata,
        )

    def _to_model(self, entry: AuditEntry) -> AuditLogModel:
        """
        Convertit une entité AuditEntry en modèle SQLAlchemy.

        Args:
            entry: L'entité AuditEntry source.

        Returns:
            Le modèle SQLAlchemy correspondant.
        """
        return AuditLogModel(
            id=entry.id,
            entity_type=entry.entity_type,
            entity_id=entry.entity_id,
            action=entry.action,
            field_name=entry.field_name,
            old_value=entry.old_value,
            new_value=entry.new_value,
            author_id=entry.author_id,
            author_name=entry.author_name,
            timestamp=entry.timestamp,
            motif=entry.motif,
            metadata=entry.metadata,
        )

    def save(self, entry: AuditEntry) -> AuditEntry:
        """
        Persiste une entrée d'audit (append-only).

        Les entrées d'audit ne sont jamais modifiées ou supprimées après création.

        Args:
            entry: L'entrée d'audit à sauvegarder.

        Returns:
            L'entrée d'audit sauvegardée (avec ID généré si nouveau).
        """
        model = self._to_model(entry)
        self._session.add(model)
        self._session.flush()

        return self._to_entity(model)

    def find_by_id(self, entry_id: UUID) -> Optional[AuditEntry]:
        """
        Trouve une entrée d'audit par son ID.

        Args:
            entry_id: L'identifiant UUID de l'entrée.

        Returns:
            L'entrée d'audit trouvée ou None.
        """
        model = self._session.query(AuditLogModel).filter(
            AuditLogModel.id == entry_id
        ).first()

        return self._to_entity(model) if model else None

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
            entity_type: Type de l'entité.
            entity_id: ID de l'entité.
            limit: Nombre maximum d'entrées à retourner.
            offset: Décalage pour pagination.

        Returns:
            Liste des entrées d'audit pour cette entité.
        """
        query = (
            self._session.query(AuditLogModel)
            .filter(
                AuditLogModel.entity_type == entity_type.lower(),
                AuditLogModel.entity_id == entity_id,
            )
            .order_by(desc(AuditLogModel.timestamp))
            .offset(offset)
            .limit(limit)
        )

        models = query.all()
        return [self._to_entity(model) for model in models]

    def get_history_for_field(
        self,
        entity_type: str,
        entity_id: str,
        field_name: str,
        limit: int = 50,
    ) -> List[AuditEntry]:
        """
        Récupère l'historique d'un champ spécifique.

        Args:
            entity_type: Type de l'entité.
            entity_id: ID de l'entité.
            field_name: Nom du champ.
            limit: Nombre maximum d'entrées à retourner.

        Returns:
            Liste des entrées d'audit pour ce champ.
        """
        query = (
            self._session.query(AuditLogModel)
            .filter(
                AuditLogModel.entity_type == entity_type.lower(),
                AuditLogModel.entity_id == entity_id,
                AuditLogModel.field_name == field_name,
            )
            .order_by(desc(AuditLogModel.timestamp))
            .limit(limit)
        )

        models = query.all()
        return [self._to_entity(model) for model in models]

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

        Args:
            author_id: ID de l'utilisateur.
            start_date: Date de début (optionnel).
            end_date: Date de fin (optionnel).
            entity_type: Filtrer par type d'entité (optionnel).
            limit: Nombre maximum d'entrées à retourner.
            offset: Décalage pour pagination.

        Returns:
            Liste des entrées d'audit pour cet utilisateur.
        """
        query = self._session.query(AuditLogModel).filter(
            AuditLogModel.author_id == author_id
        )

        # Filtres optionnels
        if start_date:
            query = query.filter(AuditLogModel.timestamp >= start_date)

        if end_date:
            query = query.filter(AuditLogModel.timestamp <= end_date)

        if entity_type:
            query = query.filter(AuditLogModel.entity_type == entity_type.lower())

        query = query.order_by(desc(AuditLogModel.timestamp)).offset(offset).limit(limit)

        models = query.all()
        return [self._to_entity(model) for model in models]

    def get_recent_entries(
        self,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 50,
    ) -> List[AuditEntry]:
        """
        Récupère les entrées d'audit récentes.

        Args:
            entity_type: Filtrer par type d'entité (optionnel).
            action: Filtrer par type d'action (optionnel).
            limit: Nombre maximum d'entrées à retourner.

        Returns:
            Liste des entrées d'audit récentes.
        """
        query = self._session.query(AuditLogModel)

        # Filtres optionnels
        if entity_type:
            query = query.filter(AuditLogModel.entity_type == entity_type.lower())

        if action:
            query = query.filter(AuditLogModel.action == action.lower())

        query = query.order_by(desc(AuditLogModel.timestamp)).limit(limit)

        models = query.all()
        return [self._to_entity(model) for model in models]

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
        return (
            self._session.query(func.count(AuditLogModel.id))
            .filter(
                AuditLogModel.entity_type == entity_type.lower(),
                AuditLogModel.entity_id == entity_id,
            )
            .scalar()
        )

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
        """
        query = self._session.query(AuditLogModel)

        # Construction des filtres dynamiques
        filters = []

        if entity_type:
            filters.append(AuditLogModel.entity_type == entity_type.lower())

        if entity_id:
            filters.append(AuditLogModel.entity_id == entity_id)

        if action:
            filters.append(AuditLogModel.action == action.lower())

        if author_id:
            filters.append(AuditLogModel.author_id == author_id)

        if start_date:
            filters.append(AuditLogModel.timestamp >= start_date)

        if end_date:
            filters.append(AuditLogModel.timestamp <= end_date)

        # Application des filtres
        if filters:
            query = query.filter(and_(*filters))

        # Total count avant pagination
        total = query.count()

        # Application pagination et tri
        query = query.order_by(desc(AuditLogModel.timestamp)).offset(offset).limit(limit)

        models = query.all()
        entries = [self._to_entity(model) for model in models]

        return entries, total
