"""Implementation SQLAlchemy du repository InterventionMessage."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from ...domain.entities import InterventionMessage, TypeMessage
from ...domain.repositories import InterventionMessageRepository
from .models import InterventionMessageModel


class SQLAlchemyInterventionMessageRepository(InterventionMessageRepository):
    """Implementation SQLAlchemy du repository des messages."""

    def __init__(self, session: Session):
        """Initialise le repository."""
        self._session = session

    def save(self, message: InterventionMessage) -> InterventionMessage:
        """Sauvegarde un message."""
        if message.id is None:
            model = InterventionMessageModel(
                intervention_id=message.intervention_id,
                auteur_id=message.auteur_id if message.auteur_id > 0 else None,
                type_message=message.type_message,
                contenu=message.contenu,
                photos_urls=message.photos_urls or [],
                extra_data=message.metadata,  # metadata -> extra_data in model
                inclure_rapport=message.inclure_rapport,
                created_at=message.created_at,
            )
            self._session.add(model)
            self._session.flush()
            message.id = model.id
        else:
            model = self._session.query(InterventionMessageModel).filter(
                InterventionMessageModel.id == message.id
            ).first()

            if model:
                model.contenu = message.contenu
                model.photos_urls = message.photos_urls or []
                model.extra_data = message.metadata  # metadata -> extra_data in model
                model.inclure_rapport = message.inclure_rapport

                if message.deleted_at:
                    model.deleted_at = message.deleted_at
                    model.deleted_by = message.deleted_by

                self._session.flush()

        return message

    def get_by_id(self, message_id: int) -> Optional[InterventionMessage]:
        """Recupere un message par son ID."""
        model = self._session.query(InterventionMessageModel).filter(
            InterventionMessageModel.id == message_id
        ).first()

        if not model:
            return None

        return self._model_to_entity(model)

    def list_by_intervention(
        self,
        intervention_id: int,
        type_message: Optional[TypeMessage] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[InterventionMessage]:
        """Liste les messages d'une intervention."""
        query = self._session.query(InterventionMessageModel).filter(
            InterventionMessageModel.intervention_id == intervention_id
        )

        if not include_deleted:
            query = query.filter(InterventionMessageModel.deleted_at.is_(None))

        if type_message:
            query = query.filter(InterventionMessageModel.type_message == type_message)

        query = query.order_by(InterventionMessageModel.created_at.asc())
        query = query.limit(limit).offset(offset)

        models = query.all()

        return [self._model_to_entity(m) for m in models]

    def list_by_interventions(
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
        if not intervention_ids:
            return []

        query = self._session.query(InterventionMessageModel).filter(
            InterventionMessageModel.intervention_id.in_(intervention_ids),
            InterventionMessageModel.deleted_at.is_(None),
        )

        if auteur_id is not None:
            query = query.filter(InterventionMessageModel.auteur_id == auteur_id)

        query = query.order_by(InterventionMessageModel.created_at.asc())
        query = query.limit(limit)

        models = query.all()
        return [self._model_to_entity(m) for m in models]

    def list_for_rapport(
        self,
        intervention_id: int,
    ) -> List[InterventionMessage]:
        """Liste les messages a inclure dans le rapport PDF."""
        query = self._session.query(InterventionMessageModel).filter(
            and_(
                InterventionMessageModel.intervention_id == intervention_id,
                InterventionMessageModel.inclure_rapport == True,
                InterventionMessageModel.deleted_at.is_(None),
            )
        )
        query = query.order_by(InterventionMessageModel.created_at.asc())

        models = query.all()

        return [self._model_to_entity(m) for m in models]

    def count_by_intervention(
        self,
        intervention_id: int,
        include_deleted: bool = False,
    ) -> int:
        """Compte les messages d'une intervention."""
        query = self._session.query(func.count(InterventionMessageModel.id)).filter(
            InterventionMessageModel.intervention_id == intervention_id
        )

        if not include_deleted:
            query = query.filter(InterventionMessageModel.deleted_at.is_(None))

        return query.scalar() or 0

    def delete(self, message_id: int, deleted_by: int) -> bool:
        """Supprime un message (soft delete)."""
        model = self._session.query(InterventionMessageModel).filter(
            and_(
                InterventionMessageModel.id == message_id,
                InterventionMessageModel.deleted_at.is_(None),
            )
        ).first()

        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        self._session.flush()

        return True

    def toggle_inclure_rapport(
        self, message_id: int, inclure: bool
    ) -> bool:
        """Active/desactive l'inclusion dans le rapport."""
        model = self._session.query(InterventionMessageModel).filter(
            and_(
                InterventionMessageModel.id == message_id,
                InterventionMessageModel.deleted_at.is_(None),
            )
        ).first()

        if not model:
            return False

        model.inclure_rapport = inclure
        self._session.flush()

        return True

    def _model_to_entity(
        self, model: InterventionMessageModel
    ) -> InterventionMessage:
        """Convertit un modele en entite."""
        return InterventionMessage(
            id=model.id,
            intervention_id=model.intervention_id,
            auteur_id=model.auteur_id or 0,
            type_message=model.type_message,
            contenu=model.contenu,
            photos_urls=model.photos_urls or [],
            metadata=model.extra_data,  # extra_data in model -> metadata in entity
            inclure_rapport=model.inclure_rapport,
            created_at=model.created_at,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )
