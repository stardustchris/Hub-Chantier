"""Tests unitaires pour les dépendances du module Documents."""

from unittest.mock import Mock, patch

from modules.documents.infrastructure.web.dependencies import (
    get_file_storage,
    get_document_controller,
)
from modules.documents.adapters.providers import LocalFileStorageService
from modules.documents.adapters.controllers import DocumentController


class TestGetFileStorage:
    """Tests pour get_file_storage."""

    def test_returns_local_file_storage(self):
        """Retourne une instance LocalFileStorageService."""
        storage = get_file_storage()
        assert isinstance(storage, LocalFileStorageService)


class TestGetDocumentController:
    """Tests pour get_document_controller."""

    def test_returns_document_controller(self):
        """Retourne un DocumentController avec toutes les dépendances."""
        mock_db = Mock()
        mock_storage = Mock(spec=LocalFileStorageService)

        controller = get_document_controller(db=mock_db, file_storage=mock_storage)
        assert isinstance(controller, DocumentController)

    def test_controller_has_all_use_cases(self):
        """Le controller a tous les use cases injectés."""
        mock_db = Mock()
        mock_storage = Mock(spec=LocalFileStorageService)

        controller = get_document_controller(db=mock_db, file_storage=mock_storage)

        # Vérifier que les attributs principaux existent
        assert hasattr(controller, 'upload_document')
        assert hasattr(controller, 'get_document')
        assert hasattr(controller, 'list_documents')
        assert hasattr(controller, 'delete_document')
        assert hasattr(controller, 'create_dossier')
        assert hasattr(controller, 'list_dossiers')
        assert hasattr(controller, 'init_arborescence')
