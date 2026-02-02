"""Tests unitaires pour les Use Cases de relances automatiques.

DEV-24: Relances automatiques.
Couche Application - relance_use_cases.py
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.entities.relance_devis import (
    RelanceDevis,
    RelanceDevisValidationError,
)
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.value_objects.config_relances import (
    ConfigRelances,
    ConfigRelancesInvalideError,
)
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.relance_devis_repository import RelanceDevisRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError
from modules.devis.application.use_cases.relance_use_cases import (
    PlanifierRelancesUseCase,
    ExecuterRelancesUseCase,
    AnnulerRelancesUseCase,
    GetRelancesDevisUseCase,
    UpdateConfigRelancesUseCase,
    RelanceDevisPlanificationError,
    RelanceDevisExecutionError,
)
from modules.devis.application.dtos.relance_dtos import (
    PlanifierRelancesDTO,
    UpdateConfigRelancesDTO,
    ConfigRelancesDTO,
    RelanceDTO,
    RelancesHistoriqueDTO,
    ExecutionRelancesResultDTO,
)


def _make_devis(**kwargs):
    """Cree un devis valide avec valeurs par defaut."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "client_email": "greg@construction.fr",
        "statut": StatutDevis.ENVOYE,
        "date_creation": date(2026, 1, 15),
        "montant_total_ht": Decimal("10000"),
        "montant_total_ttc": Decimal("12000"),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


def _make_relance(**kwargs):
    """Cree une relance valide."""
    defaults = {
        "id": 1,
        "devis_id": 1,
        "numero_relance": 1,
        "type_relance": "email",
        "date_prevue": datetime(2026, 1, 22, 10, 0, 0),
        "statut": "planifiee",
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return RelanceDevis(**defaults)


# ─────────────────────────────────────────────────────────────────────────────
# Tests PlanifierRelancesUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestPlanifierRelancesUseCase:
    """Tests pour la planification des relances."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_relance_repo = Mock(spec=RelanceDevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = PlanifierRelancesUseCase(
            devis_repository=self.mock_devis_repo,
            relance_repository=self.mock_relance_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_planifier_relances_success(self):
        """Test: planification des 3 relances par defaut."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        relances_creees = [
            _make_relance(id=1, numero_relance=1),
            _make_relance(id=2, numero_relance=2),
            _make_relance(id=3, numero_relance=3),
        ]

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_relance_repo.find_planifiees_by_devis_id.return_value = []
        self.mock_relance_repo.find_by_devis_id.return_value = []
        self.mock_relance_repo.save_batch.return_value = relances_creees
        self.mock_journal_repo.save.return_value = Mock()

        dto = PlanifierRelancesDTO()
        result = self.use_case.execute(devis_id=1, dto=dto, planifie_par=1)

        assert isinstance(result, list)
        assert len(result) == 3
        self.mock_relance_repo.save_batch.assert_called_once()
        self.mock_journal_repo.save.assert_called_once()

    def test_planifier_relances_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        dto = PlanifierRelancesDTO()
        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, dto=dto, planifie_par=1)

    def test_planifier_relances_statut_invalide(self):
        """Test: erreur si devis pas en statut envoye."""
        devis = _make_devis(statut=StatutDevis.BROUILLON)
        self.mock_devis_repo.find_by_id.return_value = devis

        dto = PlanifierRelancesDTO()
        with pytest.raises(RelanceDevisPlanificationError):
            self.use_case.execute(devis_id=1, dto=dto, planifie_par=1)

    def test_planifier_relances_deja_planifiees(self):
        """Test: erreur si relances deja planifiees."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        relances_existantes = [_make_relance()]

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_relance_repo.find_planifiees_by_devis_id.return_value = relances_existantes

        dto = PlanifierRelancesDTO()
        with pytest.raises(RelanceDevisPlanificationError):
            self.use_case.execute(devis_id=1, dto=dto, planifie_par=1)

    def test_planifier_relances_avec_message(self):
        """Test: planification avec message personnalise."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        relances_creees = [
            _make_relance(id=i, numero_relance=i, message_personnalise="Rappel devis")
            for i in range(1, 4)
        ]

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_relance_repo.find_planifiees_by_devis_id.return_value = []
        self.mock_relance_repo.find_by_devis_id.return_value = []
        self.mock_relance_repo.save_batch.return_value = relances_creees
        self.mock_journal_repo.save.return_value = Mock()

        dto = PlanifierRelancesDTO(message_personnalise="Rappel devis")
        result = self.use_case.execute(devis_id=1, dto=dto, planifie_par=1)

        assert len(result) == 3


