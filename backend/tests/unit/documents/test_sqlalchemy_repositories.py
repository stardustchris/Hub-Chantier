"""Tests unitaires pour les repositories SQLAlchemy du module Documents."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from modules.documents.domain.entities import Document, Dossier, AutorisationDocument, TypeAutorisation
from modules.documents.domain.value_objects import TypeDocument, NiveauAcces, DossierType
from modules.documents.infrastructure.persistence.sqlalchemy_document_repository import SQLAlchemyDocumentRepository
from modules.documents.infrastructure.persistence.sqlalchemy_dossier_repository import SQLAlchemyDossierRepository
from modules.documents.infrastructure.persistence.sqlalchemy_autorisation_repository import SQLAlchemyAutorisationRepository


class TestSQLAlchemyDocumentRepository:
    """Tests pour SQLAlchemyDocumentRepository."""

    def test_init(self):
        """Test initialisation du repository."""
        session = Mock()
        repo = SQLAlchemyDocumentRepository(session)

        assert repo._session == session

    def test_find_by_id_found(self):
        """Test find_by_id quand document trouvé."""
        session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.chantier_id = 2
        mock_model.dossier_id = 3
        mock_model.nom = "test.pdf"
        mock_model.nom_original = "test.pdf"
        mock_model.type_document = "pdf"  # Valeur valide de TypeDocument
        mock_model.taille = 1024
        mock_model.chemin_stockage = "/path/to/file"
        mock_model.mime_type = "application/pdf"
        mock_model.niveau_acces = "compagnon"  # Valeur valide de NiveauAcces
        mock_model.uploaded_by = 5
        mock_model.description = "Description"
        mock_model.version = 1
        mock_model.uploaded_at = datetime.now()
        mock_model.updated_at = datetime.now()

        session.query.return_value.filter_by.return_value.first.return_value = mock_model

        repo = SQLAlchemyDocumentRepository(session)
        result = repo.find_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.nom == "test.pdf"

    def test_find_by_id_not_found(self):
        """Test find_by_id quand document non trouvé."""
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = None

        repo = SQLAlchemyDocumentRepository(session)
        result = repo.find_by_id(999)

        assert result is None

    def test_delete_existing(self):
        """Test suppression document existant."""
        session = Mock()
        mock_model = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = mock_model

        repo = SQLAlchemyDocumentRepository(session)
        result = repo.delete(1)

        assert result is True
        session.delete.assert_called_once_with(mock_model)
        session.flush.assert_called_once()

    def test_delete_not_existing(self):
        """Test suppression document non existant."""
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = None

        repo = SQLAlchemyDocumentRepository(session)
        result = repo.delete(999)

        assert result is False
        session.delete.assert_not_called()

    def test_find_by_dossier(self):
        """Test récupération documents par dossier."""
        session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.chantier_id = 2
        mock_model.dossier_id = 3
        mock_model.nom = "test.pdf"
        mock_model.nom_original = "test.pdf"
        mock_model.type_document = "pdf"  # Valeur valide de TypeDocument
        mock_model.taille = 1024
        mock_model.chemin_stockage = "/path/to/file"
        mock_model.mime_type = "application/pdf"
        mock_model.niveau_acces = None
        mock_model.uploaded_by = 5
        mock_model.description = None
        mock_model.version = 1
        mock_model.uploaded_at = datetime.now()
        mock_model.updated_at = datetime.now()

        query_mock = Mock()
        session.query.return_value = query_mock
        query_mock.filter_by.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = [mock_model]

        repo = SQLAlchemyDocumentRepository(session)
        result = repo.find_by_dossier(3)

        assert len(result) == 1
        assert result[0].dossier_id == 3

    def test_find_by_chantier(self):
        """Test récupération documents par chantier."""
        session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.chantier_id = 2
        mock_model.dossier_id = 3
        mock_model.nom = "test.pdf"
        mock_model.nom_original = "test.pdf"
        mock_model.type_document = "pdf"  # Valeur valide de TypeDocument
        mock_model.taille = 1024
        mock_model.chemin_stockage = "/path/to/file"
        mock_model.mime_type = "application/pdf"
        mock_model.niveau_acces = None
        mock_model.uploaded_by = 5
        mock_model.description = None
        mock_model.version = 1
        mock_model.uploaded_at = datetime.now()
        mock_model.updated_at = datetime.now()

        query_mock = Mock()
        session.query.return_value = query_mock
        query_mock.filter_by.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = [mock_model]

        repo = SQLAlchemyDocumentRepository(session)
        result = repo.find_by_chantier(2)

        assert len(result) == 1
        assert result[0].chantier_id == 2

    def test_count_by_dossier(self):
        """Test comptage documents par dossier."""
        session = Mock()
        session.query.return_value.filter_by.return_value.count.return_value = 5

        repo = SQLAlchemyDocumentRepository(session)
        result = repo.count_by_dossier(3)

        assert result == 5

    def test_count_by_chantier(self):
        """Test comptage documents par chantier."""
        session = Mock()
        session.query.return_value.filter_by.return_value.count.return_value = 10

        repo = SQLAlchemyDocumentRepository(session)
        result = repo.count_by_chantier(2)

        assert result == 10

    def test_exists_by_nom_in_dossier_true(self):
        """Test existence nom dans dossier - existe."""
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = Mock()

        repo = SQLAlchemyDocumentRepository(session)
        result = repo.exists_by_nom_in_dossier("test.pdf", 3)

        assert result is True

    def test_exists_by_nom_in_dossier_false(self):
        """Test existence nom dans dossier - n'existe pas."""
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = None

        repo = SQLAlchemyDocumentRepository(session)
        result = repo.exists_by_nom_in_dossier("test.pdf", 3)

        assert result is False

    def test_get_total_size_by_chantier(self):
        """Test calcul taille totale par chantier."""
        session = Mock()
        session.query.return_value.filter_by.return_value.scalar.return_value = 5000

        repo = SQLAlchemyDocumentRepository(session)
        result = repo.get_total_size_by_chantier(2)

        assert result == 5000

    def test_get_total_size_by_chantier_none(self):
        """Test calcul taille totale retourne 0 si None."""
        session = Mock()
        session.query.return_value.filter_by.return_value.scalar.return_value = None

        repo = SQLAlchemyDocumentRepository(session)
        result = repo.get_total_size_by_chantier(2)

        assert result == 0


class TestSQLAlchemyDossierRepository:
    """Tests pour SQLAlchemyDossierRepository."""

    def test_init(self):
        """Test initialisation du repository."""
        session = Mock()
        repo = SQLAlchemyDossierRepository(session)

        assert repo._session == session

    def test_find_by_id_found(self):
        """Test find_by_id quand dossier trouvé."""
        session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.chantier_id = 2
        mock_model.nom = "Plans"
        mock_model.type_dossier = "01_plans"  # Valeur valide de DossierType
        mock_model.niveau_acces = "compagnon"  # Valeur valide de NiveauAcces
        mock_model.parent_id = None
        mock_model.ordre = 0
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        session.query.return_value.filter_by.return_value.first.return_value = mock_model

        repo = SQLAlchemyDossierRepository(session)
        result = repo.find_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.nom == "Plans"

    def test_find_by_id_not_found(self):
        """Test find_by_id quand dossier non trouvé."""
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = None

        repo = SQLAlchemyDossierRepository(session)
        result = repo.find_by_id(999)

        assert result is None

    def test_delete_existing(self):
        """Test suppression dossier existant."""
        session = Mock()
        mock_model = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = mock_model

        repo = SQLAlchemyDossierRepository(session)
        result = repo.delete(1)

        assert result is True
        session.delete.assert_called_once_with(mock_model)
        session.flush.assert_called_once()

    def test_delete_not_existing(self):
        """Test suppression dossier non existant."""
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = None

        repo = SQLAlchemyDossierRepository(session)
        result = repo.delete(999)

        assert result is False
        session.delete.assert_not_called()

    def test_find_children(self):
        """Test récupération sous-dossiers."""
        session = Mock()
        mock_model = Mock()
        mock_model.id = 2
        mock_model.chantier_id = 1
        mock_model.nom = "Sous-dossier"
        mock_model.type_dossier = "custom"  # Valeur valide de DossierType
        mock_model.niveau_acces = "compagnon"  # Valeur valide de NiveauAcces
        mock_model.parent_id = 1
        mock_model.ordre = 0
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        query_mock = Mock()
        session.query.return_value = query_mock
        query_mock.filter_by.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.all.return_value = [mock_model]

        repo = SQLAlchemyDossierRepository(session)
        result = repo.find_children(1)

        assert len(result) == 1
        assert result[0].parent_id == 1

    def test_count_by_chantier(self):
        """Test comptage dossiers par chantier."""
        session = Mock()
        session.query.return_value.filter_by.return_value.count.return_value = 3

        repo = SQLAlchemyDossierRepository(session)
        result = repo.count_by_chantier(2)

        assert result == 3

    def test_has_documents_true(self):
        """Test si dossier contient des documents - oui."""
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = Mock()

        repo = SQLAlchemyDossierRepository(session)
        result = repo.has_documents(1)

        assert result is True

    def test_has_documents_false(self):
        """Test si dossier contient des documents - non."""
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = None

        repo = SQLAlchemyDossierRepository(session)
        result = repo.has_documents(1)

        assert result is False

    def test_has_children_true(self):
        """Test si dossier a des sous-dossiers - oui."""
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = Mock()

        repo = SQLAlchemyDossierRepository(session)
        result = repo.has_children(1)

        assert result is True

    def test_has_children_false(self):
        """Test si dossier a des sous-dossiers - non."""
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = None

        repo = SQLAlchemyDossierRepository(session)
        result = repo.has_children(1)

        assert result is False


