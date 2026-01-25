"""Implementation SQLAlchemy du repository SignatureIntervention."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities import SignatureIntervention, TypeSignataire
from ...domain.repositories import SignatureInterventionRepository
from .models import SignatureInterventionModel, AffectationInterventionModel


class SQLAlchemySignatureInterventionRepository(SignatureInterventionRepository):
    """Implementation SQLAlchemy du repository des signatures."""

    def __init__(self, session: AsyncSession):
        """Initialise le repository."""
        self._session = session

    async def save(self, signature: SignatureIntervention) -> SignatureIntervention:
        """Sauvegarde une signature."""
        if signature.id is None:
            model = SignatureInterventionModel(
                intervention_id=signature.intervention_id,
                type_signataire=signature.type_signataire,
                nom_signataire=signature.nom_signataire,
                signature_data=signature.signature_data,
                utilisateur_id=signature.utilisateur_id,
                ip_address=signature.ip_address,
                user_agent=signature.user_agent,
                latitude=str(signature.latitude) if signature.latitude else None,
                longitude=str(signature.longitude) if signature.longitude else None,
                signed_at=signature.signed_at,
            )
            self._session.add(model)
            await self._session.flush()
            signature.id = model.id
        else:
            stmt = select(SignatureInterventionModel).where(
                SignatureInterventionModel.id == signature.id
            )
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                model.nom_signataire = signature.nom_signataire
                model.signature_data = signature.signature_data

                if signature.deleted_at:
                    model.deleted_at = signature.deleted_at
                    model.deleted_by = signature.deleted_by

                await self._session.flush()

        return signature

    async def get_by_id(self, signature_id: int) -> Optional[SignatureIntervention]:
        """Recupere une signature par son ID."""
        stmt = select(SignatureInterventionModel).where(
            SignatureInterventionModel.id == signature_id
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
    ) -> List[SignatureIntervention]:
        """Liste les signatures d'une intervention."""
        stmt = select(SignatureInterventionModel).where(
            SignatureInterventionModel.intervention_id == intervention_id
        )

        if not include_deleted:
            stmt = stmt.where(SignatureInterventionModel.deleted_at.is_(None))

        stmt = stmt.order_by(SignatureInterventionModel.signed_at.asc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(m) for m in models]

    async def get_signature_client(
        self, intervention_id: int
    ) -> Optional[SignatureIntervention]:
        """Recupere la signature client d'une intervention."""
        stmt = select(SignatureInterventionModel).where(
            and_(
                SignatureInterventionModel.intervention_id == intervention_id,
                SignatureInterventionModel.type_signataire == TypeSignataire.CLIENT,
                SignatureInterventionModel.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._model_to_entity(model)

    async def get_signature_technicien(
        self, intervention_id: int, utilisateur_id: int
    ) -> Optional[SignatureIntervention]:
        """Recupere la signature d'un technicien."""
        stmt = select(SignatureInterventionModel).where(
            and_(
                SignatureInterventionModel.intervention_id == intervention_id,
                SignatureInterventionModel.type_signataire == TypeSignataire.TECHNICIEN,
                SignatureInterventionModel.utilisateur_id == utilisateur_id,
                SignatureInterventionModel.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._model_to_entity(model)

    async def has_signature_client(self, intervention_id: int) -> bool:
        """Verifie si l'intervention a une signature client."""
        stmt = select(func.count(SignatureInterventionModel.id)).where(
            and_(
                SignatureInterventionModel.intervention_id == intervention_id,
                SignatureInterventionModel.type_signataire == TypeSignataire.CLIENT,
                SignatureInterventionModel.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        count = result.scalar() or 0

        return count > 0

    async def has_all_signatures_techniciens(
        self, intervention_id: int
    ) -> bool:
        """Verifie si tous les techniciens ont signe."""
        # Compte les techniciens affectes
        affectations_stmt = select(
            func.count(AffectationInterventionModel.id)
        ).where(
            and_(
                AffectationInterventionModel.intervention_id == intervention_id,
                AffectationInterventionModel.deleted_at.is_(None),
            )
        )
        affectations_result = await self._session.execute(affectations_stmt)
        nb_techniciens = affectations_result.scalar() or 0

        if nb_techniciens == 0:
            return True  # Pas de technicien = tous ont signe (trivial)

        # Compte les signatures techniciens
        signatures_stmt = select(
            func.count(SignatureInterventionModel.id)
        ).where(
            and_(
                SignatureInterventionModel.intervention_id == intervention_id,
                SignatureInterventionModel.type_signataire == TypeSignataire.TECHNICIEN,
                SignatureInterventionModel.deleted_at.is_(None),
            )
        )
        signatures_result = await self._session.execute(signatures_stmt)
        nb_signatures = signatures_result.scalar() or 0

        return nb_signatures >= nb_techniciens

    async def delete(self, signature_id: int, deleted_by: int) -> bool:
        """Supprime une signature (soft delete)."""
        stmt = select(SignatureInterventionModel).where(
            and_(
                SignatureInterventionModel.id == signature_id,
                SignatureInterventionModel.deleted_at.is_(None),
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

    def _model_to_entity(
        self, model: SignatureInterventionModel
    ) -> SignatureIntervention:
        """Convertit un modele en entite."""
        return SignatureIntervention(
            id=model.id,
            intervention_id=model.intervention_id,
            type_signataire=model.type_signataire,
            nom_signataire=model.nom_signataire,
            signature_data=model.signature_data,
            utilisateur_id=model.utilisateur_id,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            latitude=float(model.latitude) if model.latitude else None,
            longitude=float(model.longitude) if model.longitude else None,
            signed_at=model.signed_at,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )
