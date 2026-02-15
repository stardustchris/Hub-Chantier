"""Tests unitaires pour les domain events et guards dans le workflow.

DEV-15: Suivi statut devis - Domain Events + Guards dans les use cases.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.domain.services.workflow_guards import TransitionNonAutoriseeError
from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError
from modules.devis.application.use_cases.workflow_use_cases import (
    SoumettreDevisUseCase,
    ValiderDevisUseCase,
    AccepterDevisUseCase,
    RefuserDevisUseCase,
    PerduDevisUseCase,
    PasserEnNegociationUseCase,
    GetWorkflowInfoUseCase,
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


class TestSoumettreGuards:
    """Tests des guards pour la soumission."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = SoumettreDevisUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_soumettre_avec_role_admin_ok(self):
        """Test: admin peut soumettre."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, submitted_by=1, role="admin")
        assert isinstance(result, DevisDTO)

    def test_soumettre_avec_role_compagnon_interdit(self):
        """Test: compagnon ne peut pas soumettre."""
        with pytest.raises(TransitionNonAutoriseeError):
            self.use_case.execute(devis_id=1, submitted_by=1, role="compagnon")

    def test_soumettre_sans_role_backward_compat(self):
        """Test: sans role = pas de guard (backward compat)."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        # Pas d'exception sans le parametre role
        result = self.use_case.execute(devis_id=1, submitted_by=1)
        assert isinstance(result, DevisDTO)


class TestValiderGuardSeuil:
    """Tests du guard seuil 50k EUR dans ValiderDevisUseCase."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = ValiderDevisUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_valider_gros_devis_conducteur_interdit(self):
        """Test: conducteur ne peut pas valider un devis >= 50k EUR."""
        devis = _make_devis(
            statut=StatutDevis.EN_VALIDATION,
            montant_total_ht=Decimal("75000"),
        )
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(TransitionNonAutoriseeError) as exc_info:
            self.use_case.execute(devis_id=1, validated_by=1, role="conducteur")
        assert "50000" in str(exc_info.value)

    def test_valider_gros_devis_admin_ok(self):
        """Test: admin peut valider un devis >= 50k EUR."""
        devis = _make_devis(
            statut=StatutDevis.EN_VALIDATION,
            montant_total_ht=Decimal("75000"),
        )
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, validated_by=1, role="admin")
        assert isinstance(result, DevisDTO)


class TestJournalContientTransition:
    """Tests: le journal contient les infos de transition avant/apres."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = SoumettreDevisUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_soumission_journal_contient_ancien_nouveau_statut(self):
        """Test: le journal de soumission contient ancien/nouveau statut."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(devis_id=1, submitted_by=5)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert journal_call.details_json["ancien_statut"] == "brouillon"
        assert journal_call.details_json["nouveau_statut"] == "en_validation"

    def test_refus_journal_contient_motif(self):
        """Test: le journal de refus contient le motif."""
        mock_devis_repo = Mock(spec=DevisRepository)
        mock_journal_repo = Mock(spec=JournalDevisRepository)
        use_case = RefuserDevisUseCase(
            devis_repository=mock_devis_repo,
            journal_repository=mock_journal_repo,
        )

        devis = _make_devis(statut=StatutDevis.ENVOYE)
        mock_devis_repo.find_by_id.return_value = devis
        mock_devis_repo.save.return_value = devis
        mock_journal_repo.save.return_value = Mock()

        use_case.execute(devis_id=1, refused_by=5, motif="Budget insuffisant")

        journal_call = mock_journal_repo.save.call_args[0][0]
        assert journal_call.details_json["motif"] == "Budget insuffisant"
        assert journal_call.details_json["ancien_statut"] == "envoye"
        assert journal_call.details_json["nouveau_statut"] == "refuse"


class TestGetWorkflowInfoUseCase:
    """Tests du use case workflow info."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.use_case = GetWorkflowInfoUseCase(
            devis_repository=self.mock_devis_repo,
        )

    def test_workflow_info_brouillon(self):
        """Test: info workflow pour un devis en brouillon."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis

        result = self.use_case.execute(devis_id=1)

        assert result["statut_actuel"] == "brouillon"
        assert result["est_modifiable"] is True
        assert result["est_final"] is False
        assert len(result["transitions_possibles"]) == 1
        assert result["transitions_possibles"][0]["statut_cible"] == "en_validation"
        assert result["transitions_possibles"][0]["transition"] == "soumettre"

    def test_workflow_info_envoye_multiple_transitions(self):
        """Test: un devis envoye a plusieurs transitions possibles."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_by_id.return_value = devis

        result = self.use_case.execute(devis_id=1)

        assert result["statut_actuel"] == "envoye"
        assert len(result["transitions_possibles"]) >= 3  # vu, negociation, accepte, refuse, expire

    def test_workflow_info_refuse_est_final(self):
        """Test: un devis refuse n'a aucune transition possible."""
        devis = _make_devis(statut=StatutDevis.REFUSE)
        self.mock_devis_repo.find_by_id.return_value = devis

        result = self.use_case.execute(devis_id=1)

        assert result["est_final"] is True
        assert len(result["transitions_possibles"]) == 0

    def test_workflow_info_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999)

    def test_workflow_info_motif_requis(self):
        """Test: les transitions vers refuse/perdu marquent motif_requis=True."""
        devis = _make_devis(statut=StatutDevis.EN_NEGOCIATION)
        self.mock_devis_repo.find_by_id.return_value = devis

        result = self.use_case.execute(devis_id=1)

        transitions = {t["statut_cible"]: t for t in result["transitions_possibles"]}
        if "refuse" in transitions:
            assert transitions["refuse"]["motif_requis"] is True
        if "perdu" in transitions:
            assert transitions["perdu"]["motif_requis"] is True
        if "accepte" in transitions:
            assert transitions["accepte"]["motif_requis"] is False

    def test_workflow_info_roles_autorises(self):
        """Test: chaque transition liste les roles autorises."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis

        result = self.use_case.execute(devis_id=1)

        transition = result["transitions_possibles"][0]
        assert "roles_autorises" in transition
        assert "admin" in transition["roles_autorises"]
