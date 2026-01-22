"""Implémentation SQLAlchemy du PostMediaRepository."""

from typing import Optional, List

from sqlalchemy.orm import Session

from ...domain.entities import PostMedia
from ...domain.entities.post_media import MediaType
from ...domain.repositories import PostMediaRepository
from .models import PostMediaModel


class SQLAlchemyPostMediaRepository(PostMediaRepository):
    """
    Implémentation du PostMediaRepository utilisant SQLAlchemy.
    """

    def __init__(self, session: Session):
        self.session = session

    def save(self, media: PostMedia) -> PostMedia:
        """Persiste un média."""
        model = self._to_model(media)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def save_all(self, medias: List[PostMedia]) -> List[PostMedia]:
        """Persiste plusieurs médias."""
        models = [self._to_model(m) for m in medias]
        self.session.add_all(models)
        self.session.commit()
        for model in models:
            self.session.refresh(model)
        return [self._to_entity(m) for m in models]

    def find_by_id(self, media_id: int) -> Optional[PostMedia]:
        """Trouve un média par son ID."""
        model = (
            self.session.query(PostMediaModel)
            .filter(PostMediaModel.id == media_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_post(self, post_id: int) -> List[PostMedia]:
        """Récupère les médias d'un post ordonnés par position."""
        models = (
            self.session.query(PostMediaModel)
            .filter(PostMediaModel.post_id == post_id)
            .order_by(PostMediaModel.position.asc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def count_by_post(self, post_id: int) -> int:
        """Compte les médias d'un post."""
        return (
            self.session.query(PostMediaModel)
            .filter(PostMediaModel.post_id == post_id)
            .count()
        )

    def delete(self, media_id: int) -> bool:
        """Supprime un média."""
        model = (
            self.session.query(PostMediaModel)
            .filter(PostMediaModel.id == media_id)
            .first()
        )
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def delete_by_post(self, post_id: int) -> int:
        """Supprime tous les médias d'un post."""
        count = (
            self.session.query(PostMediaModel)
            .filter(PostMediaModel.post_id == post_id)
            .delete()
        )
        self.session.commit()
        return count

    def _to_entity(self, model: PostMediaModel) -> PostMedia:
        """Convertit un modèle en entité."""
        return PostMedia(
            id=model.id,
            post_id=model.post_id,
            media_type=MediaType(model.media_type),
            file_url=model.file_url,
            thumbnail_url=model.thumbnail_url,
            original_filename=model.original_filename,
            file_size_bytes=model.file_size_bytes,
            mime_type=model.mime_type,
            width=model.width,
            height=model.height,
            position=model.position,
            created_at=model.created_at,
        )

    def _to_model(self, media: PostMedia) -> PostMediaModel:
        """Convertit une entité en modèle."""
        return PostMediaModel(
            id=media.id,
            post_id=media.post_id,
            media_type=media.media_type.value,
            file_url=media.file_url,
            thumbnail_url=media.thumbnail_url,
            original_filename=media.original_filename,
            file_size_bytes=media.file_size_bytes,
            mime_type=media.mime_type,
            width=media.width,
            height=media.height,
            position=media.position,
            created_at=media.created_at,
        )
