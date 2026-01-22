"""Implémentation SQLAlchemy du LikeRepository."""

from typing import Optional, List

from sqlalchemy.orm import Session

from ...domain.entities import Like
from ...domain.repositories import LikeRepository
from .models import LikeModel


class SQLAlchemyLikeRepository(LikeRepository):
    """
    Implémentation du LikeRepository utilisant SQLAlchemy.
    """

    def __init__(self, session: Session):
        self.session = session

    def save(self, like: Like) -> Like:
        """Persiste un like."""
        model = self._to_model(like)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, like_id: int) -> Optional[Like]:
        """Trouve un like par son ID."""
        model = (
            self.session.query(LikeModel)
            .filter(LikeModel.id == like_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_post_and_user(
        self,
        post_id: int,
        user_id: int,
    ) -> Optional[Like]:
        """Trouve un like par post et utilisateur."""
        model = (
            self.session.query(LikeModel)
            .filter(LikeModel.post_id == post_id)
            .filter(LikeModel.user_id == user_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_post(self, post_id: int) -> List[Like]:
        """Récupère tous les likes d'un post."""
        models = (
            self.session.query(LikeModel)
            .filter(LikeModel.post_id == post_id)
            .order_by(LikeModel.created_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_user_ids_by_post(self, post_id: int) -> List[int]:
        """Récupère les IDs des utilisateurs ayant liké un post."""
        results = (
            self.session.query(LikeModel.user_id)
            .filter(LikeModel.post_id == post_id)
            .all()
        )
        return [r[0] for r in results]

    def count_by_post(self, post_id: int) -> int:
        """Compte les likes d'un post."""
        return (
            self.session.query(LikeModel)
            .filter(LikeModel.post_id == post_id)
            .count()
        )

    def delete(self, like_id: int) -> bool:
        """Supprime un like."""
        model = (
            self.session.query(LikeModel)
            .filter(LikeModel.id == like_id)
            .first()
        )
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def delete_by_post_and_user(self, post_id: int, user_id: int) -> bool:
        """Supprime un like par post et utilisateur."""
        model = (
            self.session.query(LikeModel)
            .filter(LikeModel.post_id == post_id)
            .filter(LikeModel.user_id == user_id)
            .first()
        )
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def _to_entity(self, model: LikeModel) -> Like:
        """Convertit un modèle en entité."""
        return Like(
            id=model.id,
            post_id=model.post_id,
            user_id=model.user_id,
            created_at=model.created_at,
        )

    def _to_model(self, like: Like) -> LikeModel:
        """Convertit une entité en modèle."""
        return LikeModel(
            id=like.id,
            post_id=like.post_id,
            user_id=like.user_id,
            created_at=like.created_at,
        )
