"""Tests unitaires pour les Use Cases Fournisseur du module Financier."""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock

from modules.financier.domain.entities import Fournisseur
from modules.financier.domain.repositories import (
    FournisseurRepository,
    JournalFinancierRepository,
)
from modules.financier.domain.value_objects import TypeFournisseur
from modules.financier.application.ports.event_bus import EventBus
from modules.financier.application.dtos import (
    FournisseurCreateDTO,
    FournisseurUpdateDTO,
)
from modules.financier.application.use_cases.fournisseur_use_cases import (
    CreateFournisseurUseCase,
    UpdateFournisseurUseCase,
    DeleteFournisseurUseCase,
    GetFournisseurUseCase,
    ListFournisseursUseCase,
    FournisseurNotFoundError,
    FournisseurSiretExistsError,
)


class TestCreateFournisseurUseCase:
    """Tests pour le use case de creation de fournisseur."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=FournisseurRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = CreateFournisseurUseCase(
            fournisseur_repository=self.mock_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_create_fournisseur_success(self):
        """Test: creation reussie d'un fournisseur."""
        dto = FournisseurCreateDTO(
            raison_sociale="Materiaux du Sud",
            type=TypeFournisseur.NEGOCE_MATERIAUX,
            siret="12345678901234",
            email="contact@materiaux.fr",
        )

        # Mock: pas de SIRET existant
        self.mock_repo.find_by_siret.return_value = None

        # Mock: save retourne le fournisseur avec ID
        def save_side_effect(fournisseur):
            fournisseur.id = 1
            return fournisseur

        self.mock_repo.save.side_effect = save_side_effect

        result = self.use_case.execute(dto, created_by=10)

        assert result.id == 1
        assert result.raison_sociale == "Materiaux du Sud"
        assert result.type == "negoce_materiaux"
        self.mock_repo.save.assert_called_once()
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_create_fournisseur_siret_duplicate(self):
        """Test: erreur si SIRET deja existant."""
        dto = FournisseurCreateDTO(
            raison_sociale="Test",
            siret="12345678901234",
        )

        # Mock: SIRET existe deja
        self.mock_repo.find_by_siret.return_value = Fournisseur(
            id=99,
            raison_sociale="Existant",
            siret="12345678901234",
        )

        with pytest.raises(FournisseurSiretExistsError) as exc_info:
            self.use_case.execute(dto, created_by=10)
        assert "12345678901234" in str(exc_info.value)
        self.mock_repo.save.assert_not_called()

    def test_create_fournisseur_sans_siret(self):
        """Test: creation reussie sans SIRET."""
        dto = FournisseurCreateDTO(
            raison_sociale="Test SARL",
        )

        def save_side_effect(fournisseur):
            fournisseur.id = 1
            return fournisseur

        self.mock_repo.save.side_effect = save_side_effect

        result = self.use_case.execute(dto, created_by=10)

        assert result.id == 1
        self.mock_repo.find_by_siret.assert_not_called()


class TestUpdateFournisseurUseCase:
    """Tests pour le use case de mise a jour de fournisseur."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=FournisseurRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = UpdateFournisseurUseCase(
            fournisseur_repository=self.mock_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_update_fournisseur_success(self):
        """Test: mise a jour reussie d'un fournisseur."""
        existing = Fournisseur(
            id=1,
            raison_sociale="Ancien nom",
            type=TypeFournisseur.NEGOCE_MATERIAUX,
            created_at=datetime.utcnow(),
        )
        self.mock_repo.find_by_id.return_value = existing
        self.mock_repo.save.return_value = existing

        dto = FournisseurUpdateDTO(raison_sociale="Nouveau nom")
        result = self.use_case.execute(1, dto, updated_by=10)

        assert result.raison_sociale == "Nouveau nom"
        self.mock_repo.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_update_fournisseur_not_found(self):
        """Test: erreur si fournisseur non trouve."""
        self.mock_repo.find_by_id.return_value = None

        dto = FournisseurUpdateDTO(raison_sociale="Nouveau nom")

        with pytest.raises(FournisseurNotFoundError):
            self.use_case.execute(999, dto, updated_by=10)

    def test_update_fournisseur_siret_duplicate(self):
        """Test: erreur si nouveau SIRET deja existant."""
        existing = Fournisseur(
            id=1,
            raison_sociale="Test",
            siret="11111111111111",
            created_at=datetime.utcnow(),
        )
        self.mock_repo.find_by_id.return_value = existing

        # Un autre fournisseur a deja ce SIRET
        other = Fournisseur(
            id=2,
            raison_sociale="Autre",
            siret="22222222222222",
        )
        self.mock_repo.find_by_siret.return_value = other

        dto = FournisseurUpdateDTO(siret="22222222222222")

        with pytest.raises(FournisseurSiretExistsError):
            self.use_case.execute(1, dto, updated_by=10)

    def test_update_fournisseur_meme_siret_ok(self):
        """Test: mise a jour avec le meme SIRET est autorisee."""
        existing = Fournisseur(
            id=1,
            raison_sociale="Test",
            siret="11111111111111",
            created_at=datetime.utcnow(),
        )
        self.mock_repo.find_by_id.return_value = existing

        # Le meme fournisseur retrouve par SIRET (meme ID)
        self.mock_repo.find_by_siret.return_value = existing
        self.mock_repo.save.return_value = existing

        dto = FournisseurUpdateDTO(siret="11111111111111")
        result = self.use_case.execute(1, dto, updated_by=10)

        # Pas d'erreur, meme fournisseur
        self.mock_repo.save.assert_called_once()


