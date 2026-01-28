"""Tests unitaires pour le use case UpdateBesoin."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.planning.domain.entities import BesoinCharge
from modules.planning.domain.value_objects import Semaine, TypeMetier
from modules.planning.application.dtos import UpdateBesoinDTO
from modules.planning.application.use_cases import (
    UpdateBesoinUseCase,
    BesoinNotFoundError,
)


class TestUpdateBesoinUseCase:
    """Tests pour le use case UpdateBesoin."""

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
        return UpdateBesoinUseCase(mock_repo, mock_event_bus)

    @pytest.fixture
    def existing_besoin(self):
        """Fixture pour un besoin existant."""
        return BesoinCharge(
            id=1,
            chantier_id=1,
            semaine=Semaine(annee=2026, numero=4),
            type_metier=TypeMetier.MACON,
            besoin_heures=35.0,
            note="Note originale",
            created_by=1,
        )

    def test_update_besoin_heures_success(self, use_case, mock_repo, existing_besoin):
        """Test mise a jour du nombre d'heures."""
        # Setup
        mock_repo.find_by_id.return_value = existing_besoin
        mock_repo.save.side_effect = lambda b: b

        dto = UpdateBesoinDTO(besoin_heures=70.0)

        # Execute
        result = use_case.execute(besoin_id=1, dto=dto, updated_by=2)

        # Verify
        assert result.besoin_heures == 70.0
        mock_repo.save.assert_called_once()

    def test_update_besoin_note_success(self, use_case, mock_repo, existing_besoin):
        """Test mise a jour de la note."""
        # Setup
        mock_repo.find_by_id.return_value = existing_besoin
        mock_repo.save.side_effect = lambda b: b

        dto = UpdateBesoinDTO(note="Nouvelle note")

        # Execute
        result = use_case.execute(besoin_id=1, dto=dto, updated_by=2)

        # Verify
        assert result.note == "Nouvelle note"

    def test_update_besoin_remove_note(self, use_case, mock_repo, existing_besoin):
        """Test suppression de la note."""
        # Setup
        mock_repo.find_by_id.return_value = existing_besoin
        mock_repo.save.side_effect = lambda b: b

        dto = UpdateBesoinDTO(note="")

        # Execute
        result = use_case.execute(besoin_id=1, dto=dto, updated_by=2)

        # Verify
        assert result.note is None

    def test_update_besoin_type_metier(self, use_case, mock_repo, existing_besoin):
        """Test changement de type metier."""
        # Setup
        mock_repo.find_by_id.return_value = existing_besoin
        mock_repo.save.side_effect = lambda b: b

        dto = UpdateBesoinDTO(type_metier="coffreur")

        # Execute
        result = use_case.execute(besoin_id=1, dto=dto, updated_by=2)

        # Verify
        assert result.type_metier == "coffreur"

    def test_update_besoin_publishes_event(self, use_case, mock_repo, mock_event_bus, existing_besoin):
        """Test que la mise a jour publie un evenement."""
        # Setup
        mock_repo.find_by_id.return_value = existing_besoin
        mock_repo.save.side_effect = lambda b: b

        dto = UpdateBesoinDTO(besoin_heures=70.0)

        # Execute
        use_case.execute(besoin_id=1, dto=dto, updated_by=2)

        # Verify
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert event.ancien_besoin_heures == 35.0
        assert event.nouveau_besoin_heures == 70.0
        assert event.updated_by == 2

    def test_update_besoin_not_found(self, use_case, mock_repo):
        """Test erreur si besoin non trouve."""
        # Setup
        mock_repo.find_by_id.return_value = None

        dto = UpdateBesoinDTO(besoin_heures=70.0)

        # Execute & Verify
        with pytest.raises(BesoinNotFoundError) as exc_info:
            use_case.execute(besoin_id=999, dto=dto, updated_by=2)

        assert exc_info.value.besoin_id == 999

    def test_update_besoin_multiple_fields(self, use_case, mock_repo, existing_besoin):
        """Test mise a jour de plusieurs champs."""
        # Setup
        mock_repo.find_by_id.return_value = existing_besoin
        mock_repo.save.side_effect = lambda b: b

        dto = UpdateBesoinDTO(
            besoin_heures=70.0,
            note="Nouvelle note",
            type_metier="coffreur",
        )

        # Execute
        result = use_case.execute(besoin_id=1, dto=dto, updated_by=2)

        # Verify
        assert result.besoin_heures == 70.0
        assert result.note == "Nouvelle note"
        assert result.type_metier == "coffreur"

    def test_update_besoin_without_event_bus(self, mock_repo, existing_besoin):
        """Test mise a jour sans event bus."""
        # Setup
        use_case = UpdateBesoinUseCase(mock_repo, event_bus=None)
        mock_repo.find_by_id.return_value = existing_besoin
        mock_repo.save.side_effect = lambda b: b

        dto = UpdateBesoinDTO(besoin_heures=70.0)

        # Execute - should not raise
        result = use_case.execute(besoin_id=1, dto=dto, updated_by=2)
        assert result.besoin_heures == 70.0

    def test_update_besoin_invalid_type_metier(self, use_case, mock_repo, existing_besoin):
        """Test erreur si type metier invalide."""
        # Setup
        mock_repo.find_by_id.return_value = existing_besoin

        dto = UpdateBesoinDTO(type_metier="invalid_type")

        # Execute & Verify
        with pytest.raises(ValueError):
            use_case.execute(besoin_id=1, dto=dto, updated_by=2)

    def test_update_besoin_no_changes(self, use_case, mock_repo, existing_besoin):
        """Test mise a jour sans modifications."""
        # Setup
        mock_repo.find_by_id.return_value = existing_besoin
        mock_repo.save.side_effect = lambda b: b

        dto = UpdateBesoinDTO()  # Aucun champ specifie

        # Execute
        result = use_case.execute(besoin_id=1, dto=dto, updated_by=2)

        # Verify - valeurs inchangees
        assert result.besoin_heures == 35.0
        assert result.note == "Note originale"
        assert result.type_metier == "macon"
