"""Tests unitaires pour ConvertirDevisEnChantierUseCase.

DEV-16: Conversion devis accepte en chantier avec budget et lots budgetaires.
Couche Application - convertir_devis_en_chantier_use_case.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch, call, ANY

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.entities.lot_devis import LotDevis
from modules.devis.domain.entities.journal_devis import JournalDevis
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.lot_devis_repository import LotDevisRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.domain.repositories.signature_devis_repository import SignatureDevisRepository

from shared.application.ports.chantier_creation_port import (
    ChantierCreationPort,
    ConversionChantierResult,
)

from modules.devis.application.use_cases.convertir_devis_en_chantier_use_case import (
    ConvertirDevisEnChantierUseCase,
    DevisNonConvertibleError,
    DevisDejaConvertiError,
    ConversionError,
)
from modules.devis.application.dtos.convertir_devis_dto import (
    ConvertirDevisOptionsDTO,
    ConvertirDevisResultDTO,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _make_devis(**kwargs) -> Devis:
    """Cree un devis valide avec valeurs par defaut (statut ACCEPTE)."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "client_adresse": "12 rue des Lilas, 73000 Chambery",
        "objet": "Renovation bureau principal",
        "statut": StatutDevis.ACCEPTE,
        "date_creation": date(2026, 1, 15),
        "montant_total_ht": Decimal("50000"),
        "montant_total_ttc": Decimal("60000"),
        "retenue_garantie_pct": Decimal("5"),
        "conducteur_id": 10,
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


def _make_lot_devis(devis_id: int = 1, **kwargs) -> LotDevis:
    """Cree un lot de devis valide avec valeurs par defaut."""
    defaults = {
        "id": None,
        "devis_id": devis_id,
        "code_lot": "LOT-01",
        "libelle": "Gros oeuvre",
        "ordre": 1,
        "montant_debourse_ht": Decimal("15000"),
        "montant_vente_ht": Decimal("20000"),
        "montant_vente_ttc": Decimal("24000"),
    }
    defaults.update(kwargs)
    return LotDevis(**defaults)


