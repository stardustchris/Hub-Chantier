"""Tests unitaires pour le use case CreateBesoin."""

import pytest
from unittest.mock import Mock, MagicMock

from modules.planning_charge.domain.entities import BesoinCharge
from modules.planning_charge.domain.value_objects import Semaine, TypeMetier
from modules.planning_charge.application.dtos import CreateBesoinDTO
from modules.planning_charge.application.use_cases import (
    CreateBesoinUseCase,
    BesoinAlreadyExistsError,
)


class TestCreateBesoinUseCase:
    """Tests pour le use case CreateBesoin."""

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
        return CreateBesoinUseCase(mock_repo, mock_event_bus)

    @pytest.fixture
    def valid_dto(self):
        """Fixture pour un DTO valide."""
        return CreateBesoinDTO(
            chantier_id=1,
            semaine_code="S04-2026",
            type_metier="macon",
            besoin_heures=35.0,
            note="Note test",
        )

    def test_create_besoin_success(self, use_case, mock_repo, valid_dto):
        """Test creation reussie d'un besoin."""
        # Setup
        mock_repo.exists.return_value = False
        mock_repo.save.side_effect = lambda b: self._set_id(b, 1)

        # Execute
        result = use_case.execute(valid_dto, created_by=1)

        # Verify
        assert result.id == 1
        assert result.chantier_id == 1
        assert result.semaine_code == "S04-2026"
        assert result.type_metier == "macon"
        assert result.besoin_heures == 35.0
        mock_repo.exists.assert_called_once()
        mock_repo.save.assert_called_once()

    def test_create_besoin_publishes_event(self, use_case, mock_repo, mock_event_bus, valid_dto):
        """Test que la creation publie un evenement."""
        # Setup
        mock_repo.exists.return_value = False
        mock_repo.save.side_effect = lambda b: self._set_id(b, 1)

        # Execute
        use_case.execute(valid_dto, created_by=1)

        # Verify
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert event.besoin_id == 1
        assert event.chantier_id == 1
        assert event.type_metier == "macon"

    def test_create_besoin_already_exists(self, use_case, mock_repo, valid_dto):
        """Test erreur si un besoin existe deja."""
        # Setup
        mock_repo.exists.return_value = True

        # Execute & Verify
        with pytest.raises(BesoinAlreadyExistsError) as exc_info:
            use_case.execute(valid_dto, created_by=1)

        assert exc_info.value.chantier_id == 1
        assert exc_info.value.semaine_code == "S04-2026"
        assert exc_info.value.type_metier == "macon"

    def test_create_besoin_without_note(self, use_case, mock_repo):
        """Test creation sans note."""
        # Setup
        dto = CreateBesoinDTO(
            chantier_id=1,
            semaine_code="S04-2026",
            type_metier="macon",
            besoin_heures=35.0,
        )
        mock_repo.exists.return_value = False
        mock_repo.save.side_effect = lambda b: self._set_id(b, 1)

        # Execute
        result = use_case.execute(dto, created_by=1)

        # Verify
        assert result.note is None

    def test_create_besoin_without_event_bus(self, mock_repo, valid_dto):
        """Test creation sans event bus."""
        # Setup
        use_case = CreateBesoinUseCase(mock_repo, event_bus=None)
        mock_repo.exists.return_value = False
        mock_repo.save.side_effect = lambda b: self._set_id(b, 1)

        # Execute - should not raise
        result = use_case.execute(valid_dto, created_by=1)
        assert result.id == 1

    def test_create_besoin_invalid_semaine(self, use_case, mock_repo):
        """Test erreur si semaine invalide."""
        dto = CreateBesoinDTO(
            chantier_id=1,
            semaine_code="INVALID",
            type_metier="macon",
            besoin_heures=35.0,
        )

        with pytest.raises(ValueError):
            use_case.execute(dto, created_by=1)

    def test_create_besoin_invalid_type_metier(self, use_case, mock_repo):
        """Test erreur si type metier invalide."""
        dto = CreateBesoinDTO(
            chantier_id=1,
            semaine_code="S04-2026",
            type_metier="invalid_type",
            besoin_heures=35.0,
        )

        with pytest.raises(ValueError):
            use_case.execute(dto, created_by=1)

    def test_create_besoin_various_types(self, use_case, mock_repo):
        """Test creation avec differents types de metier."""
        mock_repo.exists.return_value = False
        mock_repo.save.side_effect = lambda b: self._set_id(b, 1)

        types = ["macon", "coffreur", "ferrailleur", "grutier", "employe"]
        for type_metier in types:
            dto = CreateBesoinDTO(
                chantier_id=1,
                semaine_code="S04-2026",
                type_metier=type_metier,
                besoin_heures=35.0,
            )
            result = use_case.execute(dto, created_by=1)
            assert result.type_metier == type_metier

    def _set_id(self, besoin: BesoinCharge, id: int) -> BesoinCharge:
        """Helper pour setter l'ID sur un besoin."""
        besoin.id = id
        return besoin
