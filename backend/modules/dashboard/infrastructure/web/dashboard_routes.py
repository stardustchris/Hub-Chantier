"""Routes FastAPI pour le module Dashboard (Fil d'actualités)."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ...application.use_cases import (
    PublishPostUseCase,
    GetFeedUseCase,
    GetPostUseCase,
    DeletePostUseCase,
    PinPostUseCase,
    AddCommentUseCase,
    AddLikeUseCase,
    RemoveLikeUseCase,
    PostContentEmptyError,
    PostNotFoundError,
    NotAuthorizedError,
    AlreadyLikedError,
)
from ...application.use_cases.add_comment import CommentContentEmptyError
from ...application.use_cases.remove_like import LikeNotFoundError
from ...application.dtos import CreatePostDTO, CreateCommentDTO
from .dependencies import (
    get_publish_post_use_case,
    get_feed_use_case,
    get_post_use_case,
    get_delete_post_use_case,
    get_pin_post_use_case,
    get_add_comment_use_case,
    get_add_like_use_case,
    get_remove_like_use_case,
)
from modules.auth.infrastructure.web.dependencies import get_current_user_id


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# =============================================================================
# Pydantic models for request/response validation
# Selon CDC Section 2 - Tableau de Bord (FEED-01 à FEED-20)
# =============================================================================


class CreatePostRequest(BaseModel):
    """Requête de création de post (FEED-01, FEED-03)."""

    content: str
    target_type: str = "everyone"  # everyone, specific_chantiers, specific_people
    chantier_ids: Optional[List[int]] = None
    user_ids: Optional[List[int]] = None
    is_urgent: bool = False


class PostResponse(BaseModel):
    """Réponse post."""

    id: int
    author_id: int
    content: str
    status: str
    is_urgent: bool
    is_pinned: bool
    target_type: str
    target_display: str
    chantier_ids: Optional[List[int]]
    user_ids: Optional[List[int]]
    created_at: datetime
    likes_count: int
    comments_count: int
    medias_count: int


class PostListResponse(BaseModel):
    """Réponse liste de posts paginée (FEED-18)."""

    posts: List[PostResponse]
    total: int
    offset: int
    limit: int
    has_next: bool
    has_previous: bool


class MediaResponse(BaseModel):
    """Réponse média."""

    id: int
    post_id: int
    media_type: str
    file_url: str
    thumbnail_url: Optional[str]
    original_filename: Optional[str]
    width: Optional[int]
    height: Optional[int]
    position: int


class CommentResponse(BaseModel):
    """Réponse commentaire (FEED-05)."""

    id: int
    post_id: int
    author_id: int
    content: str
    created_at: datetime


class CreateCommentRequest(BaseModel):
    """Requête de création de commentaire."""

    content: str


class PostDetailResponse(BaseModel):
    """Réponse détail post avec médias, commentaires, likes."""

    post: PostResponse
    medias: List[MediaResponse]
    comments: List[CommentResponse]
    liked_by_user_ids: List[int]


class LikeResponse(BaseModel):
    """Réponse like (FEED-04)."""

    id: int
    post_id: int
    user_id: int
    created_at: datetime


# =============================================================================
# Routes Posts
# =============================================================================


@router.get("/feed", response_model=PostListResponse)
def get_feed(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    include_archived: bool = Query(default=False),
    chantier_ids: Optional[str] = Query(default=None, description="IDs chantiers séparés par virgule"),
    current_user_id: int = Depends(get_current_user_id),
    use_case: GetFeedUseCase = Depends(get_feed_use_case),
):
    """
    Récupère le fil d'actualités de l'utilisateur (FEED-09, FEED-18).

    Les posts sont filtrés selon le ciblage et triés par date décroissante.
    Les posts épinglés apparaissent en premier.
    """
    # Parser les IDs de chantiers
    user_chantier_ids = None
    if chantier_ids:
        user_chantier_ids = [int(id.strip()) for id in chantier_ids.split(",") if id.strip()]

    result = use_case.execute(
        user_id=current_user_id,
        user_chantier_ids=user_chantier_ids,
        limit=limit,
        offset=offset,
        include_archived=include_archived,
    )

    return PostListResponse(
        posts=[_post_dto_to_response(p) for p in result.posts],
        total=result.total,
        offset=result.offset,
        limit=result.limit,
        has_next=result.has_next,
        has_previous=result.has_previous,
    )


@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    request: CreatePostRequest,
    current_user_id: int = Depends(get_current_user_id),
    use_case: PublishPostUseCase = Depends(get_publish_post_use_case),
):
    """
    Publie un nouveau post (FEED-01, FEED-03, FEED-08).

    Args:
        request: Contenu et ciblage du post.

    Returns:
        Le post créé.
    """
    try:
        dto = CreatePostDTO(
            content=request.content,
            target_type=request.target_type,
            chantier_ids=request.chantier_ids,
            user_ids=request.user_ids,
            is_urgent=request.is_urgent,
        )
        result = use_case.execute(dto, author_id=current_user_id)
        return _post_dto_to_response(result)

    except PostContentEmptyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/posts/{post_id}", response_model=PostDetailResponse)
def get_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    use_case: GetPostUseCase = Depends(get_post_use_case),
):
    """Récupère un post avec ses détails."""
    try:
        result = use_case.execute(post_id=post_id, user_id=current_user_id)

        return PostDetailResponse(
            post=_post_dto_to_response(result.post),
            medias=[
                MediaResponse(
                    id=m.id,
                    post_id=m.post_id,
                    media_type=m.media_type,
                    file_url=m.file_url,
                    thumbnail_url=m.thumbnail_url,
                    original_filename=m.original_filename,
                    width=m.width,
                    height=m.height,
                    position=m.position,
                )
                for m in result.medias
            ],
            comments=[
                CommentResponse(
                    id=c.id,
                    post_id=c.post_id,
                    author_id=c.author_id,
                    content=c.content,
                    created_at=c.created_at,
                )
                for c in result.comments
            ],
            liked_by_user_ids=result.liked_by_user_ids,
        )

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    use_case: DeletePostUseCase = Depends(get_delete_post_use_case),
):
    """
    Supprime un post (FEED-16 - Modération).

    Seul l'auteur ou un modérateur peut supprimer un post.
    """
    try:
        # TODO: Vérifier si l'utilisateur est modérateur (Admin/Conducteur)
        is_moderator = False  # À implémenter avec le service auth
        use_case.execute(
            post_id=post_id,
            user_id=current_user_id,
            is_moderator=is_moderator,
        )

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except NotAuthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )


@router.post("/posts/{post_id}/pin", status_code=status.HTTP_204_NO_CONTENT)
def pin_post(
    post_id: int,
    duration_hours: int = Query(default=48, ge=1, le=48),
    current_user_id: int = Depends(get_current_user_id),
    use_case: PinPostUseCase = Depends(get_pin_post_use_case),
):
    """
    Épingle un post en haut du fil (FEED-08).

    Durée max: 48 heures.
    """
    try:
        is_moderator = False  # À implémenter avec le service auth
        use_case.execute(
            post_id=post_id,
            user_id=current_user_id,
            duration_hours=duration_hours,
            is_moderator=is_moderator,
        )

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except NotAuthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )


@router.delete("/posts/{post_id}/pin", status_code=status.HTTP_204_NO_CONTENT)
def unpin_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    use_case: PinPostUseCase = Depends(get_pin_post_use_case),
):
    """Retire l'épinglage d'un post."""
    try:
        is_moderator = False
        use_case.unpin(
            post_id=post_id,
            user_id=current_user_id,
            is_moderator=is_moderator,
        )

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except NotAuthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )


# =============================================================================
# Routes Comments (FEED-05)
# =============================================================================


@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    request: CreateCommentRequest,
    current_user_id: int = Depends(get_current_user_id),
    use_case: AddCommentUseCase = Depends(get_add_comment_use_case),
):
    """Ajoute un commentaire sur un post (FEED-05)."""
    try:
        dto = CreateCommentDTO(
            post_id=post_id,
            content=request.content,
        )
        result = use_case.execute(dto, author_id=current_user_id)

        return CommentResponse(
            id=result.id,
            post_id=result.post_id,
            author_id=result.author_id,
            content=result.content,
            created_at=result.created_at,
        )

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except CommentContentEmptyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


# =============================================================================
# Routes Likes (FEED-04)
# =============================================================================


@router.post("/posts/{post_id}/like", response_model=LikeResponse, status_code=status.HTTP_201_CREATED)
def like_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    use_case: AddLikeUseCase = Depends(get_add_like_use_case),
):
    """Ajoute un like sur un post (FEED-04)."""
    try:
        result = use_case.execute(post_id=post_id, user_id=current_user_id)

        return LikeResponse(
            id=result.id,
            post_id=result.post_id,
            user_id=result.user_id,
            created_at=result.created_at,
        )

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except AlreadyLikedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@router.delete("/posts/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    use_case: RemoveLikeUseCase = Depends(get_remove_like_use_case),
):
    """Retire un like d'un post."""
    try:
        use_case.execute(post_id=post_id, user_id=current_user_id)

    except LikeNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


# =============================================================================
# Helpers
# =============================================================================


def _post_dto_to_response(dto) -> PostResponse:
    """Convertit un PostDTO en PostResponse."""
    return PostResponse(
        id=dto.id,
        author_id=dto.author_id,
        content=dto.content,
        status=dto.status,
        is_urgent=dto.is_urgent,
        is_pinned=dto.is_pinned,
        target_type=dto.target_type,
        target_display=dto.target_display,
        chantier_ids=list(dto.chantier_ids) if dto.chantier_ids else None,
        user_ids=list(dto.user_ids) if dto.user_ids else None,
        created_at=dto.created_at,
        likes_count=dto.likes_count,
        comments_count=dto.comments_count,
        medias_count=dto.medias_count,
    )
