"""Tests unitaires pour les Use Cases du dashboard devis.

DEV-17: Tableau de bord devis - KPI pipeline commercial.
Couche Application - dashboard_use_cases.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.application.use_cases.dashboard_use_cases import GetDashboardDevisUseCase
from modules.devis.application.dtos.dashboard_dtos import DashboardDevisDTO, KPIDevisDTO


def _make_devis(**kwargs):
    """Cree un devis valide."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "objet": "Renovation",
        "statut": StatutDevis.BROUILLON,
        "date_creation": date(2026, 1, 15),
        "montant_total_ht": Decimal("50000"),
        "montant_total_ttc": Decimal("60000"),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


class TestGetDashboardDevisUseCase:
    """Tests pour le calcul du dashboard KPI."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.use_case = GetDashboardDevisUseCase(
            devis_repository=self.mock_devis_repo,
        )

    def test_dashboard_empty(self):
        """Test: dashboard avec aucun devis."""
        self.mock_devis_repo.count_by_statut.return_value = {}
        self.mock_devis_repo.somme_montant_by_statut.return_value = {}
        self.mock_devis_repo.find_all.return_value = []

        result = self.use_case.execute()

        assert isinstance(result, DashboardDevisDTO)
        assert result.kpi.nb_total == 0
        assert result.kpi.taux_conversion == "0.00"
        assert result.kpi.total_pipeline_ht == "0"
        assert result.derniers_devis == []

    def test_dashboard_with_data(self):
        """Test: dashboard avec des donnees reelles."""
        self.mock_devis_repo.count_by_statut.return_value = {
            "brouillon": 5,
            "en_validation": 2,
            "envoye": 3,
            "vu": 1,
            "en_negociation": 2,
            "accepte": 10,
            "refuse": 3,
            "perdu": 2,
            "expire": 1,
        }
        self.mock_devis_repo.somme_montant_by_statut.return_value = {
            "brouillon": Decimal("100000"),
            "en_validation": Decimal("50000"),
            "envoye": Decimal("150000"),
            "vu": Decimal("30000"),
            "en_negociation": Decimal("80000"),
            "accepte": Decimal("500000"),
            "refuse": Decimal("75000"),
        }
        self.mock_devis_repo.find_all.return_value = [
            _make_devis(id=i, numero=f"DEV-{i:03d}") for i in range(1, 4)
        ]

        result = self.use_case.execute()

        assert result.kpi.nb_brouillon == 5
        assert result.kpi.nb_en_validation == 2
        assert result.kpi.nb_envoye == 3
        assert result.kpi.nb_vu == 1
        assert result.kpi.nb_en_negociation == 2
        assert result.kpi.nb_accepte == 10
        assert result.kpi.nb_refuse == 3
        assert result.kpi.nb_perdu == 2
        assert result.kpi.nb_expire == 1
        assert result.kpi.nb_total == 29

    def test_dashboard_taux_conversion(self):
        """Test: calcul du taux de conversion."""
        # 10 acceptes / (10 + 3 + 2) = 10/15 = 66.67%
        self.mock_devis_repo.count_by_statut.return_value = {
            "accepte": 10,
            "refuse": 3,
            "perdu": 2,
        }
        self.mock_devis_repo.somme_montant_by_statut.return_value = {
            "accepte": Decimal("500000"),
        }
        self.mock_devis_repo.find_all.return_value = []

        result = self.use_case.execute()

        assert result.kpi.taux_conversion == "66.67"

    def test_dashboard_taux_conversion_zero_decides(self):
        """Test: taux conversion = 0 si aucun devis decide."""
        self.mock_devis_repo.count_by_statut.return_value = {
            "brouillon": 5,
            "envoye": 3,
        }
        self.mock_devis_repo.somme_montant_by_statut.return_value = {}
        self.mock_devis_repo.find_all.return_value = []

        result = self.use_case.execute()

        assert result.kpi.taux_conversion == "0.00"

    def test_dashboard_pipeline_ht(self):
        """Test: calcul du total pipeline HT."""
        self.mock_devis_repo.count_by_statut.return_value = {}
        self.mock_devis_repo.somme_montant_by_statut.return_value = {
            "en_validation": Decimal("50000"),
            "envoye": Decimal("150000"),
            "vu": Decimal("30000"),
            "en_negociation": Decimal("80000"),
        }
        self.mock_devis_repo.find_all.return_value = []

        result = self.use_case.execute()

        # Pipeline = en_validation + envoye + vu + en_negociation
        assert result.kpi.total_pipeline_ht == "310000"

    def test_dashboard_total_accepte(self):
        """Test: calcul du total accepte HT."""
        self.mock_devis_repo.count_by_statut.return_value = {}
        self.mock_devis_repo.somme_montant_by_statut.return_value = {
            "accepte": Decimal("500000"),
        }
        self.mock_devis_repo.find_all.return_value = []

        result = self.use_case.execute()

        assert result.kpi.total_accepte_ht == "500000"

    def test_dashboard_derniers_devis(self):
        """Test: les 10 derniers devis sont retournes."""
        devis_list = [_make_devis(id=i, numero=f"DEV-{i:03d}") for i in range(1, 6)]
        self.mock_devis_repo.count_by_statut.return_value = {}
        self.mock_devis_repo.somme_montant_by_statut.return_value = {}
        self.mock_devis_repo.find_all.return_value = devis_list

        result = self.use_case.execute()

        assert len(result.derniers_devis) == 5
        self.mock_devis_repo.find_all.assert_called_once_with(limit=10, offset=0)

    def test_dashboard_taux_conversion_100_percent(self):
        """Test: taux de conversion 100% (tous acceptes)."""
        self.mock_devis_repo.count_by_statut.return_value = {
            "accepte": 5,
        }
        self.mock_devis_repo.somme_montant_by_statut.return_value = {
            "accepte": Decimal("250000"),
        }
        self.mock_devis_repo.find_all.return_value = []

        result = self.use_case.execute()

        assert result.kpi.taux_conversion == "100.00"
