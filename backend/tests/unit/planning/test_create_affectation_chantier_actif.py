"""Tests unitaires pour GAP-CHT-003 - Validation chantier actif.

Ce fichier teste la règle métier RG-PLN-008 :
- Impossible d'affecter sur un chantier fermé
- Possible d'affecter sur chantiers OUVERT, EN_COURS, RECEPTIONNE
"""

import pytest
from unittest.mock import Mock
from datetime import date

from modules.planning.domain.entities.affectation import Affectation
from modules.planning.domain.repositories.affectation_repository import AffectationRepository
from modules.planning.application.use_cases.create_affectation import CreateAffectationUseCase
from modules.planning.application.use_cases.exceptions import ChantierInactifError
from modules.planning.application.dtos.create_affectation_dto import CreateAffectationDTO
from modules.chantiers.domain.entities.chantier import Chantier
from modules.chantiers.domain.value_objects.code_chantier import CodeChantier
from modules.chantiers.domain.value_objects.statut_chantier import StatutChantier


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_affectation_repository():
    """Fixture: mock du repository d'affectations."""
    mock = Mock(spec=AffectationRepository)
    mock.exists_for_utilisateur_and_date.return_value = False
    mock.find_by_utilisateur_and_date.return_value = []  # Pas d'affectation existante
    mock.save.side_effect = lambda a: setattr(a, "id", 1) or a
    return mock


@pytest.fixture
def mock_chantier_repository():
    """Fixture: mock du repository de chantiers."""
    return Mock()


@pytest.fixture
def use_case_with_chantier_validation(mock_affectation_repository, mock_chantier_repository):
    """Fixture: use case avec validation de chantier."""
    return CreateAffectationUseCase(
        affectation_repo=mock_affectation_repository,
        event_bus=None,
        chantier_repo=mock_chantier_repository,
        user_repo=None,
    )


def create_chantier(chantier_id: int, statut: StatutChantier) -> Chantier:
    """Helper: crée un chantier de test avec un statut donné."""
    return Chantier(
        id=chantier_id,
        code=CodeChantier(f"A{chantier_id:03d}"),  # Format valide: lettre + 3 chiffres
        nom=f"Chantier {chantier_id}",
        adresse="123 Rue Test",
        statut=statut,
    )


# =============================================================================
# Tests GAP-CHT-003: Validation chantier actif
# =============================================================================

class TestCreateAffectationChantierFerme:
    """Tests: Impossible d'affecter sur un chantier fermé (RG-PLN-008)."""

    def test_should_raise_when_chantier_ferme(
        self,
        use_case_with_chantier_validation,
        mock_chantier_repository,
    ):
        """Test: échec si le chantier est FERME."""
        # Arrange
        chantier_ferme = create_chantier(10, StatutChantier.ferme())
        mock_chantier_repository.find_by_id.return_value = chantier_ferme

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=10,
            date=date(2026, 1, 22),
        )

        # Act & Assert
        with pytest.raises(ChantierInactifError) as exc_info:
            use_case_with_chantier_validation.execute(dto, created_by=3)

        # Vérifier le message d'erreur
        assert exc_info.value.chantier_id == 10
        assert exc_info.value.statut == "ferme"
        assert "inactif" in exc_info.value.message
        assert "OUVERT, EN_COURS ou RECEPTIONNE" in exc_info.value.message

    def test_should_not_save_when_chantier_ferme(
        self,
        use_case_with_chantier_validation,
        mock_chantier_repository,
        mock_affectation_repository,
    ):
        """Test: pas de sauvegarde si le chantier est fermé."""
        # Arrange
        chantier_ferme = create_chantier(10, StatutChantier.ferme())
        mock_chantier_repository.find_by_id.return_value = chantier_ferme

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=10,
            date=date(2026, 1, 22),
        )

        # Act
        with pytest.raises(ChantierInactifError):
            use_case_with_chantier_validation.execute(dto, created_by=3)

        # Assert
        mock_affectation_repository.save.assert_not_called()


