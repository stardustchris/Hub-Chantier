"""Tests unitaires pour le service AuditService."""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from uuid import uuid4

from modules.shared.application.services.audit_service import AuditService, AuditServiceError
from modules.shared.domain.entities.audit_entry import AuditEntry
from modules.shared.domain.repositories.audit_repository import AuditRepository


class TestAuditService:
    """Tests pour le service AuditService."""

    @pytest.fixture
    def mock_repository(self):
        """Fixture pour un repository mocké."""
        return Mock(spec=AuditRepository)

    @pytest.fixture
    def service(self, mock_repository):
        """Fixture pour le service avec repository mocké."""
        return AuditService(repository=mock_repository)

    def test_log_creates_entry_and_persists(self, service, mock_repository):
        """Test que log() crée et persiste une entrée d'audit."""
        # Arrange
        entry_id = uuid4()
        saved_entry = AuditEntry(
            id=entry_id,
            entity_type="devis",
            entity_id="123",
            action="created",
            author_id=1,
            author_name="Jean Dupont",
        )
        mock_repository.save.return_value = saved_entry

        # Act
        result = service.log(
            entity_type="devis",
            entity_id="123",
            action="created",
            author_id=1,
            author_name="Jean Dupont",
        )

        # Assert
        assert mock_repository.save.called
        assert result.id == str(entry_id)
        assert result.entity_type == "devis"
        assert result.action == "created"

    def test_log_with_field_change(self, service, mock_repository):
        """Test log() avec modification de champ."""
        # Arrange
        saved_entry = AuditEntry(
            entity_type="devis",
            entity_id="123",
            action="updated",
            field_name="montant_ht",
            old_value="10000.0",
            new_value="12000.0",
            author_id=1,
            author_name="Jean Dupont",
        )
        mock_repository.save.return_value = saved_entry

        # Act
        result = service.log(
            entity_type="devis",
            entity_id="123",
            action="updated",
            author_id=1,
            author_name="Jean Dupont",
            field_name="montant_ht",
            old_value=10000.00,
            new_value=12000.00,
        )

        # Assert
        assert result.field_name == "montant_ht"
        assert result.old_value == "10000.0"
        assert result.new_value == "12000.0"

    def test_log_invalid_data_raises_error(self, service, mock_repository):
        """Test que log() avec données invalides lève une erreur."""
        # Act & Assert
        with pytest.raises(AuditServiceError, match="Données d'audit invalides"):
            service.log(
                entity_type="",  # entity_type vide
                entity_id="123",
                action="created",
                author_id=1,
                author_name="Jean Dupont",
            )

    def test_log_creation_helper(self, service, mock_repository):
        """Test helper log_creation()."""
        # Arrange
        saved_entry = AuditEntry.create_for_creation(
            entity_type="devis",
            entity_id="123",
            author_id=1,
            author_name="Jean Dupont",
        )
        mock_repository.save.return_value = saved_entry

        # Act
        result = service.log_creation(
            entity_type="devis",
            entity_id="123",
            author_id=1,
            author_name="Jean Dupont",
        )

        # Assert
        assert result.action == "created"
        assert mock_repository.save.called

    def test_log_update_helper(self, service, mock_repository):
        """Test helper log_update()."""
        # Arrange
        saved_entry = AuditEntry.create_for_update(
            entity_type="devis",
            entity_id="123",
            field_name="montant_ht",
            old_value=10000.00,
            new_value=12000.00,
            author_id=1,
            author_name="Jean Dupont",
        )
        mock_repository.save.return_value = saved_entry

        # Act
        result = service.log_update(
            entity_type="devis",
            entity_id="123",
            field_name="montant_ht",
            old_value=10000.00,
            new_value=12000.00,
            author_id=1,
            author_name="Jean Dupont",
        )

        # Assert
        assert result.action == "updated"
        assert result.field_name == "montant_ht"
        assert mock_repository.save.called

    def test_log_deletion_helper(self, service, mock_repository):
        """Test helper log_deletion()."""
        # Arrange
        saved_entry = AuditEntry.create_for_deletion(
            entity_type="devis",
            entity_id="123",
            author_id=1,
            author_name="Jean Dupont",
        )
        mock_repository.save.return_value = saved_entry

        # Act
        result = service.log_deletion(
            entity_type="devis",
            entity_id="123",
            author_id=1,
            author_name="Jean Dupont",
        )

        # Assert
        assert result.action == "deleted"
        assert mock_repository.save.called

    def test_log_status_change_helper(self, service, mock_repository):
        """Test helper log_status_change()."""
        # Arrange
        saved_entry = AuditEntry.create_for_status_change(
            entity_type="devis",
            entity_id="123",
            old_status="brouillon",
            new_status="valide",
            author_id=1,
            author_name="Jean Dupont",
        )
        mock_repository.save.return_value = saved_entry

        # Act
        result = service.log_status_change(
            entity_type="devis",
            entity_id="123",
            old_status="brouillon",
            new_status="valide",
            author_id=1,
            author_name="Jean Dupont",
        )

        # Assert
        assert result.action == "status_changed"
        assert result.old_value == "brouillon"
        assert result.new_value == "valide"
        assert mock_repository.save.called

    def test_get_history_returns_entries(self, service, mock_repository):
        """Test get_history() retourne les entrées."""
        # Arrange
        entries = [
            AuditEntry(
                entity_type="devis",
                entity_id="123",
                action="created",
                author_id=1,
                author_name="Jean Dupont",
            ),
            AuditEntry(
                entity_type="devis",
                entity_id="123",
                action="updated",
                author_id=1,
                author_name="Jean Dupont",
            ),
        ]
        mock_repository.get_history.return_value = entries
        mock_repository.count_entries.return_value = 2

        # Act
        result = service.get_history(
            entity_type="devis",
            entity_id="123",
            limit=50,
        )

        # Assert
        assert len(result.entries) == 2
        assert result.total == 2
        assert result.limit == 50
        assert result.offset == 0
        assert mock_repository.get_history.called
        assert mock_repository.count_entries.called

    def test_get_history_with_pagination(self, service, mock_repository):
        """Test get_history() avec pagination."""
        # Arrange
        mock_repository.get_history.return_value = []
        mock_repository.count_entries.return_value = 100

        # Act
        result = service.get_history(
            entity_type="devis",
            entity_id="123",
            limit=20,
            offset=40,
        )

        # Assert
        assert result.limit == 20
        assert result.offset == 40
        assert result.total == 100
        assert result.has_more is True

    def test_get_user_actions_returns_entries(self, service, mock_repository):
        """Test get_user_actions() retourne les entrées."""
        # Arrange
        entries = [
            AuditEntry(
                entity_type="devis",
                entity_id="123",
                action="created",
                author_id=1,
                author_name="Jean Dupont",
            ),
        ]
        mock_repository.get_user_actions.return_value = entries

        # Act
        result = service.get_user_actions(
            author_id=1,
            limit=100,
        )

        # Assert
        assert len(result) == 1
        assert result[0].author_id == 1
        assert mock_repository.get_user_actions.called

    def test_get_user_actions_with_date_filter(self, service, mock_repository):
        """Test get_user_actions() avec filtre de date."""
        # Arrange
        start_date = datetime(2026, 1, 1)
        end_date = datetime(2026, 1, 31)
        mock_repository.get_user_actions.return_value = []

        # Act
        service.get_user_actions(
            author_id=1,
            start_date=start_date,
            end_date=end_date,
        )

        # Assert
        mock_repository.get_user_actions.assert_called_once_with(
            author_id=1,
            start_date=start_date,
            end_date=end_date,
            entity_type=None,
            limit=100,
            offset=0,
        )

    def test_get_recent_entries_returns_entries(self, service, mock_repository):
        """Test get_recent_entries() retourne les entrées."""
        # Arrange
        entries = [
            AuditEntry(
                entity_type="devis",
                entity_id="123",
                action="created",
                author_id=1,
                author_name="Jean Dupont",
            ),
        ]
        mock_repository.get_recent_entries.return_value = entries

        # Act
        result = service.get_recent_entries(limit=50)

        # Assert
        assert len(result) == 1
        assert mock_repository.get_recent_entries.called

    def test_search_returns_entries(self, service, mock_repository):
        """Test search() retourne les entrées."""
        # Arrange
        entries = [
            AuditEntry(
                entity_type="devis",
                entity_id="123",
                action="updated",
                author_id=1,
                author_name="Jean Dupont",
            ),
        ]
        mock_repository.search.return_value = (entries, 1)

        # Act
        result = service.search(
            entity_type="devis",
            action="updated",
            limit=100,
        )

        # Assert
        assert len(result.entries) == 1
        assert result.total == 1
        assert mock_repository.search.called

    def test_search_with_all_filters(self, service, mock_repository):
        """Test search() avec tous les filtres."""
        # Arrange
        start_date = datetime(2026, 1, 1)
        end_date = datetime(2026, 1, 31)
        mock_repository.search.return_value = ([], 0)

        # Act
        service.search(
            entity_type="devis",
            entity_id="123",
            action="updated",
            author_id=1,
            start_date=start_date,
            end_date=end_date,
            limit=100,
            offset=0,
        )

        # Assert
        mock_repository.search.assert_called_once_with(
            entity_type="devis",
            entity_id="123",
            action="updated",
            author_id=1,
            start_date=start_date,
            end_date=end_date,
            limit=100,
            offset=0,
        )
