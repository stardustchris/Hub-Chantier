"""Tests unitaires pour les Use Cases de workflow devis.

DEV-15: Suivi statut devis - Transitions de statut.
Couche Application - workflow_use_cases.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.devis.domain.entities.devis import (
    Devis,
    TransitionStatutDevisInvalideError,
)
from modules.devis.domain.entities.journal_devis import JournalDevis
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError
from modules.devis.application.use_cases.workflow_use_cases import (
    SoumettreDevisUseCase,
    ValiderDevisUseCase,
    RetournerBrouillonUseCase,
    MarquerVuUseCase,
    PasserEnNegociationUseCase,
    AccepterDevisUseCase,
    RefuserDevisUseCase,
    PerduDevisUseCase,
    MarquerExpireUseCase,
)
from modules.devis.application.dtos.devis_dtos import DevisDTO


def _make_devis(**kwargs):
    """Cree un devis valide avec valeurs par defaut."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "objet": "Renovation",
        "statut": StatutDevis.BROUILLON,
        "date_creation": date(2026, 1, 15),
        "montant_total_ht": Decimal("0"),
        "montant_total_ttc": Decimal("0"),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


class TestSoumettreDevisUseCase:
    """Tests pour la soumission de devis (Brouillon -> En validation)."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = SoumettreDevisUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_soumettre_success(self):
        """Test: soumission reussie depuis brouillon."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, submitted_by=1)

        assert isinstance(result, DevisDTO)
        assert devis.statut == StatutDevis.EN_VALIDATION
        self.mock_devis_repo.save.assert_called_once()
        self.mock_journal_repo.save.assert_called_once()

    def test_soumettre_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, submitted_by=1)

    def test_soumettre_depuis_envoye_interdit(self):
        """Test: erreur si devis deja envoye."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(TransitionStatutDevisInvalideError):
            self.use_case.execute(devis_id=1, submitted_by=1)

    def test_soumettre_journal_entry(self):
        """Test: entree de journal pour soumission."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(devis_id=1, submitted_by=5)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert journal_call.action == "soumission"
        assert journal_call.auteur_id == 5


class TestValiderDevisUseCase:
    """Tests pour la validation de devis (En validation -> Envoye)."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = ValiderDevisUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_valider_success(self):
        """Test: validation reussie depuis en_validation."""
        devis = _make_devis(statut=StatutDevis.EN_VALIDATION)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, validated_by=1)

        assert isinstance(result, DevisDTO)
        assert devis.statut == StatutDevis.ENVOYE

    def test_valider_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, validated_by=1)

    def test_valider_depuis_brouillon_interdit(self):
        """Test: erreur si devis en brouillon."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(TransitionStatutDevisInvalideError):
            self.use_case.execute(devis_id=1, validated_by=1)


class TestRetournerBrouillonUseCase:
    """Tests pour le retour en brouillon (En validation -> Brouillon)."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = RetournerBrouillonUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_retourner_brouillon_success(self):
        """Test: retour en brouillon reussi."""
        devis = _make_devis(statut=StatutDevis.EN_VALIDATION)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, returned_by=1)

        assert isinstance(result, DevisDTO)
        assert devis.statut == StatutDevis.BROUILLON

    def test_retourner_brouillon_avec_motif(self):
        """Test: retour en brouillon avec motif."""
        devis = _make_devis(statut=StatutDevis.EN_VALIDATION)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(devis_id=1, returned_by=1, motif="Corrections necessaires")

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert "Corrections necessaires" in journal_call.details_json["message"]

    def test_retourner_brouillon_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, returned_by=1)

    def test_retourner_brouillon_depuis_envoye_interdit(self):
        """Test: erreur si devis envoye."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(TransitionStatutDevisInvalideError):
            self.use_case.execute(devis_id=1, returned_by=1)


class TestMarquerVuUseCase:
    """Tests pour marquer un devis comme vu (Envoye -> Vu)."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = MarquerVuUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_marquer_vu_success(self):
        """Test: marquer comme vu reussi."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1)

        assert isinstance(result, DevisDTO)
        assert devis.statut == StatutDevis.VU

    def test_marquer_vu_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999)

    def test_marquer_vu_depuis_brouillon_interdit(self):
        """Test: erreur si devis en brouillon."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(TransitionStatutDevisInvalideError):
            self.use_case.execute(devis_id=1)

    def test_marquer_vu_journal_auteur_none(self):
        """Test: le journal de vu n'a pas d'auteur (action client)."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(devis_id=1)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert journal_call.auteur_id is None


