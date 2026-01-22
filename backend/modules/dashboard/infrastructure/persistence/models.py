"""Modèles SQLAlchemy pour le module Dashboard."""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

from ...domain.value_objects import PostStatus, TargetType
from ...domain.entities.post_media import MediaType

Base = declarative_base()


class PostModel(Base):
    """
    Modèle SQLAlchemy pour les posts.

    Selon CDC Section 2 - Tableau de Bord (FEED-01 à FEED-20).
    """

    __tablename__ = "posts"

    # Identifiant
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Auteur (référence vers users)
    author_id = Column(Integer, nullable=False, index=True)

    # Contenu
    content = Column(Text, nullable=False)  # FEED-01, FEED-10, FEED-11

    # Statut
    status = Column(
        String(20), nullable=False, default=PostStatus.PUBLISHED.value
    )  # FEED-08, FEED-16, FEED-20

    # Urgence et épinglage (FEED-08)
    is_urgent = Column(Boolean, nullable=False, default=False)
    pinned_until = Column(DateTime, nullable=True)

    # Ciblage (FEED-03)
    target_type = Column(
        String(30), nullable=False, default=TargetType.EVERYONE.value
    )
    # JSON serait mieux mais pour compatibilité SQLite, on utilise des strings séparées par virgules
    target_chantier_ids = Column(String(500), nullable=True)  # "1,2,3"
    target_user_ids = Column(String(500), nullable=True)  # "1,2,3"

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now, index=True)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )
    archived_at = Column(DateTime, nullable=True)  # FEED-20

    # Relations
    comments = relationship("CommentModel", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("LikeModel", back_populates="post", cascade="all, delete-orphan")
    medias = relationship("PostMediaModel", back_populates="post", cascade="all, delete-orphan")

    # Index pour la recherche du feed
    __table_args__ = (
        Index("ix_posts_feed", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<PostModel(id={self.id}, author_id={self.author_id}, status={self.status})>"


class CommentModel(Base):
    """
    Modèle SQLAlchemy pour les commentaires.

    Selon CDC Section 2 - FEED-05.
    """

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    author_id = Column(Integer, nullable=False, index=True)
    content = Column(Text, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    # Relations
    post = relationship("PostModel", back_populates="comments")

    def __repr__(self) -> str:
        return f"<CommentModel(id={self.id}, post_id={self.post_id})>"


class LikeModel(Base):
    """
    Modèle SQLAlchemy pour les likes.

    Selon CDC Section 2 - FEED-04.
    """

    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    # Relations
    post = relationship("PostModel", back_populates="likes")

    # Contrainte d'unicité: un user ne peut liker qu'une fois par post
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_like_post_user"),
    )

    def __repr__(self) -> str:
        return f"<LikeModel(id={self.id}, post_id={self.post_id}, user_id={self.user_id})>"


class PostMediaModel(Base):
    """
    Modèle SQLAlchemy pour les médias de posts.

    Selon CDC Section 2 - FEED-02, FEED-13, FEED-19.
    """

    __tablename__ = "post_medias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    media_type = Column(String(20), nullable=False, default=MediaType.IMAGE.value)
    file_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)  # FEED-13
    original_filename = Column(String(255), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)  # FEED-19
    mime_type = Column(String(100), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    position = Column(Integer, nullable=False, default=0)  # Ordre dans la galerie
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    # Relations
    post = relationship("PostModel", back_populates="medias")

    def __repr__(self) -> str:
        return f"<PostMediaModel(id={self.id}, post_id={self.post_id})>"
