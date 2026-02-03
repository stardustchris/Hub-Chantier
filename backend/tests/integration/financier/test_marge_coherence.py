"""Tests d'integration pour la coherence des calculs de marge.

Verifie que la marge d'un chantier est identique qu'elle soit consultee
via le dashboard individuel ou via la vue consolidee.

FIN-11 (dashboard) et FIN-20 (consolidation) doivent utiliser la meme
formule de marge BTP avec repartition des couts fixes.
"""

import pytest
from decimal import Decimal
from typing import Optional

from modules.financier.application.use_cases.dashboard_use_cases import (
    GetDashboardFinancierUseCase,
)
from modules.financier.application.use_cases.consolidation_use_cases import (
    GetVueConsolideeFinancesUseCase,
)
from modules.financier.domain.repositories import (
    BudgetRepository,
    LotBudgetaireRepository,
    AchatRepository,
    AlerteRepository,
    SituationRepository,
    CoutMainOeuvreRepository,
)
from shared.application.ports.chantier_info_port import ChantierInfoPort


class TestMargeCoherence:
    """Tests de coherence des calculs de marge entre dashboard et consolidation."""

    @pytest.fixture
    def ca_total_entreprise(self) -> Decimal:
        """CA total entreprise pour repartition couts fixes."""
        return Decimal("4300000")

    def test_marge_dashboard_equals_consolidation(
        self,
        budget_repository: BudgetRepository,
        lot_repository: LotBudgetaireRepository,
        achat_repository: AchatRepository,
        situation_repository: SituationRepository,
        cout_mo_repository: CoutMainOeuvreRepository,
        alerte_repository: AlerteRepository,
        chantier_info_port: ChantierInfoPort,
        ca_total_entreprise: Decimal,
    ):
        """La marge d'un chantier doit etre identique dashboard vs consolidation.

        Cas de test : Chantier 8 "Extension gymnase Ville-E"
        - Prix vente : 390 000 €
        - Achats realises : 300 089.43 €
        - Cout MO : 31 704 €
        - Quote-part couts fixes : 54 418.60 €
        - Marge attendue : 0.97%
        """
        chantier_id = 8

        # Dashboard individuel
        dashboard_use_case = GetDashboardFinancierUseCase(
            budget_repository=budget_repository,
            lot_repository=lot_repository,
            achat_repository=achat_repository,
            situation_repository=situation_repository,
            cout_mo_repository=cout_mo_repository,
        )
        dashboard_result = dashboard_use_case.execute(
            chantier_id, ca_total_annee=ca_total_entreprise
        )
        marge_dashboard = dashboard_result.kpi.marge_estimee

        # Vue consolidee
        consolidation_use_case = GetVueConsolideeFinancesUseCase(
            budget_repository=budget_repository,
            lot_repository=lot_repository,
            achat_repository=achat_repository,
            alerte_repository=alerte_repository,
            chantier_info_port=chantier_info_port,
            situation_repository=situation_repository,
            cout_mo_repository=cout_mo_repository,
        )
        consolidation_result = consolidation_use_case.execute(
            user_accessible_chantier_ids=[chantier_id],
            ca_total_entreprise=ca_total_entreprise,
        )

        # Trouver le chantier 8 dans la liste consolidee
        chantier_8_consolidation = next(
            (c for c in consolidation_result.chantiers if c.chantier_id == chantier_id),
            None,
        )
        assert chantier_8_consolidation is not None, "Chantier 8 introuvable dans consolidation"
        marge_consolidation = chantier_8_consolidation.marge_estimee_pct

        # Assertions
        assert marge_dashboard is not None, "Marge dashboard ne doit pas etre None"
        assert marge_consolidation is not None, "Marge consolidation ne doit pas etre None"

        marge_dashboard_decimal = Decimal(marge_dashboard)
        marge_consolidation_decimal = Decimal(marge_consolidation)

        # Tolerance de 0.01% pour arrondi
        tolerance = Decimal("0.01")
        ecart = abs(marge_dashboard_decimal - marge_consolidation_decimal)

        assert ecart <= tolerance, (
            f"Marge incohérente : "
            f"dashboard={marge_dashboard}% vs consolidation={marge_consolidation}% "
            f"(écart={ecart}%)"
        )

        # Verification marge attendue (environ 0.97%)
        # Prix vente : 390 000
        # Cout revient : 300 089.43 + 31 704 + 54 418.60 = 386 212.03
        # Marge : (390000 - 386212.03) / 390000 * 100 = 0.97%
        marge_attendue = Decimal("0.97")
        tolerance_valeur = Decimal("0.5")  # +/- 0.5%

        assert abs(marge_dashboard_decimal - marge_attendue) <= tolerance_valeur, (
            f"Marge dashboard hors plage attendue : "
            f"{marge_dashboard}% (attendu ~{marge_attendue}%)"
        )

    def test_dashboard_sans_ca_total_annee_exclut_couts_fixes(
        self,
        budget_repository: BudgetRepository,
        lot_repository: LotBudgetaireRepository,
        achat_repository: AchatRepository,
        situation_repository: SituationRepository,
        cout_mo_repository: CoutMainOeuvreRepository,
    ):
        """Sans ca_total_annee, le dashboard ne repartit PAS les couts fixes.

        Marge sans couts fixes (chantier 8) : ~14.92%
        Cout revient = 300 089.43 + 31 704 = 331 793.43
        Marge = (390000 - 331793.43) / 390000 * 100 = 14.92%

        Ce test verifie le comportement legacy (avant correction).
        """
        chantier_id = 8

        dashboard_use_case = GetDashboardFinancierUseCase(
            budget_repository=budget_repository,
            lot_repository=lot_repository,
            achat_repository=achat_repository,
            situation_repository=situation_repository,
            cout_mo_repository=cout_mo_repository,
        )

        # Appel SANS ca_total_annee
        result = dashboard_use_case.execute(chantier_id, ca_total_annee=None)
        marge = result.kpi.marge_estimee

        assert marge is not None
        marge_decimal = Decimal(marge)

        # Marge attendue sans couts fixes : ~14.92%
        marge_attendue_sans_fixes = Decimal("14.92")
        tolerance = Decimal("0.5")

        assert abs(marge_decimal - marge_attendue_sans_fixes) <= tolerance, (
            f"Marge sans couts fixes incorrecte : "
            f"{marge}% (attendu ~{marge_attendue_sans_fixes}%)"
        )

    def test_consolidation_calcule_ca_si_non_fourni(
        self,
        budget_repository: BudgetRepository,
        lot_repository: LotBudgetaireRepository,
        achat_repository: AchatRepository,
        alerte_repository: AlerteRepository,
        situation_repository: SituationRepository,
        cout_mo_repository: CoutMainOeuvreRepository,
        chantier_info_port: Optional[ChantierInfoPort],
    ):
        """Si ca_total_entreprise=None, la consolidation calcule le CA des chantiers visibles.

        CA calcule (5 chantiers avec situations) : 1 462 500 €
        Quote-part chantier 8 : (390000 / 1462500) * 600000 = 160 000 €
        Marge plus faible qu'avec CA entreprise complet (4.3M€)
        """
        chantier_id = 8

        consolidation_use_case = GetVueConsolideeFinancesUseCase(
            budget_repository=budget_repository,
            lot_repository=lot_repository,
            achat_repository=achat_repository,
            alerte_repository=alerte_repository,
            chantier_info_port=chantier_info_port,
            situation_repository=situation_repository,
            cout_mo_repository=cout_mo_repository,
        )

        # Appel SANS ca_total_entreprise
        result = consolidation_use_case.execute(
            user_accessible_chantier_ids=[5, 6, 7, 8, 9],
            ca_total_entreprise=None,  # Force calcul dynamique
        )

        chantier_8 = next(
            (c for c in result.chantiers if c.chantier_id == chantier_id),
            None,
        )
        assert chantier_8 is not None
        assert chantier_8.marge_estimee_pct is not None

        # Avec CA calcule (1.46M au lieu de 4.3M), quote-part plus elevee
        # donc marge plus faible (peut meme etre negative)
        marge_decimal = Decimal(chantier_8.marge_estimee_pct)

        # La marge doit etre inferieure a celle avec CA complet (0.97%)
        # Car quote-part : (390000/1462500)*600000 = 160000 vs 54418.60
        marge_avec_ca_complet = Decimal("0.97")

        assert marge_decimal < marge_avec_ca_complet, (
            f"Marge avec CA calcule devrait etre inferieure : "
            f"{marge_decimal}% >= {marge_avec_ca_complet}%"
        )