def _make_conversion_result(**kwargs) -> ConversionChantierResult:
    """Cree un resultat de conversion par defaut."""
    defaults = {
        "chantier_id": 100,
        "code_chantier": "A042",
        "budget_id": 200,
        "nb_lots_transferes": 2,
    }
    defaults.update(kwargs)
    return ConversionChantierResult(**defaults)


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestConvertirDevisEnChantierUseCase:
    """Tests pour le use case de conversion devis -> chantier."""

    def setup_method(self):
        """Configuration avant chaque test : mocks des repositories + port."""
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_devis_repo = Mock(spec=LotDevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.mock_chantier_creation_port = Mock(spec=ChantierCreationPort)
        self.mock_signature_repo = Mock(spec=SignatureDevisRepository)

        # Par defaut, le devis est signe (happy path)
        self.mock_signature_repo.find_by_devis_id.return_value = Mock()

        self.use_case = ConvertirDevisEnChantierUseCase(
            devis_repo=self.mock_devis_repo,
            lot_devis_repo=self.mock_lot_devis_repo,
            journal_repo=self.mock_journal_repo,
            chantier_creation_port=self.mock_chantier_creation_port,
            signature_repo=self.mock_signature_repo,
        )

    # ─────────────────────────────────────────────────────────────────────
    # Happy path
    # ─────────────────────────────────────────────────────────────────────

    def test_conversion_success_happy_path(self):
        """Test: conversion reussie - devis accepte avec lots cree chantier + budget + lots."""
        devis = _make_devis()
        lot1 = _make_lot_devis(id=10, devis_id=1, code_lot="LOT-01", libelle="Gros oeuvre", ordre=1, montant_vente_ht=Decimal("30000"))
        lot2 = _make_lot_devis(id=11, devis_id=1, code_lot="LOT-02", libelle="Electricite", ordre=2, montant_vente_ht=Decimal("20000"))
        conversion_result = _make_conversion_result(nb_lots_transferes=2)

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot1, lot2]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        result = self.use_case.execute(devis_id=1, current_user_id=5)

        # Assert result DTO
        assert isinstance(result, ConvertirDevisResultDTO)
        assert result.chantier_id == 100
        assert result.code_chantier == "A042"
        assert result.budget_id == 200
        assert result.nb_lots_transferes == 2
        assert result.montant_total_ht == Decimal("50000")
        assert result.devis_id == 1
        assert result.devis_numero == "DEV-2026-001"

        # Assert repo calls
        self.mock_devis_repo.find_by_id.assert_called_once_with(1)
        self.mock_lot_devis_repo.find_by_devis.assert_called_once_with(1)
        self.mock_chantier_creation_port.create_chantier_from_devis.assert_called_once()
        # Devis archived (convertir + save)
        self.mock_devis_repo.save.assert_called_once_with(devis)
        assert devis.statut == StatutDevis.CONVERTI
        assert devis.chantier_ref == "100"

    def test_conversion_success_single_lot(self):
        """Test: conversion reussie avec un seul lot."""
        devis = _make_devis()
        lot = _make_lot_devis(id=10, montant_vente_ht=Decimal("50000"))
        conversion_result = _make_conversion_result(nb_lots_transferes=1)

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        result = self.use_case.execute(devis_id=1, current_user_id=5)

        assert result.nb_lots_transferes == 1

    def test_conversion_success_with_options(self):
        """Test: conversion reussie avec options personnalisees."""
        devis = _make_devis()
        lot = _make_lot_devis(id=10)
        conversion_result = _make_conversion_result()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        options = ConvertirDevisOptionsDTO(notify_client=True, notify_team=False)
        result = self.use_case.execute(devis_id=1, current_user_id=5, options=options)

        assert result.chantier_id == 100

    # ─────────────────────────────────────────────────────────────────────
    # Audit trail (DEFAUT 2)
    # ─────────────────────────────────────────────────────────────────────

    def test_journal_entry_created_on_success(self):
        """Test: une entree journal est creee apres conversion reussie."""
        devis = _make_devis()
        lot = _make_lot_devis(id=10)
        conversion_result = _make_conversion_result(nb_lots_transferes=1)

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        self.use_case.execute(devis_id=1, current_user_id=5)

        # Verify journal_repo.save was called
        self.mock_journal_repo.save.assert_called_once()
        journal_entry = self.mock_journal_repo.save.call_args[0][0]
        assert isinstance(journal_entry, JournalDevis)
        assert journal_entry.devis_id == 1
        assert journal_entry.action == "conversion"
        assert journal_entry.auteur_id == 5
        assert journal_entry.details_json["chantier_id"] == 100
        assert journal_entry.details_json["code_chantier"] == "A042"
        assert journal_entry.details_json["budget_id"] == 200
        assert journal_entry.details_json["nb_lots_transferes"] == 1

    def test_journal_not_created_on_failure(self):
        """Test: pas d'entree journal si la conversion echoue."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNonConvertibleError):
            self.use_case.execute(devis_id=999, current_user_id=5)

        self.mock_journal_repo.save.assert_not_called()

    # ─────────────────────────────────────────────────────────────────────
    # Devis introuvable
    # ─────────────────────────────────────────────────────────────────────

    def test_devis_introuvable_raises_non_convertible(self):
        """Test: echec si devis n'existe pas -> DevisNonConvertibleError."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNonConvertibleError, match="n'existe pas"):
            self.use_case.execute(devis_id=999, current_user_id=5)

        # Aucune creation ne doit avoir eu lieu
        self.mock_chantier_creation_port.create_chantier_from_devis.assert_not_called()

    # ─────────────────────────────────────────────────────────────────────
    # Devis pas en statut ACCEPTE
    # ─────────────────────────────────────────────────────────────────────

    def test_devis_brouillon_raises_non_convertible(self):
        """Test: echec si devis en brouillon -> DevisNonConvertibleError."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(DevisNonConvertibleError, match="accepte"):
            self.use_case.execute(devis_id=1, current_user_id=5)

    def test_devis_envoye_raises_non_convertible(self):
        """Test: echec si devis en statut envoye -> DevisNonConvertibleError."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(DevisNonConvertibleError, match="accepte"):
            self.use_case.execute(devis_id=1, current_user_id=5)

    def test_devis_refuse_raises_non_convertible(self):
        """Test: echec si devis refuse -> DevisNonConvertibleError."""
        devis = _make_devis(statut=StatutDevis.REFUSE)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(DevisNonConvertibleError, match="accepte"):
            self.use_case.execute(devis_id=1, current_user_id=5)

    def test_devis_en_negociation_raises_non_convertible(self):
        """Test: echec si devis en negociation -> DevisNonConvertibleError."""
        devis = _make_devis(statut=StatutDevis.EN_NEGOCIATION)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(DevisNonConvertibleError, match="accepte"):
            self.use_case.execute(devis_id=1, current_user_id=5)

    # ─────────────────────────────────────────────────────────────────────
    # Devis deja converti
    # ─────────────────────────────────────────────────────────────────────

    def test_devis_deja_converti_statut_converti(self):
        """Test: echec si devis deja en statut CONVERTI -> DevisDejaConvertiError."""
        devis = _make_devis(statut=StatutDevis.CONVERTI, chantier_ref="50")
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(DevisDejaConvertiError, match="deja ete converti"):
            self.use_case.execute(devis_id=1, current_user_id=5)

    def test_devis_deja_converti_chantier_ref_present(self):
        """Test: echec si chantier_ref deja renseigne -> DevisDejaConvertiError."""
        devis = _make_devis(chantier_ref="42")
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(DevisDejaConvertiError) as exc_info:
            self.use_case.execute(devis_id=1, current_user_id=5)

        assert exc_info.value.devis_id == 1
        assert exc_info.value.chantier_ref == "42"

    # ─────────────────────────────────────────────────────────────────────
    # Devis non signe
    # ─────────────────────────────────────────────────────────────────────

    def test_devis_non_signe_raises_non_convertible(self):
        """Test: echec si devis accepte mais non signe -> DevisNonConvertibleError."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = None

        with pytest.raises(DevisNonConvertibleError, match="signe"):
            self.use_case.execute(devis_id=1, current_user_id=5)

        # Aucune creation ne doit avoir eu lieu
        self.mock_chantier_creation_port.create_chantier_from_devis.assert_not_called()

    # ─────────────────────────────────────────────────────────────────────
    # Montant invalide
    # ─────────────────────────────────────────────────────────────────────

    def test_montant_zero_raises_non_convertible(self):
        """Test: echec si montant_total_ht = 0 -> DevisNonConvertibleError."""
        devis = _make_devis(montant_total_ht=Decimal("0"))
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(DevisNonConvertibleError, match="superieur a 0"):
            self.use_case.execute(devis_id=1, current_user_id=5)

    def test_montant_negatif_raises_non_convertible(self):
        """Test: echec si montant_total_ht < 0 -> DevisNonConvertibleError."""
        devis = _make_devis(montant_total_ht=Decimal("-100"))
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(DevisNonConvertibleError, match="superieur a 0"):
            self.use_case.execute(devis_id=1, current_user_id=5)

    # ─────────────────────────────────────────────────────────────────────
    # Aucun lot
    # ─────────────────────────────────────────────────────────────────────

    def test_aucun_lot_raises_non_convertible(self):
        """Test: echec si devis n'a aucun lot -> DevisNonConvertibleError."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = []

        with pytest.raises(DevisNonConvertibleError, match="au moins un lot"):
            self.use_case.execute(devis_id=1, current_user_id=5)

    def test_lots_tous_supprimes_raises_non_convertible(self):
        """Test: echec si tous les lots sont supprimes (soft delete)."""
        devis = _make_devis()
        lot_supprime = _make_lot_devis(
            id=10,
            deleted_at=datetime(2026, 1, 20, 12, 0, 0),
            deleted_by=5,
        )
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot_supprime]

        with pytest.raises(DevisNonConvertibleError, match="au moins un lot"):
            self.use_case.execute(devis_id=1, current_user_id=5)

    # ─────────────────────────────────────────────────────────────────────
    # Chantier creation data mapping
    # ─────────────────────────────────────────────────────────────────────

    def test_chantier_data_with_objet(self):
        """Test: le nom du chantier est l'objet du devis quand il existe."""
        devis = _make_devis(objet="Construction hangar")
        lot = _make_lot_devis(id=10)
        conversion_result = _make_conversion_result()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        self.use_case.execute(devis_id=1, current_user_id=5)

        call_args = self.mock_chantier_creation_port.create_chantier_from_devis.call_args
        chantier_data = call_args.kwargs["chantier_data"]
        assert chantier_data.nom == "Construction hangar"

    def test_chantier_data_without_objet(self):
        """Test: le nom du chantier utilise client_nom si objet absent."""
        devis = _make_devis(objet=None)
        lot = _make_lot_devis(id=10)
        conversion_result = _make_conversion_result()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        self.use_case.execute(devis_id=1, current_user_id=5)

        call_args = self.mock_chantier_creation_port.create_chantier_from_devis.call_args
        chantier_data = call_args.kwargs["chantier_data"]
        assert "Greg Construction" in chantier_data.nom

    def test_chantier_data_with_conducteur(self):
        """Test: le conducteur du devis est assigne au chantier."""
        devis = _make_devis(conducteur_id=42)
        lot = _make_lot_devis(id=10)
        conversion_result = _make_conversion_result()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        self.use_case.execute(devis_id=1, current_user_id=5)

        call_args = self.mock_chantier_creation_port.create_chantier_from_devis.call_args
        chantier_data = call_args.kwargs["chantier_data"]
        assert 42 in chantier_data.conducteur_ids

    def test_chantier_data_without_conducteur(self):
        """Test: chantier sans conducteur si devis n'en a pas."""
        devis = _make_devis(conducteur_id=None)
        lot = _make_lot_devis(id=10)
        conversion_result = _make_conversion_result()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        self.use_case.execute(devis_id=1, current_user_id=5)

        call_args = self.mock_chantier_creation_port.create_chantier_from_devis.call_args
        chantier_data = call_args.kwargs["chantier_data"]
        assert chantier_data.conducteur_ids == []

    def test_chantier_adresse_from_devis(self):
        """Test: l'adresse du chantier vient de l'adresse client du devis."""
        devis = _make_devis(client_adresse="99 avenue des Alpes, 38000 Grenoble")
        lot = _make_lot_devis(id=10)
        conversion_result = _make_conversion_result()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        self.use_case.execute(devis_id=1, current_user_id=5)

        call_args = self.mock_chantier_creation_port.create_chantier_from_devis.call_args
        chantier_data = call_args.kwargs["chantier_data"]
        assert chantier_data.adresse == "99 avenue des Alpes, 38000 Grenoble"

    def test_chantier_adresse_default_when_missing(self):
        """Test: adresse par defaut si client_adresse absent."""
        devis = _make_devis(client_adresse=None)
        lot = _make_lot_devis(id=10)
        conversion_result = _make_conversion_result()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        self.use_case.execute(devis_id=1, current_user_id=5)

        call_args = self.mock_chantier_creation_port.create_chantier_from_devis.call_args
        chantier_data = call_args.kwargs["chantier_data"]
        assert chantier_data.adresse == "Adresse a definir"

    # ─────────────────────────────────────────────────────────────────────
    # Budget creation data
    # ─────────────────────────────────────────────────────────────────────

    def test_budget_data_with_correct_values(self):
        """Test: le budget est cree avec les montants du devis."""
        devis = _make_devis(
            montant_total_ht=Decimal("75000"),
            retenue_garantie_pct=Decimal("10"),
        )
        lot = _make_lot_devis(id=10)
        conversion_result = _make_conversion_result()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        self.use_case.execute(devis_id=1, current_user_id=5)

        call_args = self.mock_chantier_creation_port.create_chantier_from_devis.call_args
        budget_data = call_args.kwargs["budget_data"]
        assert budget_data.montant_initial_ht == Decimal("75000")
        assert budget_data.retenue_garantie_pct == Decimal("10")
        assert budget_data.seuil_alerte_pct == Decimal("80")
        assert budget_data.seuil_validation_achat == Decimal("5000")

    def test_budget_data_includes_devis_id(self):
        """Test GAP #6: budget_data transmet devis_id pour tracabilite."""
        devis = _make_devis(id=42)
        lot = _make_lot_devis(id=10, devis_id=42)
        conversion_result = _make_conversion_result()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        self.use_case.execute(devis_id=42, current_user_id=5)

        call_args = self.mock_chantier_creation_port.create_chantier_from_devis.call_args
        budget_data = call_args.kwargs["budget_data"]
        assert budget_data.devis_id == 42

    # ─────────────────────────────────────────────────────────────────────
    # Lots data mapping
    # ─────────────────────────────────────────────────────────────────────

    def test_lots_data_mapping_correct(self):
        """Test: les lots budgetaires transferent debourse et vente du devis."""
        devis = _make_devis()
        lot1 = _make_lot_devis(
            id=10,
            code_lot="GOE",
            libelle="Gros oeuvre",
            ordre=1,
            montant_debourse_ht=Decimal("22000"),
            montant_vente_ht=Decimal("30000"),
        )
        lot2 = _make_lot_devis(
            id=11,
            code_lot="ELEC",
            libelle="Electricite",
            ordre=2,
            montant_debourse_ht=Decimal("14000"),
            montant_vente_ht=Decimal("20000"),
        )
        conversion_result = _make_conversion_result(nb_lots_transferes=2)

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot1, lot2]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        self.use_case.execute(devis_id=1, current_user_id=5)

        call_args = self.mock_chantier_creation_port.create_chantier_from_devis.call_args
        lots_data = call_args.kwargs["lots_data"]
        assert len(lots_data) == 2

        # Premier lot - prix_unitaire_ht = debourse, prix_vente_ht = vente
        assert lots_data[0].code_lot == "GOE"
        assert lots_data[0].libelle == "Gros oeuvre"
        assert lots_data[0].unite == "forfait"
        assert lots_data[0].quantite_prevue == Decimal("1")
        assert lots_data[0].prix_unitaire_ht == Decimal("22000")
        assert lots_data[0].ordre == 1
        assert lots_data[0].prix_vente_ht == Decimal("30000")

        # Deuxieme lot
        assert lots_data[1].code_lot == "ELEC"
        assert lots_data[1].libelle == "Electricite"
        assert lots_data[1].prix_unitaire_ht == Decimal("14000")
        assert lots_data[1].prix_vente_ht == Decimal("20000")
        assert lots_data[1].ordre == 2

    def test_lots_data_fallback_debourse_zero(self):
        """Test: si montant_debourse_ht est 0, prix_unitaire_ht utilise montant_vente_ht."""
        devis = _make_devis()
        lot = _make_lot_devis(
            id=10,
            code_lot="GOE",
            libelle="Gros oeuvre",
            ordre=1,
            montant_debourse_ht=Decimal("0"),
            montant_vente_ht=Decimal("30000"),
        )
        conversion_result = _make_conversion_result(nb_lots_transferes=1)

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        self.use_case.execute(devis_id=1, current_user_id=5)

        call_args = self.mock_chantier_creation_port.create_chantier_from_devis.call_args
        lots_data = call_args.kwargs["lots_data"]
        assert lots_data[0].prix_unitaire_ht == Decimal("30000")
        assert lots_data[0].prix_vente_ht == Decimal("30000")

    def test_plusieurs_lots_count_correct(self):
        """Test: le nombre de lots transferes correspond au resultat du port."""
        devis = _make_devis()
        lots = [
            _make_lot_devis(id=i, code_lot=f"LOT-{i:02d}", libelle=f"Lot {i}", ordre=i, montant_vente_ht=Decimal("10000"))
            for i in range(1, 6)
        ]
        conversion_result = _make_conversion_result(nb_lots_transferes=5)

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = lots
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        result = self.use_case.execute(devis_id=1, current_user_id=5)

        assert result.nb_lots_transferes == 5

    # ─────────────────────────────────────────────────────────────────────
    # Archivage devis
    # ─────────────────────────────────────────────────────────────────────

    def test_devis_archived_after_conversion(self):
        """Test: le devis passe en statut CONVERTI avec chantier_ref."""
        devis = _make_devis()
        lot = _make_lot_devis(id=10)
        conversion_result = _make_conversion_result(chantier_id=55)

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        self.use_case.execute(devis_id=1, current_user_id=5)

        assert devis.statut == StatutDevis.CONVERTI
        assert devis.chantier_ref == "55"
        self.mock_devis_repo.save.assert_called_once_with(devis)

    # ─────────────────────────────────────────────────────────────────────
    # Lots avec melange supprimes / actifs
    # ─────────────────────────────────────────────────────────────────────

    def test_lots_supprimes_are_filtered_out(self):
        """Test: les lots supprimes (soft delete) sont ignores lors de la conversion."""
        devis = _make_devis()
        lot_actif = _make_lot_devis(id=10, code_lot="LOT-01", libelle="Actif", ordre=1)
        lot_supprime = _make_lot_devis(
            id=11,
            code_lot="LOT-02",
            libelle="Supprime",
            ordre=2,
            deleted_at=datetime(2026, 1, 20),
            deleted_by=5,
        )
        conversion_result = _make_conversion_result(nb_lots_transferes=1)

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot_actif, lot_supprime]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        result = self.use_case.execute(devis_id=1, current_user_id=5)

        # Only 1 lot should be passed to the port (the non-deleted one)
        call_args = self.mock_chantier_creation_port.create_chantier_from_devis.call_args
        lots_data = call_args.kwargs["lots_data"]
        assert len(lots_data) == 1
        assert lots_data[0].code_lot == "LOT-01"

    # ─────────────────────────────────────────────────────────────────────
    # Erreur technique -> ConversionError
    # ─────────────────────────────────────────────────────────────────────

    def test_exception_technique_raises_conversion_error(self):
        """Test: une exception inattendue est wrappee en ConversionError."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [_make_lot_devis(id=10)]
        self.mock_chantier_creation_port.create_chantier_from_devis.side_effect = RuntimeError("DB down")

        with pytest.raises(ConversionError, match="Erreur lors de la conversion"):
            self.use_case.execute(devis_id=1, current_user_id=5)

    def test_conversion_error_preserves_original_cause(self):
        """Test: ConversionError conserve l'exception d'origine dans __cause__."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [_make_lot_devis(id=10)]
        original_error = RuntimeError("connection refused")
        self.mock_chantier_creation_port.create_chantier_from_devis.side_effect = original_error

        with pytest.raises(ConversionError) as exc_info:
            self.use_case.execute(devis_id=1, current_user_id=5)

        assert exc_info.value.__cause__ is original_error

    def test_metier_exceptions_not_wrapped(self):
        """Test: DevisNonConvertibleError et DevisDejaConvertiError ne sont pas wrappees."""
        # DevisNonConvertibleError (devis introuvable)
        self.mock_devis_repo.find_by_id.return_value = None
        with pytest.raises(DevisNonConvertibleError):
            self.use_case.execute(devis_id=1, current_user_id=5)

    # ─────────────────────────────────────────────────────────────────────
    # Result DTO
    # ─────────────────────────────────────────────────────────────────────

    def test_result_dto_to_dict(self):
        """Test: le DTO de resultat se serialise correctement."""
        devis = _make_devis()
        lot = _make_lot_devis(id=10)
        conversion_result = _make_conversion_result(nb_lots_transferes=1)

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_devis_repo.find_by_devis.return_value = [lot]
        self.mock_chantier_creation_port.create_chantier_from_devis.return_value = conversion_result

        result = self.use_case.execute(devis_id=1, current_user_id=5)
        result_dict = result.to_dict()

        assert result_dict["chantier_id"] == 100
        assert result_dict["code_chantier"] == "A042"
        assert result_dict["budget_id"] == 200
        assert result_dict["nb_lots_transferes"] == 1
        assert result_dict["devis_id"] == 1
        assert result_dict["devis_numero"] == "DEV-2026-001"
