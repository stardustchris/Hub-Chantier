"""Implémentation locale du service de stockage de fichiers."""

import os
import shutil
from typing import BinaryIO, Optional
from pathlib import Path
import uuid

from ...domain.services import FileStorageService


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
        file_path = self._base_path / chemin_stockage
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def get(self, chemin_stockage: str) -> Optional[BinaryIO]:
        """Récupère le contenu d'un fichier."""
        file_path = self._base_path / chemin_stockage
        if file_path.exists():
            return open(file_path, "rb")
        return None

    def exists(self, chemin_stockage: str) -> bool:
        """Vérifie si un fichier existe."""
        file_path = self._base_path / chemin_stockage
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
        file_path = self._base_path / chemin_stockage
        if file_path.exists():
            return file_path.stat().st_size
        return 0

    def move(self, ancien_chemin: str, nouveau_chemin: str) -> bool:
        """Déplace un fichier."""
        source = self._base_path / ancien_chemin
        dest = self._base_path / nouveau_chemin

        if not source.exists():
            return False

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(dest))
        return True

    def copy(self, source_chemin: str, destination_chemin: str) -> bool:
        """Copie un fichier."""
        source = self._base_path / source_chemin
        dest = self._base_path / destination_chemin

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

    def get_full_path(self, chemin_stockage: str) -> Path:
        """Retourne le chemin complet d'un fichier."""
        return self._base_path / chemin_stockage
