"""Implémentation SQLAlchemy du AutorisationRepository."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from ...domain.entities import AutorisationDocument, TypeAutorisation
from ...domain.repositories import AutorisationRepository
from .models import AutorisationDocumentModel


class SQLAlchemyAutorisationRepository(AutorisationRepository):
    """Implémentation SQLAlchemy du repository autorisations."""

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self._session = session

    def find_by_id(self, autorisation_id: int) -> Optional[AutorisationDocument]:
        """Trouve une autorisation par son ID."""
        model = (
            self._session.query(AutorisationDocumentModel)
            .filter_by(id=autorisation_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def save(self, autorisation: AutorisationDocument) -> AutorisationDocument:
        """Persiste une autorisation."""
        if autorisation.id:
            model = (
                self._session.query(AutorisationDocumentModel)
                .filter_by(id=autorisation.id)
                .first()
            )
            if model:
                model.type_autorisation = autorisation.type_autorisation.value
                model.expire_at = autorisation.expire_at
        else:
            model = AutorisationDocumentModel(
                user_id=autorisation.user_id,
                type_autorisation=autorisation.type_autorisation.value,
                dossier_id=autorisation.dossier_id,
                document_id=autorisation.document_id,
                accorde_par=autorisation.accorde_par,
                created_at=autorisation.created_at,
                expire_at=autorisation.expire_at,
            )
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def delete(self, autorisation_id: int) -> bool:
        """Supprime une autorisation."""
        model = (
            self._session.query(AutorisationDocumentModel)
            .filter_by(id=autorisation_id)
            .first()
        )
        if model:
            self._session.delete(model)
            self._session.flush()
            return True
        return False

    def find_by_dossier(self, dossier_id: int) -> List[AutorisationDocument]:
        """Récupère les autorisations d'un dossier."""
        models = (
            self._session.query(AutorisationDocumentModel)
            .filter_by(dossier_id=dossier_id)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_document(self, document_id: int) -> List[AutorisationDocument]:
        """Récupère les autorisations d'un document."""
        models = (
            self._session.query(AutorisationDocumentModel)
            .filter_by(document_id=document_id)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_user(self, user_id: int) -> List[AutorisationDocument]:
        """Récupère les autorisations d'un utilisateur."""
        models = (
            self._session.query(AutorisationDocumentModel)
            .filter_by(user_id=user_id)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_user_ids_for_dossier(self, dossier_id: int) -> List[int]:
        """Récupère les IDs des utilisateurs autorisés sur un dossier."""
        models = (
            self._session.query(AutorisationDocumentModel.user_id)
            .filter_by(dossier_id=dossier_id)
            .filter(
                (AutorisationDocumentModel.expire_at.is_(None))
                | (AutorisationDocumentModel.expire_at > datetime.now())
            )
            .all()
        )
        return [m[0] for m in models]

    def find_user_ids_for_document(self, document_id: int) -> List[int]:
        """Récupère les IDs des utilisateurs autorisés sur un document."""
        models = (
            self._session.query(AutorisationDocumentModel.user_id)
            .filter_by(document_id=document_id)
            .filter(
                (AutorisationDocumentModel.expire_at.is_(None))
                | (AutorisationDocumentModel.expire_at > datetime.now())
            )
            .all()
        )
        return [m[0] for m in models]

    def exists(
        self,
        user_id: int,
        dossier_id: Optional[int] = None,
        document_id: Optional[int] = None,
    ) -> bool:
        """Vérifie si une autorisation existe."""
        query = self._session.query(AutorisationDocumentModel).filter_by(user_id=user_id)

        if dossier_id:
            query = query.filter_by(dossier_id=dossier_id)
        if document_id:
            query = query.filter_by(document_id=document_id)

        return query.first() is not None

    def delete_by_dossier(self, dossier_id: int) -> int:
        """Supprime toutes les autorisations d'un dossier."""
        count = (
            self._session.query(AutorisationDocumentModel)
            .filter_by(dossier_id=dossier_id)
            .delete()
        )
        self._session.flush()
        return count

    def delete_by_document(self, document_id: int) -> int:
        """Supprime toutes les autorisations d'un document."""
        count = (
            self._session.query(AutorisationDocumentModel)
            .filter_by(document_id=document_id)
            .delete()
        )
        self._session.flush()
        return count

    def delete_expired(self) -> int:
        """Supprime les autorisations expirées."""
        count = (
            self._session.query(AutorisationDocumentModel)
            .filter(AutorisationDocumentModel.expire_at < datetime.now())
            .delete()
        )
        self._session.flush()
        return count

    def _to_entity(self, model: AutorisationDocumentModel) -> AutorisationDocument:
        """Convertit un modèle en entité."""
        return AutorisationDocument(
            id=model.id,
            user_id=model.user_id,
            type_autorisation=TypeAutorisation(model.type_autorisation),
            dossier_id=model.dossier_id,
            document_id=model.document_id,
            accorde_par=model.accorde_par,
            created_at=model.created_at,
            expire_at=model.expire_at,
        )
