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
from ...application.dtos import CreatePostDTO, CreateCommentDTO, PostDTO
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
from shared.infrastructure.web import get_current_user_id, get_is_moderator


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# =============================================================================
# Pydantic models for request/response validation
# Selon CDC Section 2 - Tableau de Bord (FEED-01 à FEED-20)
# =============================================================================


class CreatePostRequest(BaseModel):
    """Requête de création de post (FEED-01, FEED-03) - format frontend."""

    contenu: str  # Renommé pour frontend
    type: Optional[str] = "message"  # message, photo, urgent
    target_type: Optional[str] = "tous"  # tous, chantiers, utilisateurs
    target_chantier_ids: Optional[List[str]] = None  # IDs en string pour frontend
    target_utilisateur_ids: Optional[List[str]] = None  # IDs en string pour frontend
    is_urgent: Optional[bool] = False


class UserSummary(BaseModel):
    """Résumé d'un utilisateur pour l'inclusion dans Post."""

    id: str
    email: str
    nom: str
    prenom: str
    role: str
    type_utilisateur: str
    is_active: bool


class PostMediaResponse(BaseModel):
    """Réponse média pour frontend."""

    id: str
    url: str
    type: str  # image, video
    thumbnail_url: Optional[str] = None


class PostCommentResponse(BaseModel):
    """Réponse commentaire pour frontend."""

    id: str
    contenu: str
    auteur: UserSummary
    created_at: str


class PostLikeResponse(BaseModel):
    """Réponse like pour frontend."""

    user_id: str
    user: UserSummary


class PostResponse(BaseModel):
    """Réponse post - format frontend."""

    id: str  # String pour frontend
    contenu: str  # Renommé pour frontend
    type: str  # message, photo, urgent
    auteur: UserSummary
    target_type: str  # tous, chantiers, utilisateurs
    target_chantiers: Optional[List[dict]] = None  # Objets Chantier simplifiés
    target_utilisateurs: Optional[List[UserSummary]] = None
    medias: List[PostMediaResponse] = []
    commentaires: List[PostCommentResponse] = []
    likes: List[PostLikeResponse] = []
    likes_count: int
    commentaires_count: int
    is_pinned: bool
    pinned_until: Optional[str] = None
    is_urgent: bool
    created_at: str
    updated_at: Optional[str] = None


class PostListResponse(BaseModel):
    """Réponse liste de posts paginée (FEED-18) - format frontend."""

    items: List[PostResponse]
    total: int
    page: int
    size: int
    pages: int


class CreateCommentRequest(BaseModel):
    """Requête de création de commentaire - format frontend."""

    contenu: str  # Renommé pour frontend


# =============================================================================
# Routes Posts
# =============================================================================


