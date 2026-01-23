"""Controller pour les documents."""

from typing import Optional, List, BinaryIO

from ...application.use_cases import (
    UploadDocumentUseCase,
    GetDocumentUseCase,
    ListDocumentsUseCase,
    SearchDocumentsUseCase,
    UpdateDocumentUseCase,
    DeleteDocumentUseCase,
    DownloadDocumentUseCase,
    CreateDossierUseCase,
    GetDossierUseCase,
    ListDossiersUseCase,
    GetArborescenceUseCase,
    UpdateDossierUseCase,
    DeleteDossierUseCase,
    InitArborescenceUseCase,
    CreateAutorisationUseCase,
    ListAutorisationsUseCase,
    RevokeAutorisationUseCase,
    CheckAccessUseCase,
)
from ...application.dtos import (
    DocumentDTO,
    DocumentUpdateDTO,
    DocumentListDTO,
    DocumentSearchDTO,
    DossierDTO,
    DossierCreateDTO,
    DossierUpdateDTO,
    ArborescenceDTO,
    AutorisationDTO,
    AutorisationCreateDTO,
    AutorisationListDTO,
)


class DocumentController:
    """Controller pour les opérations sur les documents et dossiers."""

    def __init__(
        self,
        upload_document: UploadDocumentUseCase,
        get_document: GetDocumentUseCase,
        list_documents: ListDocumentsUseCase,
        search_documents: SearchDocumentsUseCase,
        update_document: UpdateDocumentUseCase,
        delete_document: DeleteDocumentUseCase,
        download_document: DownloadDocumentUseCase,
        create_dossier: CreateDossierUseCase,
        get_dossier: GetDossierUseCase,
        list_dossiers: ListDossiersUseCase,
        get_arborescence: GetArborescenceUseCase,
        update_dossier: UpdateDossierUseCase,
        delete_dossier: DeleteDossierUseCase,
        init_arborescence: InitArborescenceUseCase,
        create_autorisation: CreateAutorisationUseCase,
        list_autorisations: ListAutorisationsUseCase,
        revoke_autorisation: RevokeAutorisationUseCase,
        check_access: CheckAccessUseCase,
    ):
        """Initialise le controller avec les use cases."""
        self._upload_document = upload_document
        self._get_document = get_document
        self._list_documents = list_documents
        self._search_documents = search_documents
        self._update_document = update_document
        self._delete_document = delete_document
        self._download_document = download_document
        self._create_dossier = create_dossier
        self._get_dossier = get_dossier
        self._list_dossiers = list_dossiers
        self._get_arborescence = get_arborescence
        self._update_dossier = update_dossier
        self._delete_dossier = delete_dossier
        self._init_arborescence = init_arborescence
        self._create_autorisation = create_autorisation
        self._list_autorisations = list_autorisations
        self._revoke_autorisation = revoke_autorisation
        self._check_access = check_access

    # Document operations
    def upload_document(
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
        """Upload un document."""
        return self._upload_document.execute(
            file_content=file_content,
            filename=filename,
            chantier_id=chantier_id,
            dossier_id=dossier_id,
            uploaded_by=uploaded_by,
            taille=taille,
            mime_type=mime_type,
            description=description,
            niveau_acces=niveau_acces,
        )

    def get_document(self, document_id: int) -> DocumentDTO:
        """Récupère un document."""
        return self._get_document.execute(document_id)

    def list_documents(
        self, dossier_id: int, skip: int = 0, limit: int = 100
    ) -> DocumentListDTO:
        """Liste les documents d'un dossier."""
        return self._list_documents.execute(dossier_id, skip, limit)

    def search_documents(self, search_dto: DocumentSearchDTO) -> DocumentListDTO:
        """Recherche des documents."""
        return self._search_documents.execute(search_dto)

    def update_document(
        self, document_id: int, dto: DocumentUpdateDTO
    ) -> DocumentDTO:
        """Met à jour un document."""
        return self._update_document.execute(document_id, dto)

    def delete_document(self, document_id: int) -> bool:
        """Supprime un document."""
        return self._delete_document.execute(document_id)

    def download_document(self, document_id: int) -> tuple[str, str, str]:
        """Télécharge un document."""
        return self._download_document.execute(document_id)

    # Dossier operations
    def create_dossier(self, dto: DossierCreateDTO) -> DossierDTO:
        """Crée un dossier."""
        return self._create_dossier.execute(dto)

    def get_dossier(self, dossier_id: int) -> DossierDTO:
        """Récupère un dossier."""
        return self._get_dossier.execute(dossier_id)

    def list_dossiers(
        self, chantier_id: int, parent_id: Optional[int] = None
    ) -> List[DossierDTO]:
        """Liste les dossiers."""
        return self._list_dossiers.execute(chantier_id, parent_id)

    def get_arborescence(self, chantier_id: int) -> ArborescenceDTO:
        """Récupère l'arborescence complète."""
        return self._get_arborescence.execute(chantier_id)

    def update_dossier(
        self, dossier_id: int, dto: DossierUpdateDTO
    ) -> DossierDTO:
        """Met à jour un dossier."""
        return self._update_dossier.execute(dossier_id, dto)

    def delete_dossier(self, dossier_id: int, force: bool = False) -> bool:
        """Supprime un dossier."""
        return self._delete_dossier.execute(dossier_id, force)

    def init_arborescence(self, chantier_id: int) -> List[DossierDTO]:
        """Initialise l'arborescence type."""
        return self._init_arborescence.execute(chantier_id)

    # Autorisation operations
    def create_autorisation(self, dto: AutorisationCreateDTO) -> AutorisationDTO:
        """Crée une autorisation."""
        return self._create_autorisation.execute(dto)

    def list_autorisations_by_dossier(
        self, dossier_id: int
    ) -> AutorisationListDTO:
        """Liste les autorisations d'un dossier."""
        return self._list_autorisations.execute_by_dossier(dossier_id)

    def list_autorisations_by_document(
        self, document_id: int
    ) -> AutorisationListDTO:
        """Liste les autorisations d'un document."""
        return self._list_autorisations.execute_by_document(document_id)

    def revoke_autorisation(self, autorisation_id: int) -> bool:
        """Révoque une autorisation."""
        return self._revoke_autorisation.execute(autorisation_id)

    def can_access_dossier(
        self, user_id: int, user_role: str, dossier_id: int
    ) -> bool:
        """Vérifie l'accès à un dossier."""
        return self._check_access.can_access_dossier(user_id, user_role, dossier_id)

    def can_access_document(
        self, user_id: int, user_role: str, document_id: int
    ) -> bool:
        """Vérifie l'accès à un document."""
        return self._check_access.can_access_document(user_id, user_role, document_id)
