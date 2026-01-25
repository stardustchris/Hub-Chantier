"""Implementation SQLAlchemy du repository InterventionMessage."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities import InterventionMessage, TypeMessage
from ...domain.repositories import InterventionMessageRepository
from .models import InterventionMessageModel


class SQLAlchemyInterventionMessageRepository(InterventionMessageRepository):
    """Implementation SQLAlchemy du repository des messages."""

    def __init__(self, session: AsyncSession):
        """Initialise le repository."""
        self._session = session

    async def save(self, message: InterventionMessage) -> InterventionMessage:
        """Sauvegarde un message."""
        if message.id is None:
            model = InterventionMessageModel(
                intervention_id=message.intervention_id,
                auteur_id=message.auteur_id if message.auteur_id > 0 else None,
                type_message=message.type_message,
                contenu=message.contenu,
                photos_urls=message.photos_urls or [],
                metadata=message.metadata,
                inclure_rapport=message.inclure_rapport,
                created_at=message.created_at,
            )
            self._session.add(model)
            await self._session.flush()
            message.id = model.id
        else:
            stmt = select(InterventionMessageModel).where(
                InterventionMessageModel.id == message.id
            )
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                model.contenu = message.contenu
                model.photos_urls = message.photos_urls or []
                model.metadata = message.metadata
                model.inclure_rapport = message.inclure_rapport

                if message.deleted_at:
                    model.deleted_at = message.deleted_at
                    model.deleted_by = message.deleted_by

                await self._session.flush()

        return message

    async def get_by_id(self, message_id: int) -> Optional[InterventionMessage]:
        """Recupere un message par son ID."""
        stmt = select(InterventionMessageModel).where(
            InterventionMessageModel.id == message_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._model_to_entity(model)

    async def list_by_intervention(
        self,
        intervention_id: int,
        type_message: Optional[TypeMessage] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[InterventionMessage]:
        """Liste les messages d'une intervention."""
        stmt = select(InterventionMessageModel).where(
            InterventionMessageModel.intervention_id == intervention_id
        )

        if not include_deleted:
            stmt = stmt.where(InterventionMessageModel.deleted_at.is_(None))

        if type_message:
            stmt = stmt.where(InterventionMessageModel.type_message == type_message)

        stmt = stmt.order_by(InterventionMessageModel.created_at.asc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(m) for m in models]

    async def list_for_rapport(
        self,
        intervention_id: int,
    ) -> List[InterventionMessage]:
        """Liste les messages a inclure dans le rapport PDF."""
        stmt = select(InterventionMessageModel).where(
            and_(
                InterventionMessageModel.intervention_id == intervention_id,
                InterventionMessageModel.inclure_rapport == True,
                InterventionMessageModel.deleted_at.is_(None),
            )
        )
        stmt = stmt.order_by(InterventionMessageModel.created_at.asc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(m) for m in models]

    async def count_by_intervention(
        self,
        intervention_id: int,
        include_deleted: bool = False,
    ) -> int:
        """Compte les messages d'une intervention."""
        stmt = select(func.count(InterventionMessageModel.id)).where(
            InterventionMessageModel.intervention_id == intervention_id
        )

        if not include_deleted:
            stmt = stmt.where(InterventionMessageModel.deleted_at.is_(None))

        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def delete(self, message_id: int, deleted_by: int) -> bool:
        """Supprime un message (soft delete)."""
        stmt = select(InterventionMessageModel).where(
            and_(
                InterventionMessageModel.id == message_id,
                InterventionMessageModel.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        await self._session.flush()

        return True

    async def toggle_inclure_rapport(
        self, message_id: int, inclure: bool
    ) -> bool:
        """Active/desactive l'inclusion dans le rapport."""
        stmt = select(InterventionMessageModel).where(
            and_(
                InterventionMessageModel.id == message_id,
                InterventionMessageModel.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        model.inclure_rapport = inclure
        await self._session.flush()

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
            metadata=model.metadata,
            inclure_rapport=model.inclure_rapport,
            created_at=model.created_at,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )
