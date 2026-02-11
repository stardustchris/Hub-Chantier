"""Tests d'integration pour la coherence des calculs de marge.

Verifie que la marge d'un chantier est identique qu'elle soit consultee
via le dashboard individuel ou via la vue consolidee.

FIN-11 (dashboard) et FIN-20 (consolidation) doivent utiliser la meme
formule de marge BTP avec coefficient FG unique sur debourse sec.
"""

import pytest
from decimal import Decimal

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

    def test_marge_dashboard_equals_consolidation(
        self,
        budget_repository: BudgetRepository,
        lot_repository: LotBudgetaireRepository,
        achat_repository: AchatRepository,
        situation_repository: SituationRepository,
        cout_mo_repository: CoutMainOeuvreRepository,
        alerte_repository: AlerteRepository,
        chantier_info_port: ChantierInfoPort,
    ):
        """La marge d'un chantier doit etre identique dashboard vs consolidation.

        Cas de test : Chantier 8 "Extension gymnase Ville-E"
        - Prix vente : 390 000 EUR
        - Achats realises : 300 089.43 EUR
        - Cout MO : 31 704 EUR
        - Debourse sec : 331 793.43 EUR
        - Quote-part FG (19%) : 63 040.75 EUR
        - Cout revient : 394 834.18 EUR
        - Marge attendue : -1.24%
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
        dashboard_result = dashboard_use_case.execute(chantier_id)
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
            f"Marge incoherente : "
            f"dashboard={marge_dashboard}% vs consolidation={marge_consolidation}% "
            f"(ecart={ecart}%)"
        )

        # Verification marge attendue (environ -1.24%)
        # Prix vente : 390 000
        # Debourse sec : 300 089.43 + 31 704 = 331 793.43
        # Quote-part FG : 331 793.43 x 19% = 63 040.75
        # Cout revient : 331 793.43 + 63 040.75 = 394 834.18
        # Marge : (390000 - 394834.18) / 390000 * 100 = -1.24%
        marge_attendue = Decimal("-1.24")
        tolerance_valeur = Decimal("1.0")  # +/- 1.0%

        assert abs(marge_dashboard_decimal - marge_attendue) <= tolerance_valeur, (
            f"Marge dashboard hors plage attendue : "
            f"{marge_dashboard}% (attendu ~{marge_attendue}%)"
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

        result = dashboard_use_case.execute(chantier_id)

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

        result = dashboard_use_case.execute(chantier_id)

        assert result.kpi.marge_estimee is not None
        assert result.kpi.marge_statut == "calculee"
