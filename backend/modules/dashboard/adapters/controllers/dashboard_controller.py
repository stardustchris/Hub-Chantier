"""Controller pour le module Dashboard.

Ce controller encapsule les operations du feed d'actualites
et fait le lien entre la couche web et les use cases.

Note: Pour l'instant, les routes appellent directement les use cases via dependencies.
Ce controller est mis en place pour aligner la structure avec les autres modules
et permettre une migration progressive.
"""

from typing import Optional, List
from dataclasses import dataclass

from ...domain.repositories import PostRepository, LikeRepository, CommentRepository, PostMediaRepository
from ...application.use_cases import (
    PublishPostUseCase,
    GetFeedUseCase,
    GetPostUseCase,
    DeletePostUseCase,
    PinPostUseCase,
    AddCommentUseCase,
    AddLikeUseCase,
    RemoveLikeUseCase,
)
from ...application.dtos import CreatePostDTO, CreateCommentDTO, PostDTO


@dataclass
class DashboardController:
    """
    Controller pour les operations du dashboard/feed.

    Encapsule les use cases et fournit une interface simplifiee
    pour les routes FastAPI.

    Attributes:
        post_repo: Repository pour les posts.
        like_repo: Repository pour les likes.
        comment_repo: Repository pour les commentaires.
        media_repo: Repository pour les medias.
    """

    post_repo: PostRepository
    like_repo: LikeRepository
    comment_repo: CommentRepository
    media_repo: PostMediaRepository

    def get_feed(
        self,
        user_id: int,
        user_chantier_ids: Optional[List[int]] = None,
        limit: int = 20,
        offset: int = 0,
        include_archived: bool = False,
    ) -> dict:
        """
        Recupere le fil d'actualites pour un utilisateur.

        Args:
            user_id: ID de l'utilisateur.
            user_chantier_ids: IDs des chantiers de l'utilisateur (None = tous).
            limit: Nombre max de posts.
            offset: Offset pour pagination.
            include_archived: Inclure les posts archives.

        Returns:
            Dict avec posts, total et metadata pagination.
        """
        use_case = GetFeedUseCase(
            post_repo=self.post_repo,
            media_repo=self.media_repo,
            like_repo=self.like_repo,
        )
        return use_case.execute(
            user_id=user_id,
            user_chantier_ids=user_chantier_ids,
            limit=limit,
            offset=offset,
            include_archived=include_archived,
        )

    def create_post(
        self,
        content: str,
        author_id: int,
        target_type: str = "everyone",
        chantier_ids: Optional[List[int]] = None,
        user_ids: Optional[List[int]] = None,
        is_urgent: bool = False,
    ) -> PostDTO:
        """
        Cree un nouveau post.

        Args:
            content: Contenu du post.
            author_id: ID de l'auteur.
            target_type: Type de ciblage (everyone, specific_chantiers, specific_people).
            chantier_ids: IDs des chantiers cibles.
            user_ids: IDs des utilisateurs cibles.
            is_urgent: Post urgent.

        Returns:
            PostDTO du post cree.
        """
        use_case = PublishPostUseCase(
            post_repo=self.post_repo,
            media_repo=self.media_repo,
        )
        dto = CreatePostDTO(
            content=content,
            target_type=target_type,
            chantier_ids=chantier_ids,
            user_ids=user_ids,
            is_urgent=is_urgent,
        )
        return use_case.execute(dto, author_id=author_id)

    def get_post(self, post_id: int, user_id: int) -> dict:
        """
        Recupere un post avec ses details.

        Args:
            post_id: ID du post.
            user_id: ID de l'utilisateur demandeur.

        Returns:
            Dict avec post, medias, comments, likes.
        """
        use_case = GetPostUseCase(
            post_repo=self.post_repo,
            media_repo=self.media_repo,
            comment_repo=self.comment_repo,
            like_repo=self.like_repo,
        )
        return use_case.execute(post_id=post_id, user_id=user_id)

    def delete_post(self, post_id: int, user_id: int, is_moderator: bool = False) -> bool:
        """
        Supprime un post.

        Args:
            post_id: ID du post.
            user_id: ID de l'utilisateur.
            is_moderator: L'utilisateur est-il moderateur.

        Returns:
            True si supprime.
        """
        use_case = DeletePostUseCase(post_repo=self.post_repo)
        use_case.execute(post_id=post_id, user_id=user_id, is_moderator=is_moderator)
        return True

    def add_comment(self, post_id: int, content: str, author_id: int) -> dict:
        """
        Ajoute un commentaire sur un post.

        Args:
            post_id: ID du post.
            content: Contenu du commentaire.
            author_id: ID de l'auteur.

        Returns:
            CommentDTO du commentaire cree.
        """
        use_case = AddCommentUseCase(
            post_repo=self.post_repo,
            comment_repo=self.comment_repo,
        )
        dto = CreateCommentDTO(post_id=post_id, content=content)
        return use_case.execute(dto, author_id=author_id)

    def add_like(self, post_id: int, user_id: int) -> bool:
        """
        Ajoute un like sur un post.

        Args:
            post_id: ID du post.
            user_id: ID de l'utilisateur.

        Returns:
            True si ajoute.
        """
        use_case = AddLikeUseCase(
            post_repo=self.post_repo,
            like_repo=self.like_repo,
        )
        use_case.execute(post_id=post_id, user_id=user_id)
        return True

    def remove_like(self, post_id: int, user_id: int) -> bool:
        """
        Retire un like d'un post.

        Args:
            post_id: ID du post.
            user_id: ID de l'utilisateur.

        Returns:
            True si retire.
        """
        use_case = RemoveLikeUseCase(like_repo=self.like_repo)
        use_case.execute(post_id=post_id, user_id=user_id)
        return True