# ─────────────────────────────────────────────────────────────────────────────
# Tests ExecuterRelancesUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestExecuterRelancesUseCase:
    """Tests pour l'execution batch des relances."""

    def setup_method(self):
        self.mock_relance_repo = Mock(spec=RelanceDevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = ExecuterRelancesUseCase(
            relance_repository=self.mock_relance_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_executer_relances_dues(self):
        """Test: execution des relances dont la date est passee."""
        relance1 = _make_relance(
            id=1, devis_id=1, numero_relance=1,
            date_prevue=datetime.utcnow() - timedelta(hours=1),
            statut="planifiee",
        )
        relance2 = _make_relance(
            id=2, devis_id=2, numero_relance=1,
            date_prevue=datetime.utcnow() - timedelta(days=1),
            statut="planifiee",
        )

        self.mock_relance_repo.find_planifiees_avant.return_value = [relance1, relance2]
        self.mock_relance_repo.save.side_effect = lambda r: r
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute()

        assert isinstance(result, ExecutionRelancesResultDTO)
        assert result.nb_relances_envoyees == 2
        assert result.nb_erreurs == 0

    def test_executer_aucune_relance_due(self):
        """Test: aucune relance a executer."""
        self.mock_relance_repo.find_planifiees_avant.return_value = []

        result = self.use_case.execute()

        assert result.nb_relances_envoyees == 0
        assert result.nb_erreurs == 0


# ─────────────────────────────────────────────────────────────────────────────
# Tests AnnulerRelancesUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestAnnulerRelancesUseCase:
    """Tests pour l'annulation des relances."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_relance_repo = Mock(spec=RelanceDevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = AnnulerRelancesUseCase(
            devis_repository=self.mock_devis_repo,
            relance_repository=self.mock_relance_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_annuler_relances_success(self):
        """Test: annulation de toutes les relances planifiees."""
        devis = _make_devis()
        relance1 = _make_relance(id=1, statut="planifiee")
        relance2 = _make_relance(id=2, numero_relance=2, statut="planifiee")

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_relance_repo.find_planifiees_by_devis_id.return_value = [relance1, relance2]
        self.mock_relance_repo.save.side_effect = lambda r: r
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, annule_par=1)

        assert len(result) == 2

    def test_annuler_relances_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, annule_par=1)

    def test_annuler_aucune_relance_planifiee(self):
        """Test: pas d'erreur si aucune relance a annuler."""
        devis = _make_devis()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_relance_repo.find_planifiees_by_devis_id.return_value = []
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, annule_par=1)

        assert len(result) == 0


# ─────────────────────────────────────────────────────────────────────────────
# Tests GetRelancesDevisUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestGetRelancesDevisUseCase:
    """Tests pour la recuperation de l'historique des relances."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_relance_repo = Mock(spec=RelanceDevisRepository)
        self.use_case = GetRelancesDevisUseCase(
            devis_repository=self.mock_devis_repo,
            relance_repository=self.mock_relance_repo,
        )

    def test_get_relances_success(self):
        """Test: recuperation de l'historique reussie."""
        devis = _make_devis()
        relance1 = _make_relance(
            id=1, statut="envoyee",
            date_envoi=datetime.utcnow(),
        )
        relance2 = _make_relance(id=2, numero_relance=2, statut="planifiee")

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_relance_repo.find_by_devis_id.return_value = [relance1, relance2]

        result = self.use_case.execute(devis_id=1)

        assert isinstance(result, RelancesHistoriqueDTO)
        assert result.devis_id == 1
        assert len(result.relances) == 2
        assert result.nb_envoyees == 1
        assert result.nb_planifiees == 1
        assert result.nb_annulees == 0

    def test_get_relances_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999)

    def test_get_relances_vide(self):
        """Test: historique vide si aucune relance."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_relance_repo.find_by_devis_id.return_value = []

        result = self.use_case.execute(devis_id=1)

        assert len(result.relances) == 0
        assert result.nb_envoyees == 0
        assert result.nb_planifiees == 0
        assert result.nb_annulees == 0


# ─────────────────────────────────────────────────────────────────────────────
# Tests UpdateConfigRelancesUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestUpdateConfigRelancesUseCase:
    """Tests pour la mise a jour de la configuration des relances."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = UpdateConfigRelancesUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_update_config_success(self):
        """Test: mise a jour de la configuration reussie."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = UpdateConfigRelancesDTO(
            delais=[5, 10, 20],
            actif=True,
            type_relance_defaut="email_push",
        )

        result = self.use_case.execute(devis_id=1, dto=dto, modifie_par=1)

        assert isinstance(result, ConfigRelancesDTO)
        assert result.delais == [5, 10, 20]
        assert result.type_relance_defaut == "email_push"
        self.mock_devis_repo.save.assert_called_once()

    def test_update_config_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        dto = UpdateConfigRelancesDTO(delais=[5, 10])
        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, dto=dto, modifie_par=1)

    def test_update_config_delais_invalides(self):
        """Test: erreur si delais non croissants."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis

        dto = UpdateConfigRelancesDTO(delais=[30, 15, 7])  # Non croissant
        with pytest.raises(ConfigRelancesInvalideError):
            self.use_case.execute(devis_id=1, dto=dto, modifie_par=1)

    def test_update_config_type_relance_invalide(self):
        """Test: erreur si type de relance invalide."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis

        dto = UpdateConfigRelancesDTO(type_relance_defaut="sms")
        with pytest.raises(ConfigRelancesInvalideError):
            self.use_case.execute(devis_id=1, dto=dto, modifie_par=1)

    def test_update_config_desactiver_relances(self):
        """Test: desactivation des relances."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = UpdateConfigRelancesDTO(actif=False)
        result = self.use_case.execute(devis_id=1, dto=dto, modifie_par=1)

        assert result.actif is False


