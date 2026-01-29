"""Use Cases pour la gestion des documents."""

import mimetypes
from typing import Optional, BinaryIO

from ..dtos import (
    DocumentDTO,
    DocumentUpdateDTO,
    DocumentListDTO,
    DocumentSearchDTO,
    DownloadZipDTO,
    DocumentPreviewDTO,
)
from ...domain.entities import Document
from ...domain.repositories import DocumentRepository, DossierRepository, AutorisationRepository
from ...domain.services import FileStorageService
from ...domain.value_objects import NiveauAcces, TypeDocument


class DocumentNotFoundError(Exception):
    """Erreur levée quand un document n'est pas trouvé."""

    pass


class DossierNotFoundError(Exception):
    """Erreur levée quand un dossier n'est pas trouvé."""

    pass


class FileTooLargeError(Exception):
    """Erreur levée quand un fichier est trop gros (GED-07)."""

    pass


class InvalidFileTypeError(Exception):
    """Erreur levée quand le type de fichier n'est pas supporté (GED-12)."""

    pass


class DuplicateDocumentNameError(Exception):
    """Erreur levée quand un document avec ce nom existe déjà."""

    pass


class AccessDeniedError(Exception):
    """Erreur levée quand l'accès est refusé."""

    pass


ALLOWED_EXTENSIONS = {
    "pdf", "png", "jpg", "jpeg", "gif", "webp",
    "xls", "xlsx", "doc", "docx",
    "mp4", "webm", "mov",
    "txt", "csv",
}


class UploadDocumentUseCase:
    """Use case pour uploader un document (GED-06, GED-07, GED-08)."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        dossier_repository: DossierRepository,
        file_storage: FileStorageService,
    ):
        """
        Initialise le use case.

        Args:
            document_repository: Repository des documents.
            dossier_repository: Repository des dossiers.
            file_storage: Service de stockage de fichiers.
        """
        self._document_repo = document_repository
        self._dossier_repo = dossier_repository
        self._file_storage = file_storage

    def execute(
        self,
        file_content: BinaryIO,
        filename: str,
        chantier_id: int,
        dossier_id: int,
        uploaded_by: int,
        taille: int,
        mime_type: str,
        description: Optional[str] = None,
        niveau_acces: Optional[str] = None,
    ) -> DocumentDTO:
        """
        Upload un document.

        Args:
            file_content: Contenu du fichier.
            filename: Nom du fichier.
            chantier_id: ID du chantier.
            dossier_id: ID du dossier.
            uploaded_by: ID de l'utilisateur.
            taille: Taille en bytes.
            mime_type: Type MIME.
            description: Description optionnelle.
            niveau_acces: Niveau d'accès optionnel.

        Returns:
            Le document créé.

        Raises:
            FileTooLargeError: Si le fichier est trop gros.
            InvalidFileTypeError: Si le type n'est pas supporté.
            DossierNotFoundError: Si le dossier n'existe pas.
        """
        # Valider la taille (GED-07: max 10 Go)
        if not Document.valider_taille(taille):
            raise FileTooLargeError("Le fichier dépasse la limite de 10 Go")

        # Valider l'extension (GED-12)
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if not extension or extension not in ALLOWED_EXTENSIONS:
            raise InvalidFileTypeError(f"Type de fichier non supporté: .{extension}")

        # Valider la cohérence MIME type / extension
        guessed_type, _ = mimetypes.guess_type(filename)
        if guessed_type and mime_type != "application/octet-stream":
            # Vérifier que le MIME déclaré est cohérent avec l'extension
            expected_type, _ = mimetypes.guess_type(f"file.{extension}")
            if expected_type and guessed_type != mime_type and expected_type != mime_type:
                raise InvalidFileTypeError(
                    f"Le type MIME '{mime_type}' ne correspond pas à l'extension '.{extension}'"
                )

        # Vérifier que le dossier existe
        dossier = self._dossier_repo.find_by_id(dossier_id)
        if not dossier:
            raise DossierNotFoundError(f"Dossier {dossier_id} non trouvé")

        # Gérer les doublons de nom
        nom = filename
        if self._document_repo.exists_by_nom_in_dossier(nom, dossier_id):
            base, ext = nom.rsplit(".", 1) if "." in nom else (nom, "")
            counter = 1
            while self._document_repo.exists_by_nom_in_dossier(
                f"{base}_{counter}.{ext}" if ext else f"{base}_{counter}",
                dossier_id,
            ):
                counter += 1
            nom = f"{base}_{counter}.{ext}" if ext else f"{base}_{counter}"

        # Sauvegarder le fichier
        chemin_stockage = self._file_storage.save(
            file_content, nom, chantier_id, dossier_id
        )

        # Créer l'entité document
        document = Document(
            chantier_id=chantier_id,
            dossier_id=dossier_id,
            nom=nom,
            nom_original=filename,
            chemin_stockage=chemin_stockage,
            taille=taille,
            mime_type=mime_type,
            uploaded_by=uploaded_by,
            type_document=TypeDocument.from_extension(extension) if extension else TypeDocument.AUTRE,
            niveau_acces=NiveauAcces.from_string(niveau_acces) if niveau_acces else None,
            description=description,
        )

        # Persister
        document = self._document_repo.save(document)

        return DocumentDTO.from_entity(document)


class GetDocumentUseCase:
    """Use case pour récupérer un document."""

    def __init__(self, document_repository: DocumentRepository):
        """Initialise le use case."""
        self._document_repo = document_repository

    def execute(self, document_id: int) -> DocumentDTO:
        """
        Récupère un document par son ID.

        Args:
            document_id: ID du document.

        Returns:
            Le document trouvé.

        Raises:
            DocumentNotFoundError: Si le document n'existe pas.
        """
        document = self._document_repo.find_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} non trouvé")

        return DocumentDTO.from_entity(document)


class ListDocumentsUseCase:
    """Use case pour lister les documents d'un dossier (GED-03)."""

    def __init__(self, document_repository: DocumentRepository):
        """Initialise le use case."""
        self._document_repo = document_repository

    def execute(
        self, dossier_id: int, skip: int = 0, limit: int = 100
    ) -> DocumentListDTO:
        """
        Liste les documents d'un dossier.

        Args:
            dossier_id: ID du dossier.
            skip: Nombre à sauter.
            limit: Limite.

        Returns:
            Liste des documents avec pagination.
        """
        documents = self._document_repo.find_by_dossier(dossier_id, skip, limit)
        total = self._document_repo.count_by_dossier(dossier_id)

        return DocumentListDTO(
            documents=[DocumentDTO.from_entity(d) for d in documents],
            total=total,
            skip=skip,
            limit=limit,
        )


