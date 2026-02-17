"""Tests unitaires pour BulkValidatePointagesUseCase (GAP-FDH-004)."""

import pytest
from datetime import date
from unittest.mock import Mock, MagicMock

from modules.pointages.application.use_cases.bulk_validate_pointages import (
    BulkValidatePointagesUseCase,
    BulkValidatePointagesError,
)
from modules.pointages.application.dtos.bulk_validate_dtos import (
    BulkValidatePointagesDTO,
)
from modules.pointages.domain.entities.pointage import Pointage
from modules.pointages.domain.value_objects import Duree, StatutPointage


class TestBulkValidatePointagesUseCase:
    """Tests pour le use case de validation par lot."""

    def setup_method(self):
        """Configure les mocks pour chaque test."""
        self.pointage_repo = Mock()
        self.event_bus = Mock()
        self.use_case = BulkValidatePointagesUseCase(
            pointage_repo=self.pointage_repo, event_bus=self.event_bus
        )

    def test_bulk_validate_success(self):
        """Test nominal: validation réussie de plusieurs pointages."""
        # Arrange
        pointages = [
            Pointage(
                id=1,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 2, 10),
                heures_normales=Duree(7, 30),
                heures_supplementaires=Duree(0, 0),
                statut=StatutPointage.SOUMIS,
            ),
            Pointage(
                id=2,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 2, 11),
                heures_normales=Duree(8, 0),
                heures_supplementaires=Duree(0, 0),
                statut=StatutPointage.SOUMIS,
            ),
        ]

        self.pointage_repo.find_by_id.side_effect = pointages
        self.pointage_repo.save.side_effect = pointages

        dto = BulkValidatePointagesDTO(pointage_ids=[1, 2], validateur_id=4)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.total_count == 2
        assert result.success_count == 2
        assert result.failure_count == 0
        assert result.validated == [1, 2]
        assert result.failed == []
        assert self.pointage_repo.save.call_count == 2
        assert self.event_bus.publish.call_count == 3  # 2 individuels + 1 bulk

    def test_bulk_validate_empty_list(self):
        """Test: liste vide doit lever une erreur."""
        # Arrange
        dto = BulkValidatePointagesDTO(pointage_ids=[], validateur_id=4)

        # Act & Assert
        with pytest.raises(BulkValidatePointagesError) as exc_info:
            self.use_case.execute(dto)

        assert "vide" in str(exc_info.value).lower()

    def test_bulk_validate_partial_failure(self):
        """Test: validation partielle (certains pointages échouent)."""
        # Arrange
        pointage_valid = Pointage(
            id=1,
            utilisateur_id=7,
            chantier_id=1,
            date_pointage=date(2026, 2, 10),
            heures_normales=Duree(7, 30),
            heures_supplementaires=Duree(0, 0),
            statut=StatutPointage.SOUMIS,
        )

        # Le pointage 2 n'existe pas
        self.pointage_repo.find_by_id.side_effect = [pointage_valid, None]
        self.pointage_repo.save.return_value = pointage_valid

        dto = BulkValidatePointagesDTO(pointage_ids=[1, 2], validateur_id=4)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.total_count == 2
        assert result.success_count == 1
        assert result.failure_count == 1
        assert result.validated == [1]
        assert len(result.failed) == 1
        assert result.failed[0].pointage_id == 2
        assert "non trouvé" in result.failed[0].error

    def test_bulk_validate_periode_locked(self):
        """Test: verrouillage mensuel empêche la validation."""
        # Arrange
        # Pointage de décembre 2025 (mois passé, donc verrouillé)
        # Janvier 2026 étant le mois en cours, décembre 2025 est déjà verrouillé
        pointage = Pointage(
            id=1,
            utilisateur_id=7,
            chantier_id=1,
            date_pointage=date(2025, 12, 5),  # Décembre 2025
            heures_normales=Duree(7, 30),
            heures_supplementaires=Duree(0, 0),
            statut=StatutPointage.SOUMIS,
        )

        self.pointage_repo.find_by_id.return_value = pointage

        dto = BulkValidatePointagesDTO(pointage_ids=[1], validateur_id=4)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        # Le résultat devrait contenir une erreur de verrouillage
        assert result.success_count == 0
        assert result.failure_count == 1
        assert "verrouillée" in result.failed[0].error.lower()

    def test_bulk_validate_invalid_status(self):
        """Test: pointage avec statut incompatible (non SOUMIS)."""
        # Arrange
        pointage = Pointage(
            id=1,
            utilisateur_id=7,
            chantier_id=1,
            date_pointage=date(2026, 2, 10),
            heures_normales=Duree(7, 30),
            heures_supplementaires=Duree(0, 0),
            statut=StatutPointage.BROUILLON,  # Pas soumis
        )

        self.pointage_repo.find_by_id.return_value = pointage

        dto = BulkValidatePointagesDTO(pointage_ids=[1], validateur_id=4)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.success_count == 0
        assert result.failure_count == 1
        # Le message d'erreur devrait mentionner le statut incompatible
