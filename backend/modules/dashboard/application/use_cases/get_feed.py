"""Use Case GetFeed - Récupération du fil d'actualités."""

from typing import Optional, List

from ...domain.repositories import PostRepository, LikeRepository, CommentRepository
from ..dtos import PostDTO, PostListDTO


class GetFeedUseCase:
    """
    Cas d'utilisation : Récupération du fil d'actualités.

    Selon CDC Section 2:
    - FEED-09: Filtrage automatique (employés voient leurs chantiers)
    - FEED-18: Infinite scroll (20 posts par chargement)
    - FEED-20: Posts archivés toujours consultables

    Attributes:
        post_repo: Repository pour accéder aux posts.
        like_repo: Repository pour compter les likes.
        comment_repo: Repository pour compter les commentaires.
    """

    DEFAULT_LIMIT = 20

    def __init__(
        self,
        post_repo: PostRepository,
        like_repo: Optional[LikeRepository] = None,
        comment_repo: Optional[CommentRepository] = None,
    ):
        """
        Initialise le use case.

        Args:
            post_repo: Repository posts (interface).
            like_repo: Repository likes (interface).
            comment_repo: Repository commentaires (interface).
        """
        self.post_repo = post_repo
        self.like_repo = like_repo
        self.comment_repo = comment_repo

    def execute(
        self,
        user_id: int,
        user_chantier_ids: Optional[List[int]] = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
        include_archived: bool = False,
    ) -> PostListDTO:
        """
        Récupère le fil d'actualités pour un utilisateur.

        Les posts sont filtrés selon le ciblage et triés:
        1. Posts épinglés en premier
        2. Puis par date décroissante

        Args:
            user_id: ID de l'utilisateur.
            user_chantier_ids: IDs des chantiers de l'utilisateur.
            limit: Nombre de posts à retourner.
            offset: Offset pour pagination.
            include_archived: Inclure les posts archivés.

        Returns:
            PostListDTO avec la liste paginée.
        """
        # Récupérer limit+1 posts pour détecter s'il y en a plus
        posts = self.post_repo.find_feed(
            user_id=user_id,
            user_chantier_ids=user_chantier_ids,
            limit=limit + 1,  # +1 pour détecter has_next
            offset=offset,
            include_archived=include_archived,
        )

        # Détecter s'il y a plus de posts (pour infinite scroll)
        has_next = len(posts) > limit
        if has_next:
            posts = posts[:limit]  # Ne retourner que limit posts

        # Convertir en DTOs avec compteurs
        post_dtos = []
        for post in posts:
            likes_count = 0
            comments_count = 0

            if self.like_repo:
                likes_count = self.like_repo.count_by_post(post.id)
            if self.comment_repo:
                comments_count = self.comment_repo.count_by_post(post.id)

            post_dtos.append(
                PostDTO.from_entity(
                    post,
                    likes_count=likes_count,
                    comments_count=comments_count,
                )
            )

        # Total approximatif (has_next est plus fiable pour infinite scroll)
        total = offset + len(posts) + (1 if has_next else 0)

        return PostListDTO(
            posts=post_dtos,
            total=total,
            offset=offset,
            limit=limit,
        )
