"""Tests unitaires pour le use case CreateAffectation.

Ce fichier teste :
- Creation simple (affectation unique)
- Creation recurrente (plusieurs affectations)
- Publication des events
- Gestion des conflits
"""

import pytest
from unittest.mock import Mock
from datetime import date

from modules.planning.domain.entities.affectation import Affectation
from modules.planning.domain.repositories.affectation_repository import AffectationRepository
from modules.planning.domain.value_objects.type_affectation import TypeAffectation
from modules.planning.domain.events.affectation_events import (
    AffectationCreatedEvent,
    AffectationBulkCreatedEvent,
)
from modules.planning.application.use_cases.create_affectation import (
    CreateAffectationUseCase,
    AffectationConflictError,
    InvalidDateRangeError,
)
from modules.planning.application.dtos.create_affectation_dto import CreateAffectationDTO
from modules.planning.application.ports.event_bus import EventBus


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_affectation_repository():
    """Fixture: mock du repository d'affectations."""
    mock = Mock(spec=AffectationRepository)
    mock.exists_for_utilisateur_and_date.return_value = False
    return mock


@pytest.fixture
def mock_event_bus():
    """Fixture: mock du bus d'evenements."""
    return Mock(spec=EventBus)


@pytest.fixture
def use_case(mock_affectation_repository, mock_event_bus):
    """Fixture: instance du use case avec mocks."""
    return CreateAffectationUseCase(
        affectation_repo=mock_affectation_repository,
        event_bus=mock_event_bus,
    )


@pytest.fixture
def use_case_without_event_bus(mock_affectation_repository):
    """Fixture: use case sans event bus."""
    return CreateAffectationUseCase(
        affectation_repo=mock_affectation_repository,
        event_bus=None,
    )


# =============================================================================
# Helper Functions
# =============================================================================

def create_saved_affectation(affectation: Affectation, id_counter=[0]) -> Affectation:
    """Simule la sauvegarde en ajoutant un ID."""
    id_counter[0] += 1
    affectation.id = id_counter[0]
    return affectation


# =============================================================================
# Tests Creation Unique
# =============================================================================

class TestCreateAffectationUnique:
    """Tests pour la creation d'une affectation unique."""

    def test_should_create_unique_affectation(
        self, use_case, mock_affectation_repository
    ):
        """Test: creation reussie d'une affectation unique."""
        # Arrange
        mock_affectation_repository.save.side_effect = lambda a: (
            setattr(a, "id", 1) or a
        )

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
        )

        # Act
        result = use_case.execute(dto, created_by=3)

        # Assert
        assert len(result) == 1
        assert result[0].utilisateur_id == 1
        assert result[0].chantier_id == 2
        assert result[0].date == date(2026, 1, 22)
        assert result[0].type_affectation == TypeAffectation.UNIQUE

    def test_should_create_unique_with_horaires(
        self, use_case, mock_affectation_repository
    ):
        """Test: creation avec horaires."""
        # Arrange
        mock_affectation_repository.save.side_effect = lambda a: (
            setattr(a, "id", 1) or a
        )

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            heure_debut="08:00",
            heure_fin="17:00",
        )

        # Act
        result = use_case.execute(dto, created_by=3)

        # Assert
        assert result[0].heure_debut is not None
        assert result[0].heure_fin is not None
        assert str(result[0].heure_debut) == "08:00"
        assert str(result[0].heure_fin) == "17:00"

    def test_should_create_unique_with_note(
        self, use_case, mock_affectation_repository
    ):
        """Test: creation avec note."""
        # Arrange
        mock_affectation_repository.save.side_effect = lambda a: (
            setattr(a, "id", 1) or a
        )

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            note="Note importante",
        )

        # Act
        result = use_case.execute(dto, created_by=3)

        # Assert
        assert result[0].note == "Note importante"

    def test_should_save_affectation_via_repository(
        self, use_case, mock_affectation_repository
    ):
        """Test: verification que save() est appele."""
        # Arrange
        mock_affectation_repository.save.side_effect = lambda a: (
            setattr(a, "id", 1) or a
        )

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
        )

        # Act
        use_case.execute(dto, created_by=3)

        # Assert
        mock_affectation_repository.save.assert_called_once()
        saved_affectation = mock_affectation_repository.save.call_args[0][0]
        assert isinstance(saved_affectation, Affectation)

    def test_should_check_conflict_before_create(
        self, use_case, mock_affectation_repository
    ):
        """Test: verification de conflit avant creation."""
        # Arrange
        mock_affectation_repository.save.side_effect = lambda a: (
            setattr(a, "id", 1) or a
        )

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
        )

        # Act
        use_case.execute(dto, created_by=3)

        # Assert
        mock_affectation_repository.exists_for_utilisateur_and_date.assert_called_with(
            1, date(2026, 1, 22)
        )


# =============================================================================
# Tests Conflits
# =============================================================================

