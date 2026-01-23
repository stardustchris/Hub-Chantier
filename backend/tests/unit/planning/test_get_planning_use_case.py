"""Tests unitaires pour le use case GetPlanning.

Ce fichier teste :
- Recuperation avec filtres
- Filtrage par role (admin voit tout, compagnon voit son planning)
- Enrichissement avec infos utilisateur et chantier
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import date

from modules.planning.domain.entities.affectation import Affectation
from modules.planning.domain.repositories.affectation_repository import AffectationRepository
from modules.planning.domain.value_objects.heure_affectation import HeureAffectation
from modules.planning.domain.value_objects.type_affectation import TypeAffectation
from modules.planning.application.use_cases.get_planning import GetPlanningUseCase
from modules.planning.application.dtos.planning_filters_dto import PlanningFiltersDTO
from modules.planning.application.dtos.affectation_dto import AffectationDTO


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_affectation_repository():
    """Fixture: mock du repository d'affectations."""
    return Mock(spec=AffectationRepository)


@pytest.fixture
def mock_get_user_info():
    """Fixture: fonction mock pour recuperer les infos utilisateur."""
    def get_info(user_id):
        users = {
            1: {"nom": "Jean Dupont", "couleur": "#FF0000", "metier": "Macon"},
            2: {"nom": "Pierre Martin", "couleur": "#00FF00", "metier": "Electricien"},
            3: {"nom": "Marie Durand", "couleur": "#0000FF", "metier": "Plombier"},
        }
        return users.get(user_id, {})
    return get_info


@pytest.fixture
def mock_get_chantier_info():
    """Fixture: fonction mock pour recuperer les infos chantier."""
    def get_info(chantier_id):
        chantiers = {
            10: {"nom": "Villa Lyon", "couleur": "#E74C3C"},
            20: {"nom": "Immeuble Paris", "couleur": "#3498DB"},
        }
        return chantiers.get(chantier_id, {})
    return get_info


@pytest.fixture
def mock_get_user_chantiers():
    """Fixture: fonction mock pour recuperer les chantiers d'un chef."""
    def get_chantiers(user_id):
        # Le chef 3 gere les chantiers 10 et 20
        user_chantiers = {
            3: [10, 20],
            4: [10],
        }
        return user_chantiers.get(user_id, [])
    return get_chantiers


@pytest.fixture
def use_case(mock_affectation_repository, mock_get_user_info, mock_get_chantier_info, mock_get_user_chantiers):
    """Fixture: instance du use case avec mocks."""
    return GetPlanningUseCase(
        affectation_repo=mock_affectation_repository,
        get_user_info=mock_get_user_info,
        get_chantier_info=mock_get_chantier_info,
        get_user_chantiers=mock_get_user_chantiers,
    )


@pytest.fixture
def use_case_minimal(mock_affectation_repository):
    """Fixture: use case sans fonctions d'enrichissement."""
    return GetPlanningUseCase(
        affectation_repo=mock_affectation_repository,
    )


@pytest.fixture
def sample_affectations():
    """Fixture: liste d'affectations de test."""
    return [
        Affectation(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date=date(2026, 1, 22),
            heure_debut=HeureAffectation(8, 0),
            heure_fin=HeureAffectation(17, 0),
            created_by=3,
        ),
        Affectation(
            id=2,
            utilisateur_id=2,
            chantier_id=10,
            date=date(2026, 1, 22),
            heure_debut=HeureAffectation(8, 0),
            heure_fin=HeureAffectation(17, 0),
            created_by=3,
        ),
        Affectation(
            id=3,
            utilisateur_id=1,
            chantier_id=20,
            date=date(2026, 1, 23),
            heure_debut=HeureAffectation(9, 0),
            heure_fin=HeureAffectation(18, 0),
            created_by=3,
        ),
    ]


# =============================================================================
# Tests Filtrage par Role - Admin
# =============================================================================

