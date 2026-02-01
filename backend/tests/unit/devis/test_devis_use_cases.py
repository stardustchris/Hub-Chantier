"""Tests unitaires pour les Use Cases CRUD de devis.

DEV-03: Creation devis structure.
Couche Application - devis_use_cases.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch, ANY

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.entities.journal_devis import JournalDevis
from modules.devis.domain.entities.lot_devis import LotDevis
from modules.devis.domain.entities.ligne_devis import LigneDevis
from modules.devis.domain.entities.debourse_detail import DebourseDetail
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.lot_devis_repository import LotDevisRepository
from modules.devis.domain.repositories.ligne_devis_repository import LigneDevisRepository
from modules.devis.domain.repositories.debourse_detail_repository import DebourseDetailRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.devis_use_cases import (
    CreateDevisUseCase,
    UpdateDevisUseCase,
    GetDevisUseCase,
    ListDevisUseCase,
    DeleteDevisUseCase,
    DevisNotFoundError,
    DevisNotModifiableError,
)
from modules.devis.application.dtos.devis_dtos import (
    DevisCreateDTO,
    DevisUpdateDTO,
    DevisDTO,
    DevisDetailDTO,
    DevisListDTO,
)


def _make_devis(**kwargs):
    """Cree un devis valide avec valeurs par defaut."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "objet": "Renovation bureau",
        "statut": StatutDevis.BROUILLON,
        "date_creation": date(2026, 1, 15),
        "montant_total_ht": Decimal("0"),
        "montant_total_ttc": Decimal("0"),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


class TestCreateDevisUseCase:
    """Tests pour le use case de creation de devis."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = CreateDevisUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_create_devis_success(self):
        """Test: creation d'un devis reussie."""
        self.mock_devis_repo.generate_numero.return_value = "DEV-2026-001"
        saved_devis = _make_devis()
        self.mock_devis_repo.save.return_value = saved_devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = DevisCreateDTO(
            client_nom="Greg Construction",
            objet="Renovation bureau",
        )

        result = self.use_case.execute(dto, created_by=1)

        assert isinstance(result, DevisDTO)
        assert result.numero == "DEV-2026-001"
        assert result.client_nom == "Greg Construction"
        self.mock_devis_repo.generate_numero.assert_called_once()
        self.mock_devis_repo.save.assert_called_once()
        self.mock_journal_repo.save.assert_called_once()

    def test_create_devis_with_all_fields(self):
        """Test: creation avec tous les champs optionnels."""
        self.mock_devis_repo.generate_numero.return_value = "DEV-2026-002"
        saved_devis = _make_devis(
            id=2,
            numero="DEV-2026-002",
            taux_marge_global=Decimal("20"),
        )
        self.mock_devis_repo.save.return_value = saved_devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = DevisCreateDTO(
            client_nom="Client SARL",
            objet="Extension",
            chantier_ref="CHANTIER-001",
            client_adresse="123 Rue de la Paix",
            client_email="contact@client.fr",
            client_telephone="0601020304",
            date_validite=date(2026, 6, 30),
            taux_marge_global=Decimal("20"),
            taux_marge_moe=Decimal("25"),
            coefficient_frais_generaux=Decimal("10"),
            retenue_garantie_pct=Decimal("5"),
            notes="Notes",
            commercial_id=5,
            conducteur_id=3,
        )

        result = self.use_case.execute(dto, created_by=1)

        assert isinstance(result, DevisDTO)
        self.mock_devis_repo.save.assert_called_once()

    def test_create_devis_journal_entry(self):
        """Test: une entree de journal est creee."""
        self.mock_devis_repo.generate_numero.return_value = "DEV-2026-003"
        self.mock_devis_repo.save.return_value = _make_devis(id=3, numero="DEV-2026-003")
        self.mock_journal_repo.save.return_value = Mock()

        dto = DevisCreateDTO(client_nom="Client", objet="Objet")
        self.use_case.execute(dto, created_by=1)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert isinstance(journal_call, JournalDevis)
        assert journal_call.action == "creation"
        assert journal_call.auteur_id == 1