class TestMargeStatut:
    """Tests du statut de la marge (en_attente, calculee, partielle)."""

    def test_marge_en_attente_sans_situation(
        self,
        budget_repository: BudgetRepository,
        lot_repository: LotBudgetaireRepository,
        achat_repository: AchatRepository,
        situation_repository: SituationRepository,
        cout_mo_repository: CoutMainOeuvreRepository,
    ):
        """Sans situation de travaux, la marge est en_attente."""
        # Utiliser un chantier sans situation (creer en test setup)
        chantier_id = 999  # Chantier test sans situation

        dashboard_use_case = GetDashboardFinancierUseCase(
            budget_repository=budget_repository,
            lot_repository=lot_repository,
            achat_repository=achat_repository,
            situation_repository=situation_repository,
            cout_mo_repository=cout_mo_repository,
        )

        result = dashboard_use_case.execute(
            chantier_id, ca_total_annee=Decimal("4300000")
        )

        assert result.kpi.marge_estimee is None
        assert result.kpi.marge_statut == "en_attente"

    def test_marge_calculee_avec_situation(
        self,
        budget_repository: BudgetRepository,
        lot_repository: LotBudgetaireRepository,
        achat_repository: AchatRepository,
        situation_repository: SituationRepository,
        cout_mo_repository: CoutMainOeuvreRepository,
    ):
        """Avec situation de travaux, la marge est calculee."""
        chantier_id = 8  # A une situation

        dashboard_use_case = GetDashboardFinancierUseCase(
            budget_repository=budget_repository,
            lot_repository=lot_repository,
            achat_repository=achat_repository,
            situation_repository=situation_repository,
            cout_mo_repository=cout_mo_repository,
        )

        result = dashboard_use_case.execute(
            chantier_id, ca_total_annee=Decimal("4300000")
        )

        assert result.kpi.marge_estimee is not None
        assert result.kpi.marge_statut == "calculee"
