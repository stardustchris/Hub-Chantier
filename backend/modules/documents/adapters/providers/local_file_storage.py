"""Implémentation locale du service de stockage de fichiers."""

import io
import logging
import shutil
import zipfile
from typing import BinaryIO, Dict, Optional
from pathlib import Path
import uuid

from PIL import Image

from ...domain.services import FileStorageService

logger = logging.getLogger(__name__)


class LocalFileStorageService(FileStorageService):
    """
    Service de stockage de fichiers local.

    Stocke les fichiers sur le système de fichiers local.
    Utilisé pour le développement et les petites installations.
    """

    def __init__(self, base_path: str = "uploads"):
        """
        Initialise le service.

        Args:
            base_path: Chemin de base pour le stockage.
        """
        self._base_path = Path(base_path)
        self._base_path.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        file_content: BinaryIO,
        filename: str,
        chantier_id: int,
        dossier_id: int,
    ) -> str:
        """
        Sauvegarde un fichier.

        Args:
            file_content: Contenu du fichier.
            filename: Nom du fichier.
            chantier_id: ID du chantier.
            dossier_id: ID du dossier.

        Returns:
            Le chemin de stockage relatif.
        """
        # Créer le répertoire de destination
        dir_path = self._base_path / f"chantiers/{chantier_id}/dossiers/{dossier_id}"
        dir_path.mkdir(parents=True, exist_ok=True)

        # Générer un nom unique pour éviter les collisions
        unique_id = uuid.uuid4().hex[:8]
        safe_filename = self._sanitize_filename(filename)
        if "." in safe_filename:
            base, ext = safe_filename.rsplit(".", 1)
            stored_filename = f"{base}_{unique_id}.{ext}"
        else:
            stored_filename = f"{safe_filename}_{unique_id}"

        # Chemin complet
        file_path = dir_path / stored_filename

        # Écrire le fichier
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file_content, f)

        # Retourner le chemin relatif
        return str(file_path.relative_to(self._base_path))

    def delete(self, chemin_stockage: str) -> bool:
        """Supprime un fichier."""
        file_path = self._validate_path(chemin_stockage)
        if not file_path:
            return False
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def get(self, chemin_stockage: str) -> Optional[BinaryIO]:
        """Récupère le contenu d'un fichier."""
        file_path = self._validate_path(chemin_stockage)
        if not file_path:
            return None
        if file_path.exists():
            return open(file_path, "rb")
        return None

    def exists(self, chemin_stockage: str) -> bool:
        """Vérifie si un fichier existe."""
        file_path = self._validate_path(chemin_stockage)
        if not file_path:
            return False
        return file_path.exists()

    def get_url(self, chemin_stockage: str, expires_in: int = 3600) -> str:
        """
        Génère une URL de téléchargement.

        Pour le stockage local, on retourne un chemin relatif.
        En production, on pourrait utiliser des URLs signées.
        """
        return f"/api/documents/download/{chemin_stockage}"

    def get_size(self, chemin_stockage: str) -> int:
        """Retourne la taille d'un fichier."""
        file_path = self._validate_path(chemin_stockage)
        if not file_path:
            return 0
        if file_path.exists():
            return file_path.stat().st_size
        return 0

    def move(self, ancien_chemin: str, nouveau_chemin: str) -> bool:
        """Déplace un fichier."""
        source = self._validate_path(ancien_chemin)
        dest = self._validate_path(nouveau_chemin)
        if not source or not dest:
            return False

        if not source.exists():
            return False

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(dest))
        return True

    def copy(self, source_chemin: str, destination_chemin: str) -> bool:
        """Copie un fichier."""
        source = self._validate_path(source_chemin)
        dest = self._validate_path(destination_chemin)
        if not source or not dest:
            return False

        if not source.exists():
            return False

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(source), str(dest))
        return True

    def _sanitize_filename(self, filename: str) -> str:
        """
        Nettoie un nom de fichier pour le stockage.

        Sécurité: empêche les attaques path traversal en retirant
        les caractères dangereux comme les points multiples.

        Args:
            filename: Nom de fichier original.

        Returns:
            Nom de fichier sécurisé.
        """
        # Séparer nom et extension
        if "." in filename:
            parts = filename.rsplit(".", 1)
            name = parts[0]
            ext = parts[1] if len(parts) > 1 else ""
        else:
            name = filename
            ext = ""

        # Nettoyer le nom (sans points pour éviter path traversal)
        safe_name = "".join(
            c if c.isalnum() or c in "_-" else "_" for c in name
        )
        safe_name = safe_name.strip("_") or "document"

        # Nettoyer l'extension (alphanumerique uniquement)
        safe_ext = "".join(c for c in ext if c.isalnum())

        if safe_ext:
            return f"{safe_name}.{safe_ext}"
        return safe_name

    # Extensions images supportées pour la génération WebP
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    WEBP_SIZES = {"thumbnail": 300, "medium": 800, "large": 1200}

    def generate_webp_thumbnails(self, chemin_stockage: str) -> Dict[str, str]:
        """Génère des thumbnails WebP pour un document image (2.5.4).

        Crée 3 variantes : thumbnail (300px), medium (800px), large (1200px).

        Args:
            chemin_stockage: Chemin relatif du fichier source.

        Returns:
            Dict avec clés webp_thumbnail, webp_medium, webp_large (chemins relatifs).
            Dict vide si le fichier n'est pas une image ou en cas d'erreur.
        """
        file_path = self._validate_path(chemin_stockage)
        if not file_path or not file_path.exists():
            return {}

        ext = file_path.suffix.lower()
        if ext not in self.IMAGE_EXTENSIONS:
            return {}

        try:
            img = Image.open(file_path)
            if img.mode in ("RGBA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[3] if len(img.split()) > 3 else None)
                img = background

            # Répertoire webp à côté du fichier source
            webp_dir = file_path.parent / "webp"
            webp_dir.mkdir(parents=True, exist_ok=True)

            stem = file_path.stem
            urls = {}
            for size_name, max_dim in self.WEBP_SIZES.items():
                resized = img.copy()
                if max(resized.size) > max_dim:
                    resized.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

                webp_filename = f"{stem}_{size_name}.webp"
                webp_path = webp_dir / webp_filename
                resized.save(webp_path, format="WEBP", quality=85, method=4)

                # Chemin relatif depuis base_path
                urls[f"webp_{size_name}"] = str(webp_path.relative_to(self._base_path))

            return urls
        except Exception as e:
            logger.warning(f"Erreur generation WebP pour {chemin_stockage}: {e}")
            return {}

    def get_full_path(self, chemin_stockage: str) -> Optional[Path]:
        """Retourne le chemin complet d'un fichier (validé contre path traversal)."""
        return self._validate_path(chemin_stockage)

    def _validate_path(self, chemin_stockage: str) -> Optional[Path]:
        """
        Valide et résout un chemin de stockage en s'assurant qu'il reste dans base_path.

        Sécurité: Prévient les attaques path traversal.

        Args:
            chemin_stockage: Chemin relatif du fichier.

        Returns:
            Le chemin résolu s'il est valide, None sinon.
        """
        try:
            file_path = (self._base_path / chemin_stockage).resolve()
            base_resolved = self._base_path.resolve()

            # Vérifier que le chemin résolu est bien dans base_path
            # Utiliser os.sep pour éviter le bypass par préfixe
            # (ex: /app/uploads_evil matcherait /app/uploads sans le sep)
            base_str = str(base_resolved) + "/"
            if not (str(file_path) + "/").startswith(base_str):
                logger.warning(f"Tentative d'accès path traversal: {chemin_stockage}")
                return None

            return file_path
        except Exception as e:
            logger.error(f"Erreur de validation de chemin: {e}")
            return None

    def create_zip(
        self,
        files: list[tuple[str, str]],
        archive_name: str,
    ) -> Optional[BinaryIO]:
        """
        Crée une archive ZIP contenant plusieurs fichiers (GED-16).

        Args:
            files: Liste de tuples (chemin_stockage, nom_dans_archive).
            archive_name: Nom de l'archive (ignoré, on retourne en mémoire).

        Returns:
            Le contenu binaire de l'archive ZIP ou None si erreur.
        """
        if not files:
            return None

        zip_buffer = io.BytesIO()

        try:
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for chemin_stockage, nom_archive in files:
                    file_path = self._validate_path(chemin_stockage)
                    if file_path and file_path.exists():
                        zip_file.write(file_path, nom_archive)

            zip_buffer.seek(0)
            return zip_buffer
        except Exception as e:
            logger.error(f"Erreur lors de la création ZIP: {e}")
            return None

    def get_preview_data(
        self,
        chemin_stockage: str,
        max_size: int = 10 * 1024 * 1024,
    ) -> Optional[tuple[bytes, str]]:
        """
        Récupère les données de prévisualisation d'un fichier (GED-17).

        Args:
            chemin_stockage: Chemin du fichier.
            max_size: Taille maximale pour la prévisualisation (défaut: 10MB).

        Returns:
            Tuple (contenu, mime_type) ou None si fichier trop gros ou non trouvé.
        """
        # Valider le chemin (sécurité path traversal)
        file_path = self._validate_path(chemin_stockage)
        if not file_path:
            return None

        if not file_path.exists():
            return None

        # Vérifier la taille
        file_size = file_path.stat().st_size
        if file_size > max_size:
            return None

        # Détecter le mime type basé sur l'extension
        extension = file_path.suffix.lower().lstrip(".")
        mime_types = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "webp": "image/webp",
            "svg": "image/svg+xml",
            "mp4": "video/mp4",
            "webm": "video/webm",
            "mov": "video/quicktime",
            "txt": "text/plain",
            "html": "text/html",
            "json": "application/json",
        }

        mime_type = mime_types.get(extension, "application/octet-stream")

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            return content, mime_type
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier pour preview: {e}")
            return None