class TestGetPlanningAdmin:
    """Tests pour le role Admin."""

    def test_should_return_all_affectations_for_admin(
        self, use_case, mock_affectation_repository, sample_affectations
    ):
        """Test: admin voit toutes les affectations."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = sample_affectations
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        # Act
        result = use_case.execute(
            filters=filters,
            current_user_id=99,
            current_user_role="admin",
        )

        # Assert
        assert len(result) == 3

    def test_should_return_all_for_administrateur(
        self, use_case, mock_affectation_repository, sample_affectations
    ):
        """Test: administrateur (variante) voit tout."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = sample_affectations
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        # Act
        result = use_case.execute(
            filters=filters,
            current_user_id=99,
            current_user_role="administrateur",
        )

        # Assert
        assert len(result) == 3


# =============================================================================
# Tests Filtrage par Role - Conducteur
# =============================================================================

class TestGetPlanningConducteur:
    """Tests pour le role Conducteur."""

    def test_should_return_all_affectations_for_conducteur(
        self, use_case, mock_affectation_repository, sample_affectations
    ):
        """Test: conducteur voit toutes les affectations."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = sample_affectations
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        # Act
        result = use_case.execute(
            filters=filters,
            current_user_id=99,
            current_user_role="conducteur",
        )

        # Assert
        assert len(result) == 3

    def test_should_return_all_for_conducteur_travaux(
        self, use_case, mock_affectation_repository, sample_affectations
    ):
        """Test: conducteur_travaux (variante) voit tout."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = sample_affectations
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        # Act
        result = use_case.execute(
            filters=filters,
            current_user_id=99,
            current_user_role="conducteur_travaux",
        )

        # Assert
        assert len(result) == 3


# =============================================================================
# Tests Filtrage par Role - Chef de Chantier
# =============================================================================

class TestGetPlanningChefChantier:
    """Tests pour le role Chef de Chantier."""

    def test_should_return_only_chantiers_managed_by_chef(
        self, use_case, mock_affectation_repository, sample_affectations
    ):
        """Test: chef de chantier voit seulement ses chantiers."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = sample_affectations
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        # Act - Chef 3 gere chantiers 10 et 20
        result = use_case.execute(
            filters=filters,
            current_user_id=3,
            current_user_role="chef_chantier",
        )

        # Assert - Toutes les affectations sont sur chantiers 10 ou 20
        assert len(result) == 3

    def test_should_filter_to_only_managed_chantiers(
        self, use_case, mock_affectation_repository
    ):
        """Test: chef voit uniquement les affectations de ses chantiers."""
        # Arrange
        affectations = [
            Affectation(
                id=1,
                utilisateur_id=1,
                chantier_id=10,  # Gere par chef 4
                date=date(2026, 1, 22),
                created_by=3,
            ),
            Affectation(
                id=2,
                utilisateur_id=2,
                chantier_id=30,  # PAS gere par chef 4
                date=date(2026, 1, 22),
                created_by=3,
            ),
        ]
        mock_affectation_repository.find_by_date_range.return_value = affectations
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        # Act - Chef 4 gere uniquement chantier 10
        result = use_case.execute(
            filters=filters,
            current_user_id=4,
            current_user_role="chef_chantier",
        )

        # Assert - Seulement l'affectation du chantier 10
        assert len(result) == 1
        assert result[0].chantier_id == 10


# =============================================================================
# Tests Filtrage par Role - Compagnon
# =============================================================================

class TestGetPlanningCompagnon:
    """Tests pour le role Compagnon."""

    def test_should_return_only_own_affectations_for_compagnon(
        self, use_case, mock_affectation_repository, sample_affectations
    ):
        """Test: compagnon voit uniquement ses affectations."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = sample_affectations
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        # Act - Utilisateur 1 est compagnon
        result = use_case.execute(
            filters=filters,
            current_user_id=1,
            current_user_role="compagnon",
        )

        # Assert - Seulement les affectations de l'utilisateur 1
        assert len(result) == 2
        for dto in result:
            assert dto.utilisateur_id == 1

    def test_should_return_only_own_for_ouvrier(
        self, use_case, mock_affectation_repository, sample_affectations
    ):
        """Test: ouvrier (variante) voit uniquement ses affectations."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = sample_affectations
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        # Act
        result = use_case.execute(
            filters=filters,
            current_user_id=2,
            current_user_role="ouvrier",
        )

        # Assert - Seulement les affectations de l'utilisateur 2
        assert len(result) == 1
        assert result[0].utilisateur_id == 2


# =============================================================================
# Tests Filtrage par Role - Role Inconnu
# =============================================================================

class TestGetPlanningUnknownRole:
    """Tests pour un role inconnu."""

    def test_should_return_only_own_affectations_for_unknown_role(
        self, use_case, mock_affectation_repository, sample_affectations
    ):
        """Test: role inconnu = securite minimale (voir que soi)."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = sample_affectations
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        # Act
        result = use_case.execute(
            filters=filters,
            current_user_id=1,
            current_user_role="role_inconnu",
        )

        # Assert - Securite: seulement ses propres affectations
        assert len(result) == 2
        for dto in result:
            assert dto.utilisateur_id == 1


# =============================================================================
# Tests Filtres
# =============================================================================

class TestGetPlanningFilters:
    """Tests pour les filtres de recherche."""

    def test_should_filter_by_utilisateur_ids(
        self, use_case, mock_affectation_repository, sample_affectations
    ):
        """Test: filtre par IDs utilisateurs."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = sample_affectations
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
            utilisateur_ids=[1],
        )

        # Act
        result = use_case.execute(
            filters=filters,
            current_user_id=99,
            current_user_role="admin",
        )

        # Assert
        assert len(result) == 2
        for dto in result:
            assert dto.utilisateur_id == 1

    def test_should_filter_by_chantier_ids(
        self, use_case, mock_affectation_repository, sample_affectations
    ):
        """Test: filtre par IDs chantiers."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = sample_affectations
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
            chantier_ids=[10],
        )

        # Act
        result = use_case.execute(
            filters=filters,
            current_user_id=99,
            current_user_role="admin",
        )

        # Assert - 2 affectations sur chantier 10
        assert len(result) == 2
        for dto in result:
            assert dto.chantier_id == 10

    def test_should_filter_by_metiers(
        self, use_case, mock_affectation_repository, sample_affectations
    ):
        """Test: filtre par metiers."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = sample_affectations
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
            metiers=["Macon"],
        )

        # Act
        result = use_case.execute(
            filters=filters,
            current_user_id=99,
            current_user_role="admin",
        )

        # Assert - Seulement les macons (utilisateur 1)
        assert len(result) == 2
        for dto in result:
            assert dto.utilisateur_metier == "Macon"

    def test_should_call_repository_with_date_range(
        self, use_case, mock_affectation_repository
    ):
        """Test: appel du repository avec la plage de dates."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = []
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        # Act
        use_case.execute(
            filters=filters,
            current_user_id=99,
            current_user_role="admin",
        )

        # Assert
        mock_affectation_repository.find_by_date_range.assert_called_once_with(
            date(2026, 1, 20),
            date(2026, 1, 26),
        )


# =============================================================================
# Tests Enrichissement
# =============================================================================