class TestCreateAffectationConflict:
    """Tests pour la gestion des conflits."""

    def test_should_raise_when_affectation_already_exists(
        self, use_case, mock_affectation_repository
    ):
        """Test: echec si affectation existe deja."""
        # Arrange
        mock_affectation_repository.exists_for_utilisateur_and_date.return_value = True

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
        )

        # Act & Assert
        with pytest.raises(AffectationConflictError) as exc_info:
            use_case.execute(dto, created_by=3)

        assert exc_info.value.utilisateur_id == 1
        assert exc_info.value.date == date(2026, 1, 22)

    def test_should_not_save_when_conflict(
        self, use_case, mock_affectation_repository
    ):
        """Test: pas de sauvegarde en cas de conflit."""
        # Arrange
        mock_affectation_repository.exists_for_utilisateur_and_date.return_value = True

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
        )

        # Act
        with pytest.raises(AffectationConflictError):
            use_case.execute(dto, created_by=3)

        # Assert
        mock_affectation_repository.save.assert_not_called()


# =============================================================================
# Tests Publication Events
# =============================================================================

class TestCreateAffectationEvents:
    """Tests pour la publication des events."""

    def test_should_publish_created_event(
        self, use_case, mock_affectation_repository, mock_event_bus
    ):
        """Test: publication de l'event apres creation."""
        # Arrange
        mock_affectation_repository.save.side_effect = lambda a: (
            setattr(a, "id", 1) or a
        )

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
        )

        # Act
        use_case.execute(dto, created_by=3)

        # Assert
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert isinstance(event, AffectationCreatedEvent)
        assert event.affectation_id == 1
        assert event.utilisateur_id == 1
        assert event.chantier_id == 2
        assert event.created_by == 3

    def test_should_not_publish_when_no_event_bus(
        self, use_case_without_event_bus, mock_affectation_repository
    ):
        """Test: pas de publication si event bus absent."""
        # Arrange
        mock_affectation_repository.save.side_effect = lambda a: (
            setattr(a, "id", 1) or a
        )

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
        )

        # Act - should not raise
        result = use_case_without_event_bus.execute(dto, created_by=3)

        # Assert
        assert len(result) == 1

    def test_should_not_publish_when_conflict(
        self, use_case, mock_affectation_repository, mock_event_bus
    ):
        """Test: pas de publication en cas de conflit."""
        # Arrange
        mock_affectation_repository.exists_for_utilisateur_and_date.return_value = True

        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
        )

        # Act
        with pytest.raises(AffectationConflictError):
            use_case.execute(dto, created_by=3)

        # Assert
        mock_event_bus.publish.assert_not_called()


# =============================================================================
# Tests Creation Recurrente
# =============================================================================

