"""Tests unitaires pour le use case DeleteBesoin."""

import pytest
from unittest.mock import Mock

from modules.planning_charge.domain.entities import BesoinCharge
from modules.planning_charge.domain.value_objects import Semaine, TypeMetier
from modules.planning_charge.application.use_cases import (
    DeleteBesoinUseCase,
    BesoinNotFoundError,
)


class TestDeleteBesoinUseCase:
    """Tests pour le use case DeleteBesoin."""

    @pytest.fixture
    def mock_repo(self):
        """Fixture pour le repository mock."""
        return Mock()

    @pytest.fixture
    def mock_event_bus(self):
        """Fixture pour l'event bus mock."""
        return Mock()

    @pytest.fixture
    def use_case(self, mock_repo, mock_event_bus):
        """Fixture pour le use case."""
        return DeleteBesoinUseCase(mock_repo, mock_event_bus)

    @pytest.fixture
    def existing_besoin(self):
        """Fixture pour un besoin existant."""
        return BesoinCharge(
            id=1,
            chantier_id=1,
            semaine=Semaine(annee=2026, numero=4),
            type_metier=TypeMetier.MACON,
            besoin_heures=35.0,
            created_by=1,
        )

    def test_delete_besoin_success(self, use_case, mock_repo, existing_besoin):
        """Test suppression reussie d'un besoin."""
        # Setup
        mock_repo.find_by_id.return_value = existing_besoin
        mock_repo.delete.return_value = True

        # Execute
        result = use_case.execute(besoin_id=1, deleted_by=2)

        # Verify
        assert result is True
        mock_repo.delete.assert_called_once_with(1)

    def test_delete_besoin_publishes_event(self, use_case, mock_repo, mock_event_bus, existing_besoin):
        """Test que la suppression publie un evenement."""
        # Setup
        mock_repo.find_by_id.return_value = existing_besoin
        mock_repo.delete.return_value = True

        # Execute
        use_case.execute(besoin_id=1, deleted_by=2)

        # Verify
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert event.besoin_id == 1
        assert event.chantier_id == 1
        assert event.deleted_by == 2

    def test_delete_besoin_not_found(self, use_case, mock_repo):
        """Test erreur si besoin non trouve."""
        # Setup
        mock_repo.find_by_id.return_value = None

        # Execute & Verify
        with pytest.raises(BesoinNotFoundError) as exc_info:
            use_case.execute(besoin_id=999, deleted_by=2)

        assert exc_info.value.besoin_id == 999

    def test_delete_besoin_without_event_bus(self, mock_repo, existing_besoin):
        """Test suppression sans event bus."""
        # Setup
        use_case = DeleteBesoinUseCase(mock_repo, event_bus=None)
        mock_repo.find_by_id.return_value = existing_besoin
        mock_repo.delete.return_value = True

        # Execute - should not raise
        result = use_case.execute(besoin_id=1, deleted_by=2)
        assert result is True

    def test_delete_besoin_preserves_info_for_event(self, use_case, mock_repo, mock_event_bus, existing_besoin):
        """Test que les infos sont preservees pour l'evenement."""
        # Setup
        mock_repo.find_by_id.return_value = existing_besoin
        mock_repo.delete.return_value = True

        # Execute
        use_case.execute(besoin_id=1, deleted_by=2)

        # Verify - l'evenement contient les infos du besoin supprime
        event = mock_event_bus.publish.call_args[0][0]
        assert event.semaine_code == "S04-2026"
        assert event.type_metier == "macon"
        assert event.besoin_heures == 35.0
