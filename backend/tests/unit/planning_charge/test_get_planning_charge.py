"""Tests unitaires pour GetPlanningChargeUseCase."""

import pytest
from unittest.mock import Mock
from datetime import date

from modules.planning_charge.application.use_cases.get_planning_charge import (
    GetPlanningChargeUseCase,
)
from modules.planning_charge.application.dtos import PlanningChargeFiltersDTO
from modules.planning_charge.domain.value_objects import Semaine


class TestGetPlanningChargeUseCase:
    """Tests pour GetPlanningChargeUseCase."""

    def test_execute_basic_without_providers(self):
        """Test exécution basique sans providers."""
        mock_repo = Mock()
        mock_repo.get_chantiers_with_besoins.return_value = [1, 2]
        mock_repo.find_all_in_range.return_value = []

        use_case = GetPlanningChargeUseCase(
            besoin_repo=mock_repo,
            chantier_provider=None,
            affectation_provider=None,
        )

        filters = PlanningChargeFiltersDTO(
            semaine_debut="S01-2026",
            semaine_fin="S02-2026",
            unite="heures",
        )

        result = use_case.execute(filters)

        assert result.semaine_debut == "S01-2026"
        assert result.semaine_fin == "S02-2026"
        assert len(result.semaines) == 2
        assert len(result.chantiers) == 2

    def test_execute_with_chantier_provider(self):
        """Test exécution avec provider chantiers."""
        mock_repo = Mock()
        mock_repo.find_all_in_range.return_value = []

        mock_chantier_provider = Mock()
        mock_chantier_provider.get_chantiers_actifs.return_value = [
            {"id": 1, "code": "CH001", "nom": "Chantier 1", "couleur": "#FF0000", "heures_estimees": 100.0},
            {"id": 2, "code": "CH002", "nom": "Chantier 2", "couleur": "#00FF00", "heures_estimees": 200.0},
        ]

        use_case = GetPlanningChargeUseCase(
            besoin_repo=mock_repo,
            chantier_provider=mock_chantier_provider,
            affectation_provider=None,
        )

        filters = PlanningChargeFiltersDTO(
            semaine_debut="S01-2026",
            semaine_fin="S01-2026",
            unite="heures",
        )

        result = use_case.execute(filters)

        assert result.total_chantiers == 2
        assert result.chantiers[0].code == "CH001"
        assert result.chantiers[1].code == "CH002"

    def test_execute_with_search_filter(self):
        """Test exécution avec filtre recherche."""
        mock_repo = Mock()
        mock_repo.find_all_in_range.return_value = []

        mock_chantier_provider = Mock()
        mock_chantier_provider.get_chantiers_actifs.return_value = [
            {"id": 1, "code": "CH001", "nom": "Chantier Test", "couleur": "#FF0000", "heures_estimees": 100.0},
        ]

        use_case = GetPlanningChargeUseCase(
            besoin_repo=mock_repo,
            chantier_provider=mock_chantier_provider,
            affectation_provider=None,
        )

        filters = PlanningChargeFiltersDTO(
            semaine_debut="S01-2026",
            semaine_fin="S01-2026",
            unite="heures",
            recherche="Test",
        )

        result = use_case.execute(filters)

        mock_chantier_provider.get_chantiers_actifs.assert_called_once_with(search="Test")

    def test_execute_with_besoins(self):
        """Test exécution avec besoins existants."""
        mock_repo = Mock()

        mock_besoin = Mock()
        mock_besoin.chantier_id = 1
        mock_besoin.semaine = Semaine(2026, 1)
        mock_besoin.besoin_heures = 35.0

        mock_repo.find_all_in_range.return_value = [mock_besoin]

        mock_chantier_provider = Mock()
        mock_chantier_provider.get_chantiers_actifs.return_value = [
            {"id": 1, "code": "CH001", "nom": "Chantier 1", "couleur": "#FF0000", "heures_estimees": 100.0},
        ]

        use_case = GetPlanningChargeUseCase(
            besoin_repo=mock_repo,
            chantier_provider=mock_chantier_provider,
            affectation_provider=None,
        )

        filters = PlanningChargeFiltersDTO(
            semaine_debut="S01-2026",
            semaine_fin="S01-2026",
            unite="heures",
        )

        result = use_case.execute(filters)

        assert result.besoin_total == 35.0
        assert result.chantiers[0].semaines[0].cellule.besoin_heures == 35.0

    def test_execute_with_affectation_provider(self):
        """Test exécution avec provider affectations."""
        mock_repo = Mock()
        mock_repo.find_all_in_range.return_value = []

        mock_chantier_provider = Mock()
        mock_chantier_provider.get_chantiers_actifs.return_value = [
            {"id": 1, "code": "CH001", "nom": "Chantier 1", "couleur": "#FF0000", "heures_estimees": 100.0},
        ]

        mock_affectation_provider = Mock()
        mock_affectation_provider.get_heures_planifiees_par_chantier_et_semaine.return_value = {
            (1, "S01-2026"): 20.0,
        }
        mock_affectation_provider.get_capacite_par_semaine.return_value = {
            "S01-2026": 175.0,  # 5 personnes * 35h
        }
        mock_affectation_provider.get_utilisateurs_non_planifies_par_semaine.return_value = {
            "S01-2026": 2,
        }

        use_case = GetPlanningChargeUseCase(
            besoin_repo=mock_repo,
            chantier_provider=mock_chantier_provider,
            affectation_provider=mock_affectation_provider,
        )

        filters = PlanningChargeFiltersDTO(
            semaine_debut="S01-2026",
            semaine_fin="S01-2026",
            unite="heures",
        )

        result = use_case.execute(filters)

        assert result.planifie_total == 20.0
        assert result.capacite_totale == 175.0
        assert result.chantiers[0].semaines[0].cellule.planifie_heures == 20.0

    def test_footer_calculation(self):
        """Test calcul du footer."""
        mock_repo = Mock()
        mock_repo.find_all_in_range.return_value = []

        mock_chantier_provider = Mock()
        mock_chantier_provider.get_chantiers_actifs.return_value = [
            {"id": 1, "code": "CH001", "nom": "Chantier 1", "couleur": "#FF0000", "heures_estimees": 100.0},
        ]

        mock_affectation_provider = Mock()
        mock_affectation_provider.get_heures_planifiees_par_chantier_et_semaine.return_value = {
            (1, "S01-2026"): 140.0,  # 80% de 175h
        }
        mock_affectation_provider.get_capacite_par_semaine.return_value = {
            "S01-2026": 175.0,
        }
        mock_affectation_provider.get_utilisateurs_non_planifies_par_semaine.return_value = {
            "S01-2026": 1,
        }

        use_case = GetPlanningChargeUseCase(
            besoin_repo=mock_repo,
            chantier_provider=mock_chantier_provider,
            affectation_provider=mock_affectation_provider,
        )

        filters = PlanningChargeFiltersDTO(
            semaine_debut="S01-2026",
            semaine_fin="S01-2026",
            unite="heures",
        )

        result = use_case.execute(filters)

        assert len(result.footer) == 1
        assert result.footer[0].semaine_code == "S01-2026"
        assert result.footer[0].taux_occupation == 80.0  # 140/175
        assert result.footer[0].a_placer == 1

    def test_generate_semaines_multiple_weeks(self):
        """Test génération de plusieurs semaines."""
        mock_repo = Mock()
        mock_repo.get_chantiers_with_besoins.return_value = []
        mock_repo.find_all_in_range.return_value = []

        use_case = GetPlanningChargeUseCase(
            besoin_repo=mock_repo,
            chantier_provider=None,
            affectation_provider=None,
        )

        filters = PlanningChargeFiltersDTO(
            semaine_debut="S01-2026",
            semaine_fin="S04-2026",
            unite="heures",
        )

        result = use_case.execute(filters)

        assert len(result.semaines) == 4
        assert result.semaines[0] == "S01-2026"
        assert result.semaines[3] == "S04-2026"

    def test_generate_semaines_year_transition(self):
        """Test génération semaines avec changement d'année."""
        mock_repo = Mock()
        mock_repo.get_chantiers_with_besoins.return_value = []
        mock_repo.find_all_in_range.return_value = []

        use_case = GetPlanningChargeUseCase(
            besoin_repo=mock_repo,
            chantier_provider=None,
            affectation_provider=None,
        )

        filters = PlanningChargeFiltersDTO(
            semaine_debut="S52-2025",
            semaine_fin="S02-2026",
            unite="heures",
        )

        result = use_case.execute(filters)

        # S52-2025, S01-2026, S02-2026
        assert len(result.semaines) >= 3

    def test_non_couvert_calculation(self):
        """Test calcul du besoin non couvert."""
        mock_repo = Mock()

        mock_besoin = Mock()
        mock_besoin.chantier_id = 1
        mock_besoin.semaine = Semaine(2026, 1)
        mock_besoin.besoin_heures = 50.0

        mock_repo.find_all_in_range.return_value = [mock_besoin]

        mock_chantier_provider = Mock()
        mock_chantier_provider.get_chantiers_actifs.return_value = [
            {"id": 1, "code": "CH001", "nom": "Chantier 1", "couleur": "#FF0000", "heures_estimees": 100.0},
        ]

        mock_affectation_provider = Mock()
        mock_affectation_provider.get_heures_planifiees_par_chantier_et_semaine.return_value = {
            (1, "S01-2026"): 30.0,  # Besoin 50, planifié 30 = non couvert 20
        }
        mock_affectation_provider.get_capacite_par_semaine.return_value = {"S01-2026": 175.0}
        mock_affectation_provider.get_utilisateurs_non_planifies_par_semaine.return_value = {"S01-2026": 0}

        use_case = GetPlanningChargeUseCase(
            besoin_repo=mock_repo,
            chantier_provider=mock_chantier_provider,
            affectation_provider=mock_affectation_provider,
        )

        filters = PlanningChargeFiltersDTO(
            semaine_debut="S01-2026",
            semaine_fin="S01-2026",
            unite="heures",
        )

        result = use_case.execute(filters)

        cellule = result.chantiers[0].semaines[0].cellule
        assert cellule.besoin_non_couvert == 20.0  # 50 - 30

    def test_a_recruter_calculation(self):
        """Test calcul du nombre à recruter."""
        mock_repo = Mock()

        mock_besoin = Mock()
        mock_besoin.chantier_id = 1
        mock_besoin.semaine = Semaine(2026, 1)
        mock_besoin.besoin_heures = 250.0  # Besoin > capacité

        mock_repo.find_all_in_range.return_value = [mock_besoin]

        mock_chantier_provider = Mock()
        mock_chantier_provider.get_chantiers_actifs.return_value = [
            {"id": 1, "code": "CH001", "nom": "Chantier 1", "couleur": "#FF0000", "heures_estimees": 100.0},
        ]

        mock_affectation_provider = Mock()
        mock_affectation_provider.get_heures_planifiees_par_chantier_et_semaine.return_value = {}
        mock_affectation_provider.get_capacite_par_semaine.return_value = {
            "S01-2026": 175.0,  # Capacité 175h, besoin 250h -> déficit 75h -> 2 personnes
        }
        mock_affectation_provider.get_utilisateurs_non_planifies_par_semaine.return_value = {"S01-2026": 0}

        use_case = GetPlanningChargeUseCase(
            besoin_repo=mock_repo,
            chantier_provider=mock_chantier_provider,
            affectation_provider=mock_affectation_provider,
        )

        filters = PlanningChargeFiltersDTO(
            semaine_debut="S01-2026",
            semaine_fin="S01-2026",
            unite="heures",
        )

        result = use_case.execute(filters)

        # Déficit = 250 - 175 = 75h -> 75/35 = 2.14 -> arrondi à 2
        assert result.footer[0].a_recruter == 2
