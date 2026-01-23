"""Implémentation SQLAlchemy du repository Reponse."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import ReponseModel
from ...domain.entities import Reponse
from ...domain.repositories import ReponseRepository


class SQLAlchemyReponseRepository(ReponseRepository):
    """Implémentation SQLAlchemy du repository Reponse."""

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self._session = session

    def find_by_id(self, reponse_id: int) -> Optional[Reponse]:
        """Trouve une réponse par son ID."""
        model = self._session.query(ReponseModel).filter(
            ReponseModel.id == reponse_id
        ).first()

        if not model:
            return None

        return self._to_entity(model)

    def save(self, reponse: Reponse) -> Reponse:
        """Persiste une réponse."""
        if reponse.id is None:
            # Création
            model = ReponseModel(
                signalement_id=reponse.signalement_id,
                contenu=reponse.contenu,
                auteur_id=reponse.auteur_id,
                photo_url=reponse.photo_url,
                est_resolution=reponse.est_resolution,
                created_at=reponse.created_at,
                updated_at=reponse.updated_at,
            )
            self._session.add(model)
            self._session.flush()
            reponse.id = model.id
        else:
            # Mise à jour
            model = self._session.query(ReponseModel).filter(
                ReponseModel.id == reponse.id
            ).first()

            if model:
                model.contenu = reponse.contenu
                model.photo_url = reponse.photo_url
                model.est_resolution = reponse.est_resolution
                model.updated_at = datetime.now()
                self._session.flush()

        return reponse

    def delete(self, reponse_id: int) -> bool:
        """Supprime une réponse."""
        result = self._session.query(ReponseModel).filter(
            ReponseModel.id == reponse_id
        ).delete()
        self._session.flush()
        return result > 0

    def find_by_signalement(
        self,
        signalement_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Reponse]:
        """Récupère les réponses d'un signalement."""
        models = self._session.query(ReponseModel).filter(
            ReponseModel.signalement_id == signalement_id
        ).order_by(
            ReponseModel.created_at.asc()
        ).offset(skip).limit(limit).all()

        return [self._to_entity(m) for m in models]

    def find_by_auteur(
        self,
        auteur_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Reponse]:
        """Récupère les réponses d'un auteur."""
        models = self._session.query(ReponseModel).filter(
            ReponseModel.auteur_id == auteur_id
        ).order_by(
            ReponseModel.created_at.desc()
        ).offset(skip).limit(limit).all()

        return [self._to_entity(m) for m in models]

    def count_by_signalement(self, signalement_id: int) -> int:
        """Compte le nombre de réponses d'un signalement."""
        return self._session.query(func.count(ReponseModel.id)).filter(
            ReponseModel.signalement_id == signalement_id
        ).scalar() or 0

    def find_resolution(self, signalement_id: int) -> Optional[Reponse]:
        """Trouve la réponse marquée comme résolution."""
        model = self._session.query(ReponseModel).filter(
            ReponseModel.signalement_id == signalement_id,
            ReponseModel.est_resolution == True
        ).first()

        if not model:
            return None

        return self._to_entity(model)

    def delete_by_signalement(self, signalement_id: int) -> int:
        """Supprime toutes les réponses d'un signalement."""
        result = self._session.query(ReponseModel).filter(
            ReponseModel.signalement_id == signalement_id
        ).delete()
        self._session.flush()
        return result

    def _to_entity(self, model: ReponseModel) -> Reponse:
        """Convertit un modèle SQLAlchemy en entité de domaine."""
        return Reponse(
            id=model.id,
            signalement_id=model.signalement_id,
            contenu=model.contenu,
            auteur_id=model.auteur_id,
            photo_url=model.photo_url,
            est_resolution=model.est_resolution,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
