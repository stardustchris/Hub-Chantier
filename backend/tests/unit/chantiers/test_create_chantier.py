"""Tests unitaires pour CreateChantierUseCase."""

import pytest
from unittest.mock import Mock

from modules.chantiers.domain.entities import Chantier
from modules.chantiers.domain.repositories import ChantierRepository
from modules.chantiers.application.use_cases import (
    CreateChantierUseCase,
    CodeChantierAlreadyExistsError,
    InvalidDatesError,
)
from modules.chantiers.application.dtos import CreateChantierDTO


class TestCreateChantierUseCase:
    """Tests pour le use case de création de chantier."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=ChantierRepository)
        self.use_case = CreateChantierUseCase(chantier_repo=self.mock_repo)

        # Configurer les mocks par défaut
        self.mock_repo.exists_by_code.return_value = False
        self.mock_repo.get_last_code.return_value = None

    def _create_saved_chantier(self, chantier: Chantier) -> Chantier:
        """Simule la sauvegarde en ajoutant un ID."""
        chantier.id = 1
        return chantier

    def test_create_success_minimal(self):
        """Test: création réussie avec données minimales."""
        # Arrange
        self.mock_repo.save.side_effect = self._create_saved_chantier

        dto = CreateChantierDTO(
            nom="Villa Lyon 3ème",
            adresse="123 Rue de la Paix, 69003 Lyon",
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.id == 1
        assert result.nom == "Villa Lyon 3ème"
        assert result.adresse == "123 Rue de la Paix, 69003 Lyon"
        assert result.code == "A001"  # Auto-généré
        assert result.statut == "ouvert"
        assert result.is_active is True

    def test_create_success_with_code(self):
        """Test: création avec code personnalisé (CHT-19)."""
        # Arrange
        self.mock_repo.save.side_effect = self._create_saved_chantier

        dto = CreateChantierDTO(
            nom="Chantier Test",
            adresse="Adresse Test",
            code="B042",
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.code == "B042"

    def test_create_success_with_gps(self):
        """Test: création avec coordonnées GPS (CHT-04)."""
        # Arrange
        self.mock_repo.save.side_effect = self._create_saved_chantier

        dto = CreateChantierDTO(
            nom="Chantier GPS",
            adresse="Adresse Test",
            latitude=45.764043,
            longitude=4.835659,
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.coordonnees_gps is not None
        assert result.coordonnees_gps["latitude"] == 45.764043
        assert result.coordonnees_gps["longitude"] == 4.835659

    def test_create_success_with_contact(self):
        """Test: création avec contact sur place (CHT-07)."""
        # Arrange
        self.mock_repo.save.side_effect = self._create_saved_chantier

        dto = CreateChantierDTO(
            nom="Chantier Contact",
            adresse="Adresse Test",
            contact_nom="Jean Dupont",
            contact_telephone="+33612345678",
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.contact is not None
        assert result.contact["nom"] == "Jean Dupont"

    def test_create_success_with_dates(self):
        """Test: création avec dates prévisionnelles (CHT-20)."""
        # Arrange
        self.mock_repo.save.side_effect = self._create_saved_chantier

        dto = CreateChantierDTO(
            nom="Chantier Daté",
            adresse="Adresse Test",
            date_debut="2026-02-01",
            date_fin="2026-06-30",
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.date_debut == "2026-02-01"
        assert result.date_fin == "2026-06-30"

    def test_create_success_with_heures_estimees(self):
        """Test: création avec budget temps (CHT-18)."""
        # Arrange
        self.mock_repo.save.side_effect = self._create_saved_chantier

        dto = CreateChantierDTO(
            nom="Chantier Budget",
            adresse="Adresse Test",
            heures_estimees=1500.0,
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.heures_estimees == 1500.0

    def test_create_success_with_responsables(self):
        """Test: création avec conducteurs et chefs (CHT-05, CHT-06)."""
        # Arrange
        self.mock_repo.save.side_effect = self._create_saved_chantier

        dto = CreateChantierDTO(
            nom="Chantier Responsables",
            adresse="Adresse Test",
            conducteur_ids=[1, 2],
            chef_chantier_ids=[3],
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.conducteur_ids == [1, 2]
        assert result.chef_chantier_ids == [3]

    def test_create_code_already_exists(self):
        """Test: échec si code déjà utilisé."""
        # Arrange
        self.mock_repo.exists_by_code.return_value = True

        dto = CreateChantierDTO(
            nom="Chantier Duppliqué",
            adresse="Adresse Test",
            code="A001",
        )

        # Act & Assert
        with pytest.raises(CodeChantierAlreadyExistsError) as exc_info:
            self.use_case.execute(dto)
        assert "A001" in str(exc_info.value)

    def test_create_invalid_dates_order(self):
        """Test: échec si date_fin < date_debut."""
        # Arrange
        dto = CreateChantierDTO(
            nom="Chantier Dates Invalides",
            adresse="Adresse Test",
            date_debut="2026-06-30",
            date_fin="2026-02-01",  # Avant date_debut
        )

        # Act & Assert
        with pytest.raises(InvalidDatesError):
            self.use_case.execute(dto)

    def test_create_invalid_code_format(self):
        """Test: échec si format de code invalide."""
        # Arrange
        dto = CreateChantierDTO(
            nom="Chantier Code Invalide",
            adresse="Adresse Test",
            code="INVALID",  # Pas le bon format
        )

        # Act & Assert
        with pytest.raises(ValueError):
            self.use_case.execute(dto)

    def test_create_auto_generate_next_code(self):
        """Test: auto-génération du code suivant."""
        # Arrange
        self.mock_repo.get_last_code.return_value = "A005"
        self.mock_repo.save.side_effect = self._create_saved_chantier

        dto = CreateChantierDTO(
            nom="Nouveau Chantier",
            adresse="Adresse Test",
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.code == "A006"

    def test_create_publishes_event(self):
        """Test: publication d'un event après création réussie."""
        # Arrange
        mock_publisher = Mock()
        use_case_with_events = CreateChantierUseCase(
            chantier_repo=self.mock_repo,
            event_publisher=mock_publisher,
        )
        self.mock_repo.save.side_effect = self._create_saved_chantier

        dto = CreateChantierDTO(
            nom="Chantier Event",
            adresse="Adresse Test",
        )

        # Act
        use_case_with_events.execute(dto)

        # Assert
        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.chantier_id == 1
        assert event.nom == "Chantier Event"
        assert event.statut == "ouvert"

    def test_create_with_all_fields(self):
        """Test: création avec tous les champs CDC."""
        # Arrange
        self.mock_repo.save.side_effect = self._create_saved_chantier

        dto = CreateChantierDTO(
            nom="Chantier Complet",
            adresse="456 Avenue des Tests, 75001 Paris",
            code="C123",
            couleur="#E74C3C",  # Rouge
            latitude=48.856614,
            longitude=2.3522219,
            photo_couverture="https://example.com/photo.jpg",
            contact_nom="Pierre Martin",
            contact_telephone="0612345678",
            heures_estimees=2000.5,
            date_debut="2026-03-01",
            date_fin="2026-12-31",
            description="Description détaillée du chantier",
            conducteur_ids=[1, 2, 3],
            chef_chantier_ids=[4, 5],
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.nom == "Chantier Complet"
        assert result.code == "C123"
        assert result.couleur == "#E74C3C"
        assert result.coordonnees_gps is not None
        assert result.photo_couverture == "https://example.com/photo.jpg"
        assert result.contact is not None
        assert result.heures_estimees == 2000.5
        assert result.date_debut == "2026-03-01"
        assert result.date_fin == "2026-12-31"
        assert result.description == "Description détaillée du chantier"
        assert len(result.conducteur_ids) == 3
        assert len(result.chef_chantier_ids) == 2
