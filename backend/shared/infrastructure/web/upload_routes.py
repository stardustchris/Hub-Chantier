"""Routes FastAPI pour l'upload de fichiers."""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
import os

from ..files import FileService, FileUploadError
from .dependencies import get_current_user_id


router = APIRouter(prefix="/uploads", tags=["uploads"])

# Configuration
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "uploads")
MAX_PHOTOS_PER_POST = 5
MAX_UPLOAD_SIZE_MB = 10  # P2-2: Limite avant compression (10 Mo max)
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024


async def validate_file_size(file: UploadFile, max_size: int = MAX_UPLOAD_SIZE_BYTES) -> bytes:
    """
    Valide la taille du fichier avant lecture complète (P2-2).

    Lit le fichier par chunks pour éviter l'épuisement mémoire.

    Args:
        file: Fichier uploadé.
        max_size: Taille maximale en bytes.

    Returns:
        Contenu du fichier si valide.

    Raises:
        HTTPException: Si le fichier dépasse la taille maximale.
    """
    chunks = []
    total_size = 0
    chunk_size = 64 * 1024  # 64 KB chunks

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Fichier trop volumineux. Maximum: {MAX_UPLOAD_SIZE_MB} Mo",
            )
        chunks.append(chunk)

    return b"".join(chunks)


def get_file_service() -> FileService:
    """Dependency injection pour FileService."""
    return FileService(upload_dir=UPLOAD_DIR)


# =============================================================================
# Pydantic models
# =============================================================================


class UploadResponse(BaseModel):
    """Réponse d'upload de fichier."""

    url: str
    thumbnail_url: Optional[str] = None
    # WebP responsive variants (P2-5)
    webp_thumbnail_url: Optional[str] = None
    webp_medium_url: Optional[str] = None
    webp_large_url: Optional[str] = None


class MultiUploadResponse(BaseModel):
    """Réponse d'upload de plusieurs fichiers."""

    files: List[UploadResponse]


# =============================================================================
# Routes d'upload
# =============================================================================


@router.post("/profile", response_model=UploadResponse)
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user_id),
    file_service: FileService = Depends(get_file_service),
):
    """
    Upload une photo de profil utilisateur (USR-02).

    Args:
        file: Fichier image à uploader.
        current_user_id: ID de l'utilisateur connecté.
        file_service: Service de gestion des fichiers.

    Returns:
        URL du fichier uploadé.
    """
    try:
        content = await validate_file_size(file)  # P2-2: Validation taille
        url = file_service.upload_profile_photo(
            file_content=content,
            filename=file.filename or "photo.jpg",
            user_id=current_user_id,
        )
        # P2-5: Generate WebP responsive variants
        prefix = url.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        webp_urls = file_service.generate_webp_variants(content, prefix)
        return UploadResponse(url=url, **webp_urls)
    except FileUploadError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.post("/posts/{post_id}", response_model=MultiUploadResponse)
async def upload_post_media(
    post_id: int,
    files: List[UploadFile] = File(...),
    current_user_id: int = Depends(get_current_user_id),
    file_service: FileService = Depends(get_file_service),
):
    """
    Upload des médias pour un post (FEED-02, FEED-19).

    Maximum 5 photos par post.

    Args:
        post_id: ID du post.
        files: Fichiers images à uploader.
        current_user_id: ID de l'utilisateur connecté.
        file_service: Service de gestion des fichiers.

    Returns:
        Liste des URLs des fichiers uploadés.
    """
    if len(files) > MAX_PHOTOS_PER_POST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_PHOTOS_PER_POST} photos par post",
        )

    results = []
    for file in files:
        try:
            content = await validate_file_size(file)  # P2-2: Validation taille
            url, thumbnail_url = file_service.upload_post_media(
                file_content=content,
                filename=file.filename or "photo.jpg",
                post_id=post_id,
            )
            # P2-5: Generate WebP responsive variants
            prefix = url.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            webp_urls = file_service.generate_webp_variants(content, prefix)
            results.append(UploadResponse(url=url, thumbnail_url=thumbnail_url, **webp_urls))
        except FileUploadError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erreur avec {file.filename}: {e.message}",
            )

    return MultiUploadResponse(files=results)


@router.post("/chantiers/{chantier_id}", response_model=UploadResponse)
async def upload_chantier_photo(
    chantier_id: int,
    file: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user_id),
    file_service: FileService = Depends(get_file_service),
):
    """
    Upload une photo de couverture de chantier (CHT-01).

    Args:
        chantier_id: ID du chantier.
        file: Fichier image à uploader.
        current_user_id: ID de l'utilisateur connecté.
        file_service: Service de gestion des fichiers.

    Returns:
        URL du fichier uploadé.
    """
    try:
        content = await validate_file_size(file)  # P2-2: Validation taille
        url = file_service.upload_chantier_photo(
            file_content=content,
            filename=file.filename or "photo.jpg",
            chantier_id=chantier_id,
        )
        # P2-5: Generate WebP responsive variants
        prefix = url.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        webp_urls = file_service.generate_webp_variants(content, prefix)
        return UploadResponse(url=url, **webp_urls)
    except FileUploadError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


# =============================================================================
# Route pour servir les fichiers statiques
# =============================================================================


@router.get("/{category}/{filename}")
async def get_uploaded_file(category: str, filename: str):
    """
    Sert un fichier uploadé.

    Args:
        category: Catégorie (profiles, posts, chantiers, thumbnails).
        filename: Nom du fichier.

    Returns:
        Le fichier.
    """
    allowed_categories = {"profiles", "posts", "chantiers", "thumbnails", "webp"}
    if category not in allowed_categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fichier non trouvé",
        )

    # SÉCURITÉ: Validation contre path traversal
    # Vérifie que le filename ne contient pas de caractères malveillants
    if os.path.basename(filename) != filename or ".." in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nom de fichier invalide",
        )

    file_path = Path(UPLOAD_DIR) / category / filename

    # SÉCURITÉ: Vérifie que le chemin résolu est bien dans UPLOAD_DIR
    try:
        resolved_path = file_path.resolve()
        upload_dir_resolved = Path(UPLOAD_DIR).resolve()
        if not str(resolved_path).startswith(str(upload_dir_resolved)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chemin de fichier invalide",
            )
    except (ValueError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chemin de fichier invalide",
        )

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fichier non trouvé",
        )

    # Déterminer le MIME type réel
    ext = file_path.suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    media_type = mime_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=filename,
    )