class TestSQLAlchemyAutorisationRepository:
    """Tests pour SQLAlchemyAutorisationRepository."""

    def test_init(self):
        """Test initialisation du repository."""
        session = Mock()
        repo = SQLAlchemyAutorisationRepository(session)

        assert repo._session == session

    def test_find_by_id_found(self):
        """Test find_by_id quand autorisation trouvée."""
        session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.user_id = 2
        mock_model.type_autorisation = "lecture"
        mock_model.dossier_id = 3
        mock_model.document_id = None
        mock_model.accorde_par = 4
        mock_model.created_at = datetime.now()
        mock_model.expire_at = None

        session.query.return_value.filter_by.return_value.first.return_value = mock_model

        repo = SQLAlchemyAutorisationRepository(session)
        result = repo.find_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.user_id == 2

    def test_find_by_id_not_found(self):
        """Test find_by_id quand autorisation non trouvée."""
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = None

        repo = SQLAlchemyAutorisationRepository(session)
        result = repo.find_by_id(999)

        assert result is None

    def test_delete_existing(self):
        """Test suppression autorisation existante."""
        session = Mock()
        mock_model = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = mock_model

        repo = SQLAlchemyAutorisationRepository(session)
        result = repo.delete(1)

        assert result is True
        session.delete.assert_called_once_with(mock_model)
        session.flush.assert_called_once()

    def test_delete_not_existing(self):
        """Test suppression autorisation non existante."""
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = None

        repo = SQLAlchemyAutorisationRepository(session)
        result = repo.delete(999)

        assert result is False
        session.delete.assert_not_called()

    def test_find_by_dossier(self):
        """Test récupération autorisations par dossier."""
        session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.user_id = 2
        mock_model.type_autorisation = "lecture"
        mock_model.dossier_id = 3
        mock_model.document_id = None
        mock_model.accorde_par = 4
        mock_model.created_at = datetime.now()
        mock_model.expire_at = None

        session.query.return_value.filter_by.return_value.all.return_value = [mock_model]

        repo = SQLAlchemyAutorisationRepository(session)
        result = repo.find_by_dossier(3)

        assert len(result) == 1
        assert result[0].dossier_id == 3

    def test_find_by_document(self):
        """Test récupération autorisations par document."""
        session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.user_id = 2
        mock_model.type_autorisation = "lecture"
        mock_model.dossier_id = None
        mock_model.document_id = 5
        mock_model.accorde_par = 4
        mock_model.created_at = datetime.now()
        mock_model.expire_at = None

        session.query.return_value.filter_by.return_value.all.return_value = [mock_model]

        repo = SQLAlchemyAutorisationRepository(session)
        result = repo.find_by_document(5)

        assert len(result) == 1
        assert result[0].document_id == 5

    def test_find_by_user(self):
        """Test récupération autorisations par utilisateur."""
        session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.user_id = 2
        mock_model.type_autorisation = "lecture"
        mock_model.dossier_id = 3
        mock_model.document_id = None
        mock_model.accorde_par = 4
        mock_model.created_at = datetime.now()
        mock_model.expire_at = None

        session.query.return_value.filter_by.return_value.all.return_value = [mock_model]

        repo = SQLAlchemyAutorisationRepository(session)
        result = repo.find_by_user(2)

        assert len(result) == 1
        assert result[0].user_id == 2

    def test_exists_true(self):
        """Test existence autorisation - existe."""
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = Mock()

        repo = SQLAlchemyAutorisationRepository(session)
        result = repo.exists(user_id=2, dossier_id=3)

        assert result is True

    def test_exists_false(self):
        """Test existence autorisation - n'existe pas."""
        session = Mock()
        # Le mock doit supporter la chaîne filter_by().filter_by().first()
        query_mock = Mock()
        session.query.return_value = query_mock
        query_mock.filter_by.return_value = query_mock
        query_mock.first.return_value = None

        repo = SQLAlchemyAutorisationRepository(session)
        result = repo.exists(user_id=2, dossier_id=3)

        assert result is False

    def test_delete_by_dossier(self):
        """Test suppression autorisations par dossier."""
        session = Mock()
        session.query.return_value.filter_by.return_value.delete.return_value = 3

        repo = SQLAlchemyAutorisationRepository(session)
        result = repo.delete_by_dossier(5)

        assert result == 3
        session.flush.assert_called_once()

    def test_delete_by_document(self):
        """Test suppression autorisations par document."""
        session = Mock()
        session.query.return_value.filter_by.return_value.delete.return_value = 2

        repo = SQLAlchemyAutorisationRepository(session)
        result = repo.delete_by_document(5)

        assert result == 2
        session.flush.assert_called_once()

    def test_delete_expired(self):
        """Test suppression autorisations expirées."""
        session = Mock()
        session.query.return_value.filter.return_value.delete.return_value = 5

        repo = SQLAlchemyAutorisationRepository(session)
        result = repo.delete_expired()

        assert result == 5
        session.flush.assert_called_once()
