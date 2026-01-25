"""Implementation SQLAlchemy du repository AffectationIntervention."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities import AffectationIntervention
from ...domain.repositories import AffectationInterventionRepository
from .models import AffectationInterventionModel


class SQLAlchemyAffectationInterventionRepository(AffectationInterventionRepository):
    """Implementation SQLAlchemy du repository des affectations."""

    def __init__(self, session: AsyncSession):
        """Initialise le repository."""
        self._session = session

    async def save(
        self, affectation: AffectationIntervention
    ) -> AffectationIntervention:
        """Sauvegarde une affectation."""
        if affectation.id is None:
            model = AffectationInterventionModel(
                intervention_id=affectation.intervention_id,
                utilisateur_id=affectation.utilisateur_id,
                est_principal=affectation.est_principal,
                commentaire=affectation.commentaire,
                created_by=affectation.created_by,
                created_at=affectation.created_at,
            )
            self._session.add(model)
            await self._session.flush()
            affectation.id = model.id
        else:
            stmt = select(AffectationInterventionModel).where(
                AffectationInterventionModel.id == affectation.id
            )
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                model.est_principal = affectation.est_principal
                model.commentaire = affectation.commentaire
                model.updated_at = datetime.utcnow()

                if affectation.deleted_at:
                    model.deleted_at = affectation.deleted_at
                    model.deleted_by = affectation.deleted_by

                await self._session.flush()

        return affectation

    async def get_by_id(
        self, affectation_id: int
    ) -> Optional[AffectationIntervention]:
        """Recupere une affectation par son ID."""
        stmt = select(AffectationInterventionModel).where(
            AffectationInterventionModel.id == affectation_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._model_to_entity(model)

    async def list_by_intervention(
        self,
        intervention_id: int,
        include_deleted: bool = False,
    ) -> List[AffectationIntervention]:
        """Liste les affectations d'une intervention."""
        stmt = select(AffectationInterventionModel).where(
            AffectationInterventionModel.intervention_id == intervention_id
        )

        if not include_deleted:
            stmt = stmt.where(AffectationInterventionModel.deleted_at.is_(None))

        stmt = stmt.order_by(
            AffectationInterventionModel.est_principal.desc(),
            AffectationInterventionModel.created_at.asc(),
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(m) for m in models]

    async def list_by_utilisateur(
        self,
        utilisateur_id: int,
        include_deleted: bool = False,
    ) -> List[AffectationIntervention]:
        """Liste les affectations d'un utilisateur."""
        stmt = select(AffectationInterventionModel).where(
            AffectationInterventionModel.utilisateur_id == utilisateur_id
        )

        if not include_deleted:
            stmt = stmt.where(AffectationInterventionModel.deleted_at.is_(None))

        stmt = stmt.order_by(AffectationInterventionModel.created_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(m) for m in models]

    async def get_principal(
        self, intervention_id: int
    ) -> Optional[AffectationIntervention]:
        """Recupere le technicien principal d'une intervention."""
        stmt = select(AffectationInterventionModel).where(
            and_(
                AffectationInterventionModel.intervention_id == intervention_id,
                AffectationInterventionModel.est_principal == True,
                AffectationInterventionModel.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._model_to_entity(model)

    async def exists(
        self,
        intervention_id: int,
        utilisateur_id: int,
    ) -> bool:
        """Verifie si une affectation existe."""
        stmt = select(func.count(AffectationInterventionModel.id)).where(
            and_(
                AffectationInterventionModel.intervention_id == intervention_id,
                AffectationInterventionModel.utilisateur_id == utilisateur_id,
                AffectationInterventionModel.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        count = result.scalar() or 0

        return count > 0

    async def delete(
        self, affectation_id: int, deleted_by: int
    ) -> bool:
        """Supprime une affectation (soft delete)."""
        stmt = select(AffectationInterventionModel).where(
            and_(
                AffectationInterventionModel.id == affectation_id,
                AffectationInterventionModel.deleted_at.is_(None),
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

    async def delete_by_intervention(
        self, intervention_id: int, deleted_by: int
    ) -> int:
        """Supprime toutes les affectations d'une intervention."""
        stmt = select(AffectationInterventionModel).where(
            and_(
                AffectationInterventionModel.intervention_id == intervention_id,
                AffectationInterventionModel.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        count = 0
        now = datetime.utcnow()
        for model in models:
            model.deleted_at = now
            model.deleted_by = deleted_by
            count += 1

        await self._session.flush()

        return count

    def _model_to_entity(
        self, model: AffectationInterventionModel
    ) -> AffectationIntervention:
        """Convertit un modele en entite."""
        return AffectationIntervention(
            id=model.id,
            intervention_id=model.intervention_id,
            utilisateur_id=model.utilisateur_id,
            est_principal=model.est_principal,
            commentaire=model.commentaire,
            created_by=model.created_by or 0,
            created_at=model.created_at,
            updated_at=model.updated_at or model.created_at,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )
