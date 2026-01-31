"""Tests unitaires pour ListChantiersUseCase.

Gap: GAP-CHT-006 - Logging structuré
"""

import pytest
from unittest.mock import Mock, patch

from modules.chantiers.domain.entities import Chantier
from modules.chantiers.domain.value_objects import CodeChantier, StatutChantier
from modules.chantiers.domain.repositories import ChantierRepository
from modules.chantiers.application.use_cases.list_chantiers import ListChantiersUseCase


class TestListChantiersUseCase:
    """Tests pour la liste des chantiers avec filtres."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=ChantierRepository)

    def _create_chantier(
        self, chantier_id: int = 1, code: str = "A001", statut: str = "ouvert"
    ) -> Chantier:
        """Crée un chantier de test."""
        return Chantier(
            id=chantier_id,
            code=CodeChantier(code),
            nom=f"Chantier {chantier_id}",
            adresse=f"Adresse {chantier_id}",
            statut=StatutChantier.from_string(statut),
        )

    # ==================== Tests Liste Sans Filtre ====================

    def test_list_chantiers_without_filters(self):
        """Test: liste chantiers sans filtre retourne tous les chantiers."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        chantiers = [
            self._create_chantier(1, "A001"),
            self._create_chantier(2, "A002"),
            self._create_chantier(3, "A003"),
        ]
        self.mock_repo.find_all.return_value = chantiers
        self.mock_repo.count.return_value = 3

        # Act
        result = use_case.execute(skip=0, limit=100)

        # Assert
        assert len(result.chantiers) == 3
        assert result.total == 3
        self.mock_repo.find_all.assert_called_once_with(skip=0, limit=100)
        self.mock_repo.count.assert_called_once()

    def test_list_chantiers_with_pagination(self):
        """Test: pagination fonctionne (skip/limit)."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        chantiers = [
            self._create_chantier(3, "A003"),
            self._create_chantier(4, "A004"),
        ]
        self.mock_repo.find_all.return_value = chantiers
        self.mock_repo.count.return_value = 10

        # Act
        result = use_case.execute(skip=2, limit=2)

        # Assert
        assert len(result.chantiers) == 2
        assert result.total == 10
        assert result.skip == 2
        assert result.limit == 2
        assert result.has_next is True
        assert result.has_previous is True

    def test_list_chantiers_empty_result(self):
        """Test: liste vide si aucun chantier."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.find_all.return_value = []
        self.mock_repo.count.return_value = 0

        # Act
        result = use_case.execute()

        # Assert
        assert len(result.chantiers) == 0
        assert result.total == 0

    # ==================== Tests Filtre par Statut ====================

    def test_list_chantiers_filter_by_statut(self):
        """Test: filtre par statut."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        chantiers = [
            self._create_chantier(1, "A001", "en_cours"),
            self._create_chantier(2, "A002", "en_cours"),
        ]
        self.mock_repo.find_by_statut.return_value = chantiers

        # Act
        result = use_case.execute(statut="en_cours")

        # Assert
        assert len(result.chantiers) == 2
        assert result.total == 2
        self.mock_repo.find_by_statut.assert_called_once()

    def test_list_chantiers_filter_actifs_uniquement(self):
        """Test: filtre actifs_uniquement."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        chantiers = [
            self._create_chantier(1, "A001", "ouvert"),
            self._create_chantier(2, "A002", "en_cours"),
        ]
        self.mock_repo.find_active.return_value = chantiers

        # Act
        result = use_case.execute(actifs_uniquement=True)

        # Assert
        assert len(result.chantiers) == 2
        assert result.total == 2
        self.mock_repo.find_active.assert_called_once()

    # ==================== Tests Filtre par Responsable ====================

    def test_list_chantiers_filter_by_conducteur(self):
        """Test: filtre par conducteur_id (CHT-05)."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        chantiers = [
            self._create_chantier(1, "A001"),
            self._create_chantier(2, "A002"),
        ]
        self.mock_repo.find_by_conducteur.return_value = chantiers

        # Act
        result = use_case.execute(conducteur_id=10)

        # Assert
        assert len(result.chantiers) == 2
        assert result.total == 2
        self.mock_repo.find_by_conducteur.assert_called_once_with(
            conducteur_id=10, skip=0, limit=10000
        )

    def test_list_chantiers_filter_by_chef_chantier(self):
        """Test: filtre par chef_chantier_id (CHT-06)."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        chantiers = [self._create_chantier(1, "A001")]
        self.mock_repo.find_by_chef_chantier.return_value = chantiers

        # Act
        result = use_case.execute(chef_chantier_id=20)

        # Assert
        assert len(result.chantiers) == 1
        assert result.total == 1
        self.mock_repo.find_by_chef_chantier.assert_called_once_with(
            chef_id=20, skip=0, limit=10000
        )

    def test_list_chantiers_filter_by_responsable(self):
        """Test: filtre par responsable_id (conducteur OU chef)."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        chantiers = [
            self._create_chantier(1, "A001"),
            self._create_chantier(2, "A002"),
            self._create_chantier(3, "A003"),
        ]
        self.mock_repo.find_by_responsable.return_value = chantiers

        # Act
        result = use_case.execute(responsable_id=30)

        # Assert
        assert len(result.chantiers) == 3
        assert result.total == 3
        self.mock_repo.find_by_responsable.assert_called_once_with(
            user_id=30, skip=0, limit=10000
        )

    # ==================== Tests Recherche Textuelle ====================

    def test_list_chantiers_search_by_text(self):
        """Test: recherche textuelle par nom ou code."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        chantiers = [
            self._create_chantier(1, "A001"),
            self._create_chantier(5, "A005"),
        ]
        self.mock_repo.search.return_value = chantiers

        # Act
        result = use_case.execute(search="A00")

        # Assert
        assert len(result.chantiers) == 2
        assert result.total == 2
        self.mock_repo.search.assert_called_once()

    def test_list_chantiers_search_with_statut(self):
        """Test: recherche textuelle avec filtre statut."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        chantiers = [self._create_chantier(1, "A001", "en_cours")]
        self.mock_repo.search.return_value = chantiers

        # Act
        result = use_case.execute(search="Test", statut="en_cours")

        # Assert
        assert len(result.chantiers) == 1
        self.mock_repo.search.assert_called_once()
        call_args = self.mock_repo.search.call_args
        assert call_args.kwargs['query'] == "Test"
        assert str(call_args.kwargs['statut']) == "en_cours"

    # ==================== Tests Pagination Filtres ====================

    def test_list_chantiers_filter_with_pagination(self):
        """Test: filtre avec pagination personnalisée."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        # Créer 10 chantiers
        all_chantiers = [self._create_chantier(i, f"A{i:03d}") for i in range(1, 11)]
        self.mock_repo.find_by_statut.return_value = all_chantiers

        # Act - Skip 3, limit 2
        result = use_case.execute(statut="ouvert", skip=3, limit=2)

        # Assert
        assert len(result.chantiers) == 2
        assert result.total == 10
        assert result.skip == 3
        assert result.limit == 2
        # Vérifier que ce sont les bons éléments (index 3 et 4)
        assert result.chantiers[0].id == 4
        assert result.chantiers[1].id == 5

    def test_list_chantiers_filter_pagination_last_page(self):
        """Test: dernière page de pagination."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        all_chantiers = [self._create_chantier(i, f"A{i:03d}") for i in range(1, 6)]
        self.mock_repo.find_active.return_value = all_chantiers

        # Act - Skip 4, limit 5 (devrait retourner 1 seul)
        result = use_case.execute(actifs_uniquement=True, skip=4, limit=5)

        # Assert
        assert len(result.chantiers) == 1
        assert result.total == 5
        assert result.has_next is False
        assert result.has_previous is True

    # ==================== Tests Cas Limites ====================

    def test_list_chantiers_filter_zero_results(self):
        """Test: filtre retourne zéro résultats."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.search.return_value = []

        # Act
        result = use_case.execute(search="Inexistant")

        # Assert
        assert len(result.chantiers) == 0
        assert result.total == 0

    def test_list_chantiers_default_limit(self):
        """Test: limite par défaut est 100."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.find_all.return_value = []
        self.mock_repo.count.return_value = 0

        # Act
        result = use_case.execute()

        # Assert
        assert result.limit == 100
        self.mock_repo.find_all.assert_called_with(skip=0, limit=100)

    def test_list_chantiers_multiple_filters_priority(self):
        """Test: priorité des filtres (search > responsable > conducteur > chef > statut > actifs)."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        chantiers = [self._create_chantier(1, "A001")]

        # Si search est fourni, il prend priorité
        self.mock_repo.search.return_value = chantiers

        # Act
        result = use_case.execute(
            search="Test",
            responsable_id=10,  # Ignoré car search prioritaire
            statut="ouvert",  # Passé à search
        )

        # Assert
        self.mock_repo.search.assert_called_once()
        self.mock_repo.find_by_responsable.assert_not_called()

    # ==================== Tests Logging Structuré (GAP-CHT-006) ====================

    @patch('modules.chantiers.application.use_cases.list_chantiers.logger')
    def test_execute_logs_started_event(self, mock_logger):
        """Test: execute() log événement 'started' avec extra dict."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        # Use concrete empty list, not Mock
        self.mock_repo.find_by_statut.return_value = []

        # Act
        use_case.execute(skip=10, limit=20, statut="en_cours")

        # Assert
        info_calls = mock_logger.info.call_args_list
        started_call = info_calls[0]

        assert "Use case execution started" in started_call.args[0]
        assert 'extra' in started_call.kwargs
        extra = started_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.started"
        assert extra['use_case'] == "ListChantiersUseCase"
        assert extra['operation'] == "list"
        assert extra['skip'] == 10
        assert extra['limit'] == 20
        assert 'filters' in extra
        assert extra['filters']['statut'] == "en_cours"

    @patch('modules.chantiers.application.use_cases.list_chantiers.logger')
    def test_execute_logs_succeeded_event(self, mock_logger):
        """Test: execute() log événement 'succeeded' avec compteur résultats."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        chantiers = [
            self._create_chantier(1, "A001"),
            self._create_chantier(2, "A002"),
        ]
        # Use filter to trigger the branch with succeeded log
        self.mock_repo.find_by_statut.return_value = chantiers

        # Act - Use statut filter to trigger succeeded log
        use_case.execute(statut="ouvert")

        # Assert
        info_calls = mock_logger.info.call_args_list
        assert len(info_calls) >= 2

        # Check last info call is succeeded
        succeeded_call = info_calls[-1]
        assert "Use case execution succeeded" in succeeded_call.args[0]
        extra = succeeded_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.succeeded"
        assert extra['use_case'] == "ListChantiersUseCase"
        assert extra['total_results'] == 2
        assert extra['returned_count'] == 2

    @patch('modules.chantiers.application.use_cases.list_chantiers.logger')
    def test_execute_logs_failed_event_on_error(self, mock_logger):
        """Test: execute() log événement 'failed' en cas d'erreur."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        # Provoquer une erreur
        self.mock_repo.find_all.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            use_case.execute()

        # Assert
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args

        assert "Use case execution failed" in error_call.args[0]
        extra = error_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.failed"
        assert extra['use_case'] == "ListChantiersUseCase"
        assert extra['error_type'] == "Exception"
        assert 'error_message' in extra

    @patch('modules.chantiers.application.use_cases.list_chantiers.logger')
    def test_execute_logs_all_filters(self, mock_logger):
        """Test: log contient tous les filtres fournis."""
        # Arrange
        use_case = ListChantiersUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.search.return_value = []

        # Act
        use_case.execute(
            skip=5,
            limit=25,
            statut="ferme",
            conducteur_id=100,
            chef_chantier_id=200,
            responsable_id=300,
            actifs_uniquement=True,
            search="Test",
        )

        # Assert
        started_call = mock_logger.info.call_args_list[0]
        extra = started_call.kwargs['extra']
        filters = extra['filters']

        assert filters['statut'] == "ferme"
        assert filters['conducteur_id'] == 100
        assert filters['chef_chantier_id'] == 200
        assert filters['responsable_id'] == 300
        assert filters['actifs_uniquement'] is True
        assert filters['search'] == "Test"