class TestCreateAffectationRecurrente:
    """Tests pour la creation d'affectations recurrentes."""

    def test_should_create_multiple_affectations_for_recurrence(
        self, use_case, mock_affectation_repository
    ):
        """Test: creation de plusieurs affectations pour recurrence."""
        # Arrange
        id_counter = [0]

        def save_with_id(a):
            id_counter[0] += 1
            a.id = id_counter[0]
            return a

        mock_affectation_repository.save.side_effect = save_with_id

        # Lundi 19/01 -> Vendredi 23/01
        # 19=Lun(0), 20=Mar(1), 21=Mer(2), 22=Jeu(3), 23=Ven(4)
        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 19),  # Lundi
            type_affectation="recurrente",
            jours_recurrence=[0, 1, 2, 3, 4],  # Lundi a Vendredi
            date_fin_recurrence=date(2026, 1, 23),
        )

        # Act
        result = use_case.execute(dto, created_by=3)

        # Assert - 5 jours ouvrables
        assert len(result) == 5
        assert mock_affectation_repository.save.call_count == 5

    def test_should_create_only_selected_days(
        self, use_case, mock_affectation_repository
    ):
        """Test: creation uniquement les jours selectionnes."""
        # Arrange
        id_counter = [0]

        def save_with_id(a):
            id_counter[0] += 1
            a.id = id_counter[0]
            return a

        mock_affectation_repository.save.side_effect = save_with_id

        # Lundi 19/01 -> Dimanche 25/01
        # Jours: seulement Lun et Mer
        # 19=Lun(0), 21=Mer(2) = 2 jours
        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 19),  # Lundi
            type_affectation="recurrente",
            jours_recurrence=[0, 2],  # Lundi et Mercredi
            date_fin_recurrence=date(2026, 1, 25),  # Dimanche
        )

        # Act
        result = use_case.execute(dto, created_by=3)

        # Assert - Lundi 19, Mercredi 21 = 2 jours
        assert len(result) == 2

    def test_should_publish_bulk_event_for_recurrence(
        self, use_case, mock_affectation_repository, mock_event_bus
    ):
        """Test: publication d'un event bulk pour recurrence."""
        # Arrange
        id_counter = [0]

        def save_with_id(a):
            id_counter[0] += 1
            a.id = id_counter[0]
            return a

        mock_affectation_repository.save.side_effect = save_with_id

        # 19=Lun(0) et 26=Lun(0) = 2 lundis
        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 19),
            type_affectation="recurrente",
            jours_recurrence=[0],  # Lundi seulement
            date_fin_recurrence=date(2026, 1, 26),  # 2 lundis
        )

        # Act
        use_case.execute(dto, created_by=3)

        # Assert
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert isinstance(event, AffectationBulkCreatedEvent)
        assert event.count == 2

    def test_should_check_conflict_for_each_date(
        self, use_case, mock_affectation_repository
    ):
        """Test: verification de conflit pour chaque date."""
        # Arrange
        id_counter = [0]

        def save_with_id(a):
            id_counter[0] += 1
            a.id = id_counter[0]
            return a

        mock_affectation_repository.save.side_effect = save_with_id

        # 19=Lun(0), 20=Mar(1) = 2 jours
        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 19),  # Lundi
            type_affectation="recurrente",
            jours_recurrence=[0, 1],  # Lundi, Mardi
            date_fin_recurrence=date(2026, 1, 20),  # Mardi
        )

        # Act
        use_case.execute(dto, created_by=3)

        # Assert - 2 verifications de conflit
        assert mock_affectation_repository.exists_for_utilisateur_and_date.call_count == 2

    def test_should_raise_on_conflict_during_recurrence(
        self, use_case, mock_affectation_repository
    ):
        """Test: echec si conflit sur une des dates de recurrence."""
        # Arrange
        # Conflict sur la 2eme date
        mock_affectation_repository.exists_for_utilisateur_and_date.side_effect = [
            False,  # Premiere date OK
            True,   # Deuxieme date en conflit
        ]

        # 19=Lun(0), 20=Mar(1) = 2 jours
        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 19),  # Lundi
            type_affectation="recurrente",
            jours_recurrence=[0, 1],  # Lundi, Mardi
            date_fin_recurrence=date(2026, 1, 20),
        )

        # Act & Assert
        with pytest.raises(AffectationConflictError):
            use_case.execute(dto, created_by=3)

        # Pas de sauvegarde effectuee
        mock_affectation_repository.save.assert_not_called()

    def test_should_raise_when_no_dates_match_recurrence(
        self, use_case, mock_affectation_repository
    ):
        """Test: echec si aucune date ne correspond a la recurrence."""
        # Arrange - 19=Lun, 20=Mar, 21=Mer, 22=Jeu, 23=Ven (pas de weekend)
        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 19),  # Lundi
            type_affectation="recurrente",
            jours_recurrence=[5, 6],  # Samedi, Dimanche
            date_fin_recurrence=date(2026, 1, 23),  # Vendredi - pas de weekend
        )

        # Act & Assert
        with pytest.raises(InvalidDateRangeError) as exc_info:
            use_case.execute(dto, created_by=3)

        assert "Aucune date ne correspond" in str(exc_info.value)

    def test_should_preserve_horaires_for_recurrence(
        self, use_case, mock_affectation_repository
    ):
        """Test: les horaires sont preserves pour chaque affectation recurrente."""
        # Arrange
        id_counter = [0]

        def save_with_id(a):
            id_counter[0] += 1
            a.id = id_counter[0]
            return a

        mock_affectation_repository.save.side_effect = save_with_id

        # 19=Lun(0), 26=Lun(0) = 2 lundis
        dto = CreateAffectationDTO(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 19),
            heure_debut="08:00",
            heure_fin="17:00",
            type_affectation="recurrente",
            jours_recurrence=[0],  # Lundi
            date_fin_recurrence=date(2026, 1, 26),
        )

        # Act
        result = use_case.execute(dto, created_by=3)

        # Assert
        for affectation in result:
            assert str(affectation.heure_debut) == "08:00"
            assert str(affectation.heure_fin) == "17:00"


# =============================================================================
# Tests Validation DTO
# =============================================================================

class TestCreateAffectationDTOValidation:
    """Tests pour la validation du DTO."""

    def test_should_raise_when_invalid_heure_format(self):
        """Test: echec si format d'heure invalide dans le DTO."""
        with pytest.raises(ValueError) as exc_info:
            CreateAffectationDTO(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                heure_debut="invalid",
            )

        assert "Format" in str(exc_info.value)

    def test_should_raise_when_recurrente_without_date_fin(self):
        """Test: echec si recurrent sans date de fin."""
        with pytest.raises(ValueError) as exc_info:
            CreateAffectationDTO(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                type_affectation="recurrente",
                jours_recurrence=[0, 1, 2],
                # date_fin_recurrence manquant
            )

        assert "date de fin" in str(exc_info.value)

    def test_should_raise_when_recurrente_date_fin_before_debut(self):
        """Test: echec si date de fin recurrence avant date debut."""
        with pytest.raises(ValueError) as exc_info:
            CreateAffectationDTO(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                type_affectation="recurrente",
                jours_recurrence=[0],
                date_fin_recurrence=date(2026, 1, 20),  # Avant date
            )

        assert "posterieure" in str(exc_info.value)