class TestGetPlanningEnrichment:
    """Tests pour l'enrichissement des donnees."""

    def test_should_enrich_with_user_info(
        self, use_case, mock_affectation_repository, sample_affectations
    ):
        """Test: enrichissement avec les infos utilisateur."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = sample_affectations[:1]
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        # Act
        result = use_case.execute(
            filters=filters,
            current_user_id=99,
            current_user_role="admin",
        )

        # Assert
        assert result[0].utilisateur_nom == "Jean Dupont"
        assert result[0].utilisateur_couleur == "#FF0000"
        assert result[0].utilisateur_metier == "Macon"

    def test_should_enrich_with_chantier_info(
        self, use_case, mock_affectation_repository, sample_affectations
    ):
        """Test: enrichissement avec les infos chantier."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = sample_affectations[:1]
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        # Act
        result = use_case.execute(
            filters=filters,
            current_user_id=99,
            current_user_role="admin",
        )

        # Assert
        assert result[0].chantier_nom == "Villa Lyon"
        assert result[0].chantier_couleur == "#E74C3C"

    def test_should_work_without_enrichment_functions(
        self, use_case_minimal, mock_affectation_repository, sample_affectations
    ):
        """Test: fonctionne sans fonctions d'enrichissement."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = sample_affectations[:1]
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        # Act
        result = use_case_minimal.execute(
            filters=filters,
            current_user_id=99,
            current_user_role="admin",
        )

        # Assert - Retourne le DTO mais sans enrichissement
        assert len(result) == 1
        assert result[0].utilisateur_id == 1


# =============================================================================
# Tests DTO Filters
# =============================================================================

class TestPlanningFiltersDTO:
    """Tests pour le DTO de filtres."""

    def test_should_create_filters_for_week(self):
        """Test: creation de filtres pour une semaine."""
        # Jeudi 22 janvier 2026 (weekday=3)
        # Lundi de cette semaine = 22 - 3 = 19 janvier
        filters = PlanningFiltersDTO.for_week(date(2026, 1, 22))  # Jeudi

        # Doit retourner Lundi 19 -> Dimanche 25
        assert filters.date_debut == date(2026, 1, 19)
        assert filters.date_fin == date(2026, 1, 25)

    def test_should_create_filters_for_month(self):
        """Test: creation de filtres pour un mois."""
        filters = PlanningFiltersDTO.for_month(2026, 1)

        assert filters.date_debut == date(2026, 1, 1)
        assert filters.date_fin == date(2026, 1, 31)

    def test_should_create_filters_for_day(self):
        """Test: creation de filtres pour une journee."""
        filters = PlanningFiltersDTO.for_day(date(2026, 1, 22))

        assert filters.date_debut == date(2026, 1, 22)
        assert filters.date_fin == date(2026, 1, 22)

    def test_should_calculate_nb_jours(self):
        """Test: calcul du nombre de jours."""
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        assert filters.nb_jours == 7

    def test_should_detect_has_utilisateur_filter(self):
        """Test: detection du filtre utilisateur."""
        filters_with = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
            utilisateur_ids=[1, 2],
        )
        filters_without = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        assert filters_with.has_utilisateur_filter is True
        assert filters_without.has_utilisateur_filter is False

    def test_should_detect_has_chantier_filter(self):
        """Test: detection du filtre chantier."""
        filters_with = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
            chantier_ids=[10],
        )
        filters_without = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        assert filters_with.has_chantier_filter is True
        assert filters_without.has_chantier_filter is False

    def test_should_raise_when_date_fin_before_date_debut(self):
        """Test: echec si date_fin < date_debut."""
        with pytest.raises(ValueError) as exc_info:
            PlanningFiltersDTO(
                date_debut=date(2026, 1, 26),
                date_fin=date(2026, 1, 20),
            )

        assert "posterieure" in str(exc_info.value)

    def test_should_raise_when_planifies_and_non_planifies(self):
        """Test: echec si planifies_only ET non_planifies_only."""
        with pytest.raises(ValueError) as exc_info:
            PlanningFiltersDTO(
                date_debut=date(2026, 1, 20),
                date_fin=date(2026, 1, 26),
                planifies_only=True,
                non_planifies_only=True,
            )

        assert "mutuellement exclusifs" in str(exc_info.value)


# =============================================================================
# Tests Edge Cases
# =============================================================================

class TestGetPlanningEdgeCases:
    """Tests pour les cas limites."""

    def test_should_return_empty_when_no_affectations(
        self, use_case, mock_affectation_repository
    ):
        """Test: retourne liste vide si pas d'affectations."""
        # Arrange
        mock_affectation_repository.find_by_date_range.return_value = []
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        # Act
        result = use_case.execute(
            filters=filters,
            current_user_id=99,
            current_user_role="admin",
        )

        # Assert
        assert len(result) == 0

    def test_should_handle_unknown_user_id_gracefully(
        self, use_case, mock_affectation_repository
    ):
        """Test: gestion gracieuse d'un utilisateur inconnu."""
        # Arrange
        affectation = Affectation(
            id=1,
            utilisateur_id=999,  # Utilisateur inconnu
            chantier_id=10,
            date=date(2026, 1, 22),
            created_by=3,
        )
        mock_affectation_repository.find_by_date_range.return_value = [affectation]
        filters = PlanningFiltersDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )

        # Act - should not raise
        result = use_case.execute(
            filters=filters,
            current_user_id=99,
            current_user_role="admin",
        )

        # Assert
        assert len(result) == 1
        assert result[0].utilisateur_nom is None  # Pas d'info trouvee
