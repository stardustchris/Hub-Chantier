"""Implémentation SQLAlchemy du CommentRepository."""

from typing import Optional, List

from sqlalchemy.orm import Session

from ...domain.entities import Comment
from ...domain.repositories import CommentRepository
from .models import CommentModel


class SQLAlchemyCommentRepository(CommentRepository):
    """
    Implémentation du CommentRepository utilisant SQLAlchemy.
    """

    def __init__(self, session: Session):
        self.session = session

    def save(self, comment: Comment) -> Comment:
        """Persiste un commentaire."""
        if comment.id:
            # Update
            model = (
                self.session.query(CommentModel)
                .filter(CommentModel.id == comment.id)
                .first()
            )
            if model:
                model.content = comment.content
                model.is_deleted = comment.is_deleted
                model.updated_at = comment.updated_at
        else:
            # Create
            model = self._to_model(comment)
            self.session.add(model)

        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, comment_id: int) -> Optional[Comment]:
        """Trouve un commentaire par son ID."""
        model = (
            self.session.query(CommentModel)
            .filter(CommentModel.id == comment_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_post(
        self,
        post_id: int,
        include_deleted: bool = False,
    ) -> List[Comment]:
        """Récupère les commentaires d'un post."""
        query = self.session.query(CommentModel).filter(
            CommentModel.post_id == post_id
        )

        if not include_deleted:
            query = query.filter(CommentModel.is_deleted == False)

        query = query.order_by(CommentModel.created_at.asc())

        models = query.all()
        return [self._to_entity(m) for m in models]

    def find_by_author(self, author_id: int) -> List[Comment]:
        """Récupère les commentaires d'un auteur."""
        models = (
            self.session.query(CommentModel)
            .filter(CommentModel.author_id == author_id)
            .filter(CommentModel.is_deleted == False)
            .order_by(CommentModel.created_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def count_by_post(self, post_id: int) -> int:
        """Compte les commentaires d'un post."""
        return (
            self.session.query(CommentModel)
            .filter(CommentModel.post_id == post_id)
            .filter(CommentModel.is_deleted == False)
            .count()
        )

    def delete(self, comment_id: int) -> bool:
        """Supprime physiquement un commentaire."""
        model = (
            self.session.query(CommentModel)
            .filter(CommentModel.id == comment_id)
            .first()
        )
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def _to_entity(self, model: CommentModel) -> Comment:
        """Convertit un modèle en entité."""
        return Comment(
            id=model.id,
            post_id=model.post_id,
            author_id=model.author_id,
            content=model.content,
            is_deleted=model.is_deleted,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, comment: Comment) -> CommentModel:
        """Convertit une entité en modèle."""
        return CommentModel(
            id=comment.id,
            post_id=comment.post_id,
            author_id=comment.author_id,
            content=comment.content,
            is_deleted=comment.is_deleted,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )
