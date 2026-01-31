"""Tests unitaires pour PrerequisReceptionService.

Gap: GAP-CHT-001 - Validation prérequis réception
"""

import pytest
from unittest.mock import Mock, MagicMock

from modules.chantiers.domain.services.prerequis_service import (
    PrerequisReceptionService,
    PrerequisResult,
)


class TestPrerequisReceptionService:
    """Tests pour le service de validation des prérequis de réception."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.service = PrerequisReceptionService()

    def test_verifier_prerequis_tous_valides(self):
        """Test: tous les prérequis sont valides (réception autorisée)."""
        # Arrange - Mock formulaire_repo avec 3 formulaires (minimum)
        mock_formulaire_repo = Mock()
        mock_formulaire_repo.count_by_chantier.return_value = 3

        # Mock signalement_repo sans signalements critiques ouverts
        mock_signalement_repo = Mock()
        mock_signalement_1 = MagicMock()
        mock_signalement_1.statut.value = "resolu"
        mock_signalement_1.priorite.value = "critique"
        mock_signalement_2 = MagicMock()
        mock_signalement_2.statut.value = "ouvert"
        mock_signalement_2.priorite.value = "moyenne"
        mock_signalement_repo.find_by_chantier.return_value = [
            mock_signalement_1,
            mock_signalement_2,
        ]

        # Mock pointage_repo avec tous pointages validés
        mock_pointage_repo = Mock()
        mock_pointage_1 = MagicMock()
        mock_pointage_1.statut.value = "valide"
        mock_pointage_2 = MagicMock()
        mock_pointage_2.statut.value = "valide"
        mock_pointage_repo.search.return_value = (
            [mock_pointage_1, mock_pointage_2],
            2,
        )

        # Act
        result = self.service.verifier_prerequis(
            chantier_id=1,
            formulaire_repo=mock_formulaire_repo,
            signalement_repo=mock_signalement_repo,
            pointage_repo=mock_pointage_repo,
        )

        # Assert
        assert result.est_valide is True
        assert len(result.prerequis_manquants) == 0
        assert result.details['formulaires_count'] == 3
        assert result.details['signalements_critiques'] == 0
        assert result.details['pointages_non_valides'] == 0

    def test_verifier_prerequis_formulaires_manquants(self):
        """Test: formulaires insuffisants (< 3)."""
        # Arrange
        mock_formulaire_repo = Mock()
        mock_formulaire_repo.count_by_chantier.return_value = 1  # Insuffisant

        # Act
        result = self.service.verifier_prerequis(
            chantier_id=1,
            formulaire_repo=mock_formulaire_repo,
        )

        # Assert
        assert result.est_valide is False
        assert len(result.prerequis_manquants) == 1
        assert "Formulaires manquants (1/3 minimum requis)" in result.prerequis_manquants
        assert result.details['formulaires_count'] == 1

    def test_verifier_prerequis_signalements_critiques_ouverts(self):
        """Test: signalements critiques encore ouverts."""
        # Arrange
        mock_signalement_repo = Mock()
        # 2 signalements critiques ouverts
        mock_signalement_1 = MagicMock()
        mock_signalement_1.statut.value = "ouvert"
        mock_signalement_1.priorite.value = "critique"
        mock_signalement_2 = MagicMock()
        mock_signalement_2.statut.value = "ouvert"
        mock_signalement_2.priorite.value = "critique"
        mock_signalement_3 = MagicMock()
        mock_signalement_3.statut.value = "ouvert"
        mock_signalement_3.priorite.value = "basse"
        mock_signalement_repo.find_by_chantier.return_value = [
            mock_signalement_1,
            mock_signalement_2,
            mock_signalement_3,
        ]

        # Act
        result = self.service.verifier_prerequis(
            chantier_id=1,
            signalement_repo=mock_signalement_repo,
        )

        # Assert
        assert result.est_valide is False
        assert len(result.prerequis_manquants) == 1
        assert "2 signalement(s) critique(s) ouvert(s)" in result.prerequis_manquants
        assert result.details['signalements_critiques'] == 2

    def test_verifier_prerequis_pointages_non_valides(self):
        """Test: pointages non validés."""
        # Arrange
        mock_pointage_repo = Mock()
        mock_pointage_1 = MagicMock()
        mock_pointage_1.statut.value = "valide"
        mock_pointage_2 = MagicMock()
        mock_pointage_2.statut.value = "brouillon"
        mock_pointage_3 = MagicMock()
        mock_pointage_3.statut.value = "refuse"
        mock_pointage_repo.search.return_value = (
            [mock_pointage_1, mock_pointage_2, mock_pointage_3],
            3,
        )

        # Act
        result = self.service.verifier_prerequis(
            chantier_id=1,
            pointage_repo=mock_pointage_repo,
        )

        # Assert
        assert result.est_valide is False
        assert len(result.prerequis_manquants) == 1
        assert "2 pointage(s) non validé(s)" in result.prerequis_manquants
        assert result.details['pointages_non_valides'] == 2

    def test_verifier_prerequis_multiples_manquants(self):
        """Test: plusieurs prérequis manquants simultanément."""
        # Arrange - Formulaires insuffisants
        mock_formulaire_repo = Mock()
        mock_formulaire_repo.count_by_chantier.return_value = 0

        # Signalements critiques ouverts
        mock_signalement_repo = Mock()
        mock_signalement = MagicMock()
        mock_signalement.statut.value = "ouvert"
        mock_signalement.priorite.value = "critique"
        mock_signalement_repo.find_by_chantier.return_value = [mock_signalement]

        # Pointages non validés
        mock_pointage_repo = Mock()
        mock_pointage = MagicMock()
        mock_pointage.statut.value = "brouillon"
        mock_pointage_repo.search.return_value = ([mock_pointage], 1)

        # Act
        result = self.service.verifier_prerequis(
            chantier_id=1,
            formulaire_repo=mock_formulaire_repo,
            signalement_repo=mock_signalement_repo,
            pointage_repo=mock_pointage_repo,
        )

        # Assert
        assert result.est_valide is False
        assert len(result.prerequis_manquants) == 3
        assert any("Formulaires manquants" in p for p in result.prerequis_manquants)
        assert any("signalement(s) critique(s)" in p for p in result.prerequis_manquants)
        assert any("pointage(s) non validé(s)" in p for p in result.prerequis_manquants)

    def test_verifier_prerequis_repo_none_graceful(self):
        """Test: repos None sont gérés sans erreur (validation partielle)."""
        # Act - Aucun repo fourni
        result = self.service.verifier_prerequis(
            chantier_id=1,
            formulaire_repo=None,
            signalement_repo=None,
            pointage_repo=None,
        )

        # Assert - Validation réussie si aucun repo fourni (pas de vérification)
        assert result.est_valide is True
        assert len(result.prerequis_manquants) == 0
        assert result.details == {}

    def test_verifier_prerequis_signalement_repo_attribute_error(self):
        """Test: AttributeError dans signalement_repo géré gracieusement."""
        # Arrange - Mock repo qui lève AttributeError
        mock_signalement_repo = Mock()
        mock_signalement_repo.find_by_chantier.side_effect = AttributeError(
            "Module not available"
        )

        # Act
        result = self.service.verifier_prerequis(
            chantier_id=1,
            signalement_repo=mock_signalement_repo,
        )

        # Assert - Validation réussie mais marque signalements comme non vérifiés
        assert result.est_valide is True
        assert result.details['signalements_critiques'] == 'non_verifie'

    def test_verifier_prerequis_pointage_repo_attribute_error(self):
        """Test: AttributeError dans pointage_repo géré gracieusement."""
        # Arrange - Mock repo qui lève AttributeError
        mock_pointage_repo = Mock()
        mock_pointage_repo.search.side_effect = AttributeError(
            "Module not available"
        )

        # Act
        result = self.service.verifier_prerequis(
            chantier_id=1,
            pointage_repo=mock_pointage_repo,
        )

        # Assert - Validation réussie mais marque pointages comme non vérifiés
        assert result.est_valide is True
        assert result.details['pointages_non_valides'] == 'non_verifie'

    def test_verifier_prerequis_formulaires_exactement_minimum(self):
        """Test: formulaires = 3 (exactement le minimum requis)."""
        # Arrange
        mock_formulaire_repo = Mock()
        mock_formulaire_repo.count_by_chantier.return_value = 3

        # Act
        result = self.service.verifier_prerequis(
            chantier_id=1,
            formulaire_repo=mock_formulaire_repo,
        )

        # Assert
        assert result.est_valide is True
        assert len(result.prerequis_manquants) == 0
        assert result.details['formulaires_count'] == 3

    def test_verifier_prerequis_signalements_critiques_resolus_ok(self):
        """Test: signalements critiques résolus n'empêchent pas réception."""
        # Arrange
        mock_signalement_repo = Mock()
        mock_signalement = MagicMock()
        mock_signalement.statut.value = "resolu"
        mock_signalement.priorite.value = "critique"
        mock_signalement_repo.find_by_chantier.return_value = [mock_signalement]

        # Act
        result = self.service.verifier_prerequis(
            chantier_id=1,
            signalement_repo=mock_signalement_repo,
        )

        # Assert
        assert result.est_valide is True
        assert result.details['signalements_critiques'] == 0

    def test_verifier_prerequis_result_structure(self):
        """Test: structure de PrerequisResult est correcte."""
        # Arrange
        mock_formulaire_repo = Mock()
        mock_formulaire_repo.count_by_chantier.return_value = 5

        # Act
        result = self.service.verifier_prerequis(
            chantier_id=1,
            formulaire_repo=mock_formulaire_repo,
        )

        # Assert - Vérifier types
        assert isinstance(result, PrerequisResult)
        assert isinstance(result.est_valide, bool)
        assert isinstance(result.prerequis_manquants, list)
        assert isinstance(result.details, dict)
