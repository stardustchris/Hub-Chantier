"""Interface FileStorageService - Service de stockage de fichiers."""

from abc import ABC, abstractmethod
from typing import BinaryIO, Dict, Optional


class FileStorageService(ABC):
    """
    Interface abstraite pour le service de stockage de fichiers.

    Cette interface définit le contrat pour le stockage des fichiers.
    L'implémentation concrète peut être locale, S3, etc.
    """

    @abstractmethod
    def save(
        self,
        file_content: BinaryIO,
        filename: str,
        chantier_id: int,
        dossier_id: int,
    ) -> str:
        """
        Sauvegarde un fichier et retourne le chemin de stockage.

        Args:
            file_content: Contenu binaire du fichier.
            filename: Nom du fichier.
            chantier_id: ID du chantier.
            dossier_id: ID du dossier.

        Returns:
            Le chemin de stockage du fichier.
        """
        pass

    @abstractmethod
    def delete(self, chemin_stockage: str) -> bool:
        """
        Supprime un fichier.

        Args:
            chemin_stockage: Chemin du fichier à supprimer.

        Returns:
            True si supprimé, False si non trouvé.
        """
        pass

    @abstractmethod
    def get(self, chemin_stockage: str) -> Optional[BinaryIO]:
        """
        Récupère le contenu d'un fichier.

        Args:
            chemin_stockage: Chemin du fichier.

        Returns:
            Le contenu binaire ou None si non trouvé.
        """
        pass

    @abstractmethod
    def exists(self, chemin_stockage: str) -> bool:
        """
        Vérifie si un fichier existe.

        Args:
            chemin_stockage: Chemin du fichier.

        Returns:
            True si le fichier existe.
        """
        pass

    @abstractmethod
    def get_url(self, chemin_stockage: str, expires_in: int = 3600) -> str:
        """
        Génère une URL de téléchargement temporaire.

        Args:
            chemin_stockage: Chemin du fichier.
            expires_in: Durée de validité en secondes.

        Returns:
            URL de téléchargement.
        """
        pass

    @abstractmethod
    def get_size(self, chemin_stockage: str) -> int:
        """
        Retourne la taille d'un fichier.

        Args:
            chemin_stockage: Chemin du fichier.

        Returns:
            Taille en bytes.
        """
        pass

    @abstractmethod
    def move(self, ancien_chemin: str, nouveau_chemin: str) -> bool:
        """
        Déplace un fichier.

        Args:
            ancien_chemin: Chemin actuel.
            nouveau_chemin: Nouveau chemin.

        Returns:
            True si déplacé avec succès.
        """
        pass

    @abstractmethod
    def copy(self, source_chemin: str, destination_chemin: str) -> bool:
        """
        Copie un fichier.

        Args:
            source_chemin: Chemin source.
            destination_chemin: Chemin destination.

        Returns:
            True si copié avec succès.
        """
        pass

    @abstractmethod
    def create_zip(
        self,
        files: list[tuple[str, str]],
        archive_name: str,
    ) -> Optional[BinaryIO]:
        """
        Crée une archive ZIP contenant plusieurs fichiers (GED-16).

        Args:
            files: Liste de tuples (chemin_stockage, nom_dans_archive).
            archive_name: Nom de l'archive.

        Returns:
            Le contenu binaire de l'archive ZIP ou None si erreur.
        """
        pass

    @abstractmethod
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
        pass

    def generate_webp_thumbnails(self, chemin_stockage: str) -> Dict[str, str]:
        """Génère des thumbnails WebP pour un document image (2.5.4).

        Args:
            chemin_stockage: Chemin relatif du fichier source.

        Returns:
            Dict avec clés webp_thumbnail, webp_medium, webp_large.
            Dict vide si non supporté ou pas une image.
        """
        return {}
