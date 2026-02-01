"""Tests unitaires pour les Use Cases Suggestions du module Financier.

FIN-21/22 Phase 3: Tests pour les suggestions financieres deterministes
et les indicateurs predictifs. Tests du use case
GetSuggestionsFinancieresUseCase avec regles algorithmiques.
"""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch

from modules.financier.domain.entities import Budget, LotBudgetaire
from modules.financier.domain.repositories import (
    BudgetRepository,
    AchatRepository,
    LotBudgetaireRepository,
    AlerteRepository,
)
from modules.financier.domain.value_objects import UniteMesure
from modules.financier.domain.value_objects.statuts_financiers import (
    STATUTS_ENGAGES,
    STATUTS_REALISES,
)
from modules.financier.application.use_cases.suggestions_use_cases import (
    GetSuggestionsFinancieresUseCase,
)
from modules.financier.application.use_cases.budget_use_cases import (
    BudgetNotFoundError,
)


class TestGetSuggestionsFinancieresUseCase:
    """Tests pour le use case de suggestions financieres."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_alerte_repo = Mock(spec=AlerteRepository)

        self.use_case = GetSuggestionsFinancieresUseCase(
            budget_repository=self.mock_budget_repo,
            achat_repository=self.mock_achat_repo,
            lot_repository=self.mock_lot_repo,
            alerte_repository=self.mock_alerte_repo,
        )

    def _make_budget(
        self,
        chantier_id=1,
        initial=Decimal("100000"),
        avenants=Decimal("0"),
        created_at=None,
    ):
        """Helper pour creer un budget."""
        return Budget(
            id=chantier_id * 10,
            chantier_id=chantier_id,
            montant_initial_ht=initial,
            montant_avenants_ht=avenants,
            created_at=created_at or datetime(2026, 1, 1),
        )

    def test_nominal_avec_suggestions(self):
        """Test: nominal retourne suggestions et indicateurs predictifs."""
        # Arrange
        budget = self._make_budget(initial=Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # pct_engage = 95%, marge = 5% -> declenche CREATE_AVENANT
        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return Decimal("95000")
            return Decimal("60000")

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_lot_repo.find_by_budget_id.return_value = []
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        assert result.chantier_id == 1
        assert len(result.suggestions) > 0
        assert result.indicateurs is not None
        assert result.indicateurs.burn_rate_mensuel != ""
        assert result.indicateurs.budget_moyen_mensuel != ""

    def test_budget_not_found_raises_error(self):
        """Test: erreur BudgetNotFoundError si pas de budget."""
        # Arrange
        self.mock_budget_repo.find_by_chantier_id.return_value = None

        # Act & Assert
        with pytest.raises(BudgetNotFoundError):
            self.use_case.execute(chantier_id=999)

    def test_suggestion_create_avenant(self):
        """Test: suggestion CREATE_AVENANT quand pct_engage > 90% et marge < 10%."""
        # Arrange
        budget = self._make_budget(initial=Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # pct_engage = 95%, marge = 5%
        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return Decimal("95000")
            return Decimal("40000")

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_lot_repo.find_by_budget_id.return_value = []
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        avenant_suggestions = [s for s in result.suggestions if s.type == "CREATE_AVENANT"]
        assert len(avenant_suggestions) == 1
        assert avenant_suggestions[0].severity == "CRITICAL"
        assert "avenant" in avenant_suggestions[0].titre.lower()
        assert "95.0%" in avenant_suggestions[0].description
        assert "5.0%" in avenant_suggestions[0].description

    def test_no_create_avenant_when_marge_sufficient(self):
        """Test: pas de CREATE_AVENANT quand marge >= 10% meme si engage > 90%."""
        # Arrange
        budget = self._make_budget(initial=Decimal("100000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # pct_engage = 85%, marge = 15% -> pas de CREATE_AVENANT
        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return Decimal("85000")
            return Decimal("40000")

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_lot_repo.find_by_budget_id.return_value = []
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        avenant_suggestions = [s for s in result.suggestions if s.type == "CREATE_AVENANT"]
        assert len(avenant_suggestions) == 0

    def test_suggestion_alert_burn_rate(self):
        """Test: suggestion ALERT_BURN_RATE quand burn_rate > budget_moyen * 1.2."""
        # Arrange - budget cree il y a 2 mois, realise elevee
        budget = self._make_budget(
            initial=Decimal("120000"),
            created_at=datetime(2025, 12, 1),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # Engage 60000, Realise 100000 (sur ~3 mois -> burn 33333/mois vs budget_moyen 40000/mois)
        # Il faut que burn_rate > budget_moyen * 1.2
        # Budget moyen = 120000 / 3 = 40000/mois
        # Pour declencher: burn_rate > 48000 -> realise > 48000 * 3 = 144000
        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return Decimal("60000")  # engage faible pour eviter CREATE_AVENANT
            return Decimal("150000")  # realise eleve -> burn_rate = 150000/3 = 50000

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_lot_repo.find_by_budget_id.return_value = []
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        burn_suggestions = [s for s in result.suggestions if s.type == "ALERT_BURN_RATE"]
        assert len(burn_suggestions) == 1
        assert burn_suggestions[0].severity == "WARNING"
        assert "rythme de depense" in burn_suggestions[0].titre.lower()

    def test_suggestion_optimize_lots(self):
        """Test: suggestion OPTIMIZE_LOTS quand un lot depasse le prevu de > 30%."""
        # Arrange
        budget = self._make_budget(initial=Decimal("50000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # Engage faible pour eviter CREATE_AVENANT
        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return Decimal("20000")
            return Decimal("10000")

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier

        # Lot avec ecart > 30%: prevu 10000, engage 14000 -> ecart 40%
        lot = LotBudgetaire(
            id=1,
            budget_id=10,
            code_lot="LOT01",
            libelle="Gros oeuvre",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("100"),  # total_prevu = 10000
        )
        self.mock_lot_repo.find_by_budget_id.return_value = [lot]
        self.mock_achat_repo.somme_by_lot.return_value = Decimal("14000")
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        lot_suggestions = [s for s in result.suggestions if s.type == "OPTIMIZE_LOTS"]
        assert len(lot_suggestions) == 1
        assert lot_suggestions[0].severity == "WARNING"
        assert "LOT01" in lot_suggestions[0].titre
        assert "LOT01" in lot_suggestions[0].description

    def test_no_optimize_lots_when_within_threshold(self):
        """Test: pas de OPTIMIZE_LOTS quand ecart lot <= 30%."""
        # Arrange
        budget = self._make_budget(initial=Decimal("50000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return Decimal("20000")
            return Decimal("10000")

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier

        # Lot avec ecart 20% (dans la limite): prevu 10000, engage 12000
        lot = LotBudgetaire(
            id=1,
            budget_id=10,
            code_lot="LOT01",
            libelle="Gros oeuvre",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("100"),
        )
        self.mock_lot_repo.find_by_budget_id.return_value = [lot]
        self.mock_achat_repo.somme_by_lot.return_value = Decimal("12000")
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        lot_suggestions = [s for s in result.suggestions if s.type == "OPTIMIZE_LOTS"]
        assert len(lot_suggestions) == 0

    def test_indicateurs_predictifs_calcul(self):
        """Test: indicateurs predictifs correctement calcules."""
        # Arrange - budget cree il y a 2 mois (jan 2026), aujourd'hui fev 2026
        budget = self._make_budget(
            initial=Decimal("120000"),
            created_at=datetime(2026, 1, 1),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # Engage 60000, Realise 40000
        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return Decimal("60000")
            return Decimal("40000")

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_lot_repo.find_by_budget_id.return_value = []
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        indicateurs = result.indicateurs

        # nb_mois = max(1, (2026-2026)*12 + (2-1) + 1) = 2
        # burn_rate = 40000 / 2 = 20000
        assert indicateurs.burn_rate_mensuel == "20000.00"

        # budget_moyen = 120000 / 2 = 60000
        assert indicateurs.budget_moyen_mensuel == "60000.00"

        # ecart = ((20000 - 60000) / 60000) * 100 = -66.67%
        assert indicateurs.ecart_burn_rate_pct == "-66.67"

        # reste = 120000 - 60000 = 60000
        # mois_restants = 60000 / 20000 = 3
        assert indicateurs.mois_restants_budget == "3.00"

        # date_epuisement = today + 3 * 30 = today + 90 jours
        assert indicateurs.date_epuisement_estimee != "N/A"

        # avancement = (40000 / 120000) * 100 = 33.33%
        assert indicateurs.avancement_financier_pct == "33.33"

    def test_aucune_suggestion_chantier_sain(self):
        """Test: aucune suggestion pour un chantier sain (faible engagement, bonne marge)."""
        # Arrange - budget petit (< 100k), engage faible, marge large
        budget = self._make_budget(initial=Decimal("50000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # Engage 20% -> marge 80%, bien en dessous de tous les seuils
        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return Decimal("10000")
            return Decimal("5000")  # realise < engage, pas de REDUCE_COSTS

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_lot_repo.find_by_budget_id.return_value = []
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert - aucune suggestion (sauf potentiellement INFO si budget > 100k)
        assert len(result.suggestions) == 0

    def test_suggestion_create_situation_big_budget(self):
        """Test: suggestion CREATE_SITUATION pour budget > 100k EUR."""
        # Arrange
        budget = self._make_budget(initial=Decimal("150000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # Engage faible pour eviter d'autres suggestions
        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return Decimal("30000")
            return Decimal("15000")

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_lot_repo.find_by_budget_id.return_value = []
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        sit_suggestions = [s for s in result.suggestions if s.type == "CREATE_SITUATION"]
        assert len(sit_suggestions) == 1
        assert sit_suggestions[0].severity == "INFO"
        assert "100 000" in sit_suggestions[0].description

    def test_suggestions_sorted_by_severity(self):
        """Test: suggestions triees par severite (CRITICAL > WARNING > INFO)."""
        # Arrange - declencher plusieurs regles simultanement
        budget = self._make_budget(initial=Decimal("200000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # pct_engage = 95%, marge = 5% -> CRITICAL (CREATE_AVENANT)
        # budget > 100k -> INFO (CREATE_SITUATION)
        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return Decimal("190000")
            return Decimal("100000")

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_lot_repo.find_by_budget_id.return_value = []
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert - CRITICAL doit etre en premier
        if len(result.suggestions) >= 2:
            severities = [s.severity for s in result.suggestions]
            severity_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
            for i in range(len(severities) - 1):
                assert severity_order[severities[i]] <= severity_order[severities[i + 1]]

    def test_max_5_suggestions(self):
        """Test: maximum 5 suggestions retournees."""
        # Arrange
        budget = self._make_budget(initial=Decimal("200000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # Declencher beaucoup de suggestions via lots en depassement
        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return Decimal("190000")  # 95% -> CREATE_AVENANT
            return Decimal("100000")

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier

        # 10 lots en depassement > 30%
        lots = []
        for i in range(10):
            lot = LotBudgetaire(
                id=i + 1,
                budget_id=10,
                code_lot=f"LOT{i:02d}",
                libelle=f"Lot test {i}",
                quantite_prevue=Decimal("100"),
                prix_unitaire_ht=Decimal("100"),  # prevu = 10000
            )
            lots.append(lot)

        self.mock_lot_repo.find_by_budget_id.return_value = lots
        # Tous les lots en depassement de 50%
        self.mock_achat_repo.somme_by_lot.return_value = Decimal("15000")
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        assert len(result.suggestions) <= 5

    def test_suggestion_reduce_costs_realise_depasse_engage(self):
        """Test: suggestion REDUCE_COSTS quand realise > engage + 10 points."""
        # Arrange
        budget = self._make_budget(initial=Decimal("80000"))  # < 100k pour eviter CREATE_SITUATION
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # pct_engage = 50%, pct_realise = 65% -> ecart 15 points > 10 -> REDUCE_COSTS
        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return Decimal("40000")  # 50%
            return Decimal("52000")  # 65%

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_lot_repo.find_by_budget_id.return_value = []
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        reduce_suggestions = [s for s in result.suggestions if s.type == "REDUCE_COSTS"]
        assert len(reduce_suggestions) == 1
        assert reduce_suggestions[0].severity == "WARNING"
        assert "realise" in reduce_suggestions[0].titre.lower() or "réalisé" in reduce_suggestions[0].titre.lower()

    def test_indicateurs_date_epuisement_na_when_no_depense(self):
        """Test: date_epuisement = N/A quand aucune depense realisee."""
        # Arrange
        budget = self._make_budget(initial=Decimal("50000"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        def somme_by_chantier(cid, statuts):
            return Decimal("0")  # rien engage, rien realise

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_lot_repo.find_by_budget_id.return_value = []
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        assert result.indicateurs.date_epuisement_estimee == "N/A"
        assert result.indicateurs.mois_restants_budget == "0.00"

    def test_indicateurs_avancement_zero_budget(self):
        """Test: avancement = 0% quand montant_revise = 0."""
        # Arrange
        budget = self._make_budget(initial=Decimal("0"))
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("0")
        self.mock_lot_repo.find_by_budget_id.return_value = []
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        assert result.indicateurs.avancement_financier_pct == "0.00"
        assert result.indicateurs.ecart_burn_rate_pct == "0.00"


class TestGetSuggestionsWithAIProvider:
    """Tests pour le use case avec AI provider (FIN-21)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_alerte_repo = Mock(spec=AlerteRepository)
        self.mock_ai_provider = Mock()

        self.use_case = GetSuggestionsFinancieresUseCase(
            budget_repository=self.mock_budget_repo,
            achat_repository=self.mock_achat_repo,
            lot_repository=self.mock_lot_repo,
            alerte_repository=self.mock_alerte_repo,
            ai_provider=self.mock_ai_provider,
        )

    def _make_budget(
        self,
        chantier_id=1,
        initial=Decimal("100000"),
        avenants=Decimal("0"),
        created_at=None,
    ):
        """Helper pour creer un budget."""
        return Budget(
            id=chantier_id * 10,
            chantier_id=chantier_id,
            montant_initial_ht=initial,
            montant_avenants_ht=avenants,
            created_at=created_at or datetime(2026, 1, 1),
        )

    def _setup_basic_mocks(self, budget=None, engage=Decimal("50000"), realise=Decimal("30000")):
        """Setup commun pour les mocks de base."""
        if budget is None:
            budget = self._make_budget()
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        def somme_by_chantier(cid, statuts):
            if statuts == STATUTS_ENGAGES:
                return engage
            return realise

        self.mock_achat_repo.somme_by_chantier.side_effect = somme_by_chantier
        self.mock_lot_repo.find_by_budget_id.return_value = []
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

    def test_ai_provider_called_when_available(self):
        """Test: le provider IA est appele quand il est disponible."""
        # Arrange
        self._setup_basic_mocks()
        self.mock_ai_provider.generate_suggestions.return_value = []

        # Act
        self.use_case.execute(chantier_id=1)

        # Assert
        self.mock_ai_provider.generate_suggestions.assert_called_once()
        call_args = self.mock_ai_provider.generate_suggestions.call_args[0][0]
        assert "montant_revise" in call_args
        assert "total_engage" in call_args
        assert "pct_engage" in call_args
        assert "burn_rate" in call_args

    def test_ai_suggestions_merged_with_algo(self):
        """Test: les suggestions IA sont fusionnees avec les algorithmiques."""
        # Arrange
        self._setup_basic_mocks(engage=Decimal("95000"))  # declenche CREATE_AVENANT
        from modules.financier.application.dtos.suggestions_dtos import SuggestionDTO

        ai_suggestion = SuggestionDTO(
            type="RENEGOCIATE_SUPPLIERS",
            severity="WARNING",
            titre="Renegocier les fournisseurs",
            description="Description IA renegociation",
            impact_estime_eur="5000.00",
        )
        self.mock_ai_provider.generate_suggestions.return_value = [ai_suggestion]

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        assert result.ai_available is True
        assert result.source == "gemini"
        types = [s.type for s in result.suggestions]
        assert "RENEGOCIATE_SUPPLIERS" in types
        # L'algo CREATE_AVENANT devrait aussi etre present (pas doublon)
        assert "CREATE_AVENANT" in types

    def test_ai_deduplication_by_type(self):
        """Test: deduplication IA vs algo par type (IA prioritaire)."""
        # Arrange
        self._setup_basic_mocks(engage=Decimal("95000"))  # declenche CREATE_AVENANT algo
        from modules.financier.application.dtos.suggestions_dtos import SuggestionDTO

        # IA retourne aussi CREATE_AVENANT -> devrait remplacer l'algo
        ai_suggestion = SuggestionDTO(
            type="CREATE_AVENANT",
            severity="CRITICAL",
            titre="Avenant recommande par IA",
            description="Description IA avenant plus detaillee",
            impact_estime_eur="10000.00",
        )
        self.mock_ai_provider.generate_suggestions.return_value = [ai_suggestion]

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        avenant_suggestions = [s for s in result.suggestions if s.type == "CREATE_AVENANT"]
        assert len(avenant_suggestions) == 1
        # La suggestion IA a la priorite
        assert avenant_suggestions[0].titre == "Avenant recommande par IA"

    def test_ai_provider_error_fallback_to_algo(self):
        """Test: fallback silencieux aux regles algo si le provider IA echoue."""
        # Arrange
        self._setup_basic_mocks(engage=Decimal("95000"))  # declenche CREATE_AVENANT
        self.mock_ai_provider.generate_suggestions.side_effect = Exception("API error")

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        assert result.ai_available is False
        assert result.source == "algorithmic"
        assert len(result.suggestions) > 0
        avenant_suggestions = [s for s in result.suggestions if s.type == "CREATE_AVENANT"]
        assert len(avenant_suggestions) == 1

    def test_ai_provider_returns_empty_list_fallback(self):
        """Test: fallback quand l'IA retourne une liste vide."""
        # Arrange
        self._setup_basic_mocks(engage=Decimal("95000"))
        self.mock_ai_provider.generate_suggestions.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        assert result.ai_available is False
        assert result.source == "algorithmic"

    def test_ai_kpi_data_format(self):
        """Test: les KPI sont correctement formates pour l'IA."""
        # Arrange
        self._setup_basic_mocks(
            budget=self._make_budget(initial=Decimal("200000")),
            engage=Decimal("100000"),
            realise=Decimal("50000"),
        )
        self.mock_ai_provider.generate_suggestions.return_value = []

        # Act
        self.use_case.execute(chantier_id=1)

        # Assert
        call_args = self.mock_ai_provider.generate_suggestions.call_args[0][0]
        assert call_args["montant_revise"] == "200000.00"
        assert call_args["total_engage"] == "100000.00"
        assert call_args["total_realise"] == "50000.00"
        assert call_args["pct_engage"] == "50.00"
        assert call_args["pct_realise"] == "25.00"
        assert call_args["marge_pct"] == "50.00"
        assert call_args["reste_a_depenser"] == "100000.00"

    def test_no_ai_provider_uses_algo_only(self):
        """Test: sans ai_provider, seul algorithmic est utilise."""
        # Arrange
        use_case_no_ai = GetSuggestionsFinancieresUseCase(
            budget_repository=self.mock_budget_repo,
            achat_repository=self.mock_achat_repo,
            lot_repository=self.mock_lot_repo,
            alerte_repository=self.mock_alerte_repo,
            ai_provider=None,
        )
        budget = self._make_budget()
        self.mock_budget_repo.find_by_chantier_id.return_value = budget
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("50000")
        self.mock_lot_repo.find_by_budget_id.return_value = []
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        # Act
        result = use_case_no_ai.execute(chantier_id=1)

        # Assert
        assert result.ai_available is False
        assert result.source == "algorithmic"

    def test_fusion_preserves_severity_order(self):
        """Test: la fusion IA+algo preserve l'ordre par severite."""
        # Arrange
        self._setup_basic_mocks(
            budget=self._make_budget(initial=Decimal("200000")),
            engage=Decimal("190000"),  # declenche CREATE_AVENANT CRITICAL
        )
        from modules.financier.application.dtos.suggestions_dtos import SuggestionDTO

        ai_suggestions = [
            SuggestionDTO(
                type="REVIEW_PLANNING",
                severity="INFO",
                titre="Revoir le planning",
                description="Description IA planning",
                impact_estime_eur="0",
            ),
            SuggestionDTO(
                type="RENEGOCIATE_SUPPLIERS",
                severity="WARNING",
                titre="Renegocier",
                description="Description IA renegociation",
                impact_estime_eur="3000.00",
            ),
        ]
        self.mock_ai_provider.generate_suggestions.return_value = ai_suggestions

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert - CRITICAL avant WARNING avant INFO
        severities = [s.severity for s in result.suggestions]
        severity_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
        for i in range(len(severities) - 1):
            assert severity_order[severities[i]] <= severity_order[severities[i + 1]]


