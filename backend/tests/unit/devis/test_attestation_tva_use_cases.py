"""Tests unitaires pour les Use Cases d'attestation TVA.

DEV-23: Generation attestation TVA reglementaire.
Couche Application - attestation_tva_use_cases.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.entities.attestation_tva import (
    AttestationTVA,
    AttestationTVAValidationError,
)
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.value_objects.taux_tva import TauxTVA
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.attestation_tva_repository import AttestationTVARepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError
from modules.devis.application.use_cases.attestation_tva_use_cases import (
    GenererAttestationTVAUseCase,
    GetAttestationTVAUseCase,
    VerifierEligibiliteTVAUseCase,
    TVANonEligibleError,
    AttestationTVADejaExistanteError,
    AttestationTVANotFoundError,
)
from modules.devis.application.dtos.attestation_tva_dtos import (
    AttestationTVACreateDTO,
    AttestationTVADTO,
    EligibiliteTVADTO,
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
        "montant_total_ht": Decimal("10000"),
        "montant_total_ttc": Decimal("11000"),
        "taux_tva_defaut": Decimal("10"),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


def _make_attestation(**kwargs):
    """Cree une attestation TVA valide."""
    defaults = {
        "id": 1,
        "devis_id": 1,
        "type_cerfa": "1300-SD",
        "taux_tva": 10.0,
        "nom_client": "Greg Construction",
        "adresse_client": "12 rue de la Paix, 75001 Paris",
        "adresse_immeuble": "45 avenue Victor Hugo, 75016 Paris",
        "nature_immeuble": "maison",
        "date_construction_plus_2ans": True,
        "description_travaux": "Renovation complete bureau",
        "nature_travaux": "amelioration",
        "atteste_par": "Jean Dupont",
        "generee_at": datetime(2026, 1, 20, 14, 0, 0),
    }
    defaults.update(kwargs)
    return AttestationTVA(**defaults)


# ─────────────────────────────────────────────────────────────────────────────
# Tests GenererAttestationTVAUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestGenererAttestationTVAUseCase:
    """Tests pour la generation d'attestation TVA."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_attestation_repo = Mock(spec=AttestationTVARepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = GenererAttestationTVAUseCase(
            devis_repository=self.mock_devis_repo,
            attestation_repository=self.mock_attestation_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_generer_attestation_10pct_success(self):
        """Test: generation attestation pour taux 10% reussie."""
        devis = _make_devis(taux_tva_defaut=Decimal("10"))
        attestation = _make_attestation()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_attestation_repo.find_by_devis_id.return_value = None
        self.mock_attestation_repo.save.return_value = attestation
        self.mock_journal_repo.save.return_value = Mock()

        dto = AttestationTVACreateDTO(
            nom_client="Greg Construction",
            adresse_client="12 rue de la Paix",
            adresse_immeuble="45 avenue Victor Hugo",
            nature_immeuble="maison",
            date_construction_plus_2ans=True,
            description_travaux="Renovation complete bureau",
            nature_travaux="amelioration",
            atteste_par="Jean Dupont",
        )

        result = self.use_case.execute(devis_id=1, dto=dto, created_by=1)

        assert isinstance(result, AttestationTVADTO)
        assert result.type_cerfa == "1300-SD"
        assert result.taux_tva == 10.0
        self.mock_attestation_repo.save.assert_called_once()
        self.mock_journal_repo.save.assert_called_once()

    def test_generer_attestation_5_5pct_success(self):
        """Test: generation attestation pour taux 5.5% reussie."""
        devis = _make_devis(taux_tva_defaut=Decimal("5.5"))
        attestation = _make_attestation(type_cerfa="1301-SD", taux_tva=5.5)

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_attestation_repo.find_by_devis_id.return_value = None
        self.mock_attestation_repo.save.return_value = attestation
        self.mock_journal_repo.save.return_value = Mock()

        dto = AttestationTVACreateDTO(
            nom_client="Greg Construction",
            adresse_client="12 rue de la Paix",
            adresse_immeuble="45 avenue Victor Hugo",
            description_travaux="Isolation thermique",
            atteste_par="Jean Dupont",
        )

        result = self.use_case.execute(devis_id=1, dto=dto, created_by=1)

        assert result.type_cerfa == "1301-SD"

    def test_generer_attestation_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        dto = AttestationTVACreateDTO(
            nom_client="Test",
            adresse_client="Test",
        )

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, dto=dto, created_by=1)

    def test_generer_attestation_taux_20_non_eligible(self):
        """Test: erreur si taux 20% (pas d'attestation necessaire)."""
        devis = _make_devis(taux_tva_defaut=Decimal("20"))
        self.mock_devis_repo.find_by_id.return_value = devis

        dto = AttestationTVACreateDTO(
            nom_client="Test",
            adresse_client="Test",
        )

        with pytest.raises(TVANonEligibleError):
            self.use_case.execute(devis_id=1, dto=dto, created_by=1)

    def test_generer_attestation_deja_existante(self):
        """Test: erreur si attestation deja generee."""
        devis = _make_devis(taux_tva_defaut=Decimal("10"))
        attestation_existante = _make_attestation()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_attestation_repo.find_by_devis_id.return_value = attestation_existante

        dto = AttestationTVACreateDTO(
            nom_client="Test",
            adresse_client="Test",
        )

        with pytest.raises(AttestationTVADejaExistanteError):
            self.use_case.execute(devis_id=1, dto=dto, created_by=1)


