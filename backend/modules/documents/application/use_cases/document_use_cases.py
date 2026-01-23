"""Use Cases pour la gestion des documents."""

from typing import Optional, List, BinaryIO

from ..dtos import DocumentDTO, DocumentCreateDTO, DocumentUpdateDTO, DocumentListDTO, DocumentSearchDTO
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
        extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
        if extension and not Document.valider_extension(extension):
            raise InvalidFileTypeError(f"Type de fichier non supporté: .{extension}")

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

        return self._to_dto(document)

    def _to_dto(self, document: Document, uploaded_by_nom: Optional[str] = None) -> DocumentDTO:
        """Convertit une entité en DTO."""
        return DocumentDTO(
            id=document.id,  # type: ignore
            chantier_id=document.chantier_id,
            dossier_id=document.dossier_id,
            nom=document.nom,
            nom_original=document.nom_original,
            type_document=document.type_document.value,
            taille=document.taille,
            taille_formatee=document.taille_formatee,
            mime_type=document.mime_type,
            uploaded_by=document.uploaded_by,
            uploaded_by_nom=uploaded_by_nom,
            uploaded_at=document.uploaded_at,
            description=document.description,
            version=document.version,
            icone=document.icone,
            extension=document.extension,
            niveau_acces=document.niveau_acces.value if document.niveau_acces else None,
        )


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

        return DocumentDTO(
            id=document.id,  # type: ignore
            chantier_id=document.chantier_id,
            dossier_id=document.dossier_id,
            nom=document.nom,
            nom_original=document.nom_original,
            type_document=document.type_document.value,
            taille=document.taille,
            taille_formatee=document.taille_formatee,
            mime_type=document.mime_type,
            uploaded_by=document.uploaded_by,
            uploaded_by_nom=None,
            uploaded_at=document.uploaded_at,
            description=document.description,
            version=document.version,
            icone=document.icone,
            extension=document.extension,
            niveau_acces=document.niveau_acces.value if document.niveau_acces else None,
        )


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
            documents=[
                DocumentDTO(
                    id=d.id,  # type: ignore
                    chantier_id=d.chantier_id,
                    dossier_id=d.dossier_id,
                    nom=d.nom,
                    nom_original=d.nom_original,
                    type_document=d.type_document.value,
                    taille=d.taille,
                    taille_formatee=d.taille_formatee,
                    mime_type=d.mime_type,
                    uploaded_by=d.uploaded_by,
                    uploaded_by_nom=None,
                    uploaded_at=d.uploaded_at,
                    description=d.description,
                    version=d.version,
                    icone=d.icone,
                    extension=d.extension,
                    niveau_acces=d.niveau_acces.value if d.niveau_acces else None,
                )
                for d in documents
            ],
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
            documents=[
                DocumentDTO(
                    id=d.id,  # type: ignore
                    chantier_id=d.chantier_id,
                    dossier_id=d.dossier_id,
                    nom=d.nom,
                    nom_original=d.nom_original,
                    type_document=d.type_document.value,
                    taille=d.taille,
                    taille_formatee=d.taille_formatee,
                    mime_type=d.mime_type,
                    uploaded_by=d.uploaded_by,
                    uploaded_by_nom=None,
                    uploaded_at=d.uploaded_at,
                    description=d.description,
                    version=d.version,
                    icone=d.icone,
                    extension=d.extension,
                    niveau_acces=d.niveau_acces.value if d.niveau_acces else None,
                )
                for d in documents
            ],
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

        return DocumentDTO(
            id=document.id,  # type: ignore
            chantier_id=document.chantier_id,
            dossier_id=document.dossier_id,
            nom=document.nom,
            nom_original=document.nom_original,
            type_document=document.type_document.value,
            taille=document.taille,
            taille_formatee=document.taille_formatee,
            mime_type=document.mime_type,
            uploaded_by=document.uploaded_by,
            uploaded_by_nom=None,
            uploaded_at=document.uploaded_at,
            description=document.description,
            version=document.version,
            icone=document.icone,
            extension=document.extension,
            niveau_acces=document.niveau_acces.value if document.niveau_acces else None,
        )


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

    def execute(self, document_id: int) -> tuple[str, str, str]:
        """
        Génère une URL de téléchargement.

        Args:
            document_id: ID du document.

        Returns:
            Tuple (url, nom_fichier, mime_type).

        Raises:
            DocumentNotFoundError: Si le document n'existe pas.
        """
        document = self._document_repo.find_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} non trouvé")

        url = self._file_storage.get_url(document.chemin_stockage)

        return url, document.nom, document.mime_type
