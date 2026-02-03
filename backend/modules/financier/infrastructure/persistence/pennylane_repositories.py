"""Repositories SQLAlchemy pour les entites Pennylane.

CONN-10 to CONN-17: Persistence des logs de sync, mappings et reconciliations.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from ...domain.entities import (
    PennylaneSyncLog,
    PennylaneMappingAnalytique,
    PennylanePendingReconciliation,
)
from .models import (
    PennylaneSyncLogModel,
    PennylaneMappingAnalytiqueModel,
    PennylanePendingReconciliationModel,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# PennylaneSyncLog Repository
# ─────────────────────────────────────────────────────────────────────────────

class SqlAlchemyPennylaneSyncLogRepository:
    """Repository SQLAlchemy pour les logs de synchronisation Pennylane."""

    def __init__(self, session: Session):
        """Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self.session = session

    def save(self, log: PennylaneSyncLog) -> PennylaneSyncLog:
        """Persiste un log de synchronisation.

        Args:
            log: L'entite PennylaneSyncLog a persister.

        Returns:
            L'entite avec son ID mis a jour.
        """
        if log.id is None:
            # Creation
            model = PennylaneSyncLogModel(
                sync_type=log.sync_type,
                started_at=log.started_at,
                completed_at=log.completed_at,
                records_processed=log.records_processed,
                records_created=log.records_created,
                records_updated=log.records_updated,
                records_pending=log.records_pending,
                error_message=log.error_message,
                status=log.status,
            )
            self.session.add(model)
            self.session.flush()
            log.id = model.id
        else:
            # Mise a jour
            model = self.session.query(PennylaneSyncLogModel).filter(
                PennylaneSyncLogModel.id == log.id
            ).first()
            if model:
                model.completed_at = log.completed_at
                model.records_processed = log.records_processed
                model.records_created = log.records_created
                model.records_updated = log.records_updated
                model.records_pending = log.records_pending
                model.error_message = log.error_message
                model.status = log.status
                self.session.flush()

        return log

    def find_by_id(self, log_id: int) -> Optional[PennylaneSyncLog]:
        """Trouve un log par son ID.

        Args:
            log_id: L'ID du log.

        Returns:
            L'entite ou None.
        """
        model = self.session.query(PennylaneSyncLogModel).filter(
            PennylaneSyncLogModel.id == log_id
        ).first()

        if not model:
            return None

        return self._to_entity(model)

    def find_last_successful(
        self,
        sync_type: str,
    ) -> Optional[PennylaneSyncLog]:
        """Trouve le dernier log reussi pour un type de sync.

        Args:
            sync_type: Type de synchronisation.

        Returns:
            L'entite ou None.
        """
        model = self.session.query(PennylaneSyncLogModel).filter(
            PennylaneSyncLogModel.sync_type == sync_type,
            PennylaneSyncLogModel.status.in_(["completed", "partial"]),
        ).order_by(
            desc(PennylaneSyncLogModel.completed_at)
        ).first()

        if not model:
            return None

        return self._to_entity(model)

    def find_by_type(
        self,
        sync_type: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[PennylaneSyncLog]:
        """Trouve les logs par type.

        Args:
            sync_type: Type de synchronisation.
            limit: Nombre max de resultats.
            offset: Offset pour pagination.

        Returns:
            Liste des entites.
        """
        models = self.session.query(PennylaneSyncLogModel).filter(
            PennylaneSyncLogModel.sync_type == sync_type,
        ).order_by(
            desc(PennylaneSyncLogModel.started_at)
        ).offset(offset).limit(limit).all()

        return [self._to_entity(m) for m in models]

    def find_all(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> List[PennylaneSyncLog]:
        """Trouve tous les logs.

        Args:
            limit: Nombre max de resultats.
            offset: Offset pour pagination.

        Returns:
            Liste des entites.
        """
        models = self.session.query(PennylaneSyncLogModel).order_by(
            desc(PennylaneSyncLogModel.started_at)
        ).offset(offset).limit(limit).all()

        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: PennylaneSyncLogModel) -> PennylaneSyncLog:
        """Convertit un model en entite."""
        return PennylaneSyncLog(
            id=model.id,
            sync_type=model.sync_type,
            started_at=model.started_at,
            completed_at=model.completed_at,
            records_processed=model.records_processed,
            records_created=model.records_created,
            records_updated=model.records_updated,
            records_pending=model.records_pending,
            error_message=model.error_message,
            status=model.status,
        )


# ─────────────────────────────────────────────────────────────────────────────
# PennylaneMappingAnalytique Repository
# ─────────────────────────────────────────────────────────────────────────────

class SqlAlchemyPennylaneMappingRepository:
    """Repository SQLAlchemy pour les mappings analytiques Pennylane."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, mapping: PennylaneMappingAnalytique) -> PennylaneMappingAnalytique:
        """Persiste un mapping.

        Args:
            mapping: L'entite a persister.

        Returns:
            L'entite avec son ID mis a jour.
        """
        if mapping.id is None:
            model = PennylaneMappingAnalytiqueModel(
                code_analytique=mapping.code_analytique,
                chantier_id=mapping.chantier_id,
                created_at=mapping.created_at or datetime.utcnow(),
                created_by=mapping.created_by,
            )
            self.session.add(model)
            self.session.flush()
            mapping.id = model.id
        else:
            model = self.session.query(PennylaneMappingAnalytiqueModel).filter(
                PennylaneMappingAnalytiqueModel.id == mapping.id
            ).first()
            if model:
                model.code_analytique = mapping.code_analytique
                model.chantier_id = mapping.chantier_id
                self.session.flush()

        return mapping

    def find_by_id(self, mapping_id: int) -> Optional[PennylaneMappingAnalytique]:
        """Trouve un mapping par son ID."""
        model = self.session.query(PennylaneMappingAnalytiqueModel).filter(
            PennylaneMappingAnalytiqueModel.id == mapping_id
        ).first()

        if not model:
            return None

        return self._to_entity(model)

    def find_by_code_analytique(
        self,
        code_analytique: str,
    ) -> Optional[PennylaneMappingAnalytique]:
        """Trouve un mapping par code analytique.

        Args:
            code_analytique: Code analytique Pennylane.

        Returns:
            L'entite ou None.
        """
        # Normaliser le code
        code_clean = code_analytique.strip().upper()

        model = self.session.query(PennylaneMappingAnalytiqueModel).filter(
            PennylaneMappingAnalytiqueModel.code_analytique == code_clean
        ).first()

        if not model:
            return None

        return self._to_entity(model)

    def find_by_chantier_id(
        self,
        chantier_id: int,
    ) -> List[PennylaneMappingAnalytique]:
        """Trouve les mappings pour un chantier.

        Args:
            chantier_id: ID du chantier.

        Returns:
            Liste des mappings.
        """
        models = self.session.query(PennylaneMappingAnalytiqueModel).filter(
            PennylaneMappingAnalytiqueModel.chantier_id == chantier_id
        ).all()

        return [self._to_entity(m) for m in models]

    def find_all(self) -> List[PennylaneMappingAnalytique]:
        """Trouve tous les mappings."""
        models = self.session.query(PennylaneMappingAnalytiqueModel).order_by(
            PennylaneMappingAnalytiqueModel.code_analytique
        ).all()

        return [self._to_entity(m) for m in models]

    def delete(self, mapping_id: int) -> bool:
        """Supprime un mapping.

        Args:
            mapping_id: ID du mapping.

        Returns:
            True si supprime.
        """
        result = self.session.query(PennylaneMappingAnalytiqueModel).filter(
            PennylaneMappingAnalytiqueModel.id == mapping_id
        ).delete()
        self.session.flush()
        return result > 0

    def _to_entity(self, model: PennylaneMappingAnalytiqueModel) -> PennylaneMappingAnalytique:
        """Convertit un model en entite."""
        return PennylaneMappingAnalytique(
            id=model.id,
            code_analytique=model.code_analytique,
            chantier_id=model.chantier_id,
            created_at=model.created_at,
            created_by=model.created_by,
        )


# ─────────────────────────────────────────────────────────────────────────────
# PennylanePendingReconciliation Repository
# ─────────────────────────────────────────────────────────────────────────────

class SqlAlchemyPennylanePendingRepository:
    """Repository SQLAlchemy pour les reconciliations en attente."""

    def __init__(self, session: Session):
        self.session = session

    def save(
        self,
        pending: PennylanePendingReconciliation,
    ) -> PennylanePendingReconciliation:
        """Persiste une reconciliation.

        Args:
            pending: L'entite a persister.

        Returns:
            L'entite avec son ID mis a jour.
        """
        if pending.id is None:
            model = PennylanePendingReconciliationModel(
                pennylane_invoice_id=pending.pennylane_invoice_id,
                supplier_name=pending.supplier_name,
                supplier_siret=pending.supplier_siret,
                amount_ht=pending.amount_ht,
                code_analytique=pending.code_analytique,
                invoice_date=pending.invoice_date,
                suggested_achat_id=pending.suggested_achat_id,
                status=pending.status,
                resolved_by=pending.resolved_by,
                resolved_at=pending.resolved_at,
                created_at=pending.created_at or datetime.utcnow(),
            )
            self.session.add(model)
            self.session.flush()
            pending.id = model.id
        else:
            model = self.session.query(PennylanePendingReconciliationModel).filter(
                PennylanePendingReconciliationModel.id == pending.id
            ).first()
            if model:
                model.suggested_achat_id = pending.suggested_achat_id
                model.status = pending.status
                model.resolved_by = pending.resolved_by
                model.resolved_at = pending.resolved_at
                self.session.flush()

        return pending

    def find_by_id(
        self,
        pending_id: int,
    ) -> Optional[PennylanePendingReconciliation]:
        """Trouve une reconciliation par son ID."""
        model = self.session.query(PennylanePendingReconciliationModel).filter(
            PennylanePendingReconciliationModel.id == pending_id
        ).first()

        if not model:
            return None

        return self._to_entity(model)

    def find_by_pennylane_invoice_id(
        self,
        invoice_id: str,
    ) -> Optional[PennylanePendingReconciliation]:
        """Trouve une reconciliation par ID facture Pennylane.

        Args:
            invoice_id: ID de la facture Pennylane.

        Returns:
            L'entite ou None.
        """
        model = self.session.query(PennylanePendingReconciliationModel).filter(
            PennylanePendingReconciliationModel.pennylane_invoice_id == invoice_id
        ).first()

        if not model:
            return None

        return self._to_entity(model)

    def find_by_status(
        self,
        status: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[PennylanePendingReconciliation]:
        """Trouve les reconciliations par statut.

        Args:
            status: Statut a filtrer.
            limit: Nombre max de resultats.
            offset: Offset pour pagination.

        Returns:
            Liste des entites.
        """
        models = self.session.query(PennylanePendingReconciliationModel).filter(
            PennylanePendingReconciliationModel.status == status
        ).order_by(
            desc(PennylanePendingReconciliationModel.created_at)
        ).offset(offset).limit(limit).all()

        return [self._to_entity(m) for m in models]

    def find_all(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> List[PennylanePendingReconciliation]:
        """Trouve toutes les reconciliations.

        Args:
            limit: Nombre max de resultats.
            offset: Offset pour pagination.

        Returns:
            Liste des entites.
        """
        models = self.session.query(PennylanePendingReconciliationModel).order_by(
            desc(PennylanePendingReconciliationModel.created_at)
        ).offset(offset).limit(limit).all()

        return [self._to_entity(m) for m in models]

    def count_by_status(self, status: str) -> int:
        """Compte les reconciliations par statut.

        Args:
            status: Statut a compter.

        Returns:
            Nombre de reconciliations.
        """
        return self.session.query(PennylanePendingReconciliationModel).filter(
            PennylanePendingReconciliationModel.status == status
        ).count()

    def _to_entity(
        self,
        model: PennylanePendingReconciliationModel,
    ) -> PennylanePendingReconciliation:
        """Convertit un model en entite."""
        return PennylanePendingReconciliation(
            id=model.id,
            pennylane_invoice_id=model.pennylane_invoice_id,
            supplier_name=model.supplier_name,
            supplier_siret=model.supplier_siret,
            amount_ht=Decimal(str(model.amount_ht)) if model.amount_ht else None,
            code_analytique=model.code_analytique,
            invoice_date=model.invoice_date,
            suggested_achat_id=model.suggested_achat_id,
            status=model.status,
            resolved_by=model.resolved_by,
            resolved_at=model.resolved_at,
            created_at=model.created_at,
        )
