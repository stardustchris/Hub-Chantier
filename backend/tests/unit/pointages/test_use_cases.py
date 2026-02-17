"""Tests unitaires pour les Use Cases du module pointages."""

import pytest
from datetime import date
from unittest.mock import Mock

from modules.pointages.application.use_cases import (
    CreatePointageUseCase,
    UpdatePointageUseCase,
    SignPointageUseCase,
    ValidatePointageUseCase,
    RejectPointageUseCase,
    GetFeuilleHeuresUseCase,
)
from modules.pointages.application.dtos import (
    CreatePointageDTO,
    UpdatePointageDTO,
    SignPointageDTO,
    ValidatePointageDTO,
    RejectPointageDTO,
)
from modules.pointages.domain.entities import Pointage
from modules.pointages.domain.value_objects import StatutPointage, Duree
from modules.pointages.application.ports import NullEventBus


class TestCreatePointageUseCase:
    """Tests pour CreatePointageUseCase."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.pointage_repo = Mock()
        self.feuille_repo = Mock()
        self.event_bus = NullEventBus()
        self.use_case = CreatePointageUseCase(
            self.pointage_repo, self.feuille_repo, self.event_bus
        )

    def test_create_success(self):
        """Test création réussie."""
        dto = CreatePointageDTO(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 2, 15),
            heures_normales="08:00",
            heures_supplementaires="01:30",
        )

        # Mock: pas de pointage existant
        self.pointage_repo.find_by_utilisateur_chantier_date.return_value = None

        # Mock: save retourne l'entité avec ID
        def save_pointage(p):
            p.id = 1
            return p

        self.pointage_repo.save.side_effect = save_pointage
        self.feuille_repo.get_or_create.return_value = (Mock(), True)

        result = self.use_case.execute(dto, created_by=1)

        assert result.id == 1
        assert result.utilisateur_id == 1
        assert result.chantier_id == 10
        assert result.heures_normales == "08:00"
        assert result.heures_supplementaires == "01:30"
        assert result.total_heures == "09:30"
        assert result.statut == "brouillon"

        self.pointage_repo.save.assert_called_once()
        self.feuille_repo.get_or_create.assert_called_once()

    def test_create_existing_raises(self):
        """Test création avec pointage existant."""
        dto = CreatePointageDTO(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 2, 15),
            heures_normales="08:00",
        )

        # Mock: pointage existant
        existing = Mock()
        self.pointage_repo.find_by_utilisateur_chantier_date.return_value = existing

        with pytest.raises(ValueError, match="existe déjà"):
            self.use_case.execute(dto, created_by=1)

    def test_create_invalid_heures_format_raises(self):
        """Test création avec format heures invalide."""
        dto = CreatePointageDTO(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 2, 15),
            heures_normales="invalid",
        )

        self.pointage_repo.find_by_utilisateur_chantier_date.return_value = None

        with pytest.raises(ValueError):
            self.use_case.execute(dto, created_by=1)


class TestUpdatePointageUseCase:
    """Tests pour UpdatePointageUseCase."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.pointage_repo = Mock()
        self.event_bus = NullEventBus()
        self.use_case = UpdatePointageUseCase(self.pointage_repo, self.event_bus)

    def test_update_success(self):
        """Test mise à jour réussie."""
        existing = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 2, 15),
            heures_normales=Duree(8, 0),
        )
        self.pointage_repo.find_by_id.return_value = existing
        self.pointage_repo.save.return_value = existing

        dto = UpdatePointageDTO(
            pointage_id=1,
            heures_normales="07:30",
        )

        result = self.use_case.execute(dto, updated_by=1)

        assert result.heures_normales == "07:30"
        self.pointage_repo.save.assert_called_once()

    def test_update_not_found_raises(self):
        """Test mise à jour pointage inexistant."""
        self.pointage_repo.find_by_id.return_value = None

        dto = UpdatePointageDTO(pointage_id=999, heures_normales="07:00")

        with pytest.raises(ValueError, match="non trouvé"):
            self.use_case.execute(dto, updated_by=1)

    def test_update_not_editable_raises(self):
        """Test mise à jour pointage non modifiable."""
        existing = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 2, 15),
            statut=StatutPointage.VALIDE,
        )
        self.pointage_repo.find_by_id.return_value = existing

        dto = UpdatePointageDTO(pointage_id=1, heures_normales="07:00")

        with pytest.raises(ValueError, match="ne peut pas être modifié"):
            self.use_case.execute(dto, updated_by=1)

    def test_update_periode_verrouillee(self):
        """Test: ValueError si période de paie verrouillée (GAP-FDH-002).

        Impossible de modifier un pointage après la clôture mensuelle.
        """
        # Arrange: Pointage de décembre 2025, on est en 2026
        existing = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2025, 12, 15),  # Mois ancien verrouillé
            heures_normales=Duree(8, 0),
        )
        self.pointage_repo.find_by_id.return_value = existing

        dto = UpdatePointageDTO(pointage_id=1, heures_normales="07:00")

        # Act & Assert
        with pytest.raises(ValueError, match="période de paie est verrouillée"):
            self.use_case.execute(dto, updated_by=1)


