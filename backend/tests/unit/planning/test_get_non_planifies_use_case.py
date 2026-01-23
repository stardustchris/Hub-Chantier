"""Tests unitaires pour GetNonPlanifiesUseCase."""

import pytest
from unittest.mock import Mock
from datetime import date, timedelta

from modules.planning.domain.entities import Affectation
from modules.planning.domain.repositories import AffectationRepository
from modules.planning.application.use_cases.get_non_planifies import (
    GetNonPlanifiesUseCase,
)


class TestGetNonPlanifiesUseCase:
    """Tests pour le use case de récupération des utilisateurs non planifiés."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_affectation_repo = Mock(spec=AffectationRepository)
        self.use_case = GetNonPlanifiesUseCase(
            affectation_repo=self.mock_affectation_repo,
        )

        self.date_debut = date(2026, 1, 20)  # Lundi
        self.date_fin = date(2026, 1, 24)  # Vendredi

    def test_get_non_planifies_from_repo(self):
        """Test: récupération depuis le repository."""
        self.mock_affectation_repo.find_non_planifies.return_value = [1, 2, 3]

        result = self.use_case.execute(self.date_debut, self.date_fin)

        assert result == [1, 2, 3]
        self.mock_affectation_repo.find_non_planifies.assert_called_once_with(
            self.date_debut, self.date_fin
        )

    def test_get_non_planifies_empty(self):
        """Test: aucun utilisateur non planifié."""
        self.mock_affectation_repo.find_non_planifies.return_value = []

        result = self.use_case.execute(self.date_debut, self.date_fin)

        assert result == []

    def test_get_non_planifies_invalid_dates(self):
        """Test: échec si dates invalides."""
        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(self.date_fin, self.date_debut)

        assert "posterieure" in str(exc_info.value)

    def test_get_non_planifies_with_active_users(self):
        """Test: calcul avec liste des utilisateurs actifs."""
        get_active_ids = Mock(return_value=[1, 2, 3, 4, 5])
        use_case = GetNonPlanifiesUseCase(
            affectation_repo=self.mock_affectation_repo,
            get_active_user_ids=get_active_ids,
        )

        # Le repo retourne vide, on utilise le calcul manuel
        self.mock_affectation_repo.find_non_planifies.return_value = []

        # Simule des affectations pour les utilisateurs 1 et 2
        affectation1 = Mock()
        affectation1.utilisateur_id = 1
        affectation2 = Mock()
        affectation2.utilisateur_id = 2
        self.mock_affectation_repo.find_by_date_range.return_value = [
            affectation1,
            affectation2,
        ]

        result = use_case.execute(self.date_debut, self.date_fin)

        # Les utilisateurs 3, 4, 5 n'ont pas d'affectation
        assert set(result) == {3, 4, 5}

    def test_execute_for_day(self):
        """Test: méthode de commodité pour une journée."""
        self.mock_affectation_repo.find_non_planifies.return_value = [1, 2]

        result = self.use_case.execute_for_day(self.date_debut)

        self.mock_affectation_repo.find_non_planifies.assert_called_once_with(
            self.date_debut, self.date_debut
        )

    def test_get_non_planifies_same_date(self):
        """Test: même date début et fin."""
        self.mock_affectation_repo.find_non_planifies.return_value = [1]

        result = self.use_case.execute(self.date_debut, self.date_debut)

        assert result == [1]