# ─────────────────────────────────────────────────────────────────────────────
# Tests Value Object ConfigRelances
# ─────────────────────────────────────────────────────────────────────────────

class TestConfigRelances:
    """Tests pour le value object ConfigRelances."""

    def test_creation_defaut(self):
        """Test: creation avec valeurs par defaut."""
        config = ConfigRelances()
        assert config.delais == (7, 15, 30)
        assert config.actif is True
        assert config.type_relance_defaut == "email"

    def test_creation_personnalisee(self):
        """Test: creation avec valeurs personnalisees."""
        config = ConfigRelances(delais=(5, 10, 20), type_relance_defaut="push")
        assert config.delais == (5, 10, 20)
        assert config.type_relance_defaut == "push"

    def test_erreur_delais_vides(self):
        """Test: erreur si delais vides."""
        with pytest.raises(ConfigRelancesInvalideError):
            ConfigRelances(delais=())

    def test_erreur_delais_non_croissants(self):
        """Test: erreur si delais non croissants."""
        with pytest.raises(ConfigRelancesInvalideError):
            ConfigRelances(delais=(15, 7, 30))

    def test_erreur_delai_negatif(self):
        """Test: erreur si delai < 1."""
        with pytest.raises(ConfigRelancesInvalideError):
            ConfigRelances(delais=(0, 7, 15))

    def test_erreur_type_relance_invalide(self):
        """Test: erreur si type de relance invalide."""
        with pytest.raises(ConfigRelancesInvalideError):
            ConfigRelances(type_relance_defaut="sms")

    def test_nombre_relances(self):
        """Test: nombre de relances."""
        config = ConfigRelances(delais=(7, 15))
        assert config.nombre_relances == 2

    def test_prochaine_relance(self):
        """Test: calcul date prochaine relance."""
        config = ConfigRelances(delais=(7, 15, 30))
        date_envoi = datetime(2026, 1, 15, 10, 0, 0)

        # Premiere relance : J+7
        prochaine = config.prochaine_relance(date_envoi, nb_relances_effectuees=0)
        assert prochaine == datetime(2026, 1, 22, 10, 0, 0)

        # Deuxieme relance : J+15
        prochaine = config.prochaine_relance(date_envoi, nb_relances_effectuees=1)
        assert prochaine == datetime(2026, 1, 30, 10, 0, 0)

        # Apres toutes les relances : None
        prochaine = config.prochaine_relance(date_envoi, nb_relances_effectuees=3)
        assert prochaine is None

    def test_prochaine_relance_desactivee(self):
        """Test: None si relances desactivees."""
        config = ConfigRelances(actif=False)
        prochaine = config.prochaine_relance(datetime.utcnow(), nb_relances_effectuees=0)
        assert prochaine is None

    def test_toutes_les_dates(self):
        """Test: calcul de toutes les dates de relance."""
        config = ConfigRelances(delais=(7, 15, 30))
        date_envoi = datetime(2026, 1, 15, 10, 0, 0)

        dates = config.toutes_les_dates(date_envoi)

        assert len(dates) == 3
        assert dates[0] == datetime(2026, 1, 22, 10, 0, 0)
        assert dates[1] == datetime(2026, 1, 30, 10, 0, 0)
        assert dates[2] == datetime(2026, 2, 14, 10, 0, 0)

    def test_toutes_les_dates_desactivees(self):
        """Test: liste vide si relances desactivees."""
        config = ConfigRelances(actif=False)
        dates = config.toutes_les_dates(datetime.utcnow())
        assert dates == []

    def test_to_dict(self):
        """Test: serialisation en dict."""
        config = ConfigRelances()
        d = config.to_dict()
        assert d["delais"] == [7, 15, 30]
        assert d["actif"] is True

    def test_from_dict(self):
        """Test: deserialization depuis dict."""
        config = ConfigRelances.from_dict({"delais": [5, 10], "actif": False, "type_relance_defaut": "push"})
        assert config.delais == (5, 10)
        assert config.actif is False

    def test_from_dict_none(self):
        """Test: valeurs par defaut si None."""
        config = ConfigRelances.from_dict(None)
        assert config.delais == (7, 15, 30)