@router.get("/feed", response_model=PostListResponse)
def get_feed(
    page: int = Query(default=1, ge=1, description="Numéro de page"),
    size: int = Query(default=20, ge=1, le=100, description="Nombre d'éléments par page"),
    current_user_id: int = Depends(get_current_user_id),
    use_case: GetFeedUseCase = Depends(get_feed_use_case),
):
    """
    Récupère le fil d'actualités de l'utilisateur (FEED-09, FEED-18).

    Les posts sont filtrés selon le ciblage et triés par date décroissante.
    Les posts épinglés apparaissent en premier.
    """
    # Convertir page/size en offset/limit
    offset = (page - 1) * size

    result = use_case.execute(
        user_id=current_user_id,
        user_chantier_ids=None,
        limit=size,
        offset=offset,
        include_archived=False,
    )

    # Convertir au format frontend
    total = result.total
    pages = (total + size - 1) // size if size > 0 else 0

    return PostListResponse(
        items=[_post_dto_to_frontend_response(p) for p in result.posts],
        total=total,
        page=page,
        size=size,
        pages=pages,
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
        # Mapper les noms frontend vers backend
        target_type_map = {"tous": "everyone", "chantiers": "specific_chantiers", "utilisateurs": "specific_people"}
        backend_target_type = target_type_map.get(request.target_type, "everyone")

        # Convertir les IDs string en int avec validation
        try:
            chantier_ids = [int(id) for id in request.target_chantier_ids] if request.target_chantier_ids else None
            user_ids = [int(id) for id in request.target_utilisateur_ids] if request.target_utilisateur_ids else None
        except (ValueError, TypeError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Les IDs doivent être des nombres valides",
            )

        dto = CreatePostDTO(
            content=request.contenu,  # Mapping frontend -> backend
            target_type=backend_target_type,
            chantier_ids=chantier_ids,
            user_ids=user_ids,
            is_urgent=request.is_urgent or request.type == "urgent",
        )
        result = use_case.execute(dto, author_id=current_user_id)
        return _post_dto_to_frontend_response(result)

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


@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    use_case: GetPostUseCase = Depends(get_post_use_case),
):
    """Récupère un post avec ses détails."""
    try:
        result = use_case.execute(post_id=post_id, user_id=current_user_id)
        return _post_dto_to_frontend_response(result.post, result.medias, result.comments, result.liked_by_user_ids)

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    is_moderator: bool = Depends(get_is_moderator),
    use_case: DeletePostUseCase = Depends(get_delete_post_use_case),
):
    """
    Supprime un post (FEED-16 - Modération).

    Seul l'auteur ou un modérateur peut supprimer un post.
    """
    try:
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


@router.post("/posts/{post_id}/pin", response_model=PostResponse)
def pin_post(
    post_id: int,
    duration_hours: int = Query(default=48, ge=1, le=48),
    current_user_id: int = Depends(get_current_user_id),
    is_moderator: bool = Depends(get_is_moderator),
    use_case: PinPostUseCase = Depends(get_pin_post_use_case),
    get_post_use_case: GetPostUseCase = Depends(get_post_use_case),
):
    """
    Épingle un post en haut du fil (FEED-08).

    Durée max: 48 heures.
    """
    try:
        use_case.execute(
            post_id=post_id,
            user_id=current_user_id,
            duration_hours=duration_hours,
            is_moderator=is_moderator,
        )
        # Retourner le post mis à jour
        result = get_post_use_case.execute(post_id=post_id, user_id=current_user_id)
        return _post_dto_to_frontend_response(result.post)

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


@router.delete("/posts/{post_id}/pin", response_model=PostResponse)
def unpin_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    is_moderator: bool = Depends(get_is_moderator),
    use_case: PinPostUseCase = Depends(get_pin_post_use_case),
    get_post_use_case: GetPostUseCase = Depends(get_post_use_case),
):
    """Retire l'épinglage d'un post."""
    try:
        use_case.unpin(
            post_id=post_id,
            user_id=current_user_id,
            is_moderator=is_moderator,
        )
        # Retourner le post mis à jour
        result = get_post_use_case.execute(post_id=post_id, user_id=current_user_id)
        return _post_dto_to_frontend_response(result.post)

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


@router.post("/posts/{post_id}/comments", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    request: CreateCommentRequest,
    current_user_id: int = Depends(get_current_user_id),
    use_case: AddCommentUseCase = Depends(get_add_comment_use_case),
    get_post_use_case: GetPostUseCase = Depends(get_post_use_case),
):
    """Ajoute un commentaire sur un post (FEED-05)."""
    try:
        dto = CreateCommentDTO(
            post_id=post_id,
            content=request.contenu,  # Mapping frontend -> backend
        )
        use_case.execute(dto, author_id=current_user_id)

        # Retourner le post mis à jour avec tous les commentaires
        result = get_post_use_case.execute(post_id=post_id, user_id=current_user_id)
        return _post_dto_to_frontend_response(result.post, result.medias, result.comments, result.liked_by_user_ids)

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


