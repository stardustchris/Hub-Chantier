"""Implementation SQLAlchemy du repository AffectationIntervention."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from ...domain.entities import AffectationIntervention
from ...domain.repositories import AffectationInterventionRepository
from .models import AffectationInterventionModel


class SQLAlchemyAffectationInterventionRepository(AffectationInterventionRepository):
    """Implementation SQLAlchemy du repository des affectations."""

    def __init__(self, session: Session):
        """Initialise le repository."""
        self._session = session

    def save(
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
            self._session.flush()
            affectation.id = model.id
        else:
            model = self._session.query(AffectationInterventionModel).filter(
                AffectationInterventionModel.id == affectation.id
            ).first()

            if model:
                model.est_principal = affectation.est_principal
                model.commentaire = affectation.commentaire
                model.updated_at = datetime.utcnow()

                if affectation.deleted_at:
                    model.deleted_at = affectation.deleted_at
                    model.deleted_by = affectation.deleted_by

                self._session.flush()

        return affectation

    def get_by_id(
        self, affectation_id: int
    ) -> Optional[AffectationIntervention]:
        """Recupere une affectation par son ID."""
        model = self._session.query(AffectationInterventionModel).filter(
            AffectationInterventionModel.id == affectation_id
        ).first()

        if not model:
            return None

        return self._model_to_entity(model)

    def list_by_intervention(
        self,
        intervention_id: int,
        include_deleted: bool = False,
    ) -> List[AffectationIntervention]:
        """Liste les affectations d'une intervention."""
        query = self._session.query(AffectationInterventionModel).filter(
            AffectationInterventionModel.intervention_id == intervention_id
        )

        if not include_deleted:
            query = query.filter(AffectationInterventionModel.deleted_at.is_(None))

        query = query.order_by(
            AffectationInterventionModel.est_principal.desc(),
            AffectationInterventionModel.created_at.asc(),
        )

        models = query.all()

        return [self._model_to_entity(m) for m in models]

    def list_by_utilisateur(
        self,
        utilisateur_id: int,
        include_deleted: bool = False,
    ) -> List[AffectationIntervention]:
        """Liste les affectations d'un utilisateur."""
        query = self._session.query(AffectationInterventionModel).filter(
            AffectationInterventionModel.utilisateur_id == utilisateur_id
        )

        if not include_deleted:
            query = query.filter(AffectationInterventionModel.deleted_at.is_(None))

        query = query.order_by(AffectationInterventionModel.created_at.desc())

        models = query.all()

        return [self._model_to_entity(m) for m in models]

    def get_principal(
        self, intervention_id: int
    ) -> Optional[AffectationIntervention]:
        """Recupere le technicien principal d'une intervention."""
        model = self._session.query(AffectationInterventionModel).filter(
            and_(
                AffectationInterventionModel.intervention_id == intervention_id,
                AffectationInterventionModel.est_principal == True,
                AffectationInterventionModel.deleted_at.is_(None),
            )
        ).first()

        if not model:
            return None

        return self._model_to_entity(model)

    def exists(
        self,
        intervention_id: int,
        utilisateur_id: int,
    ) -> bool:
        """Verifie si une affectation existe."""
        count = self._session.query(func.count(AffectationInterventionModel.id)).filter(
            and_(
                AffectationInterventionModel.intervention_id == intervention_id,
                AffectationInterventionModel.utilisateur_id == utilisateur_id,
                AffectationInterventionModel.deleted_at.is_(None),
            )
        ).scalar() or 0

        return count > 0

    def delete(
        self, affectation_id: int, deleted_by: int
    ) -> bool:
        """Supprime une affectation (soft delete)."""
        model = self._session.query(AffectationInterventionModel).filter(
            and_(
                AffectationInterventionModel.id == affectation_id,
                AffectationInterventionModel.deleted_at.is_(None),
            )
        ).first()

        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        self._session.flush()

        return True

    def delete_by_intervention(
        self, intervention_id: int, deleted_by: int
    ) -> int:
        """Supprime toutes les affectations d'une intervention."""
        models = self._session.query(AffectationInterventionModel).filter(
            and_(
                AffectationInterventionModel.intervention_id == intervention_id,
                AffectationInterventionModel.deleted_at.is_(None),
            )
        ).all()

        count = 0
        now = datetime.utcnow()
        for model in models:
            model.deleted_at = now
            model.deleted_by = deleted_by
            count += 1

        self._session.flush()

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