class TestSignPointageUseCase:
    """Tests pour SignPointageUseCase (FDH-12)."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.pointage_repo = Mock()
        self.event_bus = NullEventBus()
        self.use_case = SignPointageUseCase(self.pointage_repo, self.event_bus)

    def test_sign_success(self):
        """Test signature réussie."""
        existing = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 2, 15),
        )
        self.pointage_repo.find_by_id.return_value = existing
        self.pointage_repo.save.return_value = existing

        dto = SignPointageDTO(pointage_id=1, signature="signature_hash_123")

        result = self.use_case.execute(dto)

        assert result.signature_utilisateur == "signature_hash_123"
        self.pointage_repo.save.assert_called_once()

    def test_sign_empty_signature_raises(self):
        """Test signature avec signature vide."""
        existing = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 2, 15),
        )
        self.pointage_repo.find_by_id.return_value = existing

        dto = SignPointageDTO(pointage_id=1, signature="   ")

        with pytest.raises(ValueError, match="ne peut pas être vide"):
            self.use_case.execute(dto)

    def test_sign_periode_verrouillee(self):
        """Test: ValueError si période de paie verrouillée (GAP-FDH-002).

        Impossible de signer un pointage après la clôture mensuelle.
        """
        # Arrange: Pointage de décembre 2025
        existing = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2025, 12, 15),  # Ancien mois verrouillé
        )
        self.pointage_repo.find_by_id.return_value = existing

        dto = SignPointageDTO(pointage_id=1, signature="signature_hash")

        # Act & Assert
        with pytest.raises(ValueError, match="période de paie est verrouillée"):
            self.use_case.execute(dto)


class TestValidatePointageUseCase:
    """Tests pour ValidatePointageUseCase."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.pointage_repo = Mock()
        self.event_bus = NullEventBus()
        self.use_case = ValidatePointageUseCase(self.pointage_repo, self.event_bus)

    def test_validate_success(self):
        """Test validation réussie."""
        existing = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 2, 15),
            statut=StatutPointage.SOUMIS,
        )
        self.pointage_repo.find_by_id.return_value = existing
        self.pointage_repo.save.return_value = existing

        dto = ValidatePointageDTO(pointage_id=1, validateur_id=5)

        result = self.use_case.execute(dto)

        assert result.statut == "valide"
        assert result.validateur_id == 5

    def test_validate_not_soumis_raises(self):
        """Test validation d'un pointage non soumis."""
        existing = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 2, 15),
            statut=StatutPointage.BROUILLON,
        )
        self.pointage_repo.find_by_id.return_value = existing

        dto = ValidatePointageDTO(pointage_id=1, validateur_id=5)

        with pytest.raises(ValueError, match="Impossible de valider"):
            self.use_case.execute(dto)

    def test_validate_periode_verrouillee(self):
        """Test: ValueError si période de paie verrouillée (GAP-FDH-002).

        Impossible de valider un pointage après la clôture mensuelle.
        """
        # Arrange: Pointage de décembre 2025
        existing = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2025, 12, 15),  # Ancien mois verrouillé
            statut=StatutPointage.SOUMIS,
        )
        self.pointage_repo.find_by_id.return_value = existing

        dto = ValidatePointageDTO(pointage_id=1, validateur_id=5)

        # Act & Assert
        with pytest.raises(ValueError, match="période de paie est verrouillée"):
            self.use_case.execute(dto)


class TestRejectPointageUseCase:
    """Tests pour RejectPointageUseCase."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.pointage_repo = Mock()
        self.event_bus = NullEventBus()
        self.use_case = RejectPointageUseCase(self.pointage_repo, self.event_bus)

    def test_reject_success(self):
        """Test rejet réussi."""
        existing = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 2, 15),
            statut=StatutPointage.SOUMIS,
        )
        self.pointage_repo.find_by_id.return_value = existing
        self.pointage_repo.save.return_value = existing

        dto = RejectPointageDTO(
            pointage_id=1, validateur_id=5, motif="Heures incorrectes"
        )

        result = self.use_case.execute(dto)

        assert result.statut == "rejete"
        assert result.motif_rejet == "Heures incorrectes"

    def test_reject_periode_verrouillee(self):
        """Test: ValueError si période de paie verrouillée (GAP-FDH-002).

        Impossible de rejeter un pointage après la clôture mensuelle.
        """
        # Arrange: Pointage de décembre 2025
        existing = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2025, 12, 15),  # Ancien mois verrouillé
            statut=StatutPointage.SOUMIS,
        )
        self.pointage_repo.find_by_id.return_value = existing

        dto = RejectPointageDTO(
            pointage_id=1, validateur_id=5, motif="Heures incorrectes"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="période de paie est verrouillée"):
            self.use_case.execute(dto)


class TestGetFeuilleHeuresUseCase:
    """Tests pour GetFeuilleHeuresUseCase."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.feuille_repo = Mock()
        self.pointage_repo = Mock()
        self.use_case = GetFeuilleHeuresUseCase(
            self.feuille_repo, self.pointage_repo
        )

    def test_get_navigation(self):
        """Test navigation par semaine (FDH-02)."""
        monday = date(2026, 1, 19)

        nav = self.use_case.get_navigation(monday)

        assert nav.semaine_courante == monday
        assert nav.semaine_precedente == date(2026, 1, 12)
        assert nav.semaine_suivante == date(2026, 1, 26)
        assert nav.numero_semaine == 4
        assert nav.annee == 2026
        assert "Semaine 4" in nav.label

    def test_get_navigation_not_monday(self):
        """Test navigation avec date qui n'est pas un lundi."""
        thursday = date(2026, 1, 22)

        nav = self.use_case.get_navigation(thursday)

        assert nav.semaine_courante == date(2026, 1, 19)  # Lundi