@router.post("/posts/{post_id}/like", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def like_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    use_case: AddLikeUseCase = Depends(get_add_like_use_case),
    get_post_use_case: GetPostUseCase = Depends(get_post_use_case),
):
    """Ajoute un like sur un post (FEED-04)."""
    try:
        use_case.execute(post_id=post_id, user_id=current_user_id)

        # Retourner le post mis à jour
        result = get_post_use_case.execute(post_id=post_id, user_id=current_user_id)
        return _post_dto_to_frontend_response(result.post, result.medias, result.comments, result.liked_by_user_ids)

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


@router.delete("/posts/{post_id}/like", response_model=PostResponse)
def unlike_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    use_case: RemoveLikeUseCase = Depends(get_remove_like_use_case),
    get_post_use_case: GetPostUseCase = Depends(get_post_use_case),
):
    """Retire un like d'un post."""
    try:
        use_case.execute(post_id=post_id, user_id=current_user_id)

        # Retourner le post mis à jour
        result = get_post_use_case.execute(post_id=post_id, user_id=current_user_id)
        return _post_dto_to_frontend_response(result.post, result.medias, result.comments, result.liked_by_user_ids)

    except LikeNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


# =============================================================================
# Helpers
# =============================================================================


def _post_dto_to_frontend_response(
    dto: PostDTO,
    medias: list = None,
    comments: list = None,
    liked_by_user_ids: list = None,
) -> PostResponse:
    """Convertit un PostDTO en PostResponse format frontend."""
    # Mapper le type de ciblage backend -> frontend
    target_type_map = {"everyone": "tous", "specific_chantiers": "chantiers", "specific_people": "utilisateurs"}
    frontend_target_type = target_type_map.get(dto.target_type, "tous")

    # Déterminer le type de post
    post_type = "urgent" if dto.is_urgent else "message"

    # Créer un auteur minimal (à enrichir avec les vraies données utilisateur)
    auteur = UserSummary(
        id=str(dto.author_id),
        email="",
        nom="",
        prenom="",
        role="compagnon",
        type_utilisateur="employe",
        is_active=True,
    )

    # Convertir les médias
    medias_response = []
    if medias:
        for m in medias:
            medias_response.append(PostMediaResponse(
                id=str(m.id),
                url=m.file_url,
                type="image" if m.media_type == "image" else "video",
                thumbnail_url=m.thumbnail_url,
            ))

    # Convertir les commentaires
    comments_response = []
    if comments:
        for c in comments:
            comments_response.append(PostCommentResponse(
                id=str(c.id),
                contenu=c.content,
                auteur=UserSummary(
                    id=str(c.author_id),
                    email="",
                    nom="",
                    prenom="",
                    role="compagnon",
                    type_utilisateur="employe",
                    is_active=True,
                ),
                created_at=c.created_at.isoformat() if hasattr(c.created_at, 'isoformat') else str(c.created_at),
            ))

    # Convertir les likes
    likes_response = []
    if liked_by_user_ids:
        for user_id in liked_by_user_ids:
            likes_response.append(PostLikeResponse(
                user_id=str(user_id),
                user=UserSummary(
                    id=str(user_id),
                    email="",
                    nom="",
                    prenom="",
                    role="compagnon",
                    type_utilisateur="employe",
                    is_active=True,
                ),
            ))

    return PostResponse(
        id=str(dto.id),
        contenu=dto.content,
        type=post_type,
        auteur=auteur,
        target_type=frontend_target_type,
        target_chantiers=None,  # TODO: Enrichir avec les vraies données
        target_utilisateurs=None,  # TODO: Enrichir avec les vraies données
        medias=medias_response,
        commentaires=comments_response,
        likes=likes_response,
        likes_count=dto.likes_count,
        commentaires_count=dto.comments_count,
        is_pinned=dto.is_pinned,
        pinned_until=None,  # TODO: Ajouter au DTO si disponible
        is_urgent=dto.is_urgent,
        created_at=dto.created_at.isoformat() if hasattr(dto.created_at, 'isoformat') else str(dto.created_at),
        updated_at=None,
    )
