"""Service de gestion des fichiers uploadés."""

import os
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import io


class FileUploadError(Exception):
    """Erreur lors de l'upload d'un fichier."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class FileService:
    """
    Service de gestion des fichiers uploadés.

    Gère l'upload, la compression et le stockage des fichiers.
    Conforme aux specs CDC :
    - FEED-02 : Max 5 photos par post
    - FEED-19 : Compression auto max 2 Mo
    - USR-02 : Photo de profil
    - CHT-01 : Photo de couverture chantier
    """

    # Configuration
    MAX_FILE_SIZE_MB = 2
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    THUMBNAIL_SIZE = (300, 300)
    MAX_IMAGE_DIMENSION = 1920  # Max width or height after compression

    def __init__(self, upload_dir: str = "uploads"):
        """
        Initialise le service de fichiers.

        Args:
            upload_dir: Répertoire racine pour les uploads.
        """
        self.upload_dir = Path(upload_dir)
        self._ensure_directories()

    def _ensure_directories(self):
        """Crée les répertoires nécessaires."""
        subdirs = ["profiles", "posts", "chantiers", "thumbnails"]
        for subdir in subdirs:
            (self.upload_dir / subdir).mkdir(parents=True, exist_ok=True)

    def _generate_filename(self, original_filename: str) -> str:
        """
        Génère un nom de fichier unique.

        Args:
            original_filename: Nom original du fichier.

        Returns:
            Nom unique avec extension préservée.
        """
        ext = Path(original_filename).suffix.lower()
        unique_id = uuid.uuid4().hex[:12]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{unique_id}{ext}"

    def _validate_image(self, file_content: bytes, filename: str) -> None:
        """
        Valide qu'un fichier est une image valide.

        Args:
            file_content: Contenu du fichier.
            filename: Nom du fichier.

        Raises:
            FileUploadError: Si le fichier n'est pas une image valide.
        """
        ext = Path(filename).suffix.lower()
        if ext not in self.ALLOWED_IMAGE_EXTENSIONS:
            raise FileUploadError(
                f"Extension non autorisée. Extensions acceptées: {', '.join(self.ALLOWED_IMAGE_EXTENSIONS)}"
            )

        try:
            img = Image.open(io.BytesIO(file_content))
            img.verify()
        except (IOError, OSError, Image.UnidentifiedImageError) as e:
            raise FileUploadError(f"Le fichier n'est pas une image valide: {type(e).__name__}")

    def _compress_image(self, file_content: bytes, max_size_bytes: int = None) -> bytes:
        """
        Compresse une image pour respecter la taille maximale (FEED-19).

        Args:
            file_content: Contenu de l'image.
            max_size_bytes: Taille maximale en bytes.

        Returns:
            Image compressée.
        """
        if max_size_bytes is None:
            max_size_bytes = self.MAX_FILE_SIZE_BYTES

        img = Image.open(io.BytesIO(file_content))

        # Convertir RGBA en RGB si nécessaire (pour JPEG)
        if img.mode in ("RGBA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[3] if len(img.split()) > 3 else None)
            img = background

        # Redimensionner si trop grande
        if max(img.size) > self.MAX_IMAGE_DIMENSION:
            ratio = self.MAX_IMAGE_DIMENSION / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # Compresser progressivement jusqu'à respecter la taille
        quality = 95
        output = io.BytesIO()

        while quality > 20:
            output.seek(0)
            output.truncate()
            img.save(output, format="JPEG", quality=quality, optimize=True)

            if output.tell() <= max_size_bytes:
                break
            quality -= 5

        return output.getvalue()

    def _create_thumbnail(self, file_content: bytes) -> bytes:
        """
        Crée une miniature d'une image (FEED-13).

        Args:
            file_content: Contenu de l'image.

        Returns:
            Miniature de l'image.
        """
        img = Image.open(io.BytesIO(file_content))

        # Convertir si nécessaire
        if img.mode in ("RGBA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[3] if len(img.split()) > 3 else None)
            img = background

        # Créer la miniature
        img.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

        output = io.BytesIO()
        img.save(output, format="JPEG", quality=85, optimize=True)
        return output.getvalue()

    def upload_profile_photo(self, file_content: bytes, filename: str, user_id: int) -> str:
        """
        Upload une photo de profil utilisateur (USR-02).

        Args:
            file_content: Contenu du fichier.
            filename: Nom original du fichier.
            user_id: ID de l'utilisateur.

        Returns:
            URL relative du fichier uploadé.
        """
        self._validate_image(file_content, filename)

        # Compresser l'image
        compressed = self._compress_image(file_content)

        # Générer le nom de fichier
        new_filename = f"user_{user_id}_{self._generate_filename(filename)}"
        if not new_filename.endswith((".jpg", ".jpeg")):
            new_filename = new_filename.rsplit(".", 1)[0] + ".jpg"

        # Sauvegarder
        file_path = self.upload_dir / "profiles" / new_filename
        file_path.write_bytes(compressed)

        return f"/uploads/profiles/{new_filename}"

    def upload_post_media(
        self, file_content: bytes, filename: str, post_id: int
    ) -> Tuple[str, str]:
        """
        Upload un média pour un post (FEED-02, FEED-19).

        Args:
            file_content: Contenu du fichier.
            filename: Nom original du fichier.
            post_id: ID du post.

        Returns:
            Tuple (url_image, url_thumbnail).
        """
        self._validate_image(file_content, filename)

        # Compresser l'image
        compressed = self._compress_image(file_content)

        # Créer la miniature
        thumbnail = self._create_thumbnail(compressed)

        # Générer les noms de fichiers
        base_filename = f"post_{post_id}_{self._generate_filename(filename)}"
        if not base_filename.endswith((".jpg", ".jpeg")):
            base_filename = base_filename.rsplit(".", 1)[0] + ".jpg"
        thumb_filename = f"thumb_{base_filename}"

        # Sauvegarder l'image principale
        file_path = self.upload_dir / "posts" / base_filename
        file_path.write_bytes(compressed)

        # Sauvegarder la miniature
        thumb_path = self.upload_dir / "thumbnails" / thumb_filename
        thumb_path.write_bytes(thumbnail)

        return f"/uploads/posts/{base_filename}", f"/uploads/thumbnails/{thumb_filename}"

    def upload_chantier_photo(
        self, file_content: bytes, filename: str, chantier_id: int
    ) -> str:
        """
        Upload une photo de couverture de chantier (CHT-01).

        Args:
            file_content: Contenu du fichier.
            filename: Nom original du fichier.
            chantier_id: ID du chantier.

        Returns:
            URL relative du fichier uploadé.
        """
        self._validate_image(file_content, filename)

        # Compresser l'image
        compressed = self._compress_image(file_content)

        # Générer le nom de fichier
        new_filename = f"chantier_{chantier_id}_{self._generate_filename(filename)}"
        if not new_filename.endswith((".jpg", ".jpeg")):
            new_filename = new_filename.rsplit(".", 1)[0] + ".jpg"

        # Sauvegarder
        file_path = self.upload_dir / "chantiers" / new_filename
        file_path.write_bytes(compressed)

        return f"/uploads/chantiers/{new_filename}"

    def delete_file(self, file_url: str) -> bool:
        """
        Supprime un fichier uploadé.

        Args:
            file_url: URL relative du fichier.

        Returns:
            True si supprimé, False sinon.
        """
        if not file_url.startswith("/uploads/"):
            return False

        relative_path = file_url[len("/uploads/"):]
        file_path = self.upload_dir / relative_path

        if file_path.exists():
            file_path.unlink()
            return True
        return False
