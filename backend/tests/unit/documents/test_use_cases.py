"""Tests des Use Cases du module Documents."""

import pytest
from unittest.mock import Mock
from io import BytesIO

from modules.documents.domain.entities import (
    Document,
    Dossier,
    AutorisationDocument,
    TypeAutorisation,
)
from modules.documents.domain.value_objects import (
    NiveauAcces,
    TypeDocument,
    DossierType,
)
from modules.documents.application.use_cases.dossier_use_cases import (
    CreateDossierUseCase,
    GetDossierUseCase,
    ListDossiersUseCase,
    GetArborescenceUseCase,
    UpdateDossierUseCase,
    DeleteDossierUseCase,
    InitArborescenceUseCase,
    DossierNotFoundError,
    DossierNotEmptyError,
    DuplicateDossierNameError,
)
from modules.documents.application.use_cases.document_use_cases import (
    UploadDocumentUseCase,
    GetDocumentUseCase,
    ListDocumentsUseCase,
    SearchDocumentsUseCase,
    UpdateDocumentUseCase,
    DeleteDocumentUseCase,
    DownloadDocumentUseCase,
    DownloadMultipleDocumentsUseCase,
    GetDocumentPreviewUseCase,
    GetDocumentPreviewContentUseCase,
    DocumentNotFoundError,
    DossierNotFoundError as DocDossierNotFoundError,
    FileTooLargeError,
    InvalidFileTypeError,
)
from modules.documents.application.use_cases.autorisation_use_cases import (
    CreateAutorisationUseCase,
    ListAutorisationsUseCase,
    RevokeAutorisationUseCase,
    CheckAccessUseCase,
    AutorisationAlreadyExistsError,
    AutorisationNotFoundError,
    InvalidTargetError,
)
from modules.documents.application.dtos import (
    DossierCreateDTO,
    DossierUpdateDTO,
    DocumentUpdateDTO,
    DocumentSearchDTO,
    AutorisationCreateDTO,
    DownloadZipDTO,
)


# ====================
# DOSSIER USE CASES
# ====================


