"""Tests unitaires pour SignalementController."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from modules.signalements.adapters.controllers.signalement_controller import SignalementController
from modules.signalements.application.dtos import (
    SignalementDTO,
    SignalementCreateDTO,
    SignalementUpdateDTO,
    SignalementListDTO,
    SignalementSearchDTO,
    SignalementStatsDTO,
    ReponseDTO,
    ReponseCreateDTO,
    ReponseUpdateDTO,
    ReponseListDTO,
)


class TestSignalementControllerInit:
    """Tests d'initialisation du controller."""

    def test_init_with_all_params(self):
        """Test init avec tous les parametres."""
        mock_sig_repo = Mock()
        mock_rep_repo = Mock()
        mock_get_name = Mock()

        controller = SignalementController(
            signalement_repository=mock_sig_repo,
            reponse_repository=mock_rep_repo,
            get_user_name=mock_get_name,
        )

        assert controller._signalement_repo == mock_sig_repo
        assert controller._reponse_repo == mock_rep_repo
        assert controller._get_user_name == mock_get_name

    def test_init_without_get_user_name(self):
        """Test init sans fonction get_user_name."""
        controller = SignalementController(
            signalement_repository=Mock(),
            reponse_repository=Mock(),
        )

        assert controller._get_user_name is None


class TestSignalementControllerCreateSignalement:
    """Tests de creation de signalement."""

    @pytest.fixture
    def controller(self):
        return SignalementController(
            signalement_repository=Mock(),
            reponse_repository=Mock(),
            get_user_name=Mock(return_value="Test User"),
        )

    @patch("modules.signalements.adapters.controllers.signalement_controller.CreateSignalementUseCase")
    def test_create_signalement_calls_use_case(self, mock_use_case_class, controller):
        """Test que create appelle le use case."""
        mock_dto = Mock(spec=SignalementCreateDTO)
        mock_result = Mock(spec=SignalementDTO)
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_result
        mock_use_case_class.return_value = mock_use_case

        result = controller.create_signalement(mock_dto)

        mock_use_case.execute.assert_called_once_with(mock_dto)
        assert result == mock_result


class TestSignalementControllerGetSignalement:
    """Tests de recuperation de signalement."""

    @pytest.fixture
    def controller(self):
        return SignalementController(
            signalement_repository=Mock(),
            reponse_repository=Mock(),
            get_user_name=Mock(),
        )

    @patch("modules.signalements.adapters.controllers.signalement_controller.GetSignalementUseCase")
    def test_get_signalement_by_id(self, mock_use_case_class, controller):
        """Test recuperation par ID."""
        mock_result = Mock(spec=SignalementDTO)
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_result
        mock_use_case_class.return_value = mock_use_case

        result = controller.get_signalement(42)

        mock_use_case.execute.assert_called_once_with(42)
        assert result == mock_result


class TestSignalementControllerListSignalements:
    """Tests de liste des signalements."""

    @pytest.fixture
    def controller(self):
        return SignalementController(
            signalement_repository=Mock(),
            reponse_repository=Mock(),
            get_user_name=Mock(),
        )

    @patch("modules.signalements.adapters.controllers.signalement_controller.ListSignalementsUseCase")
    def test_list_with_defaults(self, mock_use_case_class, controller):
        """Test liste avec parametres par defaut."""
        mock_result = Mock(spec=SignalementListDTO)
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_result
        mock_use_case_class.return_value = mock_use_case

        result = controller.list_signalements(chantier_id=1)

        mock_use_case.execute.assert_called_once_with(1, 0, 100, None, None)

    @patch("modules.signalements.adapters.controllers.signalement_controller.ListSignalementsUseCase")
    def test_list_with_filters(self, mock_use_case_class, controller):
        """Test liste avec filtres."""
        mock_use_case = Mock()
        mock_use_case.execute.return_value = Mock()
        mock_use_case_class.return_value = mock_use_case

        controller.list_signalements(
            chantier_id=1,
            skip=10,
            limit=50,
            statut="ouvert",
            priorite="haute",
        )

        mock_use_case.execute.assert_called_once_with(1, 10, 50, "ouvert", "haute")


class TestSignalementControllerSearchSignalements:
    """Tests de recherche de signalements."""

    @pytest.fixture
    def controller(self):
        return SignalementController(
            signalement_repository=Mock(),
            reponse_repository=Mock(),
            get_user_name=Mock(),
        )

    @patch("modules.signalements.adapters.controllers.signalement_controller.SearchSignalementsUseCase")
    def test_search_signalements(self, mock_use_case_class, controller):
        """Test recherche avec DTO."""
        search_dto = Mock(spec=SignalementSearchDTO)
        mock_result = Mock(spec=SignalementListDTO)
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_result
        mock_use_case_class.return_value = mock_use_case

        result = controller.search_signalements(search_dto)

        mock_use_case.execute.assert_called_once_with(search_dto)
        assert result == mock_result


