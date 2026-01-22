"""Use Case GetPost - Récupération d'un post avec ses détails."""

from typing import Optional, List

from ...domain.repositories import (
    PostRepository,
    LikeRepository,
    CommentRepository,
    PostMediaRepository,
)
from ..dtos import PostDTO, PostDetailDTO, CommentDTO, MediaDTO


class PostNotFoundError(Exception):
    """Exception levée quand un post n'est pas trouvé."""

    def __init__(self, post_id: int):
        self.post_id = post_id
        self.message = f"Post {post_id} non trouvé"
        super().__init__(self.message)


class GetPostUseCase:
    """
    Cas d'utilisation : Récupération d'un post avec ses détails.

    Retourne le post avec ses médias, commentaires et likes.
    """

    def __init__(
        self,
        post_repo: PostRepository,
        like_repo: Optional[LikeRepository] = None,
        comment_repo: Optional[CommentRepository] = None,
        media_repo: Optional[PostMediaRepository] = None,
    ):
        """
        Initialise le use case.

        Args:
            post_repo: Repository posts (interface).
            like_repo: Repository likes (interface).
            comment_repo: Repository commentaires (interface).
            media_repo: Repository médias (interface).
        """
        self.post_repo = post_repo
        self.like_repo = like_repo
        self.comment_repo = comment_repo
        self.media_repo = media_repo

    def execute(self, post_id: int, user_id: int) -> PostDetailDTO:
        """
        Récupère un post avec tous ses détails.

        Args:
            post_id: ID du post.
            user_id: ID de l'utilisateur qui consulte.

        Returns:
            PostDetailDTO avec toutes les données.

        Raises:
            PostNotFoundError: Si le post n'existe pas.
        """
        # Récupérer le post
        post = self.post_repo.find_by_id(post_id)
        if not post:
            raise PostNotFoundError(post_id)

        # Compter likes et commentaires
        likes_count = 0
        comments_count = 0
        medias_count = 0

        if self.like_repo:
            likes_count = self.like_repo.count_by_post(post_id)
        if self.comment_repo:
            comments_count = self.comment_repo.count_by_post(post_id)
        if self.media_repo:
            medias_count = self.media_repo.count_by_post(post_id)

        # Créer le DTO de base
        post_dto = PostDTO.from_entity(
            post,
            likes_count=likes_count,
            comments_count=comments_count,
            medias_count=medias_count,
        )

        # Récupérer les médias
        medias = []
        if self.media_repo:
            media_entities = self.media_repo.find_by_post(post_id)
            medias = [MediaDTO.from_entity(m) for m in media_entities]

        # Récupérer les commentaires
        comments = []
        if self.comment_repo:
            comment_entities = self.comment_repo.find_by_post(post_id)
            comments = [CommentDTO.from_entity(c) for c in comment_entities]

        # Récupérer les IDs des utilisateurs ayant liké
        liked_by_user_ids = []
        if self.like_repo:
            liked_by_user_ids = self.like_repo.find_user_ids_by_post(post_id)

        return PostDetailDTO(
            post=post_dto,
            medias=medias,
            comments=comments,
            liked_by_user_ids=liked_by_user_ids,
        )