class TestFusionnerSuggestions:
    """Tests pour la methode _fusionner_suggestions."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.use_case = GetSuggestionsFinancieresUseCase(
            budget_repository=Mock(spec=BudgetRepository),
            achat_repository=Mock(spec=AchatRepository),
            lot_repository=Mock(spec=LotBudgetaireRepository),
            alerte_repository=Mock(spec=AlerteRepository),
        )

    def test_fusion_empty_ia_returns_algo(self):
        """Test: si IA vide, retourne les algo."""
        from modules.financier.application.dtos.suggestions_dtos import SuggestionDTO
        algo = [
            SuggestionDTO(type="CREATE_AVENANT", severity="CRITICAL",
                          titre="T", description="D", impact_estime_eur="0"),
        ]
        result = self.use_case._fusionner_suggestions([], algo)
        assert len(result) == 1
        assert result[0].type == "CREATE_AVENANT"

    def test_fusion_empty_algo_returns_ia(self):
        """Test: si algo vide, retourne les IA."""
        from modules.financier.application.dtos.suggestions_dtos import SuggestionDTO
        ia = [
            SuggestionDTO(type="RENEGOCIATE_SUPPLIERS", severity="WARNING",
                          titre="T", description="D", impact_estime_eur="0"),
        ]
        result = self.use_case._fusionner_suggestions(ia, [])
        assert len(result) == 1
        assert result[0].type == "RENEGOCIATE_SUPPLIERS"

    def test_fusion_dedup_same_type_keeps_ia(self):
        """Test: meme type -> garde IA, ignore algo."""
        from modules.financier.application.dtos.suggestions_dtos import SuggestionDTO
        ia = [
            SuggestionDTO(type="CREATE_AVENANT", severity="CRITICAL",
                          titre="IA Avenant", description="D IA", impact_estime_eur="100"),
        ]
        algo = [
            SuggestionDTO(type="CREATE_AVENANT", severity="CRITICAL",
                          titre="Algo Avenant", description="D Algo", impact_estime_eur="50"),
        ]
        result = self.use_case._fusionner_suggestions(ia, algo)
        assert len(result) == 1
        assert result[0].titre == "IA Avenant"

    def test_fusion_different_types_merged(self):
        """Test: types differents -> tous inclus."""
        from modules.financier.application.dtos.suggestions_dtos import SuggestionDTO
        ia = [
            SuggestionDTO(type="RENEGOCIATE_SUPPLIERS", severity="WARNING",
                          titre="IA", description="D", impact_estime_eur="0"),
        ]
        algo = [
            SuggestionDTO(type="CREATE_AVENANT", severity="CRITICAL",
                          titre="Algo", description="D", impact_estime_eur="0"),
        ]
        result = self.use_case._fusionner_suggestions(ia, algo)
        assert len(result) == 2

    def test_fusion_sorted_by_severity(self):
        """Test: resultat trie par severite."""
        from modules.financier.application.dtos.suggestions_dtos import SuggestionDTO
        ia = [
            SuggestionDTO(type="REVIEW_PLANNING", severity="INFO",
                          titre="T", description="D", impact_estime_eur="0"),
        ]
        algo = [
            SuggestionDTO(type="CREATE_AVENANT", severity="CRITICAL",
                          titre="T", description="D", impact_estime_eur="0"),
        ]
        result = self.use_case._fusionner_suggestions(ia, algo)
        assert result[0].severity == "CRITICAL"
        assert result[1].severity == "INFO"