# ─────────────────────────────────────────────────────────────────────────────
# Tests GetAttestationTVAUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestGetAttestationTVAUseCase:
    """Tests pour la recuperation d'attestation TVA."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_attestation_repo = Mock(spec=AttestationTVARepository)
        self.use_case = GetAttestationTVAUseCase(
            devis_repository=self.mock_devis_repo,
            attestation_repository=self.mock_attestation_repo,
        )

    def test_get_attestation_success(self):
        """Test: recuperation reussie."""
        devis = _make_devis()
        attestation = _make_attestation()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_attestation_repo.find_by_devis_id.return_value = attestation

        result = self.use_case.execute(devis_id=1)

        assert isinstance(result, AttestationTVADTO)
        assert result.devis_id == 1

    def test_get_attestation_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999)

    def test_get_attestation_non_generee(self):
        """Test: erreur si attestation pas encore generee."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_attestation_repo.find_by_devis_id.return_value = None

        with pytest.raises(AttestationTVANotFoundError):
            self.use_case.execute(devis_id=1)


# ─────────────────────────────────────────────────────────────────────────────
# Tests VerifierEligibiliteTVAUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestVerifierEligibiliteTVAUseCase:
    """Tests pour la verification d'eligibilite TVA reduite."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.use_case = VerifierEligibiliteTVAUseCase(
            devis_repository=self.mock_devis_repo,
        )

    def test_eligible_taux_10(self):
        """Test: eligible pour taux 10%."""
        devis = _make_devis(taux_tva_defaut=Decimal("10"))
        self.mock_devis_repo.find_by_id.return_value = devis

        result = self.use_case.execute(devis_id=1)

        assert isinstance(result, EligibiliteTVADTO)
        assert result.est_eligible is True
        assert result.type_cerfa == "1300-SD"

    def test_eligible_taux_5_5(self):
        """Test: eligible pour taux 5.5%."""
        devis = _make_devis(taux_tva_defaut=Decimal("5.5"))
        self.mock_devis_repo.find_by_id.return_value = devis

        result = self.use_case.execute(devis_id=1)

        assert result.est_eligible is True
        assert result.type_cerfa == "1301-SD"

    def test_non_eligible_taux_20(self):
        """Test: non eligible pour taux 20%."""
        devis = _make_devis(taux_tva_defaut=Decimal("20"))
        self.mock_devis_repo.find_by_id.return_value = devis

        result = self.use_case.execute(devis_id=1)

        assert result.est_eligible is False

    def test_eligibilite_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999)
