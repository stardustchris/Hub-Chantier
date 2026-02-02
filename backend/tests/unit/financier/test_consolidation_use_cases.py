"""Tests unitaires pour les Use Cases Consolidation du module Financier.

FIN-20 Phase 3: Tests pour la vue consolidee multi-chantiers.
Tests du use case GetVueConsolideeFinancesUseCase avec calcul des KPI
globaux, classification ok/attention/depassement, top rentables/derives.

GAP #1: Noms chantiers via ChantierInfoPort
GAP #3: Filtre par statut chantier
GAP #4: Marge definitive vs estimee (chantier ferme)
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, MagicMock

from modules.financier.domain.entities import Budget
from modules.financier.domain.repositories import (
    BudgetRepository,
    LotBudgetaireRepository,
    AchatRepository,
    AlerteRepository,
)
from modules.financier.domain.value_objects.statuts_financiers import (
    STATUTS_ENGAGES,
    STATUTS_REALISES,
)
from modules.financier.application.use_cases.consolidation_use_cases import (
    GetVueConsolideeFinancesUseCase,
)
from shared.application.ports.chantier_info_port import (
    ChantierInfoPort,
    ChantierInfoDTO,
)


class TestGetVueConsolideeFinancesUseCase:
    """Tests pour le use case de vue consolidee multi-chantiers."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_alerte_repo = Mock(spec=AlerteRepository)

        self.use_case = GetVueConsolideeFinancesUseCase(
            budget_repository=self.mock_budget_repo,
            lot_repository=self.mock_lot_repo,
            achat_repository=self.mock_achat_repo,
            alerte_repository=self.mock_alerte_repo,
        )

    def _make_budget(self, chantier_id, initial, avenants=Decimal("0")):
        """Helper pour creer un budget mock."""
        return Budget(
            id=chantier_id * 10,
            chantier_id=chantier_id,
            montant_initial_ht=initial,
            montant_avenants_ht=avenants,
            created_at=datetime(2026, 1, 1),
        )

    def test_nominal_multi_chantier(self):
        """Test: vue consolidee nominale avec 3 chantiers."""
        # Arrange
        budgets = {
            1: self._make_budget(1, Decimal("100000"), Decimal("10000")),
            2: self._make_budget(2, Decimal("200000"), Decimal("20000")),
            3: self._make_budget(3, Decimal("50000"), Decimal("5000")),
        }

        def find_budget(cid):
            return budgets.get(cid)

        self.mock_budget_repo.find_by_chantier_id.side_effect = find_budget

        # Chantier 1: engage 50000, realise 30000 -> pct_engage=45.45%, marge=54.55%
        # Chantier 2: engage 180000, realise 150000 -> pct_engage=81.82%, marge=18.18%
        # Chantier 3: engage 60000, realise 55000 -> pct_engage=109.09%, marge=-9.09%
        engage_map = {
            (1, tuple(STATUTS_ENGAGES)): Decimal("50000"),
            (2, tuple(STATUTS_ENGAGES)): Decimal("180000"),
            (3, tuple(STATUTS_ENGAGES)): Decimal("60000"),
            (1, tuple(STATUTS_REALISES)): Decimal("30000"),
            (2, tuple(STATUTS_REALISES)): Decimal("150000"),
            (3, tuple(STATUTS_REALISES)): Decimal("55000"),
        }

        def somme_by_chantier(cid, statuts):
            return engage_map.get((cid, tuple(statuts)), Decimal("0"))

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1, 2, 3])

        # Assert
        assert result.kpi_globaux.nb_chantiers == 3
        assert len(result.chantiers) == 3
        assert len(result.top_rentables) == 3
        assert len(result.top_derives) == 3

        # Totaux globaux
        # total_budget = 110000 + 220000 + 55000 = 385000
        assert result.kpi_globaux.total_budget_revise == "385000.00"
        # total_engage = 50000 + 180000 + 60000 = 290000
        assert result.kpi_globaux.total_engage == "290000.00"
        # total_realise = 30000 + 150000 + 55000 = 235000
        assert result.kpi_globaux.total_realise == "235000.00"
        # total_reste = 385000 - 290000 = 95000
        assert result.kpi_globaux.total_reste_a_depenser == "95000.00"

    def test_chantier_sans_budget_skip(self):
        """Test: un chantier sans budget est ignore (pas d'erreur)."""
        # Arrange
        budget_chantier_1 = self._make_budget(1, Decimal("100000"))

        def find_budget(cid):
            if cid == 1:
                return budget_chantier_1
            return None  # Chantier 2 n'a pas de budget

        self.mock_budget_repo.find_by_chantier_id.side_effect = find_budget
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("30000")
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1, 2])

        # Assert - seul le chantier 1 est present
        assert result.kpi_globaux.nb_chantiers == 1
        assert len(result.chantiers) == 1
        assert result.chantiers[0].chantier_id == 1

    def test_classification_ok(self):
        """Test: chantier avec pct_engage < 80% est classe 'ok'."""
        # Arrange
        budget = self._make_budget(1, Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget
        # Engage 50% du budget -> statut "ok"
        self.mock_achat_repo.somme_by_chantier.side_effect = (
            lambda cid, statuts: Decimal("50000")
            if statuts == STATUTS_ENGAGES
            else Decimal("20000")
        )
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1])

        # Assert
        assert result.chantiers[0].statut == "ok"
        assert result.kpi_globaux.nb_chantiers_ok == 1
        assert result.kpi_globaux.nb_chantiers_attention == 0
        assert result.kpi_globaux.nb_chantiers_depassement == 0

    def test_classification_attention(self):
        """Test: chantier avec 80% <= pct_engage <= 100% est classe 'attention'."""
        # Arrange
        budget = self._make_budget(1, Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget
        # Engage 85% du budget -> statut "attention"
        self.mock_achat_repo.somme_by_chantier.side_effect = (
            lambda cid, statuts: Decimal("85000")
            if statuts == STATUTS_ENGAGES
            else Decimal("40000")
        )
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1])

        # Assert
        assert result.chantiers[0].statut == "attention"
        assert result.kpi_globaux.nb_chantiers_attention == 1

    def test_classification_depassement(self):
        """Test: chantier avec pct_engage > 100% est classe 'depassement'."""
        # Arrange
        budget = self._make_budget(1, Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget
        # Engage 110% du budget -> statut "depassement"
        self.mock_achat_repo.somme_by_chantier.side_effect = (
            lambda cid, statuts: Decimal("110000")
            if statuts == STATUTS_ENGAGES
            else Decimal("90000")
        )
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1])

        # Assert
        assert result.chantiers[0].statut == "depassement"
        assert result.kpi_globaux.nb_chantiers_depassement == 1

    def test_top_rentables_sorted_by_marge(self):
        """Test: top_rentables trie par marge decroissante, max 3."""
        # Arrange - 4 chantiers avec marges differentes
        budgets = {
            1: self._make_budget(1, Decimal("100000")),
            2: self._make_budget(2, Decimal("100000")),
            3: self._make_budget(3, Decimal("100000")),
            4: self._make_budget(4, Decimal("100000")),
        }
        self.mock_budget_repo.find_by_chantier_id.side_effect = lambda cid: budgets.get(cid)

        # Chantier 1: engage 30000 -> marge 70%
        # Chantier 2: engage 50000 -> marge 50%
        # Chantier 3: engage 10000 -> marge 90% (le plus rentable)
        # Chantier 4: engage 80000 -> marge 20%
        engage_values = {1: Decimal("30000"), 2: Decimal("50000"), 3: Decimal("10000"), 4: Decimal("80000")}

        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return engage_values.get(cid, Decimal("0"))
            return Decimal("0")  # realise = 0

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1, 2, 3, 4])

        # Assert - top 3 rentables: chantier 3 (90%), 1 (70%), 2 (50%)
        assert len(result.top_rentables) == 3
        assert result.top_rentables[0].chantier_id == 3
        assert result.top_rentables[1].chantier_id == 1
        assert result.top_rentables[2].chantier_id == 2

    def test_top_derives_sorted_by_pct_engage(self):
        """Test: top_derives trie par pct_engage decroissant, max 3."""
        # Arrange - 4 chantiers avec engagements differents
        budgets = {
            1: self._make_budget(1, Decimal("100000")),
            2: self._make_budget(2, Decimal("100000")),
            3: self._make_budget(3, Decimal("100000")),
            4: self._make_budget(4, Decimal("100000")),
        }
        self.mock_budget_repo.find_by_chantier_id.side_effect = lambda cid: budgets.get(cid)

        # Chantier 1: engage 120000 -> pct 120% (le plus derive)
        # Chantier 2: engage 90000 -> pct 90%
        # Chantier 3: engage 110000 -> pct 110%
        # Chantier 4: engage 50000 -> pct 50%
        engage_values = {1: Decimal("120000"), 2: Decimal("90000"), 3: Decimal("110000"), 4: Decimal("50000")}

        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return engage_values.get(cid, Decimal("0"))
            return Decimal("0")

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1, 2, 3, 4])

        # Assert - top 3 derives: chantier 1 (120%), 3 (110%), 2 (90%)
        assert len(result.top_derives) == 3
        assert result.top_derives[0].chantier_id == 1
        assert result.top_derives[1].chantier_id == 3
        assert result.top_derives[2].chantier_id == 2

    def test_liste_vide(self):
        """Test: liste de chantier_ids vide retourne des KPI a zero."""
        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[])

        # Assert
        assert result.kpi_globaux.nb_chantiers == 0
        assert result.kpi_globaux.total_budget_revise == "0.00"
        assert result.kpi_globaux.total_engage == "0.00"
        assert result.kpi_globaux.total_realise == "0.00"
        assert result.kpi_globaux.total_reste_a_depenser == "0.00"
        assert result.kpi_globaux.marge_moyenne_pct == "0.00"
        assert result.kpi_globaux.nb_chantiers_ok == 0
        assert result.kpi_globaux.nb_chantiers_attention == 0
        assert result.kpi_globaux.nb_chantiers_depassement == 0
        assert len(result.chantiers) == 0
        assert len(result.top_rentables) == 0
        assert len(result.top_derives) == 0

    def test_marge_moyenne_calculation(self):
        """Test: la marge moyenne est bien la moyenne des marges individuelles."""
        # Arrange - 2 chantiers
        budgets = {
            1: self._make_budget(1, Decimal("100000")),
            2: self._make_budget(2, Decimal("200000")),
        }
        self.mock_budget_repo.find_by_chantier_id.side_effect = lambda cid: budgets.get(cid)

        # Chantier 1: engage 40000 -> marge 60%
        # Chantier 2: engage 100000 -> marge 50%
        # Marge moyenne = (60 + 50) / 2 = 55%
        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return {1: Decimal("40000"), 2: Decimal("100000")}[cid]
            return Decimal("0")

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1, 2])

        # Assert
        assert result.kpi_globaux.marge_moyenne_pct == "55.00"

    def test_nb_alertes_per_chantier(self):
        """Test: le nombre d'alertes non acquittees est bien reporte."""
        # Arrange
        budget = self._make_budget(1, Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("30000")
        # 3 alertes non acquittees
        self.mock_alerte_repo.find_non_acquittees.return_value = [
            MagicMock(), MagicMock(), MagicMock()
        ]

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1])

        # Assert
        assert result.chantiers[0].nb_alertes == 3

    def test_chantier_nom_fallback(self):
        """Test: le nom du chantier utilise le fallback 'Chantier {id}'."""
        # Arrange
        budget = self._make_budget(42, Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("0")
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[42])

        # Assert
        assert result.chantiers[0].nom_chantier == "Chantier 42"

    def test_budget_zero_montant(self):
        """Test: budget avec montant_revise = 0 donne des pourcentages a 0."""
        # Arrange
        budget = self._make_budget(1, Decimal("0"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("0")
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1])

        # Assert
        assert result.chantiers[0].pct_engage == "0.00"
        assert result.chantiers[0].pct_realise == "0.00"
        assert result.chantiers[0].marge_estimee_pct == "0.00"
        assert result.chantiers[0].statut == "ok"


