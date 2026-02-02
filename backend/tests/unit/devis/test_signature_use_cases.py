"""Tests unitaires pour les Use Cases de signature electronique.

DEV-14: Signature electronique client.
Couche Application - signature_use_cases.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.entities.signature_devis import (
    SignatureDevis,
    SignatureDevisValidationError,
)
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.value_objects.type_signature import TypeSignature
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.signature_devis_repository import SignatureDevisRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError
from modules.devis.application.use_cases.signature_use_cases import (
    SignerDevisUseCase,
    GetSignatureUseCase,
    RevoquerSignatureUseCase,
    VerifierSignatureUseCase,
    SignatureNotFoundError,
    DevisNonSignableError,
    DevisDejaSigneError,
)
from modules.devis.application.dtos.signature_dtos import (
    SignatureCreateDTO,
    SignatureDTO,
    VerificationSignatureDTO,
)


# Hash SHA-512 valide (128 hex chars)
VALID_SHA512 = "a" * 128


def _make_devis(**kwargs):
    """Cree un devis valide avec valeurs par defaut."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "statut": StatutDevis.ENVOYE,
        "date_creation": date(2026, 1, 15),
        "montant_total_ht": Decimal("10000"),
        "montant_total_ttc": Decimal("12000"),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


def _make_signature(**kwargs):
    """Cree une signature valide avec valeurs par defaut."""
    defaults = {
        "id": 1,
        "devis_id": 1,
        "type_signature": TypeSignature.DESSIN_TACTILE,
        "signataire_nom": "Jean Dupont",
        "signataire_email": "jean@dupont.fr",
        "signature_data": "data:image/png;base64,FAKE",
        "ip_adresse": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120",
        "horodatage": datetime(2026, 1, 20, 14, 30, 0),
        "hash_document": VALID_SHA512,
        "valide": True,
        "created_at": datetime(2026, 1, 20, 14, 30, 0),
    }
    defaults.update(kwargs)
    return SignatureDevis(**defaults)


# ─────────────────────────────────────────────────────────────────────────────
# Tests SignerDevisUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestSignerDevisUseCase:
    """Tests pour le use case de signature de devis."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_signature_repo = Mock(spec=SignatureDevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = SignerDevisUseCase(
            devis_repository=self.mock_devis_repo,
            signature_repository=self.mock_signature_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_signer_success(self):
        """Test: signature reussie."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        signature = _make_signature()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = None
        self.mock_signature_repo.save.return_value = signature
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = SignatureCreateDTO(
            type_signature="dessin_tactile",
            signataire_nom="Jean Dupont",
            signataire_email="jean@dupont.fr",
            signature_data="data:image/png;base64,FAKE",
            ip_adresse="192.168.1.100",
            user_agent="Mozilla/5.0",
        )

        result = self.use_case.execute(devis_id=1, dto=dto)

        assert isinstance(result, SignatureDTO)
        assert result.signataire_nom == "Jean Dupont"
        self.mock_signature_repo.save.assert_called_once()
        self.mock_journal_repo.save.assert_called_once()

    def test_signer_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        dto = SignatureCreateDTO(
            type_signature="dessin_tactile",
            signataire_nom="Jean Dupont",
            signataire_email="jean@dupont.fr",
            signature_data="data:image/png;base64,FAKE",
            ip_adresse="192.168.1.100",
            user_agent="Mozilla/5.0",
        )

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, dto=dto)

    def test_signer_devis_deja_signe(self):
        """Test: erreur si devis deja signe."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        signature_existante = _make_signature()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = signature_existante

        dto = SignatureCreateDTO(
            type_signature="dessin_tactile",
            signataire_nom="Jean Dupont",
            signataire_email="jean@dupont.fr",
            signature_data="data:image/png;base64,FAKE",
            ip_adresse="192.168.1.100",
            user_agent="Mozilla/5.0",
        )

        with pytest.raises(DevisDejaSigneError):
            self.use_case.execute(devis_id=1, dto=dto)

    def test_signer_statut_invalide(self):
        """Test: erreur si statut du devis ne permet pas la signature."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = None

        dto = SignatureCreateDTO(
            type_signature="dessin_tactile",
            signataire_nom="Jean Dupont",
            signataire_email="jean@dupont.fr",
            signature_data="data:image/png;base64,FAKE",
            ip_adresse="192.168.1.100",
            user_agent="Mozilla/5.0",
        )

        with pytest.raises(DevisNonSignableError):
            self.use_case.execute(devis_id=1, dto=dto)