class TestCreateAffectationChantierActif:
    """Tests: Affectation autorisée sur chantiers actifs (RG-PLN-008)."""

    def test_should_create_affectation_on_chantier_ouvert(
        self,
        use_case_with_chantier_validation,
        mock_chantier_repository,
        mock_affectation_repository,
    ):
        """Test: création OK si chantier OUVERT."""
        # Arrange
        chantier_ouvert = create_chantier(10, StatutChantier.ouvert())
        mock_chantier_repository.find_by_id.return_value = chantier_ouvert

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=10,
            date=date(2026, 1, 22),
        )

        # Act
        result = use_case_with_chantier_validation.execute(dto, created_by=3)

        # Assert
        assert len(result) == 1
        assert result[0].chantier_id == 10
        mock_affectation_repository.save.assert_called_once()

    def test_should_create_affectation_on_chantier_en_cours(
        self,
        use_case_with_chantier_validation,
        mock_chantier_repository,
        mock_affectation_repository,
    ):
        """Test: création OK si chantier EN_COURS."""
        # Arrange
        chantier_en_cours = create_chantier(10, StatutChantier.en_cours())
        mock_chantier_repository.find_by_id.return_value = chantier_en_cours

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=10,
            date=date(2026, 1, 22),
        )

        # Act
        result = use_case_with_chantier_validation.execute(dto, created_by=3)

        # Assert
        assert len(result) == 1
        assert result[0].chantier_id == 10
        mock_affectation_repository.save.assert_called_once()

    def test_should_create_affectation_on_chantier_receptionne(
        self,
        use_case_with_chantier_validation,
        mock_chantier_repository,
        mock_affectation_repository,
    ):
        """Test: création OK si chantier RECEPTIONNE."""
        # Arrange
        chantier_receptionne = create_chantier(10, StatutChantier.receptionne())
        mock_chantier_repository.find_by_id.return_value = chantier_receptionne

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=10,
            date=date(2026, 1, 22),
        )

        # Act
        result = use_case_with_chantier_validation.execute(dto, created_by=3)

        # Assert
        assert len(result) == 1
        assert result[0].chantier_id == 10
        mock_affectation_repository.save.assert_called_once()


class TestCreateAffectationChantierValidation:
    """Tests: Cas limites de validation."""

    def test_should_skip_validation_when_no_chantier_repo(
        self,
        mock_affectation_repository,
    ):
        """Test: pas de validation si chantier_repo absent."""
        # Arrange
        use_case_no_validation = CreateAffectationUseCase(
            affectation_repo=mock_affectation_repository,
            event_bus=None,
            chantier_repo=None,  # Pas de repo = pas de validation
        )

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=10,
            date=date(2026, 1, 22),
        )

        # Act - should not raise
        result = use_case_no_validation.execute(dto, created_by=3)

        # Assert
        assert len(result) == 1

    def test_should_skip_validation_when_chantier_not_found(
        self,
        use_case_with_chantier_validation,
        mock_chantier_repository,
        mock_affectation_repository,
    ):
        """Test: pas d'erreur si chantier introuvable (validation skip)."""
        # Arrange
        mock_chantier_repository.find_by_id.return_value = None

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=999,  # Chantier inexistant
            date=date(2026, 1, 22),
        )

        # Act - should not raise
        result = use_case_with_chantier_validation.execute(dto, created_by=3)

        # Assert - L'affectation est créée malgré chantier introuvable
        assert len(result) == 1
        assert result[0].chantier_id == 999

    def test_should_validate_chantier_before_checking_conflict(
        self,
        use_case_with_chantier_validation,
        mock_chantier_repository,
        mock_affectation_repository,
    ):
        """Test: validation chantier se fait AVANT vérification conflit."""
        # Arrange
        chantier_ferme = create_chantier(10, StatutChantier.ferme())
        mock_chantier_repository.find_by_id.return_value = chantier_ferme
        # Même si pas de conflit, l'erreur chantier fermé doit être levée
        mock_affectation_repository.exists_for_utilisateur_and_date.return_value = False

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=10,
            date=date(2026, 1, 22),
        )

        # Act & Assert - Erreur chantier fermé, pas erreur conflit
        with pytest.raises(ChantierInactifError):
            use_case_with_chantier_validation.execute(dto, created_by=3)

    def test_should_validate_for_recurrent_affectation(
        self,
        use_case_with_chantier_validation,
        mock_chantier_repository,
        mock_affectation_repository,
    ):
        """Test: validation chantier fonctionne aussi pour affectations récurrentes."""
        # Arrange
        chantier_ferme = create_chantier(10, StatutChantier.ferme())
        mock_chantier_repository.find_by_id.return_value = chantier_ferme

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=10,
            date=date(2026, 1, 19),  # Lundi
            type_affectation="recurrente",
            jours_recurrence=[0, 1, 2],  # Lun, Mar, Mer
            date_fin_recurrence=date(2026, 1, 21),
        )

        # Act & Assert
        with pytest.raises(ChantierInactifError):
            use_case_with_chantier_validation.execute(dto, created_by=3)

        # Pas de sauvegarde
        mock_affectation_repository.save.assert_not_called()