# ============================================================
# GAP #1 - Noms chantiers via ChantierInfoPort
# ============================================================


class TestConsolidationWithChantierInfoPort:
    """Tests pour la resolution des noms de chantiers via ChantierInfoPort."""

    def setup_method(self):
        """Configuration avec ChantierInfoPort injecte."""
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_alerte_repo = Mock(spec=AlerteRepository)
        self.mock_chantier_info_port = Mock(spec=ChantierInfoPort)

        self.use_case = GetVueConsolideeFinancesUseCase(
            budget_repository=self.mock_budget_repo,
            lot_repository=self.mock_lot_repo,
            achat_repository=self.mock_achat_repo,
            alerte_repository=self.mock_alerte_repo,
            chantier_info_port=self.mock_chantier_info_port,
        )

    def _make_budget(self, chantier_id, initial, avenants=Decimal("0")):
        """Helper pour creer un budget mock."""
        return Budget(
            id=chantier_id * 10,
            chantier_id=chantier_id,
            montant_initial_ht=initial,
            montant_avenants_ht=avenants,
            created_at=datetime(2026, 1, 1),
        )

    def test_nom_chantier_from_port(self):
        """Test GAP #1: le nom du chantier vient du ChantierInfoPort."""
        # Arrange
        budget = self._make_budget(1, Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("30000")
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        self.mock_chantier_info_port.get_chantiers_info_batch.return_value = {
            1: ChantierInfoDTO(id=1, nom="Renovation Mairie", statut="en_cours"),
        }

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1])

        # Assert
        assert result.chantiers[0].nom_chantier == "Renovation Mairie"
        self.mock_chantier_info_port.get_chantiers_info_batch.assert_called_once_with([1])

    def test_nom_chantier_fallback_when_port_returns_no_info(self):
        """Test GAP #1: fallback 'Chantier {id}' si le port ne retourne pas l'info."""
        # Arrange
        budget = self._make_budget(99, Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("0")
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        # Port retourne un dict vide (chantier non trouve dans le batch)
        self.mock_chantier_info_port.get_chantiers_info_batch.return_value = {}

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[99])

        # Assert
        assert result.chantiers[0].nom_chantier == "Chantier 99"

    def test_nom_chantier_multiple_chantiers(self):
        """Test GAP #1: noms corrects pour plusieurs chantiers."""
        # Arrange
        budgets = {
            1: self._make_budget(1, Decimal("100000")),
            2: self._make_budget(2, Decimal("200000")),
        }
        self.mock_budget_repo.find_by_chantier_id.side_effect = lambda cid: budgets.get(cid)
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("30000")
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        self.mock_chantier_info_port.get_chantiers_info_batch.return_value = {
            1: ChantierInfoDTO(id=1, nom="Chantier Alpha", statut="ouvert"),
            2: ChantierInfoDTO(id=2, nom="Chantier Beta", statut="en_cours"),
        }

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1, 2])

        # Assert
        noms = {c.chantier_id: c.nom_chantier for c in result.chantiers}
        assert noms[1] == "Chantier Alpha"
        assert noms[2] == "Chantier Beta"

    def test_statut_chantier_populated(self):
        """Test GAP #1: statut_chantier est renseigne quand le port est disponible."""
        # Arrange
        budget = self._make_budget(1, Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("30000")
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        self.mock_chantier_info_port.get_chantiers_info_batch.return_value = {
            1: ChantierInfoDTO(id=1, nom="Chantier Test", statut="receptionne"),
        }

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1])

        # Assert
        assert result.chantiers[0].statut_chantier == "receptionne"

    def test_statut_chantier_empty_when_port_has_no_info(self):
        """Test: statut_chantier est vide quand le port ne retourne pas l'info."""
        # Arrange
        budget = self._make_budget(1, Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("0")
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        self.mock_chantier_info_port.get_chantiers_info_batch.return_value = {}

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1])

        # Assert
        assert result.chantiers[0].statut_chantier == ""