class TestSignalementControllerUpdateSignalement:
    """Tests de mise a jour de signalement."""

    @pytest.fixture
    def controller(self):
        return SignalementController(
            signalement_repository=Mock(),
            reponse_repository=Mock(),
            get_user_name=Mock(),
        )

    @patch("modules.signalements.adapters.controllers.signalement_controller.UpdateSignalementUseCase")
    def test_update_signalement(self, mock_use_case_class, controller):
        """Test mise a jour."""
        update_dto = Mock(spec=SignalementUpdateDTO)
        mock_result = Mock(spec=SignalementDTO)
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_result
        mock_use_case_class.return_value = mock_use_case

        result = controller.update_signalement(
            signalement_id=1,
            dto=update_dto,
            user_id=10,
            user_role="admin",
        )

        mock_use_case.execute.assert_called_once_with(1, update_dto, 10, "admin")
        assert result == mock_result


class TestSignalementControllerDeleteSignalement:
    """Tests de suppression de signalement."""

    @pytest.fixture
    def controller(self):
        return SignalementController(
            signalement_repository=Mock(),
            reponse_repository=Mock(),
        )

    @patch("modules.signalements.adapters.controllers.signalement_controller.DeleteSignalementUseCase")
    def test_delete_signalement(self, mock_use_case_class, controller):
        """Test suppression."""
        mock_use_case = Mock()
        mock_use_case.execute.return_value = True
        mock_use_case_class.return_value = mock_use_case

        result = controller.delete_signalement(
            signalement_id=1,
            user_id=10,
            user_role="admin",
        )

        mock_use_case.execute.assert_called_once_with(1, 10, "admin")
        assert result is True


class TestSignalementControllerWorkflow:
    """Tests des operations de workflow."""

    @pytest.fixture
    def controller(self):
        return SignalementController(
            signalement_repository=Mock(),
            reponse_repository=Mock(),
            get_user_name=Mock(),
        )

    @patch("modules.signalements.adapters.controllers.signalement_controller.AssignerSignalementUseCase")
    def test_assigner_signalement(self, mock_use_case_class, controller):
        """Test assignation."""
        mock_result = Mock(spec=SignalementDTO)
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_result
        mock_use_case_class.return_value = mock_use_case

        result = controller.assigner_signalement(
            signalement_id=1,
            assigne_a=20,
            user_role="conducteur",
        )

        mock_use_case.execute.assert_called_once_with(1, 20, "conducteur")

    @patch("modules.signalements.adapters.controllers.signalement_controller.MarquerTraiteUseCase")
    def test_marquer_traite(self, mock_use_case_class, controller):
        """Test marquer comme traite."""
        mock_result = Mock(spec=SignalementDTO)
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_result
        mock_use_case_class.return_value = mock_use_case

        result = controller.marquer_traite(
            signalement_id=1,
            commentaire="Traitement effectue",
            user_role="admin",
        )

        mock_use_case.execute.assert_called_once_with(1, "Traitement effectue", "admin")

    @patch("modules.signalements.adapters.controllers.signalement_controller.CloturerSignalementUseCase")
    def test_cloturer_signalement(self, mock_use_case_class, controller):
        """Test cloture."""
        mock_result = Mock(spec=SignalementDTO)
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_result
        mock_use_case_class.return_value = mock_use_case

        result = controller.cloturer_signalement(
            signalement_id=1,
            user_role="admin",
        )

        mock_use_case.execute.assert_called_once_with(1, "admin")

    @patch("modules.signalements.adapters.controllers.signalement_controller.ReouvrirsignalementUseCase")
    def test_reouvrir_signalement(self, mock_use_case_class, controller):
        """Test reouverture."""
        mock_result = Mock(spec=SignalementDTO)
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_result
        mock_use_case_class.return_value = mock_use_case

        result = controller.reouvrir_signalement(
            signalement_id=1,
            user_role="admin",
        )

        mock_use_case.execute.assert_called_once_with(1, "admin")