# ─────────────────────────────────────────────────────────────────────────────
# Tests GetSignatureUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestGetSignatureUseCase:
    """Tests pour le use case de recuperation de signature."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_signature_repo = Mock(spec=SignatureDevisRepository)
        self.use_case = GetSignatureUseCase(
            devis_repository=self.mock_devis_repo,
            signature_repository=self.mock_signature_repo,
        )

    def test_get_signature_success(self):
        """Test: recuperation reussie."""
        devis = _make_devis()
        signature = _make_signature()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = signature

        result = self.use_case.execute(devis_id=1)

        assert isinstance(result, SignatureDTO)
        assert result.devis_id == 1

    def test_get_signature_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999)

    def test_get_signature_non_signe(self):
        """Test: erreur si devis pas signe."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = None

        with pytest.raises(SignatureNotFoundError):
            self.use_case.execute(devis_id=1)


# ─────────────────────────────────────────────────────────────────────────────
# Tests RevoquerSignatureUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestRevoquerSignatureUseCase:
    """Tests pour le use case de revocation de signature."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_signature_repo = Mock(spec=SignatureDevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = RevoquerSignatureUseCase(
            devis_repository=self.mock_devis_repo,
            signature_repository=self.mock_signature_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_revoquer_success(self):
        """Test: revocation reussie - le devis doit etre en statut accepte."""
        devis = _make_devis(statut=StatutDevis.ACCEPTE)
        signature = _make_signature()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = signature
        self.mock_signature_repo.save.return_value = signature
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(
            devis_id=1, motif="Erreur de signataire", revoque_par=1
        )

        assert isinstance(result, SignatureDTO)
        assert signature.valide is False
        self.mock_signature_repo.save.assert_called_once()
        self.mock_journal_repo.save.assert_called_once()

    def test_revoquer_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, motif="Erreur", revoque_par=1)

    def test_revoquer_sans_signature(self):
        """Test: erreur si pas de signature a revoquer."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = None

        with pytest.raises(SignatureNotFoundError):
            self.use_case.execute(devis_id=1, motif="Erreur", revoque_par=1)

    def test_revoquer_deja_revoquee(self):
        """Test: erreur si signature deja revoquee."""
        devis = _make_devis()
        signature = _make_signature(
            valide=False,
            revoquee_at=datetime.utcnow(),
            revoquee_par=1,
            motif_revocation="Premiere revocation",
        )

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = signature

        with pytest.raises(SignatureDevisValidationError, match="deja revoquee"):
            self.use_case.execute(devis_id=1, motif="Deuxieme tentative", revoque_par=1)


# ─────────────────────────────────────────────────────────────────────────────
# Tests VerifierSignatureUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestVerifierSignatureUseCase:
    """Tests pour le use case de verification de signature."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_signature_repo = Mock(spec=SignatureDevisRepository)
        self.use_case = VerifierSignatureUseCase(
            devis_repository=self.mock_devis_repo,
            signature_repository=self.mock_signature_repo,
        )

    def test_verifier_signature_valide(self):
        """Test: verification d'une signature valide."""
        devis = _make_devis()
        signature = _make_signature()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = signature

        result = self.use_case.execute(devis_id=1)

        assert isinstance(result, VerificationSignatureDTO)
        assert result.est_signee is True

    def test_verifier_pas_signe(self):
        """Test: devis pas encore signe."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = None

        result = self.use_case.execute(devis_id=1)

        assert isinstance(result, VerificationSignatureDTO)
        assert result.est_signee is False
        assert result.est_valide is False

    def test_verifier_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999)

    def test_verifier_signature_revoquee(self):
        """Test: verification d'une signature revoquee."""
        devis = _make_devis()
        signature = _make_signature(
            valide=False,
            revoquee_at=datetime.utcnow(),
            revoquee_par=1,
            motif_revocation="Erreur",
        )

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_signature_repo.find_by_devis_id.return_value = signature

        result = self.use_case.execute(devis_id=1)

        assert result.est_signee is True
        assert result.est_valide is False