class TestCreateDossierUseCase:
    """Tests pour CreateDossierUseCase."""

    def test_create_dossier_success(self):
        """Creation de dossier reussie."""
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()
        mock_dossier_repo.exists_by_nom_in_parent.return_value = False

        saved_dossier = Dossier(
            id=1,
            chantier_id=1,
            nom="Plans",
            type_dossier=DossierType.PLANS,
            niveau_acces=NiveauAcces.COMPAGNON,
        )
        mock_dossier_repo.save.return_value = saved_dossier
        mock_document_repo.count_by_dossier.return_value = 0
        mock_dossier_repo.find_children.return_value = []

        use_case = CreateDossierUseCase(
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        dto = DossierCreateDTO(
            chantier_id=1,
            nom="Plans",
            type_dossier="01_plans",
            niveau_acces="compagnon",
        )

        result = use_case.execute(dto)

        assert result.id == 1
        assert result.nom == "Plans"
        assert result.type_dossier == "01_plans"
        mock_dossier_repo.save.assert_called_once()

    def test_create_dossier_duplicate_name(self):
        """Erreur si dossier avec meme nom existe."""
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()
        mock_dossier_repo.exists_by_nom_in_parent.return_value = True

        use_case = CreateDossierUseCase(
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        dto = DossierCreateDTO(chantier_id=1, nom="Plans")

        with pytest.raises(DuplicateDossierNameError):
            use_case.execute(dto)

    def test_create_dossier_with_parent(self):
        """Creation de sous-dossier."""
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()
        mock_dossier_repo.exists_by_nom_in_parent.return_value = False

        saved_dossier = Dossier(
            id=2,
            chantier_id=1,
            nom="Sous-dossier",
            parent_id=1,
        )
        mock_dossier_repo.save.return_value = saved_dossier
        mock_document_repo.count_by_dossier.return_value = 0
        mock_dossier_repo.find_children.return_value = []

        use_case = CreateDossierUseCase(
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        dto = DossierCreateDTO(chantier_id=1, nom="Sous-dossier", parent_id=1)

        result = use_case.execute(dto)

        assert result.parent_id == 1


class TestGetDossierUseCase:
    """Tests pour GetDossierUseCase."""

    def test_get_dossier_success(self):
        """Recuperation reussie."""
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        mock_dossier_repo.find_by_id.return_value = Dossier(
            id=1,
            chantier_id=1,
            nom="Plans",
        )
        mock_document_repo.count_by_dossier.return_value = 5
        mock_dossier_repo.find_children.return_value = []

        use_case = GetDossierUseCase(
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        result = use_case.execute(1)

        assert result.id == 1
        assert result.nom == "Plans"
        assert result.nombre_documents == 5

    def test_get_dossier_not_found(self):
        """Erreur si dossier non trouve."""
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()
        mock_dossier_repo.find_by_id.return_value = None

        use_case = GetDossierUseCase(
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        with pytest.raises(DossierNotFoundError):
            use_case.execute(999)


class TestListDossiersUseCase:
    """Tests pour ListDossiersUseCase."""

    def test_list_dossiers_success(self):
        """Liste des dossiers reussie."""
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        dossiers = [
            Dossier(id=1, chantier_id=1, nom="Plans"),
            Dossier(id=2, chantier_id=1, nom="Securite"),
        ]
        mock_dossier_repo.find_by_chantier.return_value = dossiers
        mock_document_repo.count_by_dossier.return_value = 0
        mock_dossier_repo.find_children.return_value = []

        use_case = ListDossiersUseCase(
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        result = use_case.execute(chantier_id=1)

        assert len(result) == 2
        assert result[0].nom == "Plans"
        assert result[1].nom == "Securite"


class TestGetArborescenceUseCase:
    """Tests pour GetArborescenceUseCase."""

    def test_get_arborescence_success(self):
        """Recuperation arborescence reussie."""
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        dossiers = [
            Dossier(id=1, chantier_id=1, nom="Plans", parent_id=None, ordre=0),
            Dossier(id=2, chantier_id=1, nom="Sous-dossier", parent_id=1, ordre=0),
        ]
        mock_dossier_repo.get_arborescence.return_value = dossiers
        mock_document_repo.count_by_dossier.return_value = 3
        mock_document_repo.get_total_size_by_chantier.return_value = 1024000

        use_case = GetArborescenceUseCase(
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        result = use_case.execute(chantier_id=1)

        assert result.chantier_id == 1
        assert len(result.dossiers) == 1  # 1 dossier racine
        # total_documents = sum of count_by_dossier for all folders (2 folders x 3 = 6)
        assert result.total_documents == 6
        assert result.total_taille == 1024000

    def test_get_arborescence_nested(self):
        """Arborescence imbriquee."""
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        dossiers = [
            Dossier(id=1, chantier_id=1, nom="Plans", parent_id=None, ordre=0),
            Dossier(id=2, chantier_id=1, nom="Niveau 1", parent_id=1, ordre=0),
            Dossier(id=3, chantier_id=1, nom="Niveau 2", parent_id=2, ordre=0),
        ]
        mock_dossier_repo.get_arborescence.return_value = dossiers
        mock_document_repo.count_by_dossier.return_value = 0
        mock_document_repo.count_by_chantier.return_value = 0
        mock_document_repo.get_total_size_by_chantier.return_value = 0

        use_case = GetArborescenceUseCase(
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        result = use_case.execute(chantier_id=1)

        assert len(result.dossiers) == 1
        assert len(result.dossiers[0].children) == 1
        assert len(result.dossiers[0].children[0].children) == 1


class TestUpdateDossierUseCase:
    """Tests pour UpdateDossierUseCase."""

    def test_update_dossier_nom_success(self):
        """Mise a jour du nom reussie."""
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        dossier = Dossier(id=1, chantier_id=1, nom="Ancien Nom")
        mock_dossier_repo.find_by_id.return_value = dossier
        mock_dossier_repo.exists_by_nom_in_parent.return_value = False
        mock_dossier_repo.save.return_value = dossier
        mock_document_repo.count_by_dossier.return_value = 0
        mock_dossier_repo.find_children.return_value = []

        use_case = UpdateDossierUseCase(
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        dto = DossierUpdateDTO(nom="Nouveau Nom")
        result = use_case.execute(1, dto)

        assert result.nom == "Nouveau Nom"

    def test_update_dossier_niveau_acces(self):
        """Mise a jour du niveau d'acces."""
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        dossier = Dossier(id=1, chantier_id=1, nom="Test", niveau_acces=NiveauAcces.COMPAGNON)
        mock_dossier_repo.find_by_id.return_value = dossier
        mock_dossier_repo.save.return_value = dossier
        mock_document_repo.count_by_dossier.return_value = 0
        mock_dossier_repo.find_children.return_value = []

        use_case = UpdateDossierUseCase(
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        dto = DossierUpdateDTO(niveau_acces="conducteur")
        result = use_case.execute(1, dto)

        assert result.niveau_acces == "conducteur"

    def test_update_dossier_not_found(self):
        """Erreur si dossier non trouve."""
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()
        mock_dossier_repo.find_by_id.return_value = None

        use_case = UpdateDossierUseCase(
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        dto = DossierUpdateDTO(nom="Test")
        with pytest.raises(DossierNotFoundError):
            use_case.execute(999, dto)


class TestDeleteDossierUseCase:
    """Tests pour DeleteDossierUseCase."""

    def test_delete_dossier_success(self):
        """Suppression reussie."""
        mock_dossier_repo = Mock()
        mock_dossier_repo.find_by_id.return_value = Dossier(id=1, chantier_id=1, nom="Test")
        mock_dossier_repo.has_documents.return_value = False
        mock_dossier_repo.has_children.return_value = False
        mock_dossier_repo.delete.return_value = True

        use_case = DeleteDossierUseCase(dossier_repository=mock_dossier_repo)

        result = use_case.execute(1)

        assert result is True

    def test_delete_dossier_not_found(self):
        """Erreur si dossier non trouve."""
        mock_dossier_repo = Mock()
        mock_dossier_repo.find_by_id.return_value = None

        use_case = DeleteDossierUseCase(dossier_repository=mock_dossier_repo)

        with pytest.raises(DossierNotFoundError):
            use_case.execute(999)

    def test_delete_dossier_not_empty_documents(self):
        """Erreur si dossier contient des documents."""
        mock_dossier_repo = Mock()
        mock_dossier_repo.find_by_id.return_value = Dossier(id=1, chantier_id=1, nom="Test")
        mock_dossier_repo.has_documents.return_value = True

        use_case = DeleteDossierUseCase(dossier_repository=mock_dossier_repo)

        with pytest.raises(DossierNotEmptyError, match="documents"):
            use_case.execute(1)

    def test_delete_dossier_not_empty_children(self):
        """Erreur si dossier contient des sous-dossiers."""
        mock_dossier_repo = Mock()
        mock_dossier_repo.find_by_id.return_value = Dossier(id=1, chantier_id=1, nom="Test")
        mock_dossier_repo.has_documents.return_value = False
        mock_dossier_repo.has_children.return_value = True

        use_case = DeleteDossierUseCase(dossier_repository=mock_dossier_repo)

        with pytest.raises(DossierNotEmptyError, match="sous-dossiers"):
            use_case.execute(1)

    def test_delete_dossier_force(self):
        """Suppression forcee."""
        mock_dossier_repo = Mock()
        mock_dossier_repo.find_by_id.return_value = Dossier(id=1, chantier_id=1, nom="Test")
        mock_dossier_repo.delete.return_value = True

        use_case = DeleteDossierUseCase(dossier_repository=mock_dossier_repo)

        result = use_case.execute(1, force=True)

        assert result is True
        # has_documents et has_children ne sont pas appeles avec force=True


class TestInitArborescenceUseCase:
    """Tests pour InitArborescenceUseCase."""

    def test_init_arborescence_success(self):
        """Initialisation arborescence reussie."""
        mock_dossier_repo = Mock()
        mock_dossier_repo.find_by_type.return_value = None  # Aucun dossier existant

        def save_side_effect(dossier):
            dossier.id = hash(dossier.nom)
            return dossier

        mock_dossier_repo.save.side_effect = save_side_effect

        use_case = InitArborescenceUseCase(dossier_repository=mock_dossier_repo)

        result = use_case.execute(chantier_id=1)

        # 7 types de dossiers (sans CUSTOM)
        assert len(result) == 7
        assert any(d.type_dossier == "01_plans" for d in result)
        assert any(d.type_dossier == "03_securite" for d in result)

    def test_init_arborescence_skip_existing(self):
        """Ignore les dossiers existants."""
        mock_dossier_repo = Mock()

        def find_by_type_side_effect(chantier_id, type_dossier):
            if type_dossier == DossierType.PLANS:
                return Dossier(id=1, chantier_id=1, nom="Plans", type_dossier=DossierType.PLANS)
            return None

        mock_dossier_repo.find_by_type.side_effect = find_by_type_side_effect

        def save_side_effect(dossier):
            dossier.id = hash(dossier.nom)
            return dossier

        mock_dossier_repo.save.side_effect = save_side_effect

        use_case = InitArborescenceUseCase(dossier_repository=mock_dossier_repo)

        result = use_case.execute(chantier_id=1)

        # 6 dossiers crees (Plans existe deja)
        assert len(result) == 6
        assert not any(d.type_dossier == "01_plans" for d in result)


# ====================
# DOCUMENT USE CASES
# ====================


class TestUploadDocumentUseCase:
    """Tests pour UploadDocumentUseCase."""

    def test_upload_document_success(self):
        """Upload de document reussi."""
        mock_document_repo = Mock()
        mock_dossier_repo = Mock()
        mock_file_storage = Mock()

        mock_dossier_repo.find_by_id.return_value = Dossier(id=1, chantier_id=1, nom="Plans")
        mock_document_repo.exists_by_nom_in_dossier.return_value = False
        mock_file_storage.save.return_value = "/storage/1/1/rapport.pdf"

        def save_side_effect(doc):
            doc.id = 1
            return doc

        mock_document_repo.save.side_effect = save_side_effect

        use_case = UploadDocumentUseCase(
            document_repository=mock_document_repo,
            dossier_repository=mock_dossier_repo,
            file_storage=mock_file_storage,
        )

        file_content = BytesIO(b"PDF content")
        result = use_case.execute(
            file_content=file_content,
            filename="rapport.pdf",
            chantier_id=1,
            dossier_id=1,
            uploaded_by=1,
            taille=1024,
            mime_type="application/pdf",
        )

        assert result.id == 1
        assert result.nom == "rapport.pdf"
        assert result.type_document == "pdf"

    def test_upload_document_file_too_large(self):
        """Erreur si fichier trop gros."""
        mock_document_repo = Mock()
        mock_dossier_repo = Mock()
        mock_file_storage = Mock()

        use_case = UploadDocumentUseCase(
            document_repository=mock_document_repo,
            dossier_repository=mock_dossier_repo,
            file_storage=mock_file_storage,
        )

        file_content = BytesIO(b"content")
        with pytest.raises(FileTooLargeError):
            use_case.execute(
                file_content=file_content,
                filename="huge.pdf",
                chantier_id=1,
                dossier_id=1,
                uploaded_by=1,
                taille=11 * 1024 * 1024 * 1024,  # 11 Go
                mime_type="application/pdf",
            )

    def test_upload_document_invalid_type(self):
        """Erreur si type de fichier non supporte."""
        mock_document_repo = Mock()
        mock_dossier_repo = Mock()
        mock_file_storage = Mock()

        use_case = UploadDocumentUseCase(
            document_repository=mock_document_repo,
            dossier_repository=mock_dossier_repo,
            file_storage=mock_file_storage,
        )

        file_content = BytesIO(b"content")
        with pytest.raises(InvalidFileTypeError):
            use_case.execute(
                file_content=file_content,
                filename="virus.exe",
                chantier_id=1,
                dossier_id=1,
                uploaded_by=1,
                taille=1024,
                mime_type="application/x-executable",
            )

    def test_upload_document_dossier_not_found(self):
        """Erreur si dossier non trouve."""
        mock_document_repo = Mock()
        mock_dossier_repo = Mock()
        mock_file_storage = Mock()

        mock_dossier_repo.find_by_id.return_value = None

        use_case = UploadDocumentUseCase(
            document_repository=mock_document_repo,
            dossier_repository=mock_dossier_repo,
            file_storage=mock_file_storage,
        )

        file_content = BytesIO(b"content")
        with pytest.raises(DocDossierNotFoundError):
            use_case.execute(
                file_content=file_content,
                filename="rapport.pdf",
                chantier_id=1,
                dossier_id=999,
                uploaded_by=1,
                taille=1024,
                mime_type="application/pdf",
            )

    def test_upload_document_duplicate_rename(self):
        """Renommage automatique si doublon."""
        mock_document_repo = Mock()
        mock_dossier_repo = Mock()
        mock_file_storage = Mock()

        mock_dossier_repo.find_by_id.return_value = Dossier(id=1, chantier_id=1, nom="Plans")

        # Premier appel: existe, deuxieme: n'existe pas
        mock_document_repo.exists_by_nom_in_dossier.side_effect = [True, False]
        mock_file_storage.save.return_value = "/storage/1/1/rapport_1.pdf"

        def save_side_effect(doc):
            doc.id = 1
            return doc

        mock_document_repo.save.side_effect = save_side_effect

        use_case = UploadDocumentUseCase(
            document_repository=mock_document_repo,
            dossier_repository=mock_dossier_repo,
            file_storage=mock_file_storage,
        )

        file_content = BytesIO(b"content")
        result = use_case.execute(
            file_content=file_content,
            filename="rapport.pdf",
            chantier_id=1,
            dossier_id=1,
            uploaded_by=1,
            taille=1024,
            mime_type="application/pdf",
        )

        assert result.nom == "rapport_1.pdf"


class TestGetDocumentUseCase:
    """Tests pour GetDocumentUseCase."""

    def test_get_document_success(self):
        """Recuperation reussie."""
        mock_document_repo = Mock()

        mock_document_repo.find_by_id.return_value = Document(
            id=1,
            chantier_id=1,
            dossier_id=1,
            nom="rapport.pdf",
            nom_original="rapport.pdf",
            chemin_stockage="/storage/rapport.pdf",
            taille=1024,
            mime_type="application/pdf",
            uploaded_by=1,
        )

        use_case = GetDocumentUseCase(document_repository=mock_document_repo)
        result = use_case.execute(1)

        assert result.id == 1
        assert result.nom == "rapport.pdf"

    def test_get_document_not_found(self):
        """Erreur si document non trouve."""
        mock_document_repo = Mock()
        mock_document_repo.find_by_id.return_value = None

        use_case = GetDocumentUseCase(document_repository=mock_document_repo)

        with pytest.raises(DocumentNotFoundError):
            use_case.execute(999)


class TestListDocumentsUseCase:
    """Tests pour ListDocumentsUseCase."""

    def test_list_documents_success(self):
        """Liste des documents reussie."""
        mock_document_repo = Mock()

        documents = [
            Document(
                id=1, chantier_id=1, dossier_id=1, nom="a.pdf", nom_original="a.pdf",
                chemin_stockage="/s/a.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
            ),
            Document(
                id=2, chantier_id=1, dossier_id=1, nom="b.pdf", nom_original="b.pdf",
                chemin_stockage="/s/b.pdf", taille=2048, mime_type="application/pdf", uploaded_by=1,
            ),
        ]
        mock_document_repo.find_by_dossier.return_value = documents
        mock_document_repo.count_by_dossier.return_value = 2

        use_case = ListDocumentsUseCase(document_repository=mock_document_repo)
        result = use_case.execute(dossier_id=1)

        assert len(result.documents) == 2
        assert result.total == 2


class TestSearchDocumentsUseCase:
    """Tests pour SearchDocumentsUseCase."""

    def test_search_documents_success(self):
        """Recherche reussie."""
        mock_document_repo = Mock()

        documents = [
            Document(
                id=1, chantier_id=1, dossier_id=1, nom="plan.pdf", nom_original="plan.pdf",
                chemin_stockage="/s/plan.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
            ),
        ]
        mock_document_repo.search.return_value = (documents, 1)

        use_case = SearchDocumentsUseCase(document_repository=mock_document_repo)

        dto = DocumentSearchDTO(chantier_id=1, query="plan")
        result = use_case.execute(dto)

        assert len(result.documents) == 1
        assert result.total == 1

    def test_search_documents_with_type_filter(self):
        """Recherche avec filtre de type."""
        mock_document_repo = Mock()

        documents = [
            Document(
                id=1, chantier_id=1, dossier_id=1, nom="image.png", nom_original="image.png",
                chemin_stockage="/s/image.png", taille=1024, mime_type="image/png", uploaded_by=1,
                type_document=TypeDocument.IMAGE,
            ),
        ]
        mock_document_repo.search.return_value = (documents, 1)

        use_case = SearchDocumentsUseCase(document_repository=mock_document_repo)

        dto = DocumentSearchDTO(chantier_id=1, type_document="image")
        result = use_case.execute(dto)

        assert len(result.documents) == 1


class TestUpdateDocumentUseCase:
    """Tests pour UpdateDocumentUseCase."""

    def test_update_document_nom_success(self):
        """Mise a jour du nom reussie."""
        mock_document_repo = Mock()
        mock_dossier_repo = Mock()

        document = Document(
            id=1, chantier_id=1, dossier_id=1, nom="ancien.pdf", nom_original="ancien.pdf",
            chemin_stockage="/s/ancien.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        mock_document_repo.find_by_id.return_value = document
        mock_document_repo.save.side_effect = lambda d: d

        use_case = UpdateDocumentUseCase(
            document_repository=mock_document_repo,
            dossier_repository=mock_dossier_repo,
        )

        dto = DocumentUpdateDTO(nom="nouveau.pdf")
        result = use_case.execute(1, dto)

        assert result.nom == "nouveau.pdf"

    def test_update_document_deplacer(self):
        """Deplacement vers autre dossier."""
        mock_document_repo = Mock()
        mock_dossier_repo = Mock()

        document = Document(
            id=1, chantier_id=1, dossier_id=1, nom="test.pdf", nom_original="test.pdf",
            chemin_stockage="/s/test.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        mock_document_repo.find_by_id.return_value = document
        mock_dossier_repo.find_by_id.return_value = Dossier(id=2, chantier_id=1, nom="Autre")
        mock_document_repo.save.side_effect = lambda d: d

        use_case = UpdateDocumentUseCase(
            document_repository=mock_document_repo,
            dossier_repository=mock_dossier_repo,
        )

        dto = DocumentUpdateDTO(dossier_id=2)
        result = use_case.execute(1, dto)

        assert result.dossier_id == 2

    def test_update_document_not_found(self):
        """Erreur si document non trouve."""
        mock_document_repo = Mock()
        mock_dossier_repo = Mock()
        mock_document_repo.find_by_id.return_value = None

        use_case = UpdateDocumentUseCase(
            document_repository=mock_document_repo,
            dossier_repository=mock_dossier_repo,
        )

        dto = DocumentUpdateDTO(nom="test.pdf")
        with pytest.raises(DocumentNotFoundError):
            use_case.execute(999, dto)


class TestDeleteDocumentUseCase:
    """Tests pour DeleteDocumentUseCase."""

    def test_delete_document_success(self):
        """Suppression reussie."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()
        mock_autorisation_repo = Mock()

        document = Document(
            id=1, chantier_id=1, dossier_id=1, nom="test.pdf", nom_original="test.pdf",
            chemin_stockage="/s/test.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        mock_document_repo.find_by_id.return_value = document
        mock_document_repo.delete.return_value = True

        use_case = DeleteDocumentUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
            autorisation_repository=mock_autorisation_repo,
        )

        result = use_case.execute(1)

        assert result is True
        mock_file_storage.delete.assert_called_once_with("/s/test.pdf")
        mock_autorisation_repo.delete_by_document.assert_called_once_with(1)

    def test_delete_document_not_found(self):
        """Erreur si document non trouve."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()
        mock_autorisation_repo = Mock()
        mock_document_repo.find_by_id.return_value = None

        use_case = DeleteDocumentUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
            autorisation_repository=mock_autorisation_repo,
        )

        with pytest.raises(DocumentNotFoundError):
            use_case.execute(999)


class TestDownloadDocumentUseCase:
    """Tests pour DownloadDocumentUseCase."""

    def test_download_document_success(self):
        """Telechargement reussi."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=1, chantier_id=1, dossier_id=1, nom="test.pdf", nom_original="test.pdf",
            chemin_stockage="/s/test.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        mock_document_repo.find_by_id.return_value = document
        mock_file_storage.get_url.return_value = "https://storage.example.com/test.pdf"

        use_case = DownloadDocumentUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        url, nom, mime_type = use_case.execute(1)

        assert url == "https://storage.example.com/test.pdf"
        assert nom == "test.pdf"
        assert mime_type == "application/pdf"

    def test_download_document_not_found(self):
        """Erreur si document non trouve."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()
        mock_document_repo.find_by_id.return_value = None

        use_case = DownloadDocumentUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        with pytest.raises(DocumentNotFoundError):
            use_case.execute(999)


# ====================
# AUTORISATION USE CASES
# ====================


class TestCreateAutorisationUseCase:
    """Tests pour CreateAutorisationUseCase."""

    def test_create_autorisation_dossier_success(self):
        """Creation autorisation sur dossier reussie."""
        mock_autorisation_repo = Mock()
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        mock_dossier_repo.find_by_id.return_value = Dossier(id=1, chantier_id=1, nom="Plans")
        mock_autorisation_repo.exists.return_value = False

        def save_side_effect(autorisation):
            autorisation.id = 1
            return autorisation

        mock_autorisation_repo.save.side_effect = save_side_effect

        use_case = CreateAutorisationUseCase(
            autorisation_repository=mock_autorisation_repo,
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        dto = AutorisationCreateDTO(
            user_id=5,
            type_autorisation="lecture",
            accorde_par=1,
            dossier_id=1,
        )

        result = use_case.execute(dto)

        assert result.id == 1
        assert result.user_id == 5
        assert result.type_autorisation == "lecture"
        assert result.dossier_id == 1

    def test_create_autorisation_document_success(self):
        """Creation autorisation sur document reussie."""
        mock_autorisation_repo = Mock()
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        mock_document_repo.find_by_id.return_value = Document(
            id=1, chantier_id=1, dossier_id=1, nom="test.pdf", nom_original="test.pdf",
            chemin_stockage="/s/test.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        mock_autorisation_repo.exists.return_value = False

        def save_side_effect(autorisation):
            autorisation.id = 1
            return autorisation

        mock_autorisation_repo.save.side_effect = save_side_effect

        use_case = CreateAutorisationUseCase(
            autorisation_repository=mock_autorisation_repo,
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        dto = AutorisationCreateDTO(
            user_id=5,
            type_autorisation="ecriture",
            accorde_par=1,
            document_id=1,
        )

        result = use_case.execute(dto)

        assert result.document_id == 1
        assert result.type_autorisation == "ecriture"

    def test_create_autorisation_already_exists(self):
        """Erreur si autorisation existe deja."""
        mock_autorisation_repo = Mock()
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        mock_dossier_repo.find_by_id.return_value = Dossier(id=1, chantier_id=1, nom="Plans")
        mock_autorisation_repo.exists.return_value = True

        use_case = CreateAutorisationUseCase(
            autorisation_repository=mock_autorisation_repo,
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        dto = AutorisationCreateDTO(
            user_id=5,
            type_autorisation="lecture",
            accorde_par=1,
            dossier_id=1,
        )

        with pytest.raises(AutorisationAlreadyExistsError):
            use_case.execute(dto)

    def test_create_autorisation_invalid_target(self):
        """Erreur si cible invalide."""
        mock_autorisation_repo = Mock()
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        use_case = CreateAutorisationUseCase(
            autorisation_repository=mock_autorisation_repo,
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        dto = AutorisationCreateDTO(
            user_id=5,
            type_autorisation="lecture",
            accorde_par=1,
        )

        with pytest.raises(InvalidTargetError):
            use_case.execute(dto)

    def test_create_autorisation_dossier_not_found(self):
        """Erreur si dossier non trouve."""
        mock_autorisation_repo = Mock()
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        mock_dossier_repo.find_by_id.return_value = None

        use_case = CreateAutorisationUseCase(
            autorisation_repository=mock_autorisation_repo,
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        dto = AutorisationCreateDTO(
            user_id=5,
            type_autorisation="lecture",
            accorde_par=1,
            dossier_id=999,
        )

        with pytest.raises(InvalidTargetError):
            use_case.execute(dto)


class TestListAutorisationsUseCase:
    """Tests pour ListAutorisationsUseCase."""

    def test_list_by_dossier_success(self):
        """Liste par dossier reussie."""
        mock_autorisation_repo = Mock()

        autorisations = [
            AutorisationDocument(
                id=1, user_id=5, type_autorisation=TypeAutorisation.LECTURE,
                accorde_par=1, dossier_id=1,
            ),
        ]
        mock_autorisation_repo.find_by_dossier.return_value = autorisations

        use_case = ListAutorisationsUseCase(autorisation_repository=mock_autorisation_repo)
        result = use_case.execute_by_dossier(1)

        assert len(result.autorisations) == 1
        assert result.total == 1

    def test_list_by_document_success(self):
        """Liste par document reussie."""
        mock_autorisation_repo = Mock()

        autorisations = [
            AutorisationDocument(
                id=1, user_id=5, type_autorisation=TypeAutorisation.ECRITURE,
                accorde_par=1, document_id=1,
            ),
        ]
        mock_autorisation_repo.find_by_document.return_value = autorisations

        use_case = ListAutorisationsUseCase(autorisation_repository=mock_autorisation_repo)
        result = use_case.execute_by_document(1)

        assert len(result.autorisations) == 1

    def test_list_by_user_success(self):
        """Liste par utilisateur reussie."""
        mock_autorisation_repo = Mock()

        autorisations = [
            AutorisationDocument(
                id=1, user_id=5, type_autorisation=TypeAutorisation.LECTURE,
                accorde_par=1, dossier_id=1,
            ),
            AutorisationDocument(
                id=2, user_id=5, type_autorisation=TypeAutorisation.ADMIN,
                accorde_par=1, document_id=2,
            ),
        ]
        mock_autorisation_repo.find_by_user.return_value = autorisations

        use_case = ListAutorisationsUseCase(autorisation_repository=mock_autorisation_repo)
        result = use_case.execute_by_user(5)

        assert len(result.autorisations) == 2
        assert result.total == 2


class TestRevokeAutorisationUseCase:
    """Tests pour RevokeAutorisationUseCase."""

    def test_revoke_autorisation_success(self):
        """Revocation reussie."""
        mock_autorisation_repo = Mock()

        mock_autorisation_repo.find_by_id.return_value = AutorisationDocument(
            id=1, user_id=5, type_autorisation=TypeAutorisation.LECTURE,
            accorde_par=1, dossier_id=1,
        )
        mock_autorisation_repo.delete.return_value = True

        use_case = RevokeAutorisationUseCase(autorisation_repository=mock_autorisation_repo)
        result = use_case.execute(1)

        assert result is True

    def test_revoke_autorisation_not_found(self):
        """Erreur si autorisation non trouvee."""
        mock_autorisation_repo = Mock()
        mock_autorisation_repo.find_by_id.return_value = None

        use_case = RevokeAutorisationUseCase(autorisation_repository=mock_autorisation_repo)

        with pytest.raises(AutorisationNotFoundError):
            use_case.execute(999)


class TestCheckAccessUseCase:
    """Tests pour CheckAccessUseCase."""

    def test_can_access_dossier_success(self):
        """Verification acces dossier reussie."""
        mock_autorisation_repo = Mock()
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        mock_dossier_repo.find_by_id.return_value = Dossier(
            id=1, chantier_id=1, nom="Plans", niveau_acces=NiveauAcces.COMPAGNON,
        )
        mock_autorisation_repo.find_user_ids_for_dossier.return_value = []

        use_case = CheckAccessUseCase(
            autorisation_repository=mock_autorisation_repo,
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        result = use_case.can_access_dossier(user_id=1, user_role="compagnon", dossier_id=1)

        assert result is True

    def test_can_access_dossier_denied(self):
        """Acces dossier refuse."""
        mock_autorisation_repo = Mock()
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        mock_dossier_repo.find_by_id.return_value = Dossier(
            id=1, chantier_id=1, nom="Admin", niveau_acces=NiveauAcces.ADMIN,
        )
        mock_autorisation_repo.find_user_ids_for_dossier.return_value = []

        use_case = CheckAccessUseCase(
            autorisation_repository=mock_autorisation_repo,
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        result = use_case.can_access_dossier(user_id=1, user_role="compagnon", dossier_id=1)

        assert result is False

    def test_can_access_dossier_via_autorisation(self):
        """Acces dossier via autorisation nominative."""
        mock_autorisation_repo = Mock()
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        mock_dossier_repo.find_by_id.return_value = Dossier(
            id=1, chantier_id=1, nom="Admin", niveau_acces=NiveauAcces.ADMIN,
        )
        mock_autorisation_repo.find_user_ids_for_dossier.return_value = [5]

        use_case = CheckAccessUseCase(
            autorisation_repository=mock_autorisation_repo,
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        result = use_case.can_access_dossier(user_id=5, user_role="compagnon", dossier_id=1)

        assert result is True

    def test_can_access_document_success(self):
        """Verification acces document reussie."""
        mock_autorisation_repo = Mock()
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        mock_document_repo.find_by_id.return_value = Document(
            id=1, chantier_id=1, dossier_id=1, nom="test.pdf", nom_original="test.pdf",
            chemin_stockage="/s/test.pdf", taille=1024, mime_type="application/pdf",
            uploaded_by=1, niveau_acces=None,
        )
        mock_dossier_repo.find_by_id.return_value = Dossier(
            id=1, chantier_id=1, nom="Plans", niveau_acces=NiveauAcces.COMPAGNON,
        )
        mock_autorisation_repo.find_user_ids_for_document.return_value = []

        use_case = CheckAccessUseCase(
            autorisation_repository=mock_autorisation_repo,
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        result = use_case.can_access_document(user_id=1, user_role="compagnon", document_id=1)

        assert result is True

    def test_can_access_document_not_found(self):
        """Acces refuse si document non trouve."""
        mock_autorisation_repo = Mock()
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        mock_document_repo.find_by_id.return_value = None

        use_case = CheckAccessUseCase(
            autorisation_repository=mock_autorisation_repo,
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        result = use_case.can_access_document(user_id=1, user_role="admin", document_id=999)

        assert result is False

    def test_can_access_dossier_not_found(self):
        """Acces refuse si dossier non trouve."""
        mock_autorisation_repo = Mock()
        mock_dossier_repo = Mock()
        mock_document_repo = Mock()

        mock_dossier_repo.find_by_id.return_value = None

        use_case = CheckAccessUseCase(
            autorisation_repository=mock_autorisation_repo,
            dossier_repository=mock_dossier_repo,
            document_repository=mock_document_repo,
        )

        result = use_case.can_access_dossier(user_id=1, user_role="admin", dossier_id=999)

        assert result is False


# ====================
# GED-16: DOWNLOAD ZIP USE CASE
# ====================


class TestDownloadMultipleDocumentsUseCase:
    """Tests pour DownloadMultipleDocumentsUseCase (GED-16)."""

    def test_download_multiple_documents_success(self):
        """Telechargement ZIP de plusieurs documents reussi."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        # Configuration des documents
        doc1 = Document(
            id=1, chantier_id=1, dossier_id=1, nom="rapport.pdf", nom_original="rapport.pdf",
            chemin_stockage="/s/rapport.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        doc2 = Document(
            id=2, chantier_id=1, dossier_id=1, nom="plan.dwg", nom_original="plan.dwg",
            chemin_stockage="/s/plan.dwg", taille=2048, mime_type="application/acad", uploaded_by=1,
        )

        mock_document_repo.find_by_id.side_effect = lambda doc_id: {1: doc1, 2: doc2}.get(doc_id)
        mock_file_storage.create_zip.return_value = BytesIO(b"PK ZIP content")

        use_case = DownloadMultipleDocumentsUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        dto = DownloadZipDTO(document_ids=[1, 2])
        result = use_case.execute(dto)

        assert result is not None
        mock_file_storage.create_zip.assert_called_once()
        call_args = mock_file_storage.create_zip.call_args[0]
        assert len(call_args[0]) == 2  # 2 fichiers dans l'archive
        assert call_args[1] == "documents.zip"

    def test_download_multiple_documents_no_ids_specified(self):
        """Erreur si aucun document specifie."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        use_case = DownloadMultipleDocumentsUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        dto = DownloadZipDTO(document_ids=[])
        with pytest.raises(DocumentNotFoundError, match="Aucun document spécifié"):
            use_case.execute(dto)

    def test_download_multiple_documents_no_valid_documents(self):
        """Erreur si aucun document valide trouve."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        # Aucun document n'existe
        mock_document_repo.find_by_id.return_value = None

        use_case = DownloadMultipleDocumentsUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        dto = DownloadZipDTO(document_ids=[999, 888])
        with pytest.raises(DocumentNotFoundError, match="Aucun document valide trouvé"):
            use_case.execute(dto)

    def test_download_multiple_documents_duplicate_names(self):
        """Gestion des doublons de noms dans l'archive."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        # Deux documents avec le meme nom
        doc1 = Document(
            id=1, chantier_id=1, dossier_id=1, nom="rapport.pdf", nom_original="rapport.pdf",
            chemin_stockage="/s/1/rapport.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        doc2 = Document(
            id=2, chantier_id=1, dossier_id=2, nom="rapport.pdf", nom_original="rapport.pdf",
            chemin_stockage="/s/2/rapport.pdf", taille=2048, mime_type="application/pdf", uploaded_by=1,
        )

        mock_document_repo.find_by_id.side_effect = lambda doc_id: {1: doc1, 2: doc2}.get(doc_id)
        mock_file_storage.create_zip.return_value = BytesIO(b"PK ZIP content")

        use_case = DownloadMultipleDocumentsUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        dto = DownloadZipDTO(document_ids=[1, 2])
        result = use_case.execute(dto)

        assert result is not None
        call_args = mock_file_storage.create_zip.call_args[0]
        files = call_args[0]
        noms = [f[1] for f in files]
        # Les noms doivent etre differents
        assert len(set(noms)) == 2
        assert "rapport.pdf" in noms
        assert "rapport_1.pdf" in noms

    def test_download_multiple_documents_partial_valid(self):
        """Telechargement avec certains documents valides seulement."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        doc1 = Document(
            id=1, chantier_id=1, dossier_id=1, nom="rapport.pdf", nom_original="rapport.pdf",
            chemin_stockage="/s/rapport.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )

        # Doc1 existe, Doc2 n'existe pas
        mock_document_repo.find_by_id.side_effect = lambda doc_id: doc1 if doc_id == 1 else None
        mock_file_storage.create_zip.return_value = BytesIO(b"PK ZIP content")

        use_case = DownloadMultipleDocumentsUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        dto = DownloadZipDTO(document_ids=[1, 999])
        result = use_case.execute(dto)

        assert result is not None
        call_args = mock_file_storage.create_zip.call_args[0]
        assert len(call_args[0]) == 1  # Seulement 1 fichier valide

    def test_download_multiple_documents_zip_creation_error(self):
        """Erreur lors de la creation de l'archive."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        doc1 = Document(
            id=1, chantier_id=1, dossier_id=1, nom="rapport.pdf", nom_original="rapport.pdf",
            chemin_stockage="/s/rapport.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        mock_document_repo.find_by_id.return_value = doc1
        mock_file_storage.create_zip.return_value = None  # Erreur de creation

        use_case = DownloadMultipleDocumentsUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        dto = DownloadZipDTO(document_ids=[1])
        with pytest.raises(DocumentNotFoundError, match="Erreur lors de la création de l'archive"):
            use_case.execute(dto)


# ====================
# GED-17: PREVIEW USE CASES
# ====================


class TestGetDocumentPreviewUseCase:
    """Tests pour GetDocumentPreviewUseCase (GED-17)."""

    def test_preview_pdf_document_success(self):
        """Previsualisation document PDF reussie."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=1, chantier_id=1, dossier_id=1, nom="rapport.pdf", nom_original="rapport.pdf",
            chemin_stockage="/s/rapport.pdf", taille=1024 * 1024,  # 1 MB
            mime_type="application/pdf", uploaded_by=1, type_document=TypeDocument.PDF,
        )
        mock_document_repo.find_by_id.return_value = document

        use_case = GetDocumentPreviewUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        result = use_case.execute(1)

        assert result.id == 1
        assert result.nom == "rapport.pdf"
        assert result.can_preview is True
        assert result.preview_url == "/api/documents/1/preview/content"
        assert result.type_document == "pdf"

    def test_preview_image_document_success(self):
        """Previsualisation document image reussie."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=2, chantier_id=1, dossier_id=1, nom="photo.jpg", nom_original="photo.jpg",
            chemin_stockage="/s/photo.jpg", taille=500 * 1024,  # 500 KB
            mime_type="image/jpeg", uploaded_by=1, type_document=TypeDocument.IMAGE,
        )
        mock_document_repo.find_by_id.return_value = document

        use_case = GetDocumentPreviewUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        result = use_case.execute(2)

        assert result.id == 2
        assert result.nom == "photo.jpg"
        assert result.can_preview is True
        assert result.preview_url == "/api/documents/2/preview/content"
        assert result.type_document == "image"

    def test_preview_document_too_large(self):
        """Document trop gros pour la previsualisation (>10MB)."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=3, chantier_id=1, dossier_id=1, nom="gros_fichier.pdf", nom_original="gros_fichier.pdf",
            chemin_stockage="/s/gros_fichier.pdf", taille=15 * 1024 * 1024,  # 15 MB
            mime_type="application/pdf", uploaded_by=1, type_document=TypeDocument.PDF,
        )
        mock_document_repo.find_by_id.return_value = document

        use_case = GetDocumentPreviewUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        result = use_case.execute(3)

        assert result.id == 3
        assert result.can_preview is False
        assert result.preview_url is None

    def test_preview_non_previewable_type(self):
        """Type de document non previsualisable."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=4, chantier_id=1, dossier_id=1, nom="plan.dwg", nom_original="plan.dwg",
            chemin_stockage="/s/plan.dwg", taille=1024 * 1024,  # 1 MB
            mime_type="application/acad", uploaded_by=1, type_document=TypeDocument.AUTRE,
        )
        mock_document_repo.find_by_id.return_value = document

        use_case = GetDocumentPreviewUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        result = use_case.execute(4)

        assert result.id == 4
        assert result.can_preview is False
        assert result.preview_url is None

    def test_preview_document_not_found(self):
        """Erreur si document non trouve."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()
        mock_document_repo.find_by_id.return_value = None

        use_case = GetDocumentPreviewUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        with pytest.raises(DocumentNotFoundError):
            use_case.execute(999)

    def test_preview_video_document_success(self):
        """Previsualisation document video reussie."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=5, chantier_id=1, dossier_id=1, nom="video.mp4", nom_original="video.mp4",
            chemin_stockage="/s/video.mp4", taille=5 * 1024 * 1024,  # 5 MB
            mime_type="video/mp4", uploaded_by=1, type_document=TypeDocument.VIDEO,
        )
        mock_document_repo.find_by_id.return_value = document

        use_case = GetDocumentPreviewUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        result = use_case.execute(5)

        assert result.id == 5
        assert result.can_preview is True
        assert result.preview_url == "/api/documents/5/preview/content"

    def test_preview_excel_document_not_previewable(self):
        """Type de document Excel non previsualisable."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=6, chantier_id=1, dossier_id=1, nom="budget.xlsx", nom_original="budget.xlsx",
            chemin_stockage="/s/budget.xlsx", taille=1024,  # 1 KB
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            uploaded_by=1, type_document=TypeDocument.EXCEL,
        )
        mock_document_repo.find_by_id.return_value = document

        use_case = GetDocumentPreviewUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        result = use_case.execute(6)

        assert result.id == 6
        # Excel n'est pas dans PREVIEWABLE_TYPES
        assert result.can_preview is False
        assert result.preview_url is None

    def test_preview_exactly_10mb(self):
        """Document de exactement 10MB - a la limite."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=7, chantier_id=1, dossier_id=1, nom="limite.pdf", nom_original="limite.pdf",
            chemin_stockage="/s/limite.pdf", taille=10 * 1024 * 1024,  # Exactement 10 MB
            mime_type="application/pdf", uploaded_by=1, type_document=TypeDocument.PDF,
        )
        mock_document_repo.find_by_id.return_value = document

        use_case = GetDocumentPreviewUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        result = use_case.execute(7)

        # A la limite exacte, le document PEUT etre previsualize (comparaison > stricte)
        assert result.can_preview is True
        assert result.preview_url == "/api/documents/7/preview/content"

    def test_preview_over_10mb(self):
        """Document juste au-dessus de 10MB - depasse la limite."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=8, chantier_id=1, dossier_id=1, nom="trop_gros.pdf", nom_original="trop_gros.pdf",
            chemin_stockage="/s/trop_gros.pdf", taille=(10 * 1024 * 1024) + 1,  # 10 MB + 1 byte
            mime_type="application/pdf", uploaded_by=1, type_document=TypeDocument.PDF,
        )
        mock_document_repo.find_by_id.return_value = document

        use_case = GetDocumentPreviewUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        result = use_case.execute(8)

        # Juste au-dessus de la limite, le document ne peut PAS etre previsualize
        assert result.can_preview is False
        assert result.preview_url is None


class TestGetDocumentPreviewContentUseCase:
    """Tests pour GetDocumentPreviewContentUseCase (GED-17)."""

    def test_get_preview_content_success(self):
        """Recuperation du contenu de previsualisation reussie."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=1, chantier_id=1, dossier_id=1, nom="rapport.pdf", nom_original="rapport.pdf",
            chemin_stockage="/s/rapport.pdf", taille=1024 * 1024,  # 1 MB
            mime_type="application/pdf", uploaded_by=1, type_document=TypeDocument.PDF,
        )
        mock_document_repo.find_by_id.return_value = document
        mock_file_storage.get_preview_data.return_value = (b"PDF content", "application/pdf")

        use_case = GetDocumentPreviewContentUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        content, mime_type = use_case.execute(1)

        assert content == b"PDF content"
        assert mime_type == "application/pdf"
        mock_file_storage.get_preview_data.assert_called_once_with(
            "/s/rapport.pdf", 10 * 1024 * 1024
        )

    def test_get_preview_content_document_too_large(self):
        """Erreur si document trop gros pour previsualisation."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=2, chantier_id=1, dossier_id=1, nom="gros.pdf", nom_original="gros.pdf",
            chemin_stockage="/s/gros.pdf", taille=15 * 1024 * 1024,  # 15 MB
            mime_type="application/pdf", uploaded_by=1, type_document=TypeDocument.PDF,
        )
        mock_document_repo.find_by_id.return_value = document

        use_case = GetDocumentPreviewContentUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        with pytest.raises(FileTooLargeError, match="trop volumineux pour la prévisualisation"):
            use_case.execute(2)

    def test_get_preview_content_document_not_found(self):
        """Erreur si document non trouve."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()
        mock_document_repo.find_by_id.return_value = None

        use_case = GetDocumentPreviewContentUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        with pytest.raises(DocumentNotFoundError):
            use_case.execute(999)

    def test_get_preview_content_file_read_error(self):
        """Erreur si lecture du fichier echoue."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=3, chantier_id=1, dossier_id=1, nom="rapport.pdf", nom_original="rapport.pdf",
            chemin_stockage="/s/rapport.pdf", taille=1024 * 1024,  # 1 MB
            mime_type="application/pdf", uploaded_by=1, type_document=TypeDocument.PDF,
        )
        mock_document_repo.find_by_id.return_value = document
        mock_file_storage.get_preview_data.return_value = None  # Erreur de lecture

        use_case = GetDocumentPreviewContentUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        with pytest.raises(DocumentNotFoundError, match="Impossible de lire le contenu"):
            use_case.execute(3)

    def test_get_preview_content_image(self):
        """Recuperation du contenu d'une image."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=4, chantier_id=1, dossier_id=1, nom="photo.jpg", nom_original="photo.jpg",
            chemin_stockage="/s/photo.jpg", taille=500 * 1024,  # 500 KB
            mime_type="image/jpeg", uploaded_by=1, type_document=TypeDocument.IMAGE,
        )
        mock_document_repo.find_by_id.return_value = document
        mock_file_storage.get_preview_data.return_value = (b"\xff\xd8\xff JPEG data", "image/jpeg")

        use_case = GetDocumentPreviewContentUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        content, mime_type = use_case.execute(4)

        assert content == b"\xff\xd8\xff JPEG data"
        assert mime_type == "image/jpeg"

    def test_get_preview_content_exactly_at_limit(self):
        """Document a la limite exacte de 10MB - est accepte."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=5, chantier_id=1, dossier_id=1, nom="limite.pdf", nom_original="limite.pdf",
            chemin_stockage="/s/limite.pdf", taille=10 * 1024 * 1024,  # Exactement 10 MB
            mime_type="application/pdf", uploaded_by=1, type_document=TypeDocument.PDF,
        )
        mock_document_repo.find_by_id.return_value = document
        mock_file_storage.get_preview_data.return_value = (b"PDF content", "application/pdf")

        use_case = GetDocumentPreviewContentUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        # A la limite exacte, le document PEUT etre recupere (comparaison > stricte)
        content, mime_type = use_case.execute(5)

        assert content == b"PDF content"
        assert mime_type == "application/pdf"

    def test_get_preview_content_over_limit(self):
        """Document juste au-dessus de 10MB - refuse."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=7, chantier_id=1, dossier_id=1, nom="trop_gros.pdf", nom_original="trop_gros.pdf",
            chemin_stockage="/s/trop_gros.pdf", taille=(10 * 1024 * 1024) + 1,  # 10 MB + 1 byte
            mime_type="application/pdf", uploaded_by=1, type_document=TypeDocument.PDF,
        )
        mock_document_repo.find_by_id.return_value = document

        use_case = GetDocumentPreviewContentUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        # Juste au-dessus de la limite, erreur
        with pytest.raises(FileTooLargeError):
            use_case.execute(7)

    def test_get_preview_content_just_under_limit(self):
        """Document juste en dessous de la limite."""
        mock_document_repo = Mock()
        mock_file_storage = Mock()

        document = Document(
            id=6, chantier_id=1, dossier_id=1, nom="ok.pdf", nom_original="ok.pdf",
            chemin_stockage="/s/ok.pdf", taille=(10 * 1024 * 1024) - 1,  # 10 MB - 1 byte
            mime_type="application/pdf", uploaded_by=1, type_document=TypeDocument.PDF,
        )
        mock_document_repo.find_by_id.return_value = document
        mock_file_storage.get_preview_data.return_value = (b"PDF content", "application/pdf")

        use_case = GetDocumentPreviewContentUseCase(
            document_repository=mock_document_repo,
            file_storage=mock_file_storage,
        )

        content, mime_type = use_case.execute(6)

        assert content == b"PDF content"
        assert mime_type == "application/pdf"