class TestSignalementControllerStatistiques:
    """Tests des statistiques."""

    @pytest.fixture
    def controller(self):
        return SignalementController(
            signalement_repository=Mock(),
            reponse_repository=Mock(),
        )

    @patch("modules.signalements.adapters.controllers.signalement_controller.GetStatistiquesUseCase")
    def test_get_statistiques_all(self, mock_use_case_class, controller):
        """Test stats globales."""
        mock_result = Mock(spec=SignalementStatsDTO)
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_result
        mock_use_case_class.return_value = mock_use_case

        result = controller.get_statistiques()

        mock_use_case.execute.assert_called_once_with(None, None, None)

    @patch("modules.signalements.adapters.controllers.signalement_controller.GetStatistiquesUseCase")
    def test_get_statistiques_filtered(self, mock_use_case_class, controller):
        """Test stats filtrees."""
        mock_use_case = Mock()
        mock_use_case.execute.return_value = Mock()
        mock_use_case_class.return_value = mock_use_case

        date_debut = datetime(2024, 1, 1)
        date_fin = datetime(2024, 12, 31)

        controller.get_statistiques(
            chantier_id=1,
            date_debut=date_debut,
            date_fin=date_fin,
        )

        mock_use_case.execute.assert_called_once_with(1, date_debut, date_fin)


class TestSignalementControllerEnRetard:
    """Tests des signalements en retard."""

    @pytest.fixture
    def controller(self):
        return SignalementController(
            signalement_repository=Mock(),
            reponse_repository=Mock(),
            get_user_name=Mock(),
        )

    @patch("modules.signalements.adapters.controllers.signalement_controller.GetSignalementsEnRetardUseCase")
    def test_get_en_retard_defaults(self, mock_use_case_class, controller):
        """Test recuperation en retard avec defaults."""
        mock_result = Mock(spec=SignalementListDTO)
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_result
        mock_use_case_class.return_value = mock_use_case

        result = controller.get_signalements_en_retard()

        mock_use_case.execute.assert_called_once_with(None, 0, 100)

    @patch("modules.signalements.adapters.controllers.signalement_controller.GetSignalementsEnRetardUseCase")
    def test_get_en_retard_filtered(self, mock_use_case_class, controller):
        """Test recuperation en retard filtree."""
        mock_use_case = Mock()
        mock_use_case.execute.return_value = Mock()
        mock_use_case_class.return_value = mock_use_case

        controller.get_signalements_en_retard(
            chantier_id=5,
            skip=10,
            limit=25,
        )

        mock_use_case.execute.assert_called_once_with(5, 10, 25)


class TestSignalementControllerReponses:
    """Tests des operations sur les reponses."""

    @pytest.fixture
    def controller(self):
        return SignalementController(
            signalement_repository=Mock(),
            reponse_repository=Mock(),
            get_user_name=Mock(),
        )

    @patch("modules.signalements.adapters.controllers.signalement_controller.CreateReponseUseCase")
    def test_create_reponse(self, mock_use_case_class, controller):
        """Test creation de reponse."""
        create_dto = Mock(spec=ReponseCreateDTO)
        mock_result = Mock(spec=ReponseDTO)
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_result
        mock_use_case_class.return_value = mock_use_case

        result = controller.create_reponse(create_dto)

        mock_use_case.execute.assert_called_once_with(create_dto)
        assert result == mock_result

    @patch("modules.signalements.adapters.controllers.signalement_controller.ListReponsesUseCase")
    def test_list_reponses(self, mock_use_case_class, controller):
        """Test liste des reponses."""
        mock_result = Mock(spec=ReponseListDTO)
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_result
        mock_use_case_class.return_value = mock_use_case

        result = controller.list_reponses(
            signalement_id=1,
            skip=5,
            limit=20,
        )

        mock_use_case.execute.assert_called_once_with(1, 5, 20)

    @patch("modules.signalements.adapters.controllers.signalement_controller.UpdateReponseUseCase")
    def test_update_reponse(self, mock_use_case_class, controller):
        """Test mise a jour de reponse."""
        update_dto = Mock(spec=ReponseUpdateDTO)
        mock_result = Mock(spec=ReponseDTO)
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_result
        mock_use_case_class.return_value = mock_use_case

        result = controller.update_reponse(
            reponse_id=10,
            dto=update_dto,
            user_id=5,
            user_role="admin",
        )

        mock_use_case.execute.assert_called_once_with(10, update_dto, 5, "admin")

    @patch("modules.signalements.adapters.controllers.signalement_controller.DeleteReponseUseCase")
    def test_delete_reponse(self, mock_use_case_class, controller):
        """Test suppression de reponse."""
        mock_use_case = Mock()
        mock_use_case.execute.return_value = True
        mock_use_case_class.return_value = mock_use_case

        result = controller.delete_reponse(
            reponse_id=10,
            user_id=5,
            user_role="admin",
        )

        mock_use_case.execute.assert_called_once_with(10, 5, "admin")
        assert result is True