class SearchDocumentsUseCase:
    """Use case pour rechercher des documents."""

    def __init__(self, document_repository: DocumentRepository):
        """Initialise le use case."""
        self._document_repo = document_repository

    def execute(self, search_dto: DocumentSearchDTO) -> DocumentListDTO:
        """
        Recherche des documents avec filtres.

        Args:
            search_dto: Critères de recherche.

        Returns:
            Liste des documents trouvés.
        """
        type_doc = None
        if search_dto.type_document:
            try:
                type_doc = TypeDocument(search_dto.type_document)
            except ValueError:
                pass

        documents, total = self._document_repo.search(
            chantier_id=search_dto.chantier_id,
            query=search_dto.query,
            type_document=type_doc,
            dossier_id=search_dto.dossier_id,
            skip=search_dto.skip,
            limit=search_dto.limit,
        )

        return DocumentListDTO(
            documents=[DocumentDTO.from_entity(d) for d in documents],
            total=total,
            skip=search_dto.skip,
            limit=search_dto.limit,
        )


class UpdateDocumentUseCase:
    """Use case pour mettre à jour un document (GED-13)."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        dossier_repository: DossierRepository,
    ):
        """Initialise le use case."""
        self._document_repo = document_repository
        self._dossier_repo = dossier_repository

    def execute(self, document_id: int, dto: DocumentUpdateDTO) -> DocumentDTO:
        """
        Met à jour un document.

        Args:
            document_id: ID du document.
            dto: Données de mise à jour.

        Returns:
            Le document mis à jour.

        Raises:
            DocumentNotFoundError: Si le document n'existe pas.
        """
        document = self._document_repo.find_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} non trouvé")

        if dto.nom is not None:
            document.renommer(dto.nom)

        if dto.description is not None:
            document.description = dto.description

        if dto.dossier_id is not None:
            # Vérifier que le dossier existe
            dossier = self._dossier_repo.find_by_id(dto.dossier_id)
            if not dossier:
                raise DossierNotFoundError(f"Dossier {dto.dossier_id} non trouvé")
            document.deplacer(dto.dossier_id)

        if dto.niveau_acces is not None:
            if dto.niveau_acces == "":
                document.changer_niveau_acces(None)
            else:
                document.changer_niveau_acces(NiveauAcces.from_string(dto.niveau_acces))

        document = self._document_repo.save(document)

        return DocumentDTO.from_entity(document)


class DeleteDocumentUseCase:
    """Use case pour supprimer un document (GED-13)."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        file_storage: FileStorageService,
        autorisation_repository: AutorisationRepository,
    ):
        """Initialise le use case."""
        self._document_repo = document_repository
        self._file_storage = file_storage
        self._autorisation_repo = autorisation_repository

    def execute(self, document_id: int) -> bool:
        """
        Supprime un document.

        Args:
            document_id: ID du document.

        Returns:
            True si supprimé.

        Raises:
            DocumentNotFoundError: Si le document n'existe pas.
        """
        document = self._document_repo.find_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} non trouvé")

        # Supprimer le fichier physique
        self._file_storage.delete(document.chemin_stockage)

        # Supprimer les autorisations liées
        self._autorisation_repo.delete_by_document(document_id)

        # Supprimer l'entrée en base
        return self._document_repo.delete(document_id)


