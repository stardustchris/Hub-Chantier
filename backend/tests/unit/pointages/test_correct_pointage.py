"""Tests unitaires pour CorrectPointageUseCase."""

import pytest
from datetime import date
from unittest.mock import Mock

from modules.pointages.application.use_cases.correct_pointage import (
    CorrectPointageUseCase,
)
from modules.pointages.domain.entities import Pointage
from modules.pointages.domain.value_objects import StatutPointage, Duree
from modules.pointages.domain.repositories import PointageRepository
from modules.pointages.application.ports import NullEventBus


class TestCorrectPointageUseCase:
    """Tests pour le use case de correction de pointage rejeté."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Mocks des dépendances
        self.mock_repo = Mock(spec=PointageRepository)
        self.event_bus = NullEventBus()

        # Use case à tester
        self.use_case = CorrectPointageUseCase(
            pointage_repo=self.mock_repo,
            event_bus=self.event_bus,
        )

    def test_execute_success(self):
        """Test: Correction d'un pointage REJETÉ en BROUILLON réussie.

        Selon § 5.5 (Rejet et correction), après un rejet, le compagnon
        peut reprendre son pointage pour le corriger.
        Le pointage passe de REJETÉ → BROUILLON.
        """
        # Arrange
        pointage = Pointage(
            id=1,
            utilisateur_id=7,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),  # Mois en cours
            heures_normales=Duree(8, 0),
            statut=StatutPointage.REJETE,
            validateur_id=4,
            motif_rejet="Heures incorrectes",
        )
        self.mock_repo.find_by_id.return_value = pointage

        # Mock save pour retourner le pointage après correction
        def save_side_effect(p):
            # Simule le save qui retourne le pointage
            return p

        self.mock_repo.save.side_effect = save_side_effect

        # Act
        result = self.use_case.execute(pointage_id=1)

        # Assert
        assert result is not None
        assert result.id == 1
        assert result.statut == StatutPointage.BROUILLON.value
        assert result.signature_utilisateur is None, "Signature doit être effacée"
        assert result.signature_date is None, "Date signature doit être effacée"

        self.mock_repo.find_by_id.assert_called_once_with(1)
        self.mock_repo.save.assert_called_once()

    def test_execute_pointage_not_found(self):
        """Test: ValueError si le pointage n'existe pas."""
        # Arrange
        self.mock_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="non trouvé"):
            self.use_case.execute(pointage_id=999)

        self.mock_repo.find_by_id.assert_called_once_with(999)
        self.mock_repo.save.assert_not_called()

    def test_execute_periode_verrouillee(self):
        """Test: ValueError si la période de paie est verrouillée.

        GAP-FDH-002: Impossible de corriger un pointage après la clôture
        mensuelle (verrouillage).
        """
        # Arrange: Pointage de décembre, on est en février
        pointage = Pointage(
            id=1,
            utilisateur_id=7,
            chantier_id=10,
            date_pointage=date(2025, 12, 15),  # Ancien mois verrouillé
            heures_normales=Duree(8, 0),
            statut=StatutPointage.REJETE,
        )
        self.mock_repo.find_by_id.return_value = pointage

        # Act & Assert
        # La période décembre 2025 est verrouillée si on est en 2026
        with pytest.raises(ValueError, match="période de paie est verrouillée"):
            self.use_case.execute(pointage_id=1)

        self.mock_repo.find_by_id.assert_called_once_with(1)
        self.mock_repo.save.assert_not_called()

    def test_execute_statut_invalide(self):
        """Test: ValueError si le statut n'est pas REJETÉ.

        Seuls les pointages REJETÉS peuvent être corrigés.
        """
        # Arrange: Pointage BROUILLON (pas REJETÉ)
        pointage = Pointage(
            id=1,
            utilisateur_id=7,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            heures_normales=Duree(8, 0),
            statut=StatutPointage.BROUILLON,  # Pas REJETÉ
        )
        self.mock_repo.find_by_id.return_value = pointage

        # Act & Assert
        with pytest.raises(ValueError, match="Impossible de corriger"):
            self.use_case.execute(pointage_id=1)

        self.mock_repo.save.assert_not_called()

    def test_execute_statut_soumis_invalide(self):
        """Test: ValueError si le pointage est SOUMIS."""
        # Arrange
        pointage = Pointage(
            id=1,
            utilisateur_id=7,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            heures_normales=Duree(8, 0),
            statut=StatutPointage.SOUMIS,
        )
        self.mock_repo.find_by_id.return_value = pointage

        # Act & Assert
        with pytest.raises(ValueError, match="Impossible de corriger"):
            self.use_case.execute(pointage_id=1)

    def test_execute_statut_valide_invalide(self):
        """Test: ValueError si le pointage est VALIDÉ."""
        # Arrange
        pointage = Pointage(
            id=1,
            utilisateur_id=7,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            heures_normales=Duree(8, 0),
            statut=StatutPointage.VALIDE,
        )
        self.mock_repo.find_by_id.return_value = pointage

        # Act & Assert
        with pytest.raises(ValueError, match="Impossible de corriger"):
            self.use_case.execute(pointage_id=1)

    def test_execute_reset_signature(self):
        """Test: La signature est effacée après correction.

        Après correction, l'utilisateur doit re-signer son pointage.
        """
        # Arrange: Pointage rejeté avec signature
        pointage = Pointage(
            id=1,
            utilisateur_id=7,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            heures_normales=Duree(8, 0),
            statut=StatutPointage.REJETE,
            signature_utilisateur="signature_hash_abc123",
            motif_rejet="Erreur heures",
        )
        self.mock_repo.find_by_id.return_value = pointage
        self.mock_repo.save.side_effect = lambda p: p

        # Act
        result = self.use_case.execute(pointage_id=1)

        # Assert
        assert result.signature_utilisateur is None, "Signature doit être reset"
        assert result.signature_date is None, "Date signature doit être reset"

    def test_execute_retourne_dto(self):
        """Test: Retourne un PointageDTO avec statut BROUILLON.

        Le DTO doit contenir toutes les informations du pointage corrigé.
        """
        # Arrange
        pointage = Pointage(
            id=1,
            utilisateur_id=7,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            heures_normales=Duree(8, 0),
            heures_supplementaires=Duree(1, 30),
            statut=StatutPointage.REJETE,
            commentaire="Pointage rejeté",
            motif_rejet="Heures incorrectes",
        )
        self.mock_repo.find_by_id.return_value = pointage
        self.mock_repo.save.side_effect = lambda p: p

        # Act
        result = self.use_case.execute(pointage_id=1)

        # Assert: Vérification du DTO
        assert result.id == 1
        assert result.utilisateur_id == 7
        assert result.chantier_id == 10
        assert result.date_pointage == date(2026, 1, 20)
        assert result.heures_normales == "08:00"
        assert result.heures_supplementaires == "01:30"
        assert result.statut == StatutPointage.BROUILLON.value
        assert result.commentaire == "Pointage rejeté"
        assert result.motif_rejet == "Heures incorrectes"

    def test_execute_preserve_donnees_existantes(self):
        """Test: Les données du pointage sont préservées après correction.

        Seul le statut et la signature changent, le reste est préservé.
        """
        # Arrange
        pointage = Pointage(
            id=1,
            utilisateur_id=7,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            heures_normales=Duree(7, 30),
            heures_supplementaires=Duree(0, 30),
            statut=StatutPointage.REJETE,
            commentaire="Travail sur fondations",
            motif_rejet="Total incorrect",
            affectation_id=5,
        )
        self.mock_repo.find_by_id.return_value = pointage
        self.mock_repo.save.side_effect = lambda p: p

        # Act
        result = self.use_case.execute(pointage_id=1)

        # Assert: Données préservées
        assert result.heures_normales == "07:30"
        assert result.heures_supplementaires == "00:30"
        assert result.commentaire == "Travail sur fondations"
        assert result.affectation_id == 5
        # Motif rejet préservé pour historique
        assert result.motif_rejet == "Total incorrect"

    def test_execute_pointage_mois_en_cours_non_verrouillee(self):
        """Test: Correction réussie pour un pointage du mois en cours.

        Les pointages du mois en cours ne sont jamais verrouillés.
        """
        # Arrange: On utilise une date récente (mois en cours)
        pointage = Pointage(
            id=1,
            utilisateur_id=7,
            chantier_id=10,
            date_pointage=date.today(),  # Aujourd'hui
            heures_normales=Duree(8, 0),
            statut=StatutPointage.REJETE,
        )
        self.mock_repo.find_by_id.return_value = pointage
        self.mock_repo.save.side_effect = lambda p: p

        # Act
        result = self.use_case.execute(pointage_id=1)

        # Assert: Correction réussie
        assert result.statut == StatutPointage.BROUILLON.value
        self.mock_repo.save.assert_called_once()

    def test_execute_sans_event_bus(self):
        """Test: Fonctionne correctement sans event bus (NullEventBus)."""
        # Arrange
        pointage = Pointage(
            id=1,
            utilisateur_id=7,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            heures_normales=Duree(8, 0),
            statut=StatutPointage.REJETE,
        )
        self.mock_repo.find_by_id.return_value = pointage
        self.mock_repo.save.side_effect = lambda p: p

        # Act
        result = self.use_case.execute(pointage_id=1)

        # Assert: Pas d'erreur, pas d'événement publié
        assert result is not None

    def test_execute_total_heures_decimal(self):
        """Test: Le total des heures en décimal est correct dans le DTO."""
        # Arrange
        pointage = Pointage(
            id=1,
            utilisateur_id=7,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            heures_normales=Duree(7, 30),  # 7.5h
            heures_supplementaires=Duree(1, 30),  # 1.5h
            statut=StatutPointage.REJETE,
        )
        self.mock_repo.find_by_id.return_value = pointage
        self.mock_repo.save.side_effect = lambda p: p

        # Act
        result = self.use_case.execute(pointage_id=1)

        # Assert
        assert result.total_heures == "09:00"  # 7h30 + 1h30
        assert result.total_heures_decimal == 9.0

    def test_execute_avec_donnees_enrichies(self):
        """Test: Les données enrichies (noms) sont préservées dans le DTO."""
        # Arrange
        pointage = Pointage(
            id=1,
            utilisateur_id=7,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            heures_normales=Duree(8, 0),
            statut=StatutPointage.REJETE,
        )
        pointage.utilisateur_nom = "Jean Dupont"
        pointage.chantier_nom = "Maison Leclerc"
        pointage.chantier_couleur = "#FF5733"

        self.mock_repo.find_by_id.return_value = pointage
        self.mock_repo.save.side_effect = lambda p: p

        # Act
        result = self.use_case.execute(pointage_id=1)

        # Assert
        assert result.utilisateur_nom == "Jean Dupont"
        assert result.chantier_nom == "Maison Leclerc"
        assert result.chantier_couleur == "#FF5733"
