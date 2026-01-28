"""Tests unitaires pour GetOccupationDetailsUseCase."""

import pytest
from unittest.mock import Mock

from modules.planning.application.use_cases.charge.get_occupation_details import (
    GetOccupationDetailsUseCase,
)
from modules.planning.domain.value_objects import Semaine, TypeMetier


class TestGetOccupationDetailsUseCase:
    """Tests pour GetOccupationDetailsUseCase."""

    def test_execute_basic_without_providers(self):
        """Test exécution basique sans providers."""
        mock_repo = Mock()
        mock_repo.find_by_semaine.return_value = []

        use_case = GetOccupationDetailsUseCase(
            besoin_repo=mock_repo,
            utilisateur_provider=None,
            affectation_provider=None,
        )

        result = use_case.execute("S01-2026")

        assert result.semaine_code == "S01-2026"
        assert result.planifie_total == 0.0
        assert result.besoin_total == 0.0

    def test_execute_with_besoins(self):
        """Test exécution avec besoins."""
        mock_repo = Mock()

        mock_besoin1 = Mock()
        mock_besoin1.type_metier = TypeMetier.MACON
        mock_besoin1.besoin_heures = 35.0

        mock_besoin2 = Mock()
        mock_besoin2.type_metier = TypeMetier.MACON
        mock_besoin2.besoin_heures = 70.0

        mock_besoin3 = Mock()
        mock_besoin3.type_metier = TypeMetier.ELECTRICIEN
        mock_besoin3.besoin_heures = 35.0

        mock_repo.find_by_semaine.return_value = [mock_besoin1, mock_besoin2, mock_besoin3]

        use_case = GetOccupationDetailsUseCase(
            besoin_repo=mock_repo,
            utilisateur_provider=None,
            affectation_provider=None,
        )

        result = use_case.execute("S01-2026")

        assert result.besoin_total == 140.0  # 35 + 70 + 35
        # Vérifie que les types sont présents
        type_keys = [t.type_metier for t in result.types]
        assert "macon" in type_keys
        assert "electricien" in type_keys

    def test_execute_with_utilisateur_provider(self):
        """Test exécution avec provider utilisateurs."""
        mock_repo = Mock()
        mock_repo.find_by_semaine.return_value = []

        mock_utilisateur_provider = Mock()
        mock_utilisateur_provider.get_capacite_par_type_metier.return_value = {
            "macon": 175.0,  # 5 maçons * 35h
            "electricien": 70.0,  # 2 électriciens * 35h
        }

        use_case = GetOccupationDetailsUseCase(
            besoin_repo=mock_repo,
            utilisateur_provider=mock_utilisateur_provider,
            affectation_provider=None,
        )

        result = use_case.execute("S01-2026")

        assert result.capacite_totale == 245.0

    def test_execute_with_affectation_provider(self):
        """Test exécution avec provider affectations."""
        mock_repo = Mock()
        mock_repo.find_by_semaine.return_value = []

        mock_utilisateur_provider = Mock()
        mock_utilisateur_provider.get_capacite_par_type_metier.return_value = {
            "macon": 175.0,
        }

        mock_affectation_provider = Mock()
        mock_affectation_provider.get_heures_planifiees_par_type_metier.return_value = {
            "macon": 140.0,  # 80% d'occupation
        }

        use_case = GetOccupationDetailsUseCase(
            besoin_repo=mock_repo,
            utilisateur_provider=mock_utilisateur_provider,
            affectation_provider=mock_affectation_provider,
        )

        result = use_case.execute("S01-2026")

        assert result.planifie_total == 140.0
        # Cherche le type macon
        macon_type = next((t for t in result.types if t.type_metier == "macon"), None)
        assert macon_type is not None
        assert macon_type.planifie_heures == 140.0
        assert macon_type.taux_occupation == 80.0

    def test_taux_global_calculation(self):
        """Test calcul du taux global."""
        mock_repo = Mock()
        mock_repo.find_by_semaine.return_value = []

        mock_utilisateur_provider = Mock()
        mock_utilisateur_provider.get_capacite_par_type_metier.return_value = {
            "macon": 100.0,
            "electricien": 100.0,
        }

        mock_affectation_provider = Mock()
        mock_affectation_provider.get_heures_planifiees_par_type_metier.return_value = {
            "macon": 80.0,
            "electricien": 60.0,
        }

        use_case = GetOccupationDetailsUseCase(
            besoin_repo=mock_repo,
            utilisateur_provider=mock_utilisateur_provider,
            affectation_provider=mock_affectation_provider,
        )

        result = use_case.execute("S01-2026")

        # 140 planifié / 200 capacité = 70%
        assert result.taux_global == 70.0

    def test_a_recruter_calculation(self):
        """Test calcul du nombre à recruter."""
        mock_repo = Mock()

        mock_besoin = Mock()
        mock_besoin.type_metier = TypeMetier.MACON
        mock_besoin.besoin_heures = 250.0

        mock_repo.find_by_semaine.return_value = [mock_besoin]

        mock_utilisateur_provider = Mock()
        mock_utilisateur_provider.get_capacite_par_type_metier.return_value = {
            "macon": 175.0,  # Déficit de 75h
        }

        use_case = GetOccupationDetailsUseCase(
            besoin_repo=mock_repo,
            utilisateur_provider=mock_utilisateur_provider,
            affectation_provider=None,
        )

        result = use_case.execute("S01-2026")

        # Déficit = 250 - 175 = 75h -> 75/35 = 2.14 -> arrondi à 2
        assert result.a_recruter == 2

    def test_a_placer_calculation(self):
        """Test calcul du nombre à placer."""
        mock_repo = Mock()
        mock_repo.find_by_semaine.return_value = []

        mock_utilisateur_provider = Mock()
        mock_utilisateur_provider.get_capacite_par_type_metier.return_value = {
            "macon": 175.0,
        }

        mock_affectation_provider = Mock()
        mock_affectation_provider.get_heures_planifiees_par_type_metier.return_value = {
            "macon": 70.0,  # Surplus de 105h
        }

        use_case = GetOccupationDetailsUseCase(
            besoin_repo=mock_repo,
            utilisateur_provider=mock_utilisateur_provider,
            affectation_provider=mock_affectation_provider,
        )

        result = use_case.execute("S01-2026")

        # Surplus = 175 - 70 = 105h -> 105/35 = 3
        assert result.a_placer == 3

    def test_skips_empty_types(self):
        """Test ignore les types sans activité."""
        mock_repo = Mock()

        mock_besoin = Mock()
        mock_besoin.type_metier = TypeMetier.MACON
        mock_besoin.besoin_heures = 35.0

        mock_repo.find_by_semaine.return_value = [mock_besoin]

        mock_utilisateur_provider = Mock()
        mock_utilisateur_provider.get_capacite_par_type_metier.return_value = {
            "macon": 175.0,
        }

        mock_affectation_provider = Mock()
        mock_affectation_provider.get_heures_planifiees_par_type_metier.return_value = {
            "macon": 35.0,
        }

        use_case = GetOccupationDetailsUseCase(
            besoin_repo=mock_repo,
            utilisateur_provider=mock_utilisateur_provider,
            affectation_provider=mock_affectation_provider,
        )

        result = use_case.execute("S01-2026")

        # Seul le type macon devrait être présent
        assert len(result.types) == 1
        assert result.types[0].type_metier == "macon"

    def test_alerte_surcharge(self):
        """Test alerte surcharge quand taux > 100%."""
        mock_repo = Mock()
        mock_repo.find_by_semaine.return_value = []

        mock_utilisateur_provider = Mock()
        mock_utilisateur_provider.get_capacite_par_type_metier.return_value = {
            "macon": 100.0,
        }

        mock_affectation_provider = Mock()
        mock_affectation_provider.get_heures_planifiees_par_type_metier.return_value = {
            "macon": 120.0,  # 120% d'occupation
        }

        use_case = GetOccupationDetailsUseCase(
            besoin_repo=mock_repo,
            utilisateur_provider=mock_utilisateur_provider,
            affectation_provider=mock_affectation_provider,
        )

        result = use_case.execute("S01-2026")

        macon_type = next((t for t in result.types if t.type_metier == "macon"), None)
        assert macon_type is not None
        assert macon_type.taux_occupation == 120.0
        assert macon_type.alerte is True

    def test_type_metier_details(self):
        """Test que les détails du type métier sont inclus."""
        mock_repo = Mock()

        mock_besoin = Mock()
        mock_besoin.type_metier = TypeMetier.ELECTRICIEN
        mock_besoin.besoin_heures = 35.0

        mock_repo.find_by_semaine.return_value = [mock_besoin]

        mock_utilisateur_provider = Mock()
        mock_utilisateur_provider.get_capacite_par_type_metier.return_value = {
            "electricien": 70.0,
        }

        use_case = GetOccupationDetailsUseCase(
            besoin_repo=mock_repo,
            utilisateur_provider=mock_utilisateur_provider,
            affectation_provider=None,
        )

        result = use_case.execute("S01-2026")

        elec_type = next((t for t in result.types if t.type_metier == "electricien"), None)
        assert elec_type is not None
        assert elec_type.type_metier_label == TypeMetier.ELECTRICIEN.label
        assert elec_type.type_metier_couleur == TypeMetier.ELECTRICIEN.couleur
