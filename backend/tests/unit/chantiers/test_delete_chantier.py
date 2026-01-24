"""Tests unitaires pour DeleteChantierUseCase."""

import pytest
from unittest.mock import Mock

from modules.chantiers.domain.entities import Chantier
from modules.chantiers.domain.value_objects import CodeChantier, StatutChantier
from modules.chantiers.domain.repositories import ChantierRepository
from modules.chantiers.application.use_cases.delete_chantier import (
    DeleteChantierUseCase,
    ChantierActifError,
)
from modules.chantiers.application.use_cases.get_chantier import ChantierNotFoundError


class TestDeleteChantierUseCase:
    """Tests pour le use case de suppression de chantier."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_chantier_repo = Mock(spec=ChantierRepository)
        self.use_case = DeleteChantierUseCase(chantier_repo=self.mock_chantier_repo)

        # Chantier fermé (peut être supprimé)
        self.chantier_ferme = Chantier(
            id=1,
            nom="Chantier Test",
            code=CodeChantier("A001"),
            adresse="1 Rue Test",
            statut=StatutChantier.ferme(),
        )

        # Chantier actif (ne peut pas être supprimé)
        self.chantier_actif = Chantier(
            id=2,
            nom="Chantier Actif",
            code=CodeChantier("A002"),
            adresse="2 Rue Test",
            statut=StatutChantier.en_cours(),
        )

    def test_delete_chantier_success(self):
        """Test: suppression réussie d'un chantier fermé."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier_ferme
        self.mock_chantier_repo.delete.return_value = True

        result = self.use_case.execute(1)

        assert result is True
        self.mock_chantier_repo.find_by_id.assert_called_once_with(1)
        self.mock_chantier_repo.delete.assert_called_once_with(1)

    def test_delete_chantier_not_found(self):
        """Test: échec si chantier non trouvé."""
        self.mock_chantier_repo.find_by_id.return_value = None

        with pytest.raises(ChantierNotFoundError):
            self.use_case.execute(999)

    def test_delete_chantier_actif_fails(self):
        """Test: échec si chantier actif."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier_actif

        with pytest.raises(ChantierActifError) as exc_info:
            self.use_case.execute(2)

        assert exc_info.value.chantier_id == 2

    def test_delete_chantier_actif_with_force(self):
        """Test: suppression forcée d'un chantier actif."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier_actif
        self.mock_chantier_repo.delete.return_value = True

        result = self.use_case.execute(2, force=True)

        assert result is True
        self.mock_chantier_repo.delete.assert_called_once_with(2)

    def test_delete_chantier_publishes_event(self):
        """Test: publication d'un event après suppression."""
        mock_publisher = Mock()
        use_case = DeleteChantierUseCase(
            chantier_repo=self.mock_chantier_repo,
            event_publisher=mock_publisher,
        )

        self.mock_chantier_repo.find_by_id.return_value = self.chantier_ferme
        self.mock_chantier_repo.delete.return_value = True

        use_case.execute(1)

        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.chantier_id == 1
        assert event.code == "A001"