class TestUpdateDevisUseCase:
    """Tests pour le use case de mise a jour de devis."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = UpdateDevisUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_update_devis_success(self):
        """Test: mise a jour reussie d'un devis en brouillon."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = DevisUpdateDTO(client_nom="Nouveau Client")
        result = self.use_case.execute(devis_id=1, dto=dto, updated_by=2)

        assert isinstance(result, DevisDTO)
        self.mock_devis_repo.save.assert_called_once()

    def test_update_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        dto = DevisUpdateDTO(client_nom="Nouveau")
        with pytest.raises(DevisNotFoundError) as exc_info:
            self.use_case.execute(devis_id=999, dto=dto, updated_by=1)
        assert exc_info.value.devis_id == 999

    def test_update_devis_not_modifiable(self):
        """Test: erreur si devis non modifiable (envoye)."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_by_id.return_value = devis

        dto = DevisUpdateDTO(client_nom="Nouveau")
        with pytest.raises(DevisNotModifiableError) as exc_info:
            self.use_case.execute(devis_id=1, dto=dto, updated_by=1)
        assert exc_info.value.devis_id == 1
        assert exc_info.value.statut == StatutDevis.ENVOYE

    def test_update_devis_multiple_fields(self):
        """Test: mise a jour de plusieurs champs."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = DevisUpdateDTO(
            client_nom="Nouveau Client",
            objet="Nouveau Objet",
            taux_marge_global=Decimal("25"),
        )
        self.use_case.execute(devis_id=1, dto=dto, updated_by=2)

        self.mock_journal_repo.save.assert_called_once()

    def test_update_devis_no_modifications(self):
        """Test: pas de journal si aucune modification."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis

        dto = DevisUpdateDTO()  # No fields set
        self.use_case.execute(devis_id=1, dto=dto, updated_by=2)

        self.mock_journal_repo.save.assert_not_called()

    def test_update_devis_en_negociation_modifiable(self):
        """Test: un devis en negociation est modifiable."""
        devis = _make_devis(statut=StatutDevis.EN_NEGOCIATION)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = DevisUpdateDTO(notes="Note de negociation")
        result = self.use_case.execute(devis_id=1, dto=dto, updated_by=1)

        assert isinstance(result, DevisDTO)


class TestGetDevisUseCase:
    """Tests pour le use case de recuperation de devis."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_debourse_repo = Mock(spec=DebourseDetailRepository)
        self.use_case = GetDevisUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            ligne_repository=self.mock_ligne_repo,
            debourse_repository=self.mock_debourse_repo,
        )

    def test_get_devis_success_empty(self):
        """Test: recuperation d'un devis sans lots."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []

        result = self.use_case.execute(devis_id=1)

        assert isinstance(result, DevisDetailDTO)
        assert result.id == 1
        assert result.numero == "DEV-2026-001"
        assert result.lots == []

    def test_get_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError) as exc_info:
            self.use_case.execute(devis_id=999)
        assert exc_info.value.devis_id == 999

    def test_get_devis_with_lots_and_lignes(self):
        """Test: recuperation avec lots, lignes et debourses."""
        devis = _make_devis()
        lot = LotDevis(id=10, devis_id=1, code_lot="LOT-001", libelle="Gros oeuvre")
        ligne = LigneDevis(id=100, lot_devis_id=10, libelle="Beton", quantite=Decimal("10"), prix_unitaire_ht=Decimal("50"))
        debourse = DebourseDetail(id=1000, ligne_devis_id=100, libelle="Ciment", quantite=Decimal("5"), prix_unitaire=Decimal("12"))

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = [lot]
        self.mock_ligne_repo.find_by_lot.return_value = [ligne]
        self.mock_debourse_repo.find_by_ligne.return_value = [debourse]

        result = self.use_case.execute(devis_id=1)

        assert len(result.lots) == 1
        assert len(result.lots[0].lignes) == 1
        assert len(result.lots[0].lignes[0].debourses) == 1


class TestListDevisUseCase:
    """Tests pour le use case de listage des devis."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.use_case = ListDevisUseCase(
            devis_repository=self.mock_devis_repo,
        )

    def test_list_devis_success(self):
        """Test: listage avec pagination."""
        devis_list = [_make_devis(id=i, numero=f"DEV-{i:03d}") for i in range(1, 4)]
        self.mock_devis_repo.find_all.return_value = devis_list
        self.mock_devis_repo.count.return_value = 3

        result = self.use_case.execute(limit=10, offset=0)

        assert isinstance(result, DevisListDTO)
        assert len(result.items) == 3
        assert result.total == 3
        assert result.limit == 10
        assert result.offset == 0

    def test_list_devis_empty(self):
        """Test: listage vide."""
        self.mock_devis_repo.find_all.return_value = []
        self.mock_devis_repo.count.return_value = 0

        result = self.use_case.execute()

        assert len(result.items) == 0
        assert result.total == 0

    def test_list_devis_default_pagination(self):
        """Test: pagination par defaut (limit=100, offset=0)."""
        self.mock_devis_repo.find_all.return_value = []
        self.mock_devis_repo.count.return_value = 0

        self.use_case.execute()

        self.mock_devis_repo.find_all.assert_called_once_with(limit=100, offset=0)


class TestDeleteDevisUseCase:
    """Tests pour le use case de suppression de devis."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = DeleteDevisUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_delete_devis_brouillon_success(self):
        """Test: suppression d'un devis en brouillon."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(devis_id=1, deleted_by=1)

        self.mock_devis_repo.delete.assert_called_once_with(1, deleted_by=1)
        self.mock_journal_repo.save.assert_called_once()

    def test_delete_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, deleted_by=1)

    def test_delete_devis_envoye_interdit(self):
        """Test: erreur si devis en statut envoye."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(DevisNotModifiableError):
            self.use_case.execute(devis_id=1, deleted_by=1)

    def test_delete_devis_accepte_interdit(self):
        """Test: erreur si devis en statut accepte."""
        devis = _make_devis(statut=StatutDevis.ACCEPTE)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(DevisNotModifiableError):
            self.use_case.execute(devis_id=1, deleted_by=1)

    def test_delete_devis_journal_entry(self):
        """Test: une entree de journal est creee lors de la suppression."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(devis_id=1, deleted_by=2)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert journal_call.action == "suppression"
        assert journal_call.auteur_id == 2