# ============================================================
# GAP #3 - Filtre par statut chantier
# ============================================================


class TestConsolidationFilterByStatutChantier:
    """Tests pour le filtre par statut operationnel du chantier."""

    def setup_method(self):
        """Configuration avec ChantierInfoPort injecte."""
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_alerte_repo = Mock(spec=AlerteRepository)
        self.mock_chantier_info_port = Mock(spec=ChantierInfoPort)

        self.use_case = GetVueConsolideeFinancesUseCase(
            budget_repository=self.mock_budget_repo,
            lot_repository=self.mock_lot_repo,
            achat_repository=self.mock_achat_repo,
            alerte_repository=self.mock_alerte_repo,
            chantier_info_port=self.mock_chantier_info_port,
        )

    def _make_budget(self, chantier_id, initial, avenants=Decimal("0")):
        """Helper pour creer un budget mock."""
        return Budget(
            id=chantier_id * 10,
            chantier_id=chantier_id,
            montant_initial_ht=initial,
            montant_avenants_ht=avenants,
            created_at=datetime(2026, 1, 1),
        )

    def test_filtre_statut_en_cours(self):
        """Test GAP #3: seuls les chantiers 'en_cours' sont inclus."""
        # Arrange
        budgets = {
            1: self._make_budget(1, Decimal("100000")),
            2: self._make_budget(2, Decimal("200000")),
            3: self._make_budget(3, Decimal("50000")),
        }
        self.mock_budget_repo.find_by_chantier_id.side_effect = lambda cid: budgets.get(cid)
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("30000")
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        self.mock_chantier_info_port.get_chantiers_info_batch.return_value = {
            1: ChantierInfoDTO(id=1, nom="Alpha", statut="en_cours"),
            2: ChantierInfoDTO(id=2, nom="Beta", statut="ferme"),
            3: ChantierInfoDTO(id=3, nom="Gamma", statut="en_cours"),
        }

        # Act
        result = self.use_case.execute(
            user_accessible_chantier_ids=[1, 2, 3],
            statut_chantier="en_cours",
        )

        # Assert - seuls chantiers 1 et 3 (en_cours) sont inclus
        assert result.kpi_globaux.nb_chantiers == 2
        ids = {c.chantier_id for c in result.chantiers}
        assert ids == {1, 3}

    def test_filtre_statut_ferme(self):
        """Test GAP #3: seuls les chantiers 'ferme' sont inclus."""
        # Arrange
        budgets = {
            1: self._make_budget(1, Decimal("100000")),
            2: self._make_budget(2, Decimal("200000")),
        }
        self.mock_budget_repo.find_by_chantier_id.side_effect = lambda cid: budgets.get(cid)
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("30000")
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        self.mock_chantier_info_port.get_chantiers_info_batch.return_value = {
            1: ChantierInfoDTO(id=1, nom="Alpha", statut="en_cours"),
            2: ChantierInfoDTO(id=2, nom="Beta", statut="ferme"),
        }

        # Act
        result = self.use_case.execute(
            user_accessible_chantier_ids=[1, 2],
            statut_chantier="ferme",
        )

        # Assert - seul chantier 2 (ferme) est inclus
        assert result.kpi_globaux.nb_chantiers == 1
        assert result.chantiers[0].chantier_id == 2

    def test_filtre_statut_none_retourne_tous(self):
        """Test GAP #3: sans filtre, tous les chantiers sont inclus."""
        # Arrange
        budgets = {
            1: self._make_budget(1, Decimal("100000")),
            2: self._make_budget(2, Decimal("200000")),
        }
        self.mock_budget_repo.find_by_chantier_id.side_effect = lambda cid: budgets.get(cid)
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("30000")
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        self.mock_chantier_info_port.get_chantiers_info_batch.return_value = {
            1: ChantierInfoDTO(id=1, nom="Alpha", statut="en_cours"),
            2: ChantierInfoDTO(id=2, nom="Beta", statut="ferme"),
        }

        # Act
        result = self.use_case.execute(
            user_accessible_chantier_ids=[1, 2],
            statut_chantier=None,
        )

        # Assert - tous les chantiers sont inclus
        assert result.kpi_globaux.nb_chantiers == 2

    def test_filtre_statut_aucun_match(self):
        """Test GAP #3: filtre retourne 0 chantier si aucun match."""
        # Arrange
        self.mock_chantier_info_port.get_chantiers_info_batch.return_value = {
            1: ChantierInfoDTO(id=1, nom="Alpha", statut="en_cours"),
        }

        budgets = {1: self._make_budget(1, Decimal("100000"))}
        self.mock_budget_repo.find_by_chantier_id.side_effect = lambda cid: budgets.get(cid)

        # Act
        result = self.use_case.execute(
            user_accessible_chantier_ids=[1],
            statut_chantier="ferme",
        )

        # Assert
        assert result.kpi_globaux.nb_chantiers == 0
        assert len(result.chantiers) == 0

    def test_filtre_statut_without_port_ignores_filter(self):
        """Test GAP #3: filtre sans port ignore le filtre et retourne tous."""
        # Use case SANS chantier_info_port
        use_case_no_port = GetVueConsolideeFinancesUseCase(
            budget_repository=self.mock_budget_repo,
            lot_repository=self.mock_lot_repo,
            achat_repository=self.mock_achat_repo,
            alerte_repository=self.mock_alerte_repo,
            chantier_info_port=None,
        )

        budget = self._make_budget(1, Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("0")
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        # Act - passe un filtre mais pas de port
        result = use_case_no_port.execute(
            user_accessible_chantier_ids=[1],
            statut_chantier="ferme",
        )

        # Assert - chantier toujours inclus (filtre ignore)
        assert result.kpi_globaux.nb_chantiers == 1


# ============================================================
# GAP #4 - Marge definitive vs estimee
# ============================================================


class TestConsolidationMargeDefinitive:
    """Tests pour la marge definitive (chantier ferme) vs estimee."""

    def setup_method(self):
        """Configuration avec ChantierInfoPort injecte."""
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_alerte_repo = Mock(spec=AlerteRepository)
        self.mock_chantier_info_port = Mock(spec=ChantierInfoPort)

        self.use_case = GetVueConsolideeFinancesUseCase(
            budget_repository=self.mock_budget_repo,
            lot_repository=self.mock_lot_repo,
            achat_repository=self.mock_achat_repo,
            alerte_repository=self.mock_alerte_repo,
            chantier_info_port=self.mock_chantier_info_port,
        )

    def _make_budget(self, chantier_id, initial, avenants=Decimal("0")):
        """Helper pour creer un budget mock."""
        return Budget(
            id=chantier_id * 10,
            chantier_id=chantier_id,
            montant_initial_ht=initial,
            montant_avenants_ht=avenants,
            created_at=datetime(2026, 1, 1),
        )

    def test_marge_definitive_chantier_ferme(self):
        """Test GAP #4: marge definitive basee sur realise pour chantier ferme."""
        # Arrange
        budget = self._make_budget(1, Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # Engage = 70000, Realise = 80000
        # Marge estimee (engage) serait: (100000-70000)/100000 = 30%
        # Marge definitive (realise) doit etre: (100000-80000)/100000 = 20%
        self.mock_achat_repo.somme_by_chantier.side_effect = (
            lambda cid, statuts: Decimal("70000")
            if statuts == STATUTS_ENGAGES
            else Decimal("80000")
        )
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        self.mock_chantier_info_port.get_chantiers_info_batch.return_value = {
            1: ChantierInfoDTO(id=1, nom="Chantier Clos", statut="ferme"),
        }

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1])

        # Assert - marge definitive = 20% (basee sur realise, pas engage)
        assert result.chantiers[0].marge_estimee_pct == "20.00"

    def test_marge_estimee_chantier_en_cours(self):
        """Test GAP #4: marge estimee basee sur engage pour chantier en cours."""
        # Arrange
        budget = self._make_budget(1, Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # Engage = 70000, Realise = 80000
        # Marge estimee (engage) doit etre: (100000-70000)/100000 = 30%
        self.mock_achat_repo.somme_by_chantier.side_effect = (
            lambda cid, statuts: Decimal("70000")
            if statuts == STATUTS_ENGAGES
            else Decimal("80000")
        )
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        self.mock_chantier_info_port.get_chantiers_info_batch.return_value = {
            1: ChantierInfoDTO(id=1, nom="Chantier Actif", statut="en_cours"),
        }

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1])

        # Assert - marge estimee = 30% (basee sur engage)
        assert result.chantiers[0].marge_estimee_pct == "30.00"

    def test_marge_estimee_when_no_port(self):
        """Test GAP #4: sans port, la marge est toujours estimee (basee sur engage)."""
        # Use case SANS port
        use_case_no_port = GetVueConsolideeFinancesUseCase(
            budget_repository=self.mock_budget_repo,
            lot_repository=self.mock_lot_repo,
            achat_repository=self.mock_achat_repo,
            alerte_repository=self.mock_alerte_repo,
            chantier_info_port=None,
        )

        budget = self._make_budget(1, Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        self.mock_achat_repo.somme_by_chantier.side_effect = (
            lambda cid, statuts: Decimal("70000")
            if statuts == STATUTS_ENGAGES
            else Decimal("80000")
        )
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        # Act
        result = use_case_no_port.execute(user_accessible_chantier_ids=[1])

        # Assert - marge estimee = 30% (basee sur engage, car pas de port)
        assert result.chantiers[0].marge_estimee_pct == "30.00"

    def test_marge_definitive_negative_chantier_ferme(self):
        """Test GAP #4: marge definitive negative (realise > budget) pour chantier ferme."""
        # Arrange
        budget = self._make_budget(1, Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # Realise = 120000 -> marge definitive = (100000-120000)/100000 = -20%
        self.mock_achat_repo.somme_by_chantier.side_effect = (
            lambda cid, statuts: Decimal("90000")
            if statuts == STATUTS_ENGAGES
            else Decimal("120000")
        )
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        self.mock_chantier_info_port.get_chantiers_info_batch.return_value = {
            1: ChantierInfoDTO(id=1, nom="Chantier Deficit", statut="ferme"),
        }

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1])

        # Assert - marge definitive negative
        assert result.chantiers[0].marge_estimee_pct == "-20.00"

    def test_marge_moyenne_mix_ferme_et_en_cours(self):
        """Test GAP #4: marge moyenne combine definitives et estimees."""
        # Arrange
        budgets = {
            1: self._make_budget(1, Decimal("100000")),
            2: self._make_budget(2, Decimal("100000")),
        }
        self.mock_budget_repo.find_by_chantier_id.side_effect = lambda cid: budgets.get(cid)

        # Chantier 1 (ferme): engage=70000, realise=80000 -> marge_definitive = 20%
        # Chantier 2 (en_cours): engage=40000, realise=30000 -> marge_estimee = 60%
        # Marge moyenne = (20 + 60) / 2 = 40%
        engage_map = {
            (1, tuple(STATUTS_ENGAGES)): Decimal("70000"),
            (2, tuple(STATUTS_ENGAGES)): Decimal("40000"),
            (1, tuple(STATUTS_REALISES)): Decimal("80000"),
            (2, tuple(STATUTS_REALISES)): Decimal("30000"),
        }

        def somme_by_chantier(cid, statuts):
            return engage_map.get((cid, tuple(statuts)), Decimal("0"))

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_alerte_repo.find_non_acquittees.return_value = []

        self.mock_chantier_info_port.get_chantiers_info_batch.return_value = {
            1: ChantierInfoDTO(id=1, nom="Clos", statut="ferme"),
            2: ChantierInfoDTO(id=2, nom="Actif", statut="en_cours"),
        }

        # Act
        result = self.use_case.execute(user_accessible_chantier_ids=[1, 2])

        # Assert
        assert result.kpi_globaux.marge_moyenne_pct == "40.00"
