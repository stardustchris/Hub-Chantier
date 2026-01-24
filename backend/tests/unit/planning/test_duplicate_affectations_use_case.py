"""Tests unitaires pour DuplicateAffectationsUseCase."""

import pytest
from unittest.mock import Mock
from datetime import date, time, timedelta

from modules.planning.domain.entities import Affectation
from modules.planning.domain.repositories import AffectationRepository
from modules.planning.domain.value_objects import TypeAffectation
from modules.planning.application.use_cases.duplicate_affectations import (
    DuplicateAffectationsUseCase,
)
from modules.planning.application.use_cases.exceptions import (
    AffectationConflictError,
)
from modules.planning.application.dtos import DuplicateAffectationsDTO


class TestDuplicateAffectationsUseCase:
    """Tests pour le use case de duplication d'affectations."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_affectation_repo = Mock(spec=AffectationRepository)
        self.mock_event_bus = Mock()
        self.use_case = DuplicateAffectationsUseCase(
            affectation_repo=self.mock_affectation_repo,
            event_bus=self.mock_event_bus,
        )

        # Dates source (semaine 1)
        self.source_debut = date(2026, 1, 20)  # Lundi semaine 1
        self.source_fin = date(2026, 1, 24)  # Vendredi semaine 1

        # Affectation de test
        self.affectation_source = Affectation(
            id=1,
            utilisateur_id=10,
            chantier_id=100,
            date=self.source_debut,
            heure_debut=time(8, 0),
            heure_fin=time(17, 0),
            type_affectation=TypeAffectation.UNIQUE,
            created_by=1,
        )

    def test_duplicate_success(self):
        """Test: duplication réussie d'affectations."""
        self.mock_affectation_repo.find_by_utilisateur.return_value = [
            self.affectation_source
        ]
        self.mock_affectation_repo.exists_for_utilisateur_and_date.return_value = False

        # Mock save pour retourner l'affectation avec un nouvel ID
        saved_affectation = Affectation(
            id=2,
            utilisateur_id=10,
            chantier_id=100,
            date=self.source_debut + timedelta(days=7),
            heure_debut=time(8, 0),
            heure_fin=time(17, 0),
            created_by=1,
        )
        self.mock_affectation_repo.save.return_value = saved_affectation

        dto = DuplicateAffectationsDTO(
            utilisateur_id=10,
            source_date_debut=self.source_debut,
            source_date_fin=self.source_fin,
            target_date_debut=self.source_debut + timedelta(days=7),
        )

        result = self.use_case.execute(dto, created_by=1)

        assert len(result) == 1
        self.mock_affectation_repo.save.assert_called_once()

    def test_duplicate_no_affectations(self):
        """Test: échec si aucune affectation source."""
        self.mock_affectation_repo.find_by_utilisateur.return_value = []

        dto = DuplicateAffectationsDTO(
            utilisateur_id=10,
            source_date_debut=self.source_debut,
            source_date_fin=self.source_fin,
            target_date_debut=self.source_debut + timedelta(days=7),
        )

        # Le use case doit lever une exception quand il n'y a pas d'affectations
        with pytest.raises(Exception):  # NoAffectationsToDuplicateError ou ValueError
            self.use_case.execute(dto, created_by=1)

    def test_duplicate_conflict(self):
        """Test: échec si conflit sur date cible."""
        self.mock_affectation_repo.find_by_utilisateur.return_value = [
            self.affectation_source
        ]
        self.mock_affectation_repo.exists_for_utilisateur_and_date.return_value = True

        dto = DuplicateAffectationsDTO(
            utilisateur_id=10,
            source_date_debut=self.source_debut,
            source_date_fin=self.source_fin,
            target_date_debut=self.source_debut + timedelta(days=7),
        )

        with pytest.raises(AffectationConflictError):
            self.use_case.execute(dto, created_by=1)

    def test_duplicate_multiple_affectations(self):
        """Test: duplication de plusieurs affectations."""
        affectation2 = Affectation(
            id=2,
            utilisateur_id=10,
            chantier_id=100,
            date=self.source_debut + timedelta(days=1),
            heure_debut=time(8, 0),
            heure_fin=time(17, 0),
            created_by=1,
        )

        self.mock_affectation_repo.find_by_utilisateur.return_value = [
            self.affectation_source,
            affectation2,
        ]
        self.mock_affectation_repo.exists_for_utilisateur_and_date.return_value = False

        saved_affectation = Mock()
        saved_affectation.id = 10
        saved_affectation.chantier_id = 100
        saved_affectation.date = self.source_debut + timedelta(days=7)
        self.mock_affectation_repo.save.return_value = saved_affectation

        dto = DuplicateAffectationsDTO(
            utilisateur_id=10,
            source_date_debut=self.source_debut,
            source_date_fin=self.source_fin,
            target_date_debut=self.source_debut + timedelta(days=7),
        )

        result = self.use_case.execute(dto, created_by=1)

        assert len(result) == 2
        assert self.mock_affectation_repo.save.call_count == 2

    def test_duplicate_publishes_event(self):
        """Test: publication d'un event bulk après duplication."""
        self.mock_affectation_repo.find_by_utilisateur.return_value = [
            self.affectation_source
        ]
        self.mock_affectation_repo.exists_for_utilisateur_and_date.return_value = False

        saved = Mock()
        saved.id = 10
        saved.chantier_id = 100
        saved.date = self.source_debut + timedelta(days=7)
        self.mock_affectation_repo.save.return_value = saved

        dto = DuplicateAffectationsDTO(
            utilisateur_id=10,
            source_date_debut=self.source_debut,
            source_date_fin=self.source_fin,
            target_date_debut=self.source_debut + timedelta(days=7),
        )

        self.use_case.execute(dto, created_by=1)

        self.mock_event_bus.publish.assert_called_once()
