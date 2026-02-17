"""Tests unitaires pour ChantierController."""

import pytest
from dataclasses import replace
from unittest.mock import Mock
from datetime import datetime

from modules.chantiers.adapters.controllers.chantier_controller import ChantierController
from modules.chantiers.application.use_cases import (
    CreateChantierUseCase,
    GetChantierUseCase,
    ListChantiersUseCase,
    UpdateChantierUseCase,
    DeleteChantierUseCase,
    ChangeStatutUseCase,
    AssignResponsableUseCase,
    ChantierNotFoundError,
    ChantierFermeError,
    ChantierActifError,
    CodeChantierAlreadyExistsError,
    InvalidDatesError,
    TransitionNonAutoriseeError,
)
from modules.chantiers.application.dtos import (
    ChantierDTO,
    ChantierListDTO,
    ContactDTO,
)


class TestChantierController:
    """Tests pour ChantierController."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Mock tous les use cases
        self.mock_create_uc = Mock(spec=CreateChantierUseCase)
        self.mock_get_uc = Mock(spec=GetChantierUseCase)
        self.mock_list_uc = Mock(spec=ListChantiersUseCase)
        self.mock_update_uc = Mock(spec=UpdateChantierUseCase)
        self.mock_delete_uc = Mock(spec=DeleteChantierUseCase)
        self.mock_change_statut_uc = Mock(spec=ChangeStatutUseCase)
        self.mock_assign_responsable_uc = Mock(spec=AssignResponsableUseCase)

        # Controller
        self.controller = ChantierController(
            create_use_case=self.mock_create_uc,
            get_use_case=self.mock_get_uc,
            list_use_case=self.mock_list_uc,
            update_use_case=self.mock_update_uc,
            delete_use_case=self.mock_delete_uc,
            change_statut_use_case=self.mock_change_statut_uc,
            assign_responsable_use_case=self.mock_assign_responsable_uc,
        )

    def _create_chantier_dto(self, chantier_id: int = 1, code: str = "A001", nom: str = "Chantier Test") -> ChantierDTO:
        """Crée un ChantierDTO de test."""
        return ChantierDTO(
            id=chantier_id,
            code=code,
            nom=nom,
            adresse="123 Rue Test",
            statut="ouvert",
            statut_icon="🔵",
            couleur="#3B82F6",
            coordonnees_gps={"latitude": 48.8566, "longitude": 2.3522},
            photo_couverture=None,
            contact={"nom": "Jean Dupont", "telephone": "0612345678"},
            contacts=[],
            maitre_ouvrage="OPAC Lyon",
            heures_estimees=100.0,
            date_debut="2026-02-01",
            date_fin="2026-06-30",
            description="Description test",
            conducteur_ids=[1, 2],
            chef_chantier_ids=[3],
            is_active=True,
            created_at=datetime(2026, 1, 1, 10, 0, 0),
            updated_at=datetime(2026, 1, 15, 14, 30, 0),
        )

    # ==================== Tests create() ====================

    def test_create_success(self):
        """Test: create() appelle le use case et retourne un dict."""
        # Arrange
        dto = self._create_chantier_dto()
        self.mock_create_uc.execute.return_value = dto

        # Act
        result = self.controller.create(
            nom="Chantier Test",
            adresse="123 Rue Test",
            code="A001",
        )

        # Assert
        assert result["id"] == 1
        assert result["code"] == "A001"
        assert result["nom"] == "Chantier Test"
        assert result["adresse"] == "123 Rue Test"
        self.mock_create_uc.execute.assert_called_once()

    def test_create_with_all_fields(self):
        """Test: create() avec tous les champs optionnels."""
        # Arrange
        dto = replace(
            self._create_chantier_dto(),
            contacts=[
                ContactDTO(nom="Jean Dupont", profession="Architecte", telephone="0612345678"),
                ContactDTO(nom="Marie Martin", profession="Ingénieur", telephone="0687654321"),
            ]
        )
        self.mock_create_uc.execute.return_value = dto

        # Act
        result = self.controller.create(
            nom="Chantier Test",
            adresse="123 Rue Test",
            code="A001",
            couleur="#3B82F6",
            latitude=48.8566,
            longitude=2.3522,
            photo_couverture="https://example.com/photo.jpg",
            contact_nom="Jean Dupont",
            contact_telephone="0612345678",
            contacts=[
                {"nom": "Jean Dupont", "profession": "Architecte", "telephone": "0612345678"},
                {"nom": "Marie Martin", "profession": "Ingénieur", "telephone": "0687654321"},
            ],
            heures_estimees=100.0,
            date_debut="2026-02-01",
            date_fin="2026-06-30",
            description="Description test",
            conducteur_ids=[1, 2],
            chef_chantier_ids=[3],
        )

        # Assert
        assert result["id"] == 1
        assert len(result["contacts"]) == 2
        assert result["contacts"][0]["nom"] == "Jean Dupont"
        assert result["contacts"][1]["nom"] == "Marie Martin"
        self.mock_create_uc.execute.assert_called_once()

    def test_create_with_code_already_exists_raises_error(self):
        """Test: create() raise CodeChantierAlreadyExistsError si code existe."""
        # Arrange
        self.mock_create_uc.execute.side_effect = CodeChantierAlreadyExistsError("A001")

        # Act & Assert
        with pytest.raises(CodeChantierAlreadyExistsError):
            self.controller.create(nom="Test", adresse="Adresse", code="A001")

    def test_create_with_invalid_dates_raises_error(self):
        """Test: create() raise InvalidDatesError si dates invalides."""
        # Arrange
        self.mock_create_uc.execute.side_effect = InvalidDatesError(
            "La date de fin doit être après la date de début"
        )

        # Act & Assert
        with pytest.raises(InvalidDatesError):
            self.controller.create(
                nom="Test",
                adresse="Adresse",
                date_debut="2026-06-30",
                date_fin="2026-02-01",
            )

    # ==================== Tests get_by_id() ====================

    def test_get_by_id_success(self):
        """Test: get_by_id() retourne un chantier."""
        # Arrange
        dto = self._create_chantier_dto(chantier_id=42)
        self.mock_get_uc.execute_by_id.return_value = dto

        # Act
        result = self.controller.get_by_id(42)

        # Assert
        assert result["id"] == 42
        assert result["code"] == "A001"
        self.mock_get_uc.execute_by_id.assert_called_once_with(42)

    def test_get_by_id_not_found_raises_error(self):
        """Test: get_by_id() raise ChantierNotFoundError si non trouvé."""
        # Arrange
        self.mock_get_uc.execute_by_id.side_effect = ChantierNotFoundError(999)

        # Act & Assert
        with pytest.raises(ChantierNotFoundError):
            self.controller.get_by_id(999)

    # ==================== Tests get_by_code() ====================

    def test_get_by_code_success(self):
        """Test: get_by_code() retourne un chantier."""
        # Arrange
        dto = self._create_chantier_dto(code="B001")
        self.mock_get_uc.execute_by_code.return_value = dto

        # Act
        result = self.controller.get_by_code("B001")

        # Assert
        assert result["code"] == "B001"
        self.mock_get_uc.execute_by_code.assert_called_once_with("B001")

    def test_get_by_code_not_found_raises_error(self):
        """Test: get_by_code() raise ChantierNotFoundError si non trouvé."""
        # Arrange
        self.mock_get_uc.execute_by_code.side_effect = ChantierNotFoundError("INVALID")

        # Act & Assert
        with pytest.raises(ChantierNotFoundError):
            self.controller.get_by_code("INVALID")

    # ==================== Tests list() ====================

    def test_list_chantiers_success(self):
        """Test: list() retourne une liste paginée."""
        # Arrange
        dto1 = self._create_chantier_dto(1, "A001")
        dto2 = self._create_chantier_dto(2, "A002")
        list_dto = ChantierListDTO(
            chantiers=[dto1, dto2],
            total=2,
            skip=0,
            limit=100,
        )
        self.mock_list_uc.execute.return_value = list_dto

        # Act
        result = self.controller.list(skip=0, limit=100)

        # Assert
        assert len(result["chantiers"]) == 2
        assert result["total"] == 2
        assert result["skip"] == 0
        assert result["limit"] == 100
        assert result["has_next"] is False
        assert result["has_previous"] is False
        self.mock_list_uc.execute.assert_called_once()

    def test_list_chantiers_with_filters(self):
        """Test: list() avec filtres (statut, responsable, search)."""
        # Arrange
        dto = self._create_chantier_dto()
        list_dto = ChantierListDTO(
            chantiers=[dto],
            total=1,
            skip=0,
            limit=100,
        )
        self.mock_list_uc.execute.return_value = list_dto

        # Act
        result = self.controller.list(
            skip=0,
            limit=50,
            statut="en_cours",
            conducteur_id=10,
            chef_chantier_id=20,
            responsable_id=30,
            actifs_uniquement=True,
            search="Test",
        )

        # Assert
        assert result["total"] == 1
        self.mock_list_uc.execute.assert_called_once_with(
            skip=0,
            limit=50,
            statut="en_cours",
            conducteur_id=10,
            chef_chantier_id=20,
            responsable_id=30,
            actifs_uniquement=True,
            search="Test",
            exclude_codes=None,
        )

    # ==================== Tests update() ====================

    def test_update_chantier_success(self):
        """Test: update() met à jour un chantier."""
        # Arrange
        dto = replace(self._create_chantier_dto(), nom="Nom Modifié")
        self.mock_update_uc.execute.return_value = dto

        # Act
        result = self.controller.update(
            chantier_id=1,
            nom="Nom Modifié",
            adresse="Nouvelle adresse",
        )

        # Assert
        assert result["nom"] == "Nom Modifié"
        self.mock_update_uc.execute.assert_called_once()

    def test_update_chantier_with_statut_change(self):
        """Test: update() avec changement de statut appelle aussi change_statut."""
        # Arrange
        dto_updated = replace(self._create_chantier_dto(), statut="ouvert")
        dto_with_new_statut = replace(self._create_chantier_dto(), statut="en_cours")

        self.mock_update_uc.execute.return_value = dto_updated
        self.mock_change_statut_uc.execute.return_value = dto_with_new_statut

        # Act
        result = self.controller.update(
            chantier_id=1,
            nom="Test",
            statut="en_cours",
        )

        # Assert
        assert result["statut"] == "en_cours"
        self.mock_update_uc.execute.assert_called_once()
        self.mock_change_statut_uc.execute.assert_called_once()

    def test_update_chantier_not_found_raises_error(self):
        """Test: update() raise ChantierNotFoundError si non trouvé."""
        # Arrange
        self.mock_update_uc.execute.side_effect = ChantierNotFoundError(999)

        # Act & Assert
        with pytest.raises(ChantierNotFoundError):
            self.controller.update(chantier_id=999, nom="Test")

    def test_update_chantier_ferme_raises_error(self):
        """Test: update() raise ChantierFermeError si chantier fermé."""
        # Arrange
        self.mock_update_uc.execute.side_effect = ChantierFermeError(1)

        # Act & Assert
        with pytest.raises(ChantierFermeError):
            self.controller.update(chantier_id=1, nom="Test")

    # ==================== Tests delete() ====================

    def test_delete_chantier_success(self):
        """Test: delete() supprime un chantier."""
        # Arrange
        self.mock_delete_uc.execute.return_value = True

        # Act
        result = self.controller.delete(chantier_id=1, force=False)

        # Assert
        assert result["deleted"] is True
        assert result["id"] == 1
        self.mock_delete_uc.execute.assert_called_once_with(1, force=False)

    def test_delete_chantier_with_force(self):
        """Test: delete() avec force=True."""
        # Arrange
        self.mock_delete_uc.execute.return_value = True

        # Act
        result = self.controller.delete(chantier_id=1, force=True)

        # Assert
        assert result["deleted"] is True
        self.mock_delete_uc.execute.assert_called_once_with(1, force=True)

    def test_delete_chantier_not_found_raises_error(self):
        """Test: delete() raise ChantierNotFoundError si non trouvé."""
        # Arrange
        self.mock_delete_uc.execute.side_effect = ChantierNotFoundError(999)

        # Act & Assert
        with pytest.raises(ChantierNotFoundError):
            self.controller.delete(chantier_id=999)

    def test_delete_chantier_actif_raises_error(self):
        """Test: delete() raise ChantierActifError si actif sans force."""
        # Arrange
        self.mock_delete_uc.execute.side_effect = ChantierActifError(1)

        # Act & Assert
        with pytest.raises(ChantierActifError):
            self.controller.delete(chantier_id=1, force=False)

    # ==================== Tests change_statut() ====================

    def test_change_statut_success(self):
        """Test: change_statut() change le statut."""
        # Arrange
        dto = replace(self._create_chantier_dto(), statut="en_cours")
        self.mock_change_statut_uc.execute.return_value = dto

        # Act
        result = self.controller.change_statut(chantier_id=1, nouveau_statut="en_cours")

        # Assert
        assert result["statut"] == "en_cours"
        self.mock_change_statut_uc.execute.assert_called_once()

    def test_change_statut_not_found_raises_error(self):
        """Test: change_statut() raise ChantierNotFoundError si non trouvé."""
        # Arrange
        self.mock_change_statut_uc.execute.side_effect = ChantierNotFoundError(999)

        # Act & Assert
        with pytest.raises(ChantierNotFoundError):
            self.controller.change_statut(chantier_id=999, nouveau_statut="en_cours")

    def test_change_statut_transition_non_autorisee_raises_error(self):
        """Test: change_statut() raise TransitionNonAutoriseeError si transition invalide."""
        # Arrange
        self.mock_change_statut_uc.execute.side_effect = TransitionNonAutoriseeError("ferme", "ouvert")

        # Act & Assert
        with pytest.raises(TransitionNonAutoriseeError):
            self.controller.change_statut(chantier_id=1, nouveau_statut="ouvert")

    # ==================== Tests Raccourcis Statut ====================

    def test_demarrer_success(self):
        """Test: demarrer() passe en 'en_cours'."""
        # Arrange
        dto = replace(self._create_chantier_dto(), statut="en_cours")
        self.mock_change_statut_uc.demarrer.return_value = dto

        # Act
        result = self.controller.demarrer(chantier_id=1)

        # Assert
        assert result["statut"] == "en_cours"
        self.mock_change_statut_uc.demarrer.assert_called_once_with(1)

    def test_receptionner_success(self):
        """Test: receptionner() passe en 'receptionne'."""
        # Arrange
        dto = replace(self._create_chantier_dto(), statut="receptionne")
        self.mock_change_statut_uc.receptionner.return_value = dto

        # Act
        result = self.controller.receptionner(chantier_id=1)

        # Assert
        assert result["statut"] == "receptionne"
        self.mock_change_statut_uc.receptionner.assert_called_once_with(1)

    def test_fermer_success(self):
        """Test: fermer() passe en 'ferme'."""
        # Arrange
        dto = replace(self._create_chantier_dto(), statut="ferme")
        self.mock_change_statut_uc.fermer.return_value = dto

        # Act
        result = self.controller.fermer(chantier_id=1)

        # Assert
        assert result["statut"] == "ferme"
        self.mock_change_statut_uc.fermer.assert_called_once_with(1)

    # ==================== Tests Assignation Responsables ====================

    def test_assigner_conducteur_success(self):
        """Test: assigner_conducteur() ajoute un conducteur."""
        # Arrange
        dto = replace(self._create_chantier_dto(), conducteur_ids=[1, 10])
        self.mock_assign_responsable_uc.assigner_conducteur.return_value = dto

        # Act
        result = self.controller.assigner_conducteur(chantier_id=1, user_id=10)

        # Assert
        assert 10 in result["conducteur_ids"]
        self.mock_assign_responsable_uc.assigner_conducteur.assert_called_once_with(1, 10)

    def test_assigner_chef_chantier_success(self):
        """Test: assigner_chef_chantier() ajoute un chef."""
        # Arrange
        dto = replace(self._create_chantier_dto(), chef_chantier_ids=[3, 20])
        self.mock_assign_responsable_uc.assigner_chef_chantier.return_value = dto

        # Act
        result = self.controller.assigner_chef_chantier(chantier_id=1, user_id=20)

        # Assert
        assert 20 in result["chef_chantier_ids"]
        self.mock_assign_responsable_uc.assigner_chef_chantier.assert_called_once_with(1, 20)

    def test_retirer_conducteur_success(self):
        """Test: retirer_conducteur() retire un conducteur."""
        # Arrange
        dto = replace(self._create_chantier_dto(), conducteur_ids=[2])
        self.mock_assign_responsable_uc.retirer_conducteur.return_value = dto

        # Act
        result = self.controller.retirer_conducteur(chantier_id=1, user_id=1)

        # Assert
        assert 1 not in result["conducteur_ids"]
        assert 2 in result["conducteur_ids"]
        self.mock_assign_responsable_uc.retirer_conducteur.assert_called_once_with(1, 1)

    def test_retirer_chef_chantier_success(self):
        """Test: retirer_chef_chantier() retire un chef."""
        # Arrange
        dto = replace(self._create_chantier_dto(), chef_chantier_ids=[])
        self.mock_assign_responsable_uc.retirer_chef_chantier.return_value = dto

        # Act
        result = self.controller.retirer_chef_chantier(chantier_id=1, user_id=3)

        # Assert
        assert 3 not in result["chef_chantier_ids"]
        self.mock_assign_responsable_uc.retirer_chef_chantier.assert_called_once_with(1, 3)
