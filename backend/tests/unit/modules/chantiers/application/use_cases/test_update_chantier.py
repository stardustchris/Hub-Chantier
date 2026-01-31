"""Tests unitaires pour UpdateChantierUseCase.

Gap: GAP-CHT-006 - Logging structuré
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

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
    """Tests pour la mise à jour d'un chantier."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=ChantierRepository)
        self.mock_event_publisher = Mock()

    def _create_chantier(self, statut: str = "en_cours", chantier_id: int = 1) -> Chantier:
        """Crée un chantier de test."""
        chantier = Chantier(
            id=chantier_id,
            code=CodeChantier("A001"),
            nom="Chantier Test",
            adresse="123 Rue Test",
            statut=StatutChantier.from_string(statut),
        )
        return chantier

    # ==================== Tests Succès ====================

    def test_update_chantier_nom_et_adresse(self):
        """Test: mise à jour nom et adresse."""
        # Arrange
        use_case = UpdateChantierUseCase(
            chantier_repo=self.mock_repo,
            event_publisher=self.mock_event_publisher,
        )

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = UpdateChantierDTO(
            nom="Nouveau Nom",
            adresse="Nouvelle Adresse",
        )

        # Act
        result = use_case.execute(1, dto)

        # Assert
        assert result.nom == "Nouveau Nom"
        assert result.adresse == "Nouvelle Adresse"
        self.mock_repo.save.assert_called_once()
        self.mock_event_publisher.assert_called_once()

    def test_update_chantier_description_et_couleur(self):
        """Test: mise à jour description et couleur."""
        # Arrange
        use_case = UpdateChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = UpdateChantierDTO(
            description="Nouvelle description",
            couleur="#00FF00",
        )

        # Act
        result = use_case.execute(1, dto)

        # Assert
        assert result.description == "Nouvelle description"
        self.mock_repo.save.assert_called_once()

    def test_update_chantier_coordonnees_gps(self):
        """Test: mise à jour coordonnées GPS (CHT-04)."""
        # Arrange
        use_case = UpdateChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = UpdateChantierDTO(
            latitude=48.8566,
            longitude=2.3522,
        )

        # Act
        result = use_case.execute(1, dto)

        # Assert
        assert result.coordonnees_gps is not None
        self.mock_repo.save.assert_called_once()

    def test_update_chantier_contact(self):
        """Test: mise à jour contact (CHT-07)."""
        # Arrange
        use_case = UpdateChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = UpdateChantierDTO(
            contact_nom="Pierre Durand",
            contact_telephone="0611223344",
        )

        # Act
        result = use_case.execute(1, dto)

        # Assert
        assert result.contact is not None
        self.mock_repo.save.assert_called_once()

    def test_update_chantier_dates(self):
        """Test: mise à jour dates (CHT-20)."""
        # Arrange
        use_case = UpdateChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = UpdateChantierDTO(
            date_debut="2026-04-01",
            date_fin="2026-10-31",
        )

        # Act
        result = use_case.execute(1, dto)

        # Assert
        assert result.date_debut == "2026-04-01"
        assert result.date_fin == "2026-10-31"
        self.mock_repo.save.assert_called_once()

    def test_update_chantier_heures_estimees(self):
        """Test: mise à jour heures estimées (CHT-18)."""
        # Arrange
        use_case = UpdateChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = UpdateChantierDTO(heures_estimees=250.5)

        # Act
        result = use_case.execute(1, dto)

        # Assert
        assert result.heures_estimees == 250.5
        self.mock_repo.save.assert_called_once()

    def test_update_chantier_photo_couverture(self):
        """Test: mise à jour photo de couverture (CHT-01)."""
        # Arrange
        use_case = UpdateChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = UpdateChantierDTO(photo_couverture="https://example.com/photo.jpg")

        # Act
        result = use_case.execute(1, dto)

        # Assert
        assert result.photo_couverture == "https://example.com/photo.jpg"
        self.mock_repo.save.assert_called_once()

    def test_update_chantier_maitre_ouvrage(self):
        """Test: mise à jour maître d'ouvrage."""
        # Arrange
        use_case = UpdateChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = UpdateChantierDTO(maitre_ouvrage="Société XYZ")

        # Act
        result = use_case.execute(1, dto)

        # Assert
        assert result.maitre_ouvrage == "Société XYZ"
        self.mock_repo.save.assert_called_once()

    def test_update_chantier_multiple_fields(self):
        """Test: mise à jour de plusieurs champs simultanément."""
        # Arrange
        use_case = UpdateChantierUseCase(
            chantier_repo=self.mock_repo,
            event_publisher=self.mock_event_publisher,
        )

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = UpdateChantierDTO(
            nom="Multi Update",
            adresse="Multi Adresse",
            couleur="#FF5733",
            heures_estimees=300.0,
            maitre_ouvrage="Multi Corp",
        )

        # Act
        result = use_case.execute(1, dto)

        # Assert
        self.mock_repo.save.assert_called_once()
        # Vérifier que l'event contient tous les changements
        event = self.mock_event_publisher.call_args[0][0]
        assert len(event.changes) >= 5

    def test_update_chantier_publishes_event(self):
        """Test: événement ChantierUpdatedEvent publié avec changements."""
        # Arrange
        use_case = UpdateChantierUseCase(
            chantier_repo=self.mock_repo,
            event_publisher=self.mock_event_publisher,
        )

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = UpdateChantierDTO(nom="Event Test")

        # Act
        use_case.execute(1, dto)

        # Assert
        self.mock_event_publisher.assert_called_once()
        event = self.mock_event_publisher.call_args[0][0]
        assert event.chantier_id == 1
        assert event.code == "A001"
        assert len(event.changes) > 0

    # ==================== Tests Erreurs ====================

    def test_update_chantier_not_found_raises_error(self):
        """Test: chantier non trouvé lève ChantierNotFoundError."""
        # Arrange
        use_case = UpdateChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.find_by_id.return_value = None

        dto = UpdateChantierDTO(nom="Not Found")

        # Act & Assert
        with pytest.raises(ChantierNotFoundError) as exc_info:
            use_case.execute(999, dto)

        assert exc_info.value.identifier == 999 or exc_info.value.identifier == "999"

    def test_update_chantier_ferme_raises_error(self):
        """Test: modification chantier fermé lève ChantierFermeError."""
        # Arrange
        use_case = UpdateChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier(statut="ferme")
        self.mock_repo.find_by_id.return_value = chantier

        dto = UpdateChantierDTO(nom="Ferme")

        # Act & Assert
        with pytest.raises(ChantierFermeError) as exc_info:
            use_case.execute(1, dto)

        assert exc_info.value.chantier_id == 1
        assert "fermé" in exc_info.value.message

    def test_update_chantier_without_event_publisher_succeeds(self):
        """Test: mise à jour réussie sans event_publisher (optionnel)."""
        # Arrange
        use_case = UpdateChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = UpdateChantierDTO(nom="No Events")

        # Act - Pas d'erreur
        result = use_case.execute(1, dto)

        # Assert
        assert result.nom == "No Events"

    # ==================== Tests Logging Structuré (GAP-CHT-006) ====================

    @patch('modules.chantiers.application.use_cases.update_chantier.logger')
    def test_execute_logs_started_event(self, mock_logger):
        """Test: execute() log événement 'started' avec extra dict."""
        # Arrange
        use_case = UpdateChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = UpdateChantierDTO(nom="Log Test")

        # Act
        use_case.execute(1, dto)

        # Assert
        info_calls = mock_logger.info.call_args_list
        started_call = info_calls[0]

        assert "Use case execution started" in started_call.args[0]
        assert 'extra' in started_call.kwargs
        extra = started_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.started"
        assert extra['use_case'] == "UpdateChantierUseCase"
        assert extra['chantier_id'] == 1
        assert extra['operation'] == "update"

    @patch('modules.chantiers.application.use_cases.update_chantier.logger')
    def test_execute_logs_succeeded_event(self, mock_logger):
        """Test: execute() log événement 'succeeded' avec compteur changements."""
        # Arrange
        use_case = UpdateChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = UpdateChantierDTO(nom="Success", adresse="Success Addr")

        # Act
        use_case.execute(1, dto)

        # Assert
        info_calls = mock_logger.info.call_args_list
        assert len(info_calls) >= 2
        succeeded_call = info_calls[1]

        assert "Use case execution succeeded" in succeeded_call.args[0]
        extra = succeeded_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.succeeded"
        assert extra['use_case'] == "UpdateChantierUseCase"
        assert extra['chantier_id'] == 1
        assert 'changes_count' in extra
        assert 'changes' in extra

    @patch('modules.chantiers.application.use_cases.update_chantier.logger')
    def test_execute_logs_failed_event_on_error(self, mock_logger):
        """Test: execute() log événement 'failed' en cas d'erreur."""
        # Arrange
        use_case = UpdateChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.find_by_id.return_value = None

        dto = UpdateChantierDTO(nom="Fail")

        # Act & Assert
        with pytest.raises(ChantierNotFoundError):
            use_case.execute(999, dto)

        # Assert
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args

        assert "Use case execution failed" in error_call.args[0]
        extra = error_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.failed"
        assert extra['use_case'] == "UpdateChantierUseCase"
        assert extra['chantier_id'] == 999
        assert extra['error_type'] == "ChantierNotFoundError"
        assert 'error_message' in extra