class TestPasserEnNegociationUseCase:
    """Tests pour passer en negociation."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = PasserEnNegociationUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_negociation_depuis_envoye(self):
        """Test: negociation depuis envoye."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, initiated_by=1)

        assert isinstance(result, DevisDTO)
        assert devis.statut == StatutDevis.EN_NEGOCIATION

    def test_negociation_depuis_vu(self):
        """Test: negociation depuis vu."""
        devis = _make_devis(statut=StatutDevis.VU)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, initiated_by=1)

        assert devis.statut == StatutDevis.EN_NEGOCIATION

    def test_negociation_depuis_expire(self):
        """Test: negociation depuis expire."""
        devis = _make_devis(statut=StatutDevis.EXPIRE)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, initiated_by=1)

        assert devis.statut == StatutDevis.EN_NEGOCIATION

    def test_negociation_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, initiated_by=1)

    def test_negociation_depuis_brouillon_interdit(self):
        """Test: erreur si devis en brouillon."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(TransitionStatutDevisInvalideError):
            self.use_case.execute(devis_id=1, initiated_by=1)


class TestAccepterDevisUseCase:
    """Tests pour l'acceptation de devis."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = AccepterDevisUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_accepter_depuis_envoye(self):
        """Test: acceptation depuis envoye."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, accepted_by=1)

        assert devis.statut == StatutDevis.ACCEPTE

    def test_accepter_depuis_vu(self):
        """Test: acceptation depuis vu."""
        devis = _make_devis(statut=StatutDevis.VU)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, accepted_by=1)

        assert devis.statut == StatutDevis.ACCEPTE

    def test_accepter_depuis_en_negociation(self):
        """Test: acceptation depuis en negociation."""
        devis = _make_devis(statut=StatutDevis.EN_NEGOCIATION)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, accepted_by=1)

        assert devis.statut == StatutDevis.ACCEPTE

    def test_accepter_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, accepted_by=1)

    def test_accepter_depuis_brouillon_interdit(self):
        """Test: erreur si devis en brouillon."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(TransitionStatutDevisInvalideError):
            self.use_case.execute(devis_id=1, accepted_by=1)

    def test_accepter_journal_entry(self):
        """Test: entree de journal pour acceptation."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(devis_id=1, accepted_by=3)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert journal_call.action == "acceptation"
        assert journal_call.auteur_id == 3


class TestRefuserDevisUseCase:
    """Tests pour le refus de devis."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = RefuserDevisUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_refuser_success(self):
        """Test: refus reussi avec motif."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, refused_by=1, motif="Trop cher")

        assert devis.statut == StatutDevis.REFUSE

    def test_refuser_motif_vide_interdit(self):
        """Test: erreur si motif vide."""
        with pytest.raises(ValueError, match="motif"):
            self.use_case.execute(devis_id=1, refused_by=1, motif="")

    def test_refuser_motif_espaces_interdit(self):
        """Test: erreur si motif uniquement espaces."""
        with pytest.raises(ValueError):
            self.use_case.execute(devis_id=1, refused_by=1, motif="   ")

    def test_refuser_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, refused_by=1, motif="Raison")

    def test_refuser_depuis_brouillon_interdit(self):
        """Test: erreur si devis en brouillon."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(TransitionStatutDevisInvalideError):
            self.use_case.execute(devis_id=1, refused_by=1, motif="Raison")

    def test_refuser_journal_contient_motif(self):
        """Test: le journal contient le motif de refus."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(devis_id=1, refused_by=1, motif="Trop cher")

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert "Trop cher" in journal_call.details_json["message"]


class TestPerduDevisUseCase:
    """Tests pour marquer un devis comme perdu."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = PerduDevisUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_perdu_success(self):
        """Test: marquer perdu reussi."""
        devis = _make_devis(statut=StatutDevis.EN_NEGOCIATION)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, marked_by=1, motif="Concurrent moins cher")

        assert devis.statut == StatutDevis.PERDU

    def test_perdu_motif_vide_interdit(self):
        """Test: erreur si motif vide."""
        with pytest.raises(ValueError, match="motif"):
            self.use_case.execute(devis_id=1, marked_by=1, motif="")

    def test_perdu_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, marked_by=1, motif="Raison")

    def test_perdu_depuis_envoye_interdit(self):
        """Test: erreur si devis en statut envoye."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(TransitionStatutDevisInvalideError):
            self.use_case.execute(devis_id=1, marked_by=1, motif="Raison")


class TestMarquerExpireUseCase:
    """Tests pour le batch d'expiration."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = MarquerExpireUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_execute_batch_success(self):
        """Test: batch d'expiration reussi."""
        devis1 = _make_devis(id=1, statut=StatutDevis.ENVOYE)
        devis2 = _make_devis(id=2, numero="DEV-2026-002", statut=StatutDevis.VU)
        self.mock_devis_repo.find_expires.return_value = [devis1, devis2]
        self.mock_devis_repo.save.side_effect = lambda d: d
        self.mock_journal_repo.save.return_value = Mock()

        count = self.use_case.execute_batch()

        assert count == 2
        assert devis1.statut == StatutDevis.EXPIRE
        assert devis2.statut == StatutDevis.EXPIRE

    def test_execute_batch_empty(self):
        """Test: aucun devis a expirer."""
        self.mock_devis_repo.find_expires.return_value = []

        count = self.use_case.execute_batch()

        assert count == 0

    def test_execute_batch_skip_invalid_transition(self):
        """Test: les devis avec transition invalide sont ignores."""
        devis_ok = _make_devis(id=1, statut=StatutDevis.ENVOYE)
        # Un devis en brouillon ne peut pas expirer
        devis_ko = _make_devis(id=2, numero="DEV-2026-002", statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_expires.return_value = [devis_ok, devis_ko]
        self.mock_devis_repo.save.side_effect = lambda d: d
        self.mock_journal_repo.save.return_value = Mock()

        count = self.use_case.execute_batch()

        assert count == 1
        assert devis_ok.statut == StatutDevis.EXPIRE

    def test_execute_batch_creates_journal_per_devis(self):
        """Test: une entree de journal par devis expire."""
        devis = _make_devis(id=1, statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_expires.return_value = [devis]
        self.mock_devis_repo.save.side_effect = lambda d: d
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute_batch()

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert journal_call.action == "expiration"
        assert journal_call.auteur_id is None
