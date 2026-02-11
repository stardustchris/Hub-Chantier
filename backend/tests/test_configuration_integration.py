"""Tests d'integration : ConfigurationEntreprise -> calculs financiers.

Verifie que le flux complet fonctionne :
  config DB -> coefficients -> calcul financier (dashboard, PnL, cout MO).

Pattern :
  - Les repositories sont mockes (pas de DB reelle).
  - Le config_repository mock retourne une ConfigurationEntreprise entity
    avec les coefficients souhaites.
  - On verifie que les use cases produisent les bons resultats numeriques.

Convention : assertions sur Decimal (via str dans les DTOs).
"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

from modules.financier.domain.entities import (
    Budget,
    ConfigurationEntreprise,
    SituationTravaux,
    FactureClient,
)
from modules.financier.domain.repositories import (
    BudgetRepository,
    LotBudgetaireRepository,
    AchatRepository,
    SituationRepository,
    CoutMainOeuvreRepository,
    CoutMaterielRepository,
    FactureRepository,
    ConfigurationEntrepriseRepository,
)
from modules.financier.application.use_cases.dashboard_use_cases import (
    GetDashboardFinancierUseCase,
)
from modules.financier.application.use_cases.pnl_use_cases import (
    GetPnLChantierUseCase,
)
from modules.financier.infrastructure.persistence.sqlalchemy_cout_main_oeuvre_repository import (
    SQLAlchemyCoutMainOeuvreRepository,
)
from shared.domain.calcul_financier import (
    COEFF_FRAIS_GENERAUX,
    COEFF_CHARGES_PATRONALES,
    COEFF_HEURES_SUP,
    COEFF_HEURES_SUP_2,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_budget(chantier_id: int = 100, montant_ht: str = "500000") -> Budget:
    """Cree un Budget de test."""
    return Budget(
        id=1,
        chantier_id=chantier_id,
        montant_initial_ht=Decimal(montant_ht),
        created_at=datetime.utcnow(),
    )


def _make_config(
    coeff_fg: str = "19",
    coeff_charges: str = "1.45",
    coeff_hs: str = "1.25",
    coeff_hs_2: str = "1.50",
    annee: int = 2026,
) -> ConfigurationEntreprise:
    """Cree une ConfigurationEntreprise de test."""
    return ConfigurationEntreprise(
        id=1,
        annee=annee,
        coeff_frais_generaux=Decimal(coeff_fg),
        coeff_charges_patronales=Decimal(coeff_charges),
        coeff_heures_sup=Decimal(coeff_hs),
        coeff_heures_sup_2=Decimal(coeff_hs_2),
    )


def _make_situation(
    chantier_id: int = 100,
    montant_cumule_ht: str = "200000",
) -> SituationTravaux:
    """Cree une SituationTravaux de test."""
    return SituationTravaux(
        id=1,
        chantier_id=chantier_id,
        budget_id=1,
        numero="SIT-001",
        montant_cumule_ht=Decimal(montant_cumule_ht),
        montant_periode_ht=Decimal(montant_cumule_ht),
        created_at=datetime.utcnow(),
    )


def _make_facture(
    chantier_id: int = 100,
    montant_ht: str = "200000",
    statut: str = "emise",
) -> FactureClient:
    """Cree une FactureClient de test."""
    return FactureClient(
        id=1,
        chantier_id=chantier_id,
        numero_facture="FAC-2026-001",
        montant_ht=Decimal(montant_ht),
        statut=statut,
    )


# ===========================================================================
# Test 1 : Config FG impacte dashboard
# ===========================================================================

class TestConfigFGImpacteDashboard:
    """Scenario: Admin change coeff_frais_generaux de 19 a 25.

    Given: un chantier avec debourse_sec = 100 000 EUR
    When: config DB a coeff_fg = 25
    Then: la marge du dashboard utilise quote_part = 25 000 EUR (pas 19 000).

    Verification par le calcul de la marge :
        debourse_sec = 100 000 (total_realise seul, MO=0, materiel=0)
        quote_part = 100 000 * 25 / 100 = 25 000
        prix_vente (situation) = 200 000
        marge = (200 000 - (100 000 + 0 + 0 + 25 000)) / 200 000 * 100 = 37.50%
    """

    def setup_method(self):
        """Configure les mocks pour le dashboard complet."""
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_situation_repo = Mock(spec=SituationRepository)
        self.mock_cout_mo_repo = Mock(spec=CoutMainOeuvreRepository)
        self.mock_cout_materiel_repo = Mock(spec=CoutMaterielRepository)
        self.mock_config_repo = Mock(spec=ConfigurationEntrepriseRepository)

        # Budget 500k
        self.mock_budget_repo.find_by_chantier_id.return_value = _make_budget()

        # Achats : engage=150k, realise=100k (debourse_sec)
        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("150000"),  # total_engage
            Decimal("100000"),  # total_realise
        ]
        self.mock_achat_repo.find_by_chantier.return_value = []
        self.mock_lot_repo.find_by_budget_id.return_value = []

        # Situation : 200k de CA facture au client
        self.mock_situation_repo.find_derniere_situation.return_value = (
            _make_situation(montant_cumule_ht="200000")
        )

        # MO et materiel : 0 pour isoler l'impact FG
        self.mock_cout_mo_repo.calculer_cout_chantier.return_value = Decimal("0")
        self.mock_cout_materiel_repo.calculer_cout_chantier.return_value = Decimal("0")

    def test_dashboard_marge_avec_config_fg_25(self):
        """Config coeff_fg=25 -> quote_part = 25000, marge = 37.50%."""
        config = _make_config(coeff_fg="25")
        self.mock_config_repo.find_by_annee.return_value = config

        use_case = GetDashboardFinancierUseCase(
            budget_repository=self.mock_budget_repo,
            lot_repository=self.mock_lot_repo,
            achat_repository=self.mock_achat_repo,
            situation_repository=self.mock_situation_repo,
            cout_mo_repository=self.mock_cout_mo_repo,
            cout_materiel_repository=self.mock_cout_materiel_repo,
            config_repository=self.mock_config_repo,
        )

        result = use_case.execute(chantier_id=100)

        # debourse_sec = 100k + 0 + 0 = 100k
        # quote_part = 100k * 25 / 100 = 25k
        # cout_revient = 100k + 0 + 0 + 25k = 125k
        # marge = (200k - 125k) / 200k * 100 = 37.50
        assert result.kpi.marge_estimee == "37.50"
        assert result.kpi.marge_statut == "calculee"

    def test_dashboard_marge_avec_config_fg_19_par_defaut(self):
        """Config coeff_fg=19 (defaut) -> quote_part = 19000, marge = 40.50%."""
        config = _make_config(coeff_fg="19")
        self.mock_config_repo.find_by_annee.return_value = config

        # Reset side_effect car deja consomme
        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("150000"),
            Decimal("100000"),
        ]

        use_case = GetDashboardFinancierUseCase(
            budget_repository=self.mock_budget_repo,
            lot_repository=self.mock_lot_repo,
            achat_repository=self.mock_achat_repo,
            situation_repository=self.mock_situation_repo,
            cout_mo_repository=self.mock_cout_mo_repo,
            cout_materiel_repository=self.mock_cout_materiel_repo,
            config_repository=self.mock_config_repo,
        )

        result = use_case.execute(chantier_id=100)

        # debourse_sec = 100k
        # quote_part = 100k * 19 / 100 = 19k
        # cout_revient = 100k + 0 + 0 + 19k = 119k
        # marge = (200k - 119k) / 200k * 100 = 40.50
        assert result.kpi.marge_estimee == "40.50"

    def test_dashboard_fg_25_vs_19_difference(self):
        """Verifie que changer le coeff FG impacte bien la marge dashboard."""
        # Calcul avec coeff_fg=25
        self.mock_config_repo.find_by_annee.return_value = _make_config(coeff_fg="25")

        use_case_25 = GetDashboardFinancierUseCase(
            budget_repository=self.mock_budget_repo,
            lot_repository=self.mock_lot_repo,
            achat_repository=self.mock_achat_repo,
            situation_repository=self.mock_situation_repo,
            cout_mo_repository=self.mock_cout_mo_repo,
            cout_materiel_repository=self.mock_cout_materiel_repo,
            config_repository=self.mock_config_repo,
        )

        result_25 = use_case_25.execute(chantier_id=100)

        # Reset mocks pour le 2e appel
        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("150000"),
            Decimal("100000"),
        ]
        self.mock_config_repo.find_by_annee.return_value = _make_config(coeff_fg="19")

        use_case_19 = GetDashboardFinancierUseCase(
            budget_repository=self.mock_budget_repo,
            lot_repository=self.mock_lot_repo,
            achat_repository=self.mock_achat_repo,
            situation_repository=self.mock_situation_repo,
            cout_mo_repository=self.mock_cout_mo_repo,
            cout_materiel_repository=self.mock_cout_materiel_repo,
            config_repository=self.mock_config_repo,
        )

        result_19 = use_case_19.execute(chantier_id=100)

        # La marge avec FG=25 est inferieure (plus de frais generaux)
        marge_25 = Decimal(result_25.kpi.marge_estimee)
        marge_19 = Decimal(result_19.kpi.marge_estimee)
        assert marge_25 < marge_19
        # Difference exacte : 40.50 - 37.50 = 3.00 points
        assert marge_19 - marge_25 == Decimal("3.00")


# ===========================================================================
# Test 2 : Config charges patronales impacte cout MO
# ===========================================================================

class TestConfigChargesImpacteMO:
    """Scenario: Admin change coeff_charges_patronales de 1.45 a 1.55.

    Given: un employe avec taux_horaire_brut = 20 EUR, 40h/semaine
    When: config DB a coeff_charges = 1.55
    Then: cout_horaire_charge = 31.00 EUR (pas 29.00)

    Le test verifie que SQLAlchemyCoutMainOeuvreRepository._get_coefficients()
    lit bien la config et retourne les bons coefficients.
    Le calcul final (SQL) n'est pas execute (pas de DB), mais on verifie
    que les coefficients corrects sont passes.
    """

    def test_get_coefficients_avec_config_charges_155(self):
        """Config coeff_charges=1.55 -> _get_coefficients retourne 1.55."""
        mock_session = Mock()
        mock_config_repo = Mock(spec=ConfigurationEntrepriseRepository)
        config = _make_config(coeff_charges="1.55")
        mock_config_repo.find_by_annee.return_value = config

        repo = SQLAlchemyCoutMainOeuvreRepository(
            session=mock_session,
            config_repository=mock_config_repo,
        )

        coeff_charges, coeff_hs_1, coeff_hs_2 = repo._get_coefficients()

        assert coeff_charges == Decimal("1.55")
        assert coeff_hs_1 == Decimal("1.25")
        assert coeff_hs_2 == Decimal("1.50")

    def test_get_coefficients_avec_config_charges_145_defaut(self):
        """Config coeff_charges=1.45 (defaut) -> _get_coefficients retourne 1.45."""
        mock_session = Mock()
        mock_config_repo = Mock(spec=ConfigurationEntrepriseRepository)
        config = _make_config(coeff_charges="1.45")
        mock_config_repo.find_by_annee.return_value = config

        repo = SQLAlchemyCoutMainOeuvreRepository(
            session=mock_session,
            config_repository=mock_config_repo,
        )

        coeff_charges, coeff_hs_1, coeff_hs_2 = repo._get_coefficients()

        assert coeff_charges == Decimal("1.45")

    def test_cout_horaire_charge_avec_config(self):
        """Verifie le calcul : taux_brut=20, coeff=1.55 -> charge=31.00."""
        taux_horaire_brut = Decimal("20")

        # Avec coeff 1.55 (nouvelle config)
        cout_155 = taux_horaire_brut * Decimal("1.55")
        assert cout_155 == Decimal("31.00")

        # Avec coeff 1.45 (ancienne config / defaut)
        cout_145 = taux_horaire_brut * Decimal("1.45")
        assert cout_145 == Decimal("29.00")

        # Difference : +2 EUR/heure
        assert cout_155 - cout_145 == Decimal("2.00")

    def test_get_coefficients_tous_modifies(self):
        """Config avec tous les coefficients MO modifies."""
        mock_session = Mock()
        mock_config_repo = Mock(spec=ConfigurationEntrepriseRepository)
        config = _make_config(
            coeff_charges="1.55",
            coeff_hs="1.30",
            coeff_hs_2="1.60",
        )
        mock_config_repo.find_by_annee.return_value = config

        repo = SQLAlchemyCoutMainOeuvreRepository(
            session=mock_session,
            config_repository=mock_config_repo,
        )

        coeff_charges, coeff_hs_1, coeff_hs_2 = repo._get_coefficients()

        assert coeff_charges == Decimal("1.55")
        assert coeff_hs_1 == Decimal("1.30")
        assert coeff_hs_2 == Decimal("1.60")

    def test_impact_cout_hebdo_employe(self):
        """Verifie l'impact sur le cout hebdomadaire d'un employe.

        Employe : taux_brut = 20 EUR/h, 40h/semaine (pas d'heures sup).
        Config coeff_charges = 1.55.
        Cout hebdo = 40h * 20 EUR * 1.55 = 1240 EUR.
        Avec defaut 1.45 = 40h * 20 EUR * 1.45 = 1160 EUR.
        Difference = 80 EUR/semaine.
        """
        taux_horaire_brut = Decimal("20")
        heures_semaine = Decimal("40")

        cout_155 = heures_semaine * taux_horaire_brut * Decimal("1.55")
        assert cout_155 == Decimal("1240.00")

        cout_145 = heures_semaine * taux_horaire_brut * Decimal("1.45")
        assert cout_145 == Decimal("1160.00")

        assert cout_155 - cout_145 == Decimal("80.00")


# ===========================================================================
# Test 3 : Config FG impacte PnL
# ===========================================================================

class TestConfigFGImpactePnL:
    """Scenario: Meme logique que test 1 mais via PnL use case.

    Given: un chantier avec debourse_sec = 100 000 EUR, CA = 200 000 EUR
    When: config DB a coeff_fg = 25
    Then: quote_part_frais_generaux = 25 000 EUR (visible dans le DTO PnL)
    """

    def setup_method(self):
        """Configure les mocks pour le PnL."""
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_facture_repo = Mock(spec=FactureRepository)
        self.mock_cout_mo_repo = Mock(spec=CoutMainOeuvreRepository)
        self.mock_cout_materiel_repo = Mock(spec=CoutMaterielRepository)
        self.mock_config_repo = Mock(spec=ConfigurationEntrepriseRepository)

        # Budget 500k
        self.mock_budget_repo.find_by_chantier_id.return_value = _make_budget()

        # MO et materiel : 0 pour isoler l'impact FG
        self.mock_cout_mo_repo.calculer_cout_chantier.return_value = Decimal("0")
        self.mock_cout_materiel_repo.calculer_cout_chantier.return_value = Decimal("0")

    def _setup_achats_et_factures(self, total_realise: str = "100000", ca_ht: str = "200000"):
        """Configure achats realises et factures CA."""
        # Achats realises (LIVRE + FACTURE)
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal(total_realise)

        # Factures emises (CA)
        facture = _make_facture(montant_ht=ca_ht, statut="emise")
        self.mock_facture_repo.find_by_chantier_id.return_value = [facture]

    def test_pnl_quote_part_fg_25(self):
        """Config coeff_fg=25 -> quote_part = 25000 EUR dans le DTO."""
        self._setup_achats_et_factures()
        self.mock_config_repo.find_by_annee.return_value = _make_config(coeff_fg="25")

        use_case = GetPnLChantierUseCase(
            facture_repository=self.mock_facture_repo,
            achat_repository=self.mock_achat_repo,
            budget_repository=self.mock_budget_repo,
            cout_mo_repository=self.mock_cout_mo_repo,
            cout_materiel_repository=self.mock_cout_materiel_repo,
            config_repository=self.mock_config_repo,
        )

        result = use_case.execute(chantier_id=100)

        # debourse_sec = 100k + 0 + 0 = 100k
        # quote_part = 100k * 25 / 100 = 25k
        assert result.quote_part_frais_generaux == "25000.00"

    def test_pnl_quote_part_fg_19_defaut(self):
        """Config coeff_fg=19 (defaut) -> quote_part = 19000 EUR."""
        self._setup_achats_et_factures()
        self.mock_config_repo.find_by_annee.return_value = _make_config(coeff_fg="19")

        use_case = GetPnLChantierUseCase(
            facture_repository=self.mock_facture_repo,
            achat_repository=self.mock_achat_repo,
            budget_repository=self.mock_budget_repo,
            cout_mo_repository=self.mock_cout_mo_repo,
            cout_materiel_repository=self.mock_cout_materiel_repo,
            config_repository=self.mock_config_repo,
        )

        result = use_case.execute(chantier_id=100)

        assert result.quote_part_frais_generaux == "19000.00"

    def test_pnl_marge_avec_fg_25(self):
        """Config coeff_fg=25 -> marge = 37.50%."""
        self._setup_achats_et_factures()
        self.mock_config_repo.find_by_annee.return_value = _make_config(coeff_fg="25")

        use_case = GetPnLChantierUseCase(
            facture_repository=self.mock_facture_repo,
            achat_repository=self.mock_achat_repo,
            budget_repository=self.mock_budget_repo,
            cout_mo_repository=self.mock_cout_mo_repo,
            cout_materiel_repository=self.mock_cout_materiel_repo,
            config_repository=self.mock_config_repo,
        )

        result = use_case.execute(chantier_id=100)

        # CA = 200k, cout_revient = 100k + 0 + 0 + 25k = 125k
        # marge = (200k - 125k) / 200k * 100 = 37.50
        assert result.marge_brute_pct == "37.50"
        assert result.marge_brute_ht == "75000.00"
        assert result.total_couts == "125000.00"

    def test_pnl_marge_avec_fg_19(self):
        """Config coeff_fg=19 -> marge = 40.50%."""
        self._setup_achats_et_factures()
        self.mock_config_repo.find_by_annee.return_value = _make_config(coeff_fg="19")

        use_case = GetPnLChantierUseCase(
            facture_repository=self.mock_facture_repo,
            achat_repository=self.mock_achat_repo,
            budget_repository=self.mock_budget_repo,
            cout_mo_repository=self.mock_cout_mo_repo,
            cout_materiel_repository=self.mock_cout_materiel_repo,
            config_repository=self.mock_config_repo,
        )

        result = use_case.execute(chantier_id=100)

        # CA = 200k, cout_revient = 100k + 0 + 0 + 19k = 119k
        # marge = (200k - 119k) / 200k * 100 = 40.50
        assert result.marge_brute_pct == "40.50"
        assert result.marge_brute_ht == "81000.00"
        assert result.total_couts == "119000.00"

    def test_pnl_detail_couts_inclut_frais_generaux(self):
        """Verifie que la ligne frais generaux apparait dans detail_couts."""
        self._setup_achats_et_factures()
        self.mock_config_repo.find_by_annee.return_value = _make_config(coeff_fg="25")

        use_case = GetPnLChantierUseCase(
            facture_repository=self.mock_facture_repo,
            achat_repository=self.mock_achat_repo,
            budget_repository=self.mock_budget_repo,
            cout_mo_repository=self.mock_cout_mo_repo,
            cout_materiel_repository=self.mock_cout_materiel_repo,
            config_repository=self.mock_config_repo,
        )

        result = use_case.execute(chantier_id=100)

        categories = [ligne.categorie for ligne in result.detail_couts]
        assert "frais_generaux" in categories

        fg_ligne = [l for l in result.detail_couts if l.categorie == "frais_generaux"][0]
        assert fg_ligne.montant == "25000.00"


# ===========================================================================
# Test 4 : Fallback quand pas de config en DB
# ===========================================================================

class TestFallbackSansConfig:
    """Scenario: Aucune config en DB pour l'annee courante.

    When: dashboard execute
    Then: utilise les constantes par defaut (19%, 1.45, etc.)
    """

    def test_dashboard_fallback_config_none(self):
        """config_repository.find_by_annee retourne None -> constantes par defaut."""
        mock_budget_repo = Mock(spec=BudgetRepository)
        mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        mock_achat_repo = Mock(spec=AchatRepository)
        mock_situation_repo = Mock(spec=SituationRepository)
        mock_cout_mo_repo = Mock(spec=CoutMainOeuvreRepository)
        mock_cout_materiel_repo = Mock(spec=CoutMaterielRepository)
        mock_config_repo = Mock(spec=ConfigurationEntrepriseRepository)

        # Config inexistante pour l'annee courante
        mock_config_repo.find_by_annee.return_value = None

        mock_budget_repo.find_by_chantier_id.return_value = _make_budget()
        mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("150000"),  # total_engage
            Decimal("100000"),  # total_realise
        ]
        mock_achat_repo.find_by_chantier.return_value = []
        mock_lot_repo.find_by_budget_id.return_value = []
        mock_situation_repo.find_derniere_situation.return_value = (
            _make_situation(montant_cumule_ht="200000")
        )
        mock_cout_mo_repo.calculer_cout_chantier.return_value = Decimal("0")
        mock_cout_materiel_repo.calculer_cout_chantier.return_value = Decimal("0")

        use_case = GetDashboardFinancierUseCase(
            budget_repository=mock_budget_repo,
            lot_repository=mock_lot_repo,
            achat_repository=mock_achat_repo,
            situation_repository=mock_situation_repo,
            cout_mo_repository=mock_cout_mo_repo,
            cout_materiel_repository=mock_cout_materiel_repo,
            config_repository=mock_config_repo,
        )

        result = use_case.execute(chantier_id=100)

        # Fallback : coeff_fg = COEFF_FRAIS_GENERAUX = 19
        # debourse_sec = 100k, quote_part = 100k * 19 / 100 = 19k
        # marge = (200k - 119k) / 200k * 100 = 40.50
        assert result.kpi.marge_estimee == "40.50"
        assert result.kpi.marge_statut == "calculee"

    def test_dashboard_fallback_sans_config_repository(self):
        """config_repository=None -> constantes par defaut (meme resultat)."""
        mock_budget_repo = Mock(spec=BudgetRepository)
        mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        mock_achat_repo = Mock(spec=AchatRepository)
        mock_situation_repo = Mock(spec=SituationRepository)
        mock_cout_mo_repo = Mock(spec=CoutMainOeuvreRepository)
        mock_cout_materiel_repo = Mock(spec=CoutMaterielRepository)

        mock_budget_repo.find_by_chantier_id.return_value = _make_budget()
        mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("150000"),
            Decimal("100000"),
        ]
        mock_achat_repo.find_by_chantier.return_value = []
        mock_lot_repo.find_by_budget_id.return_value = []
        mock_situation_repo.find_derniere_situation.return_value = (
            _make_situation(montant_cumule_ht="200000")
        )
        mock_cout_mo_repo.calculer_cout_chantier.return_value = Decimal("0")
        mock_cout_materiel_repo.calculer_cout_chantier.return_value = Decimal("0")

        # Pas de config_repository du tout
        use_case = GetDashboardFinancierUseCase(
            budget_repository=mock_budget_repo,
            lot_repository=mock_lot_repo,
            achat_repository=mock_achat_repo,
            situation_repository=mock_situation_repo,
            cout_mo_repository=mock_cout_mo_repo,
            cout_materiel_repository=mock_cout_materiel_repo,
            config_repository=None,
        )

        result = use_case.execute(chantier_id=100)

        # Meme resultat : fallback sur COEFF_FRAIS_GENERAUX = 19
        assert result.kpi.marge_estimee == "40.50"

    def test_pnl_fallback_config_none(self):
        """PnL avec config_repository.find_by_annee=None -> constantes par defaut."""
        mock_budget_repo = Mock(spec=BudgetRepository)
        mock_achat_repo = Mock(spec=AchatRepository)
        mock_facture_repo = Mock(spec=FactureRepository)
        mock_cout_mo_repo = Mock(spec=CoutMainOeuvreRepository)
        mock_cout_materiel_repo = Mock(spec=CoutMaterielRepository)
        mock_config_repo = Mock(spec=ConfigurationEntrepriseRepository)

        mock_config_repo.find_by_annee.return_value = None
        mock_budget_repo.find_by_chantier_id.return_value = _make_budget()
        mock_achat_repo.somme_by_chantier.return_value = Decimal("100000")
        facture = _make_facture(montant_ht="200000", statut="emise")
        mock_facture_repo.find_by_chantier_id.return_value = [facture]
        mock_cout_mo_repo.calculer_cout_chantier.return_value = Decimal("0")
        mock_cout_materiel_repo.calculer_cout_chantier.return_value = Decimal("0")

        use_case = GetPnLChantierUseCase(
            facture_repository=mock_facture_repo,
            achat_repository=mock_achat_repo,
            budget_repository=mock_budget_repo,
            cout_mo_repository=mock_cout_mo_repo,
            cout_materiel_repository=mock_cout_materiel_repo,
            config_repository=mock_config_repo,
        )

        result = use_case.execute(chantier_id=100)

        # Fallback : coeff_fg = 19 -> quote_part = 100k * 19 / 100 = 19k
        assert result.quote_part_frais_generaux == "19000.00"
        assert result.marge_brute_pct == "40.50"

    def test_mo_fallback_get_coefficients_sans_config(self):
        """CoutMO repository sans config -> coefficients par defaut."""
        mock_session = Mock()
        mock_config_repo = Mock(spec=ConfigurationEntrepriseRepository)
        mock_config_repo.find_by_annee.return_value = None

        repo = SQLAlchemyCoutMainOeuvreRepository(
            session=mock_session,
            config_repository=mock_config_repo,
        )

        coeff_charges, coeff_hs_1, coeff_hs_2 = repo._get_coefficients()

        assert coeff_charges == COEFF_CHARGES_PATRONALES  # 1.45
        assert coeff_hs_1 == COEFF_HEURES_SUP  # 1.25
        assert coeff_hs_2 == COEFF_HEURES_SUP_2  # 1.50

    def test_mo_fallback_get_coefficients_sans_repo(self):
        """CoutMO repository sans config_repository -> coefficients par defaut."""
        mock_session = Mock()

        repo = SQLAlchemyCoutMainOeuvreRepository(
            session=mock_session,
            config_repository=None,
        )

        coeff_charges, coeff_hs_1, coeff_hs_2 = repo._get_coefficients()

        assert coeff_charges == COEFF_CHARGES_PATRONALES
        assert coeff_hs_1 == COEFF_HEURES_SUP
        assert coeff_hs_2 == COEFF_HEURES_SUP_2

    def test_fallback_constantes_valeurs_connues(self):
        """Verifie les valeurs par defaut des constantes (contrat implicite)."""
        assert COEFF_FRAIS_GENERAUX == Decimal("19")
        assert COEFF_CHARGES_PATRONALES == Decimal("1.45")
        assert COEFF_HEURES_SUP == Decimal("1.25")
        assert COEFF_HEURES_SUP_2 == Decimal("1.50")
