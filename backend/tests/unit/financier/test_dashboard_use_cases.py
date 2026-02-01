"""Tests unitaires pour les Use Cases Dashboard du module Financier."""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.financier.domain.entities import (
    Achat,
    Budget,
    LotBudgetaire,
)
from modules.financier.domain.repositories import (
    BudgetRepository,
    LotBudgetaireRepository,
    AchatRepository,
)
from modules.financier.domain.value_objects import StatutAchat, UniteMesure
from modules.financier.application.use_cases.dashboard_use_cases import (
    GetDashboardFinancierUseCase,
)
from modules.financier.application.use_cases.budget_use_cases import (
    BudgetNotFoundError,
)


class TestGetDashboardFinancierUseCase:
    """Tests pour le use case du tableau de bord financier."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.use_case = GetDashboardFinancierUseCase(
            budget_repository=self.mock_budget_repo,
            lot_repository=self.mock_lot_repo,
            achat_repository=self.mock_achat_repo,
        )

    def test_dashboard_success(self):
        """Test: construction reussie du tableau de bord."""
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
            montant_avenants_ht=Decimal("50000"),
            created_at=datetime.utcnow(),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # Montants engages et realises
        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("200000"),  # total_engage
            Decimal("100000"),  # total_realise
        ]

        # Derniers achats
        derniers = [
            Achat(
                id=1,
                chantier_id=100,
                libelle="Ciment",
                quantite=Decimal("10"),
                prix_unitaire_ht=Decimal("100"),
                taux_tva=Decimal("20"),
                statut=StatutAchat.VALIDE,
                created_at=datetime.utcnow(),
            ),
        ]
        self.mock_achat_repo.find_by_chantier.return_value = derniers

        # Lots budgetaires
        lots = [
            LotBudgetaire(
                id=1,
                budget_id=1,
                code_lot="GO-01",
                libelle="Gros oeuvre",
                quantite_prevue=Decimal("100"),
                prix_unitaire_ht=Decimal("2000"),
                created_at=datetime.utcnow(),
            ),
        ]
        self.mock_lot_repo.find_by_budget_id.return_value = lots

        # Engage et realise par lot
        self.mock_achat_repo.somme_by_lot.side_effect = [
            Decimal("100000"),  # lot engage
            Decimal("50000"),   # lot realise
        ]

        result = self.use_case.execute(chantier_id=100)

        assert result.kpi is not None
        assert result.kpi.montant_revise_ht == "550000"
        assert result.kpi.total_engage == "200000"
        assert result.kpi.total_realise == "100000"
        assert result.kpi.marge_estimee == "63.64"
        assert result.kpi.reste_a_depenser == "350000"
        assert result.kpi.pct_reste == "63.64"  # (350000/550000)*100
        assert len(result.derniers_achats) == 1
        assert len(result.repartition_par_lot) == 1

    def test_dashboard_budget_not_found(self):
        """Test: erreur si pas de budget pour le chantier."""
        self.mock_budget_repo.find_by_chantier_id.return_value = None

        with pytest.raises(BudgetNotFoundError):
            self.use_case.execute(chantier_id=999)

    def test_dashboard_kpi_pourcentages(self):
        """Test: calcul correct des pourcentages KPI."""
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("100000"),
            created_at=datetime.utcnow(),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("80000"),   # total_engage = 80%
            Decimal("50000"),   # total_realise = 50%
        ]

        self.mock_achat_repo.find_by_chantier.return_value = []
        self.mock_lot_repo.find_by_budget_id.return_value = []

        result = self.use_case.execute(chantier_id=100)

        assert result.kpi.pct_engage == "80.00"
        assert result.kpi.pct_realise == "50.00"
        assert result.kpi.reste_a_depenser == "20000"  # 100000 - 80000
        assert result.kpi.pct_reste == "20.00"  # (20000/100000)*100
        # marge_estimee en % : ((100000 - 80000) / 100000) * 100 = 20.00%
        assert result.kpi.marge_estimee == "20.00"

    def test_dashboard_budget_zero_montant(self):
        """Test: pourcentages a 0 si budget revise a 0."""
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("0"),
            created_at=datetime.utcnow(),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("0"),
            Decimal("0"),
        ]
        self.mock_achat_repo.find_by_chantier.return_value = []
        self.mock_lot_repo.find_by_budget_id.return_value = []

        result = self.use_case.execute(chantier_id=100)

        # quantize(Decimal("0.01")) formate toujours avec 2 decimales
        assert result.kpi.pct_engage == "0.00"
        assert result.kpi.pct_realise == "0.00"
        assert result.kpi.reste_a_depenser == "0"  # 0 - 0
        assert result.kpi.pct_reste == "0.00"  # division par zero evitee
        assert result.kpi.marge_estimee == "0.00"  # marge_estimee en % (0 sans division)

    def test_dashboard_repartition_par_lot(self):
        """Test: repartition correcte par lot budgetaire."""
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
            created_at=datetime.utcnow(),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("150000"),
            Decimal("80000"),
        ]
        self.mock_achat_repo.find_by_chantier.return_value = []

        lots = [
            LotBudgetaire(
                id=1,
                budget_id=1,
                code_lot="GO-01",
                libelle="Gros oeuvre",
                quantite_prevue=Decimal("100"),
                prix_unitaire_ht=Decimal("2000"),
                created_at=datetime.utcnow(),
            ),
            LotBudgetaire(
                id=2,
                budget_id=1,
                code_lot="SEC-01",
                libelle="Second oeuvre",
                quantite_prevue=Decimal("50"),
                prix_unitaire_ht=Decimal("1000"),
                created_at=datetime.utcnow(),
            ),
        ]
        self.mock_lot_repo.find_by_budget_id.return_value = lots

        self.mock_achat_repo.somme_by_lot.side_effect = [
            Decimal("100000"),  # GO-01 engage
            Decimal("50000"),   # GO-01 realise
            Decimal("50000"),   # SEC-01 engage
            Decimal("30000"),   # SEC-01 realise
        ]

        result = self.use_case.execute(chantier_id=100)

        assert len(result.repartition_par_lot) == 2
        go = result.repartition_par_lot[0]
        assert go.code_lot == "GO-01"
        assert go.total_prevu_ht == "200000"
        assert go.engage == "100000"
        assert go.realise == "50000"
        assert go.ecart == "100000"  # 200000 - 100000

        sec = result.repartition_par_lot[1]
        assert sec.code_lot == "SEC-01"
        assert sec.total_prevu_ht == "50000"
        assert sec.engage == "50000"
        assert sec.ecart == "0"  # 50000 - 50000

    def test_dashboard_reste_a_depenser_negatif(self):
        """Test: reste_a_depenser negatif quand total_engage > montant_revise."""
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("100000"),
            created_at=datetime.utcnow(),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("150000"),  # total_engage depasse le budget
            Decimal("120000"),  # total_realise
        ]
        self.mock_achat_repo.find_by_chantier.return_value = []
        self.mock_lot_repo.find_by_budget_id.return_value = []

        result = self.use_case.execute(chantier_id=100)

        # reste_a_depenser = 100000 - 150000 = -50000
        assert result.kpi.reste_a_depenser == "-50000"
        # pct_reste = (-50000 / 100000) * 100 = -50.00
        assert result.kpi.pct_reste == "-50.00"
        # marge_estimee aussi negative
        assert result.kpi.marge_estimee == "-50.00"

    def test_dashboard_reste_a_depenser_exact_budget(self):
        """Test: reste_a_depenser = 0 quand engage == montant_revise."""
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("200000"),
            created_at=datetime.utcnow(),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("200000"),  # total_engage == budget
            Decimal("100000"),
        ]
        self.mock_achat_repo.find_by_chantier.return_value = []
        self.mock_lot_repo.find_by_budget_id.return_value = []

        result = self.use_case.execute(chantier_id=100)

        assert result.kpi.reste_a_depenser == "0"
        assert result.kpi.pct_reste == "0.00"
        # marge_estimee en % : ((200000 - 200000) / 200000) * 100 = 0.00%
        assert result.kpi.marge_estimee == "0.00"

    def test_dashboard_derniers_achats(self):
        """Test: les derniers achats sont retournes correctement."""
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
            created_at=datetime.utcnow(),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("0"),
            Decimal("0"),
        ]

        now = datetime.utcnow()
        derniers = [
            Achat(
                id=1,
                chantier_id=100,
                libelle="Ciment",
                quantite=Decimal("10"),
                prix_unitaire_ht=Decimal("100"),
                taux_tva=Decimal("20"),
                statut=StatutAchat.DEMANDE,
                created_at=now,
            ),
            Achat(
                id=2,
                chantier_id=100,
                libelle="Sable",
                quantite=Decimal("5"),
                prix_unitaire_ht=Decimal("50"),
                taux_tva=Decimal("20"),
                statut=StatutAchat.VALIDE,
                created_at=now,
            ),
        ]
        self.mock_achat_repo.find_by_chantier.return_value = derniers

        self.mock_lot_repo.find_by_budget_id.return_value = []

        result = self.use_case.execute(chantier_id=100)

        assert len(result.derniers_achats) == 2
        assert result.derniers_achats[0].libelle == "Ciment"
        assert result.derniers_achats[0].statut == "demande"
        assert result.derniers_achats[1].libelle == "Sable"
        assert result.derniers_achats[1].statut == "valide"

    def test_dashboard_marge_estimee_pourcentage_avec_avenants(self):
        """Test: marge_estimee retourne un pourcentage (pas EUR) avec avenants."""
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("400000"),
            montant_avenants_ht=Decimal("100000"),  # revise = 500000
            created_at=datetime.utcnow(),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("300000"),  # total_engage
            Decimal("150000"),  # total_realise
        ]
        self.mock_achat_repo.find_by_chantier.return_value = []
        self.mock_lot_repo.find_by_budget_id.return_value = []

        result = self.use_case.execute(chantier_id=100)

        # marge_estimee = ((500000 - 300000) / 500000) * 100 = 40.00%
        assert result.kpi.marge_estimee == "40.00"
        # Verifie que ce n'est PAS en EUR (200000) mais bien en %
        assert result.kpi.marge_estimee != "200000"
        assert result.kpi.montant_revise_ht == "500000"
        assert result.kpi.reste_a_depenser == "200000"

    def test_dashboard_marge_estimee_haute_precision(self):
        """Test: marge_estimee arrondie a 2 decimales."""
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("333333"),
            created_at=datetime.utcnow(),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("111111"),  # total_engage
            Decimal("50000"),
        ]
        self.mock_achat_repo.find_by_chantier.return_value = []
        self.mock_lot_repo.find_by_budget_id.return_value = []

        result = self.use_case.execute(chantier_id=100)

        # marge_estimee = ((333333 - 111111) / 333333) * 100 = 66.6667...%
        assert result.kpi.marge_estimee == "66.67"

    def test_dashboard_derniers_achats_sans_created_at(self):
        """Test: achat sans created_at ne provoque pas d'erreur."""
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("100000"),
            created_at=datetime.utcnow(),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget
        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("0"), Decimal("0"),
        ]
        achat_sans_date = Achat(
            id=1,
            chantier_id=100,
            libelle="Beton",
            quantite=Decimal("5"),
            prix_unitaire_ht=Decimal("200"),
            taux_tva=Decimal("20"),
            statut=StatutAchat.DEMANDE,
            created_at=None,
        )
        self.mock_achat_repo.find_by_chantier.return_value = [achat_sans_date]
        self.mock_lot_repo.find_by_budget_id.return_value = []

        result = self.use_case.execute(chantier_id=100)

        assert len(result.derniers_achats) == 1
        assert result.derniers_achats[0].created_at is None

    def test_dashboard_repartition_lot_ecart_negatif(self):
        """Test: ecart negatif quand engage > prevu pour un lot."""
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
            created_at=datetime.utcnow(),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("300000"), Decimal("100000"),
        ]
        self.mock_achat_repo.find_by_chantier.return_value = []

        lot = LotBudgetaire(
            id=1,
            budget_id=1,
            code_lot="GO-01",
            libelle="Gros oeuvre",
            quantite_prevue=Decimal("50"),
            prix_unitaire_ht=Decimal("2000"),
            created_at=datetime.utcnow(),
        )
        self.mock_lot_repo.find_by_budget_id.return_value = [lot]

        self.mock_achat_repo.somme_by_lot.side_effect = [
            Decimal("150000"),  # engage > prevu (100000)
            Decimal("80000"),
        ]

        result = self.use_case.execute(chantier_id=100)

        assert len(result.repartition_par_lot) == 1
        assert result.repartition_par_lot[0].ecart == "-50000"  # 100000 - 150000
