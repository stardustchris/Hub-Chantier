"""Tests unitaires pour GetChantierUseCase."""

import pytest
from unittest.mock import Mock
from datetime import date

from modules.chantiers.domain.entities import Chantier
from modules.chantiers.domain.value_objects import CodeChantier, StatutChantier
from modules.chantiers.domain.repositories import ChantierRepository
from modules.chantiers.application.use_cases.get_chantier import (
    GetChantierUseCase,
    ChantierNotFoundError,
)


class TestGetChantierUseCase:
    """Tests pour le use case de récupération de chantier."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_chantier_repo = Mock(spec=ChantierRepository)
        self.use_case = GetChantierUseCase(chantier_repo=self.mock_chantier_repo)

        self.test_chantier = Chantier(
            id=1,
            nom="Chantier Test",
            code=CodeChantier("A001"),
            adresse="123 Rue Test",
            statut=StatutChantier.ouvert(),
        )

    def test_get_chantier_by_id_success(self):
        """Test: récupération réussie par ID."""
        self.mock_chantier_repo.find_by_id.return_value = self.test_chantier

        result = self.use_case.execute_by_id(1)

        assert result.id == 1
        assert result.nom == "Chantier Test"
        assert result.code == "A001"
        self.mock_chantier_repo.find_by_id.assert_called_once_with(1)

    def test_get_chantier_by_id_not_found(self):
        """Test: échec si chantier non trouvé par ID."""
        self.mock_chantier_repo.find_by_id.return_value = None

        with pytest.raises(ChantierNotFoundError) as exc_info:
            self.use_case.execute_by_id(999)

        assert "999" in str(exc_info.value.identifier)

    def test_get_chantier_by_code_success(self):
        """Test: récupération réussie par code."""
        self.mock_chantier_repo.find_by_code.return_value = self.test_chantier

        result = self.use_case.execute_by_code("A001")

        assert result.id == 1
        assert result.code == "A001"
        self.mock_chantier_repo.find_by_code.assert_called_once()

    def test_get_chantier_by_code_not_found(self):
        """Test: échec si chantier non trouvé par code."""
        self.mock_chantier_repo.find_by_code.return_value = None

        with pytest.raises(ChantierNotFoundError) as exc_info:
            self.use_case.execute_by_code("Z999")

        assert exc_info.value.identifier == "Z999"
