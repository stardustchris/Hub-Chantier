"""Value Object TypeDocument - Types de fichiers supportés (GED-12)."""

from enum import Enum


class TypeDocument(Enum):
    """
    Types de documents supportés.

    Selon CDC GED-12: PDF, Images (PNG/JPG), XLS/XLSX, DOC/DOCX, Vidéos.
    """

    PDF = "pdf"
    IMAGE = "image"
    EXCEL = "excel"
    WORD = "word"
    VIDEO = "video"
    AUTRE = "autre"

    @property
    def extensions(self) -> list[str]:
        """Retourne les extensions de fichier associées."""
        extensions_map = {
            TypeDocument.PDF: [".pdf"],
            TypeDocument.IMAGE: [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"],
            TypeDocument.EXCEL: [".xls", ".xlsx", ".csv"],
            TypeDocument.WORD: [".doc", ".docx", ".odt"],
            TypeDocument.VIDEO: [".mp4", ".avi", ".mov", ".mkv", ".webm"],
            TypeDocument.AUTRE: [],
        }
        return extensions_map[self]

    @property
    def mime_types(self) -> list[str]:
        """Retourne les types MIME associés."""
        mime_map = {
            TypeDocument.PDF: ["application/pdf"],
            TypeDocument.IMAGE: ["image/png", "image/jpeg", "image/gif", "image/webp", "image/bmp"],
            TypeDocument.EXCEL: [
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "text/csv",
            ],
            TypeDocument.WORD: [
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.oasis.opendocument.text",
            ],
            TypeDocument.VIDEO: ["video/mp4", "video/avi", "video/quicktime", "video/x-matroska", "video/webm"],
            TypeDocument.AUTRE: ["application/octet-stream"],
        }
        return mime_map[self]

    @property
    def icone(self) -> str:
        """Retourne l'icône associée au type."""
        icones = {
            TypeDocument.PDF: "file-pdf",
            TypeDocument.IMAGE: "file-image",
            TypeDocument.EXCEL: "file-excel",
            TypeDocument.WORD: "file-word",
            TypeDocument.VIDEO: "file-video",
            TypeDocument.AUTRE: "file",
        }
        return icones[self]

    @classmethod
    def from_extension(cls, extension: str) -> "TypeDocument":
        """
        Détermine le type de document depuis l'extension.

        Args:
            extension: L'extension du fichier (avec ou sans point).

        Returns:
            Le type de document correspondant.
        """
        ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"

        for type_doc in cls:
            if ext in type_doc.extensions:
                return type_doc

        return cls.AUTRE

    @classmethod
    def from_mime_type(cls, mime_type: str) -> "TypeDocument":
        """
        Détermine le type de document depuis le type MIME.

        Args:
            mime_type: Le type MIME du fichier.

        Returns:
            Le type de document correspondant.
        """
        mime = mime_type.lower()

        for type_doc in cls:
            if mime in type_doc.mime_types:
                return type_doc

        return cls.AUTRE

    @classmethod
    def list_extensions_acceptees(cls) -> list[str]:
        """Retourne toutes les extensions acceptées."""
        extensions = []
        for type_doc in cls:
            if type_doc != cls.AUTRE:
                extensions.extend(type_doc.extensions)
        return extensions
