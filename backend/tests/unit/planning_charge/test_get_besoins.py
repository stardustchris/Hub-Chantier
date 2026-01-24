"""Tests unitaires pour le use case GetBesoinsByChantier."""

import pytest
from unittest.mock import Mock

from modules.planning_charge.domain.entities import BesoinCharge
from modules.planning_charge.domain.value_objects import Semaine, TypeMetier
from modules.planning_charge.application.use_cases import (
    GetBesoinsByChantierUseCase,
    InvalidSemaineRangeError,
)


class TestGetBesoinsByChantierUseCase:
    """Tests pour le use case GetBesoinsByChantier."""

    @pytest.fixture
    def mock_repo(self):
        """Fixture pour le repository mock."""
        return Mock()

    @pytest.fixture
    def use_case(self, mock_repo):
        """Fixture pour le use case."""
        return GetBesoinsByChantierUseCase(mock_repo)

    @pytest.fixture
    def sample_besoins(self):
        """Fixture pour une liste de besoins."""
        return [
            BesoinCharge(
                id=1,
                chantier_id=1,
                semaine=Semaine(annee=2026, numero=4),
                type_metier=TypeMetier.MACON,
                besoin_heures=35.0,
                created_by=1,
            ),
            BesoinCharge(
                id=2,
                chantier_id=1,
                semaine=Semaine(annee=2026, numero=4),
                type_metier=TypeMetier.COFFREUR,
                besoin_heures=28.0,
                created_by=1,
            ),
            BesoinCharge(
                id=3,
                chantier_id=1,
                semaine=Semaine(annee=2026, numero=5),
                type_metier=TypeMetier.MACON,
                besoin_heures=42.0,
                created_by=1,
            ),
        ]

    def test_get_besoins_success(self, use_case, mock_repo, sample_besoins):
        """Test recuperation reussie des besoins."""
        # Setup
        mock_repo.find_by_chantier.return_value = sample_besoins

        # Execute
        result = use_case.execute(
            chantier_id=1,
            semaine_debut="S04-2026",
            semaine_fin="S06-2026",
        )

        # Verify
        assert len(result) == 3
        assert result[0].id == 1
        assert result[0].type_metier == "macon"

    def test_get_besoins_empty(self, use_case, mock_repo):
        """Test recuperation sans besoins."""
        # Setup
        mock_repo.find_by_chantier.return_value = []

        # Execute
        result = use_case.execute(
            chantier_id=1,
            semaine_debut="S04-2026",
            semaine_fin="S06-2026",
        )

        # Verify
        assert len(result) == 0

    def test_get_besoins_invalid_range(self, use_case, mock_repo):
        """Test erreur si debut > fin."""
        # Execute & Verify
        with pytest.raises(InvalidSemaineRangeError):
            use_case.execute(
                chantier_id=1,
                semaine_debut="S10-2026",
                semaine_fin="S04-2026",
            )

    def test_get_besoins_same_week(self, use_case, mock_repo, sample_besoins):
        """Test recuperation pour une seule semaine."""
        # Setup
        mock_repo.find_by_chantier.return_value = sample_besoins[:2]

        # Execute
        result = use_case.execute(
            chantier_id=1,
            semaine_debut="S04-2026",
            semaine_fin="S04-2026",
        )

        # Verify
        assert len(result) == 2

    def test_get_besoins_invalid_semaine_format(self, use_case, mock_repo):
        """Test erreur si format semaine invalide."""
        with pytest.raises(ValueError):
            use_case.execute(
                chantier_id=1,
                semaine_debut="INVALID",
                semaine_fin="S04-2026",
            )

    def test_get_besoins_dto_conversion(self, use_case, mock_repo, sample_besoins):
        """Test que les entites sont converties en DTOs."""
        # Setup
        mock_repo.find_by_chantier.return_value = sample_besoins

        # Execute
        result = use_case.execute(
            chantier_id=1,
            semaine_debut="S04-2026",
            semaine_fin="S06-2026",
        )

        # Verify - les resultats sont des DTOs
        assert hasattr(result[0], "type_metier_label")
        assert hasattr(result[0], "type_metier_couleur")
        assert hasattr(result[0], "besoin_jours_homme")
