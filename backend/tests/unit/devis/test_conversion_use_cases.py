"""Tests unitaires pour les Use Cases de conversion devis -> chantier.

DEV-16: Conversion en chantier.
Couche Application - conversion_use_cases.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch

from modules.devis.domain.entities.devis import Devis, DevisValidationError
from modules.devis.domain.entities.lot_devis import LotDevis
from modules.devis.domain.entities.signature_devis import SignatureDevis
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.value_objects.type_signature import TypeSignature
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.lot_devis_repository import LotDevisRepository
from modules.devis.domain.repositories.signature_devis_repository import SignatureDevisRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError
from modules.devis.application.use_cases.conversion_use_cases import (
    ConvertirDevisUseCase,
    GetConversionInfoUseCase,
    DevisNonConvertibleError,
    DevisDejaConvertiError,
)
from modules.devis.application.dtos.conversion_dtos import (
    ConversionDevisDTO,
    ConversionInfoDTO,
)


# Hash SHA-512 valide
VALID_SHA512 = "a" * 128


def _make_devis(**kwargs):
    """Cree un devis valide avec valeurs par defaut."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "client_adresse": "12 rue de la Paix, 75001 Paris",
        "client_email": "greg@construction.fr",
        "objet": "Renovation bureau",
        "statut": StatutDevis.ACCEPTE,
        "date_creation": date(2026, 1, 15),
        "montant_total_ht": Decimal("50000"),
        "montant_total_ttc": Decimal("60000"),
        "retenue_garantie_pct": Decimal("5"),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


def _make_lot(**kwargs):
    """Cree un lot de devis valide."""
    defaults = {
        "id": 1,
        "devis_id": 1,
        "code_lot": "LOT-01",
        "libelle": "Gros oeuvre",
        "ordre": 1,
        "montant_debourse_ht": Decimal("20000"),
        "montant_vente_ht": Decimal("30000"),
        "montant_vente_ttc": Decimal("36000"),
    }
    defaults.update(kwargs)
    return LotDevis(**defaults)


def _make_signature(**kwargs):
    """Cree une signature valide."""
    defaults = {
        "id": 1,
        "devis_id": 1,
        "type_signature": TypeSignature.DESSIN_TACTILE,
        "signataire_nom": "Jean Dupont",
        "signataire_email": "jean@dupont.fr",
        "signature_data": "data:image/png;base64,FAKE",
        "ip_adresse": "192.168.1.100",
        "user_agent": "Mozilla/5.0 Chrome/120",
        "horodatage": datetime(2026, 1, 20, 14, 30, 0),
        "hash_document": VALID_SHA512,
        "valide": True,
    }
    defaults.update(kwargs)
    return SignatureDevis(**defaults)


# ─────────────────────────────────────────────────────────────────────────────
# Tests ConvertirDevisUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestConvertirDevisUseCase:
    """Tests pour le use case de conversion devis -> chantier."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_signature_repo = Mock(spec=SignatureDevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = ConvertirDevisUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            journal_repository=self.mock_journal_repo,
            signature_repository=self.mock_signature_repo,
        )

    def test_convertir_success(self):
        """Test: conversion reussie d'un devis accepte et signe."""
        devis = _make_devis(statut=StatutDevis.ACCEPTE)
        lots = [_make_lot()]
        signature = _make_signature()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = lots
        self.mock_signature_repo.find_by_devis_id.return_value = signature
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, converted_by=1, chantier_id=42)

        assert isinstance(result, ConversionDevisDTO)
        assert result.devis_id == 1
        assert result.client_nom == "Greg Construction"
        assert len(result.lots) == 1
        assert result.converti is True
        self.mock_devis_repo.save.assert_called_once()
        self.mock_journal_repo.save.assert_called_once()

    def test_convertir_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, converted_by=1)

    def test_convertir_statut_non_accepte(self):
        """Test: erreur si devis pas en statut accepte."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(DevisNonConvertibleError):
            self.use_case.execute(devis_id=1, converted_by=1)

    def test_convertir_deja_converti(self):
        """Test: erreur si devis deja converti."""
        devis = _make_devis(
            statut=StatutDevis.ACCEPTE,
            converti_en_chantier_id=42,
        )
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(DevisDejaConvertiError):
            self.use_case.execute(devis_id=1, converted_by=1)

    def test_convertir_multiple_lots(self):
        """Test: conversion avec plusieurs lots."""
        devis = _make_devis(statut=StatutDevis.ACCEPTE)
        lots = [
            _make_lot(id=1, code_lot="LOT-01", libelle="Gros oeuvre"),
            _make_lot(id=2, code_lot="LOT-02", libelle="Electricite"),
            _make_lot(id=3, code_lot="LOT-03", libelle="Plomberie"),
        ]
        signature = _make_signature()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = lots
        self.mock_signature_repo.find_by_devis_id.return_value = signature
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, converted_by=1, chantier_id=100)

        assert len(result.lots) == 3

    def test_convertir_sans_signature(self):
        """Test: erreur si devis pas signe."""
        devis = _make_devis(statut=StatutDevis.ACCEPTE)

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = None

        with pytest.raises(DevisNonConvertibleError):
            self.use_case.execute(devis_id=1, converted_by=1)

    def test_convertir_avec_event_publisher(self):
        """Test: l'event publisher est appele lors de la conversion."""
        mock_publisher = Mock()
        use_case = ConvertirDevisUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            journal_repository=self.mock_journal_repo,
            signature_repository=self.mock_signature_repo,
            event_publisher=mock_publisher,
        )

        devis = _make_devis(statut=StatutDevis.ACCEPTE)
        lots = [_make_lot()]
        signature = _make_signature()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = lots
        self.mock_signature_repo.find_by_devis_id.return_value = signature
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        use_case.execute(devis_id=1, converted_by=1, chantier_id=42)

        mock_publisher.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# Tests GetConversionInfoUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestGetConversionInfoUseCase:
    """Tests pour le use case d'info de conversion."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_signature_repo = Mock(spec=SignatureDevisRepository)
        self.use_case = GetConversionInfoUseCase(
            devis_repository=self.mock_devis_repo,
            signature_repository=self.mock_signature_repo,
        )

    def test_info_conversion_possible(self):
        """Test: conversion possible pour un devis accepte et signe."""
        devis = _make_devis(statut=StatutDevis.ACCEPTE)
        signature = _make_signature()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = signature

        result = self.use_case.execute(devis_id=1)

        assert isinstance(result, ConversionInfoDTO)
        assert result.conversion_possible is True
        assert result.est_accepte is True
        assert result.est_signe is True
        assert result.deja_converti is False
        assert len(result.pre_requis_manquants) == 0

    def test_info_conversion_non_accepte(self):
        """Test: pre-requis manquant si pas en statut accepte."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = None

        result = self.use_case.execute(devis_id=1)

        assert result.conversion_possible is False
        assert result.est_accepte is False
        assert len(result.pre_requis_manquants) > 0

    def test_info_conversion_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999)

    def test_info_conversion_deja_converti(self):
        """Test: info correcte si deja converti."""
        devis = _make_devis(
            statut=StatutDevis.ACCEPTE,
            converti_en_chantier_id=42,
        )
        signature = _make_signature()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = signature

        result = self.use_case.execute(devis_id=1)

        assert result.deja_converti is True
        assert result.converti_en_chantier_id == 42
        assert result.conversion_possible is False

    def test_info_conversion_non_signe(self):
        """Test: pre-requis manquant si pas signe."""
        devis = _make_devis(statut=StatutDevis.ACCEPTE)

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = None

        result = self.use_case.execute(devis_id=1)

        assert result.est_signe is False
