"""Tests unitaires pour UpdateChantierUseCase."""

import pytest
from unittest.mock import Mock
from datetime import date

from modules.chantiers.domain.entities import Chantier
from modules.chantiers.domain.value_objects import CodeChantier, StatutChantier
from modules.chantiers.domain.repositories import ChantierRepository
from modules.chantiers.application.use_cases.update_chantier import (
    UpdateChantierUseCase,
    ChantierFermeError,
)
from modules.chantiers.application.use_cases.get_chantier import ChantierNotFoundError
from modules.chantiers.application.dtos import UpdateChantierDTO


class TestUpdateChantierUseCase:
    """Tests pour le use case de mise à jour de chantier."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_chantier_repo = Mock(spec=ChantierRepository)
        self.use_case = UpdateChantierUseCase(chantier_repo=self.mock_chantier_repo)

        self.chantier_ouvert = Chantier(
            id=1,
            nom="Chantier Test",
            code=CodeChantier("A001"),
            adresse="1 Rue Test",
            statut=StatutChantier.ouvert(),
        )

        self.chantier_ferme = Chantier(
            id=2,
            nom="Chantier Fermé",
            code=CodeChantier("A002"),
            adresse="2 Rue Test",
            statut=StatutChantier.ferme(),
        )

    def test_update_chantier_nom_success(self):
        """Test: mise à jour réussie du nom."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier_ouvert
        self.mock_chantier_repo.save.return_value = self.chantier_ouvert

        dto = UpdateChantierDTO(nom="Nouveau Nom")

        result = self.use_case.execute(1, dto)

        self.mock_chantier_repo.save.assert_called_once()

    def test_update_chantier_not_found(self):
        """Test: échec si chantier non trouvé."""
        self.mock_chantier_repo.find_by_id.return_value = None

        dto = UpdateChantierDTO(nom="Test")

        with pytest.raises(ChantierNotFoundError):
            self.use_case.execute(999, dto)

    def test_update_chantier_ferme_fails(self):
        """Test: échec si chantier fermé."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier_ferme

        dto = UpdateChantierDTO(nom="Test")

        with pytest.raises(ChantierFermeError) as exc_info:
            self.use_case.execute(2, dto)

        assert exc_info.value.chantier_id == 2

    def test_update_chantier_coordonnees_gps(self):
        """Test: mise à jour des coordonnées GPS."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier_ouvert
        self.mock_chantier_repo.save.return_value = self.chantier_ouvert

        dto = UpdateChantierDTO(latitude=48.8566, longitude=2.3522)

        result = self.use_case.execute(1, dto)

        self.mock_chantier_repo.save.assert_called_once()

    def test_update_chantier_contact(self):
        """Test: mise à jour du contact."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier_ouvert
        self.mock_chantier_repo.save.return_value = self.chantier_ouvert

        dto = UpdateChantierDTO(
            contact_nom="M. Dupont",
            contact_telephone="0612345678",
        )

        result = self.use_case.execute(1, dto)

        self.mock_chantier_repo.save.assert_called_once()

    def test_update_chantier_dates(self):
        """Test: mise à jour des dates."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier_ouvert
        self.mock_chantier_repo.save.return_value = self.chantier_ouvert

        dto = UpdateChantierDTO(
            date_debut="2026-02-01",
            date_fin="2026-12-31",
        )

        result = self.use_case.execute(1, dto)

        self.mock_chantier_repo.save.assert_called_once()

    def test_update_chantier_heures_estimees(self):
        """Test: mise à jour des heures estimées."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier_ouvert
        self.mock_chantier_repo.save.return_value = self.chantier_ouvert

        dto = UpdateChantierDTO(heures_estimees=500.0)

        result = self.use_case.execute(1, dto)

        self.mock_chantier_repo.save.assert_called_once()

    def test_update_chantier_publishes_event(self):
        """Test: publication d'un event après mise à jour."""
        mock_publisher = Mock()
        use_case = UpdateChantierUseCase(
            chantier_repo=self.mock_chantier_repo,
            event_publisher=mock_publisher,
        )

        self.mock_chantier_repo.find_by_id.return_value = self.chantier_ouvert
        self.mock_chantier_repo.save.return_value = self.chantier_ouvert

        dto = UpdateChantierDTO(nom="Nouveau Nom")

        use_case.execute(1, dto)

        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.chantier_id == 1
