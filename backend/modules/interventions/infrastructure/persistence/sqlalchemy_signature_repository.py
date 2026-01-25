"""Implementation SQLAlchemy du repository SignatureIntervention."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from ...domain.entities import SignatureIntervention, TypeSignataire
from ...domain.repositories import SignatureInterventionRepository
from .models import SignatureInterventionModel, AffectationInterventionModel


class SQLAlchemySignatureInterventionRepository(SignatureInterventionRepository):
    """Implementation SQLAlchemy du repository des signatures."""

    def __init__(self, session: Session):
        """Initialise le repository."""
        self._session = session

    def save(self, signature: SignatureIntervention) -> SignatureIntervention:
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
            self._session.flush()
            signature.id = model.id
        else:
            model = self._session.query(SignatureInterventionModel).filter(
                SignatureInterventionModel.id == signature.id
            ).first()

            if model:
                model.nom_signataire = signature.nom_signataire
                model.signature_data = signature.signature_data

                if signature.deleted_at:
                    model.deleted_at = signature.deleted_at
                    model.deleted_by = signature.deleted_by

                self._session.flush()

        return signature

    def get_by_id(self, signature_id: int) -> Optional[SignatureIntervention]:
        """Recupere une signature par son ID."""
        model = self._session.query(SignatureInterventionModel).filter(
            SignatureInterventionModel.id == signature_id
        ).first()

        if not model:
            return None

        return self._model_to_entity(model)

    def list_by_intervention(
        self,
        intervention_id: int,
        include_deleted: bool = False,
    ) -> List[SignatureIntervention]:
        """Liste les signatures d'une intervention."""
        query = self._session.query(SignatureInterventionModel).filter(
            SignatureInterventionModel.intervention_id == intervention_id
        )

        if not include_deleted:
            query = query.filter(SignatureInterventionModel.deleted_at.is_(None))

        query = query.order_by(SignatureInterventionModel.signed_at.asc())

        models = query.all()

        return [self._model_to_entity(m) for m in models]

    def get_signature_client(
        self, intervention_id: int
    ) -> Optional[SignatureIntervention]:
        """Recupere la signature client d'une intervention."""
        model = self._session.query(SignatureInterventionModel).filter(
            and_(
                SignatureInterventionModel.intervention_id == intervention_id,
                SignatureInterventionModel.type_signataire == TypeSignataire.CLIENT,
                SignatureInterventionModel.deleted_at.is_(None),
            )
        ).first()

        if not model:
            return None

        return self._model_to_entity(model)

    def get_signature_technicien(
        self, intervention_id: int, utilisateur_id: int
    ) -> Optional[SignatureIntervention]:
        """Recupere la signature d'un technicien."""
        model = self._session.query(SignatureInterventionModel).filter(
            and_(
                SignatureInterventionModel.intervention_id == intervention_id,
                SignatureInterventionModel.type_signataire == TypeSignataire.TECHNICIEN,
                SignatureInterventionModel.utilisateur_id == utilisateur_id,
                SignatureInterventionModel.deleted_at.is_(None),
            )
        ).first()

        if not model:
            return None

        return self._model_to_entity(model)

    def has_signature_client(self, intervention_id: int) -> bool:
        """Verifie si l'intervention a une signature client."""
        count = self._session.query(func.count(SignatureInterventionModel.id)).filter(
            and_(
                SignatureInterventionModel.intervention_id == intervention_id,
                SignatureInterventionModel.type_signataire == TypeSignataire.CLIENT,
                SignatureInterventionModel.deleted_at.is_(None),
            )
        ).scalar() or 0

        return count > 0

    def has_all_signatures_techniciens(
        self, intervention_id: int
    ) -> bool:
        """Verifie si tous les techniciens ont signe."""
        # Compte les techniciens affectes
        nb_techniciens = self._session.query(
            func.count(AffectationInterventionModel.id)
        ).filter(
            and_(
                AffectationInterventionModel.intervention_id == intervention_id,
                AffectationInterventionModel.deleted_at.is_(None),
            )
        ).scalar() or 0

        if nb_techniciens == 0:
            return True  # Pas de technicien = tous ont signe (trivial)

        # Compte les signatures techniciens
        nb_signatures = self._session.query(
            func.count(SignatureInterventionModel.id)
        ).filter(
            and_(
                SignatureInterventionModel.intervention_id == intervention_id,
                SignatureInterventionModel.type_signataire == TypeSignataire.TECHNICIEN,
                SignatureInterventionModel.deleted_at.is_(None),
            )
        ).scalar() or 0

        return nb_signatures >= nb_techniciens

    def delete(self, signature_id: int, deleted_by: int) -> bool:
        """Supprime une signature (soft delete)."""
        model = self._session.query(SignatureInterventionModel).filter(
            and_(
                SignatureInterventionModel.id == signature_id,
                SignatureInterventionModel.deleted_at.is_(None),
            )
        ).first()

        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        self._session.flush()

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