class DownloadDocumentUseCase:
    """Use case pour télécharger un document."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        file_storage: FileStorageService,
    ):
        """Initialise le use case."""
        self._document_repo = document_repository
        self._file_storage = file_storage

    def execute(self, document_id: int) -> tuple[BinaryIO, str, str]:
        """
        Récupère le contenu binaire d'un document pour téléchargement.

        Args:
            document_id: ID du document.

        Returns:
            Tuple (file_content, nom_fichier, mime_type).

        Raises:
            DocumentNotFoundError: Si le document n'existe pas.
        """
        document = self._document_repo.find_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} non trouvé")

        # Récupérer le contenu du fichier
        file_content = self._file_storage.get(document.chemin_stockage)
        if not file_content:
            raise DocumentNotFoundError(
                f"Fichier non trouvé sur le disque: {document.chemin_stockage}"
            )

        return file_content, document.nom_original, document.mime_type


class DownloadMultipleDocumentsUseCase:
    """Use case pour télécharger plusieurs documents en ZIP (GED-16)."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        file_storage: FileStorageService,
    ):
        """Initialise le use case."""
        self._document_repo = document_repository
        self._file_storage = file_storage

    def execute(self, dto: DownloadZipDTO) -> Optional[BinaryIO]:
        """
        Crée une archive ZIP contenant les documents demandés.

        Args:
            dto: DTO contenant les IDs des documents.

        Returns:
            Le contenu binaire de l'archive ZIP.

        Raises:
            DocumentNotFoundError: Si aucun document valide n'est trouvé.
        """
        if not dto.document_ids:
            raise DocumentNotFoundError("Aucun document spécifié")

        # Récupérer les documents
        files: list[tuple[str, str]] = []
        for doc_id in dto.document_ids:
            document = self._document_repo.find_by_id(doc_id)
            if document:
                # Gérer les doublons de noms
                nom_archive = document.nom
                counter = 1
                while any(f[1] == nom_archive for f in files):
                    base, ext = nom_archive.rsplit(".", 1) if "." in nom_archive else (nom_archive, "")
                    nom_archive = f"{base}_{counter}.{ext}" if ext else f"{base}_{counter}"
                    counter += 1
                files.append((document.chemin_stockage, nom_archive))

        if not files:
            raise DocumentNotFoundError("Aucun document valide trouvé")

        # Créer l'archive
        archive = self._file_storage.create_zip(files, "documents.zip")
        if not archive:
            raise DocumentNotFoundError("Erreur lors de la création de l'archive")

        return archive


class GetDocumentPreviewUseCase:
    """Use case pour obtenir la prévisualisation d'un document (GED-17)."""

    # Types de fichiers supportés pour la prévisualisation
    PREVIEWABLE_TYPES = {
        "pdf": True,
        "image": True,
        "video": True,
        "txt": True,
    }

    def __init__(
        self,
        document_repository: DocumentRepository,
        file_storage: FileStorageService,
    ):
        """Initialise le use case."""
        self._document_repo = document_repository
        self._file_storage = file_storage

    def execute(self, document_id: int) -> DocumentPreviewDTO:
        """
        Obtient les informations de prévisualisation d'un document.

        Args:
            document_id: ID du document.

        Returns:
            DTO avec les informations de prévisualisation.

        Raises:
            DocumentNotFoundError: Si le document n'existe pas.
        """
        document = self._document_repo.find_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} non trouvé")

        # Vérifier si le type est prévisualisable
        can_preview = document.type_document.value in self.PREVIEWABLE_TYPES

        # Vérifier la taille (max 10MB pour prévisualisation)
        max_preview_size = 10 * 1024 * 1024
        if document.taille > max_preview_size:
            can_preview = False

        # Générer l'URL de prévisualisation si possible
        preview_url = None
        if can_preview:
            preview_url = f"/api/documents/{document_id}/preview/content"

        return DocumentPreviewDTO(
            id=document.id,  # type: ignore
            nom=document.nom,
            type_document=document.type_document.value,
            mime_type=document.mime_type,
            taille=document.taille,
            can_preview=can_preview,
            preview_url=preview_url,
        )


class GetDocumentPreviewContentUseCase:
    """Use case pour récupérer le contenu de prévisualisation (GED-17)."""

    # Taille max pour prévisualisation (10 MB)
    MAX_PREVIEW_SIZE = 10 * 1024 * 1024

    def __init__(
        self,
        document_repository: DocumentRepository,
        file_storage: FileStorageService,
    ):
        """Initialise le use case."""
        self._document_repo = document_repository
        self._file_storage = file_storage

    def execute(self, document_id: int) -> tuple[bytes, str]:
        """
        Récupère le contenu d'un document pour prévisualisation.

        Args:
            document_id: ID du document.

        Returns:
            Tuple (contenu, mime_type).

        Raises:
            DocumentNotFoundError: Si le document n'existe pas.
            FileTooLargeError: Si le fichier est trop gros pour la prévisualisation.
        """
        document = self._document_repo.find_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} non trouvé")

        if document.taille > self.MAX_PREVIEW_SIZE:
            raise FileTooLargeError("Le fichier est trop volumineux pour la prévisualisation")

        result = self._file_storage.get_preview_data(
            document.chemin_stockage, self.MAX_PREVIEW_SIZE
        )
        if not result:
            raise DocumentNotFoundError("Impossible de lire le contenu du fichier")

        return result
