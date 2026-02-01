"""Implementation SQLAlchemy du repository JournalDevis.

DEV-18: Historique modifications - CRUD du journal d'audit.
Table append-only (pas de soft delete, pas de modification).
"""

import json
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ...domain.entities import JournalDevis
from ...domain.repositories.journal_devis_repository import (
    JournalDevisRepository,
)
from .models import JournalDevisModel


class SQLAlchemyJournalDevisRepository(JournalDevisRepository):
    """Implementation SQLAlchemy du repository JournalDevis.

    Table append-only: pas de mise a jour, pas de suppression.
    """

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: JournalDevisModel) -> JournalDevis:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite JournalDevis correspondante.
        """
        details_json: Optional[Dict[str, Any]] = None
        if model.details:
            try:
                details_json = json.loads(model.details)
            except (json.JSONDecodeError, TypeError):
                details_json = {"raw": model.details}

        return JournalDevis(
            id=model.id,
            devis_id=model.devis_id,
            action=model.action,
            auteur_id=model.auteur_id,
            details_json=details_json,
            created_at=model.created_at,
        )

    def save(self, entry: JournalDevis) -> JournalDevis:
        """Persiste une entree de journal (creation uniquement).

        Args:
            entry: L'entree de journal a persister.

        Returns:
            L'entree avec son ID attribue.
        """
        details_str: Optional[str] = None
        if entry.details_json is not None:
            details_str = json.dumps(entry.details_json, ensure_ascii=False)

        model = JournalDevisModel(
            devis_id=entry.devis_id,
            action=entry.action,
            details=details_str,
            auteur_id=entry.auteur_id,
            created_at=entry.created_at or datetime.utcnow(),
        )
        self._session.add(model)
        self._session.flush()

        return self._to_entity(model)

    def find_by_devis(
        self,
        devis_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[JournalDevis]:
        """Liste les entrees de journal d'un devis.

        Args:
            devis_id: L'ID du devis.
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des entrees ordonnee par date decroissante.
        """
        query = (
            self._session.query(JournalDevisModel)
            .filter(JournalDevisModel.devis_id == devis_id)
            .order_by(JournalDevisModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [self._to_entity(model) for model in query.all()]

    def find_by_auteur(
        self,
        auteur_id: int,
        date_min: Optional[date] = None,
        date_max: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[JournalDevis]:
        """Liste les entrees de journal d'un auteur.

        Args:
            auteur_id: L'ID de l'auteur.
            date_min: Date minimale (optionnel).
            date_max: Date maximale (optionnel).
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des entrees ordonnee par date decroissante.
        """
        query = self._session.query(JournalDevisModel).filter(
            JournalDevisModel.auteur_id == auteur_id
        )

        if date_min is not None:
            query = query.filter(
                JournalDevisModel.created_at >= datetime.combine(
                    date_min, datetime.min.time()
                )
            )

        if date_max is not None:
            query = query.filter(
                JournalDevisModel.created_at <= datetime.combine(
                    date_max, datetime.max.time()
                )
            )

        query = (
            query.order_by(JournalDevisModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [self._to_entity(model) for model in query.all()]

    def count_by_devis(self, devis_id: int) -> int:
        """Compte le nombre d'entrees de journal d'un devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            Le nombre d'entrees.
        """
        return (
            self._session.query(JournalDevisModel)
            .filter(JournalDevisModel.devis_id == devis_id)
            .count()
        )