class TestDeleteFournisseurUseCase:
    """Tests pour le use case de suppression de fournisseur."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=FournisseurRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = DeleteFournisseurUseCase(
            fournisseur_repository=self.mock_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_delete_fournisseur_success(self):
        """Test: suppression reussie d'un fournisseur."""
        existing = Fournisseur(
            id=1,
            raison_sociale="Test",
            created_at=datetime.utcnow(),
        )
        self.mock_repo.find_by_id.return_value = existing
        self.mock_repo.delete.return_value = True

        result = self.use_case.execute(1, deleted_by=10)

        assert result is True
        self.mock_repo.delete.assert_called_once_with(1, deleted_by=10)
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_delete_fournisseur_not_found(self):
        """Test: erreur si fournisseur non trouve."""
        self.mock_repo.find_by_id.return_value = None

        with pytest.raises(FournisseurNotFoundError):
            self.use_case.execute(999, deleted_by=10)

    def test_delete_fournisseur_delete_fails(self):
        """Test: pas d'event ni journal si delete retourne False."""
        existing = Fournisseur(
            id=1,
            raison_sociale="Test",
            created_at=datetime.utcnow(),
        )
        self.mock_repo.find_by_id.return_value = existing
        self.mock_repo.delete.return_value = False

        result = self.use_case.execute(1, deleted_by=10)

        assert result is False
        self.mock_journal.save.assert_not_called()
        self.mock_event_bus.publish.assert_not_called()


class TestGetFournisseurUseCase:
    """Tests pour le use case de recuperation d'un fournisseur."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=FournisseurRepository)
        self.use_case = GetFournisseurUseCase(
            fournisseur_repository=self.mock_repo,
        )

    def test_get_fournisseur_success(self):
        """Test: recuperation reussie d'un fournisseur."""
        existing = Fournisseur(
            id=1,
            raison_sociale="Test",
            type=TypeFournisseur.LOUEUR,
            created_at=datetime.utcnow(),
        )
        self.mock_repo.find_by_id.return_value = existing

        result = self.use_case.execute(1)

        assert result.id == 1
        assert result.raison_sociale == "Test"
        assert result.type == "loueur"

    def test_get_fournisseur_not_found(self):
        """Test: erreur si fournisseur non trouve."""
        self.mock_repo.find_by_id.return_value = None

        with pytest.raises(FournisseurNotFoundError):
            self.use_case.execute(999)


class TestListFournisseursUseCase:
    """Tests pour le use case de listage des fournisseurs."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=FournisseurRepository)
        self.use_case = ListFournisseursUseCase(
            fournisseur_repository=self.mock_repo,
        )

    def test_list_fournisseurs_success(self):
        """Test: listage reussi des fournisseurs."""
        fournisseurs = [
            Fournisseur(
                id=1,
                raison_sociale="Test 1",
                type=TypeFournisseur.NEGOCE_MATERIAUX,
                created_at=datetime.utcnow(),
            ),
            Fournisseur(
                id=2,
                raison_sociale="Test 2",
                type=TypeFournisseur.LOUEUR,
                created_at=datetime.utcnow(),
            ),
        ]
        self.mock_repo.find_all.return_value = fournisseurs
        self.mock_repo.count.return_value = 2

        result = self.use_case.execute()

        assert len(result.items) == 2
        assert result.total == 2
        assert result.items[0].raison_sociale == "Test 1"

    def test_list_fournisseurs_with_type_filter(self):
        """Test: listage avec filtre par type."""
        self.mock_repo.find_all.return_value = []
        self.mock_repo.count.return_value = 0

        result = self.use_case.execute(type=TypeFournisseur.LOUEUR)

        self.mock_repo.find_all.assert_called_once_with(
            type=TypeFournisseur.LOUEUR,
            actif_seulement=True,
            limit=100,
            offset=0,
        )

    def test_list_fournisseurs_pagination(self):
        """Test: listage avec pagination."""
        self.mock_repo.find_all.return_value = []
        self.mock_repo.count.return_value = 50

        result = self.use_case.execute(limit=10, offset=20)

        assert result.limit == 10
        assert result.offset == 20
