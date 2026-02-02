"""Tests unitaires pour ChantierCreationAdapter.

DEV-16: Tests de l'adapter pour creation chantier depuis devis.
Couche Infrastructure - chantier_creation_adapter.py
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock

from shared.infrastructure.adapters.chantier_creation_adapter import (
    ChantierCreationAdapter,
)
from shared.application.ports.chantier_creation_port import (
    ChantierCreationData,
    BudgetCreationData,
    LotBudgetaireCreationData,
    ConversionChantierResult,
)

from modules.chantiers.domain.entities import Chantier
from modules.chantiers.domain.repositories import ChantierRepository
from modules.chantiers.domain.value_objects import CodeChantier, StatutChantier
from modules.financier.domain.entities import Budget, LotBudgetaire
from modules.financier.domain.repositories.budget_repository import BudgetRepository
from modules.financier.domain.repositories.lot_budgetaire_repository import (
    LotBudgetaireRepository,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _make_chantier_data(**kwargs):
    """Cree des donnees de chantier par defaut."""
    defaults = {
        "nom": "Chantier test",
        "adresse": "12 rue Test",
        "description": "Description test",
        "conducteur_ids": [1],
    }
    defaults.update(kwargs)
    return ChantierCreationData(**defaults)


def _make_budget_data(**kwargs):
    """Cree des donnees de budget par defaut."""
    defaults = {
        "montant_initial_ht": Decimal("50000"),
        "retenue_garantie_pct": Decimal("5"),
        "seuil_alerte_pct": Decimal("80"),
        "seuil_validation_achat": Decimal("5000"),
    }
    defaults.update(kwargs)
    return BudgetCreationData(**defaults)


def _make_lot_data(**kwargs):
    """Cree des donnees de lot budgetaire par defaut."""
    defaults = {
        "code_lot": "LOT-01",
        "libelle": "Lot test",
        "unite": "U",
        "quantite_prevue": Decimal("1"),
        "prix_unitaire_ht": Decimal("20000"),
        "ordre": 1,
        "prix_vente_ht": Decimal("20000"),
    }
    defaults.update(kwargs)
    return LotBudgetaireCreationData(**defaults)


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestChantierCreationAdapter:
    """Tests pour l'adapter de creation chantier."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_chantier_repo = Mock(spec=ChantierRepository)
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_lot_budgetaire_repo = Mock(spec=LotBudgetaireRepository)

        self.adapter = ChantierCreationAdapter(
            chantier_repo=self.mock_chantier_repo,
            budget_repo=self.mock_budget_repo,
            lot_budgetaire_repo=self.mock_lot_budgetaire_repo,
        )

    # ─────────────────────────────────────────────────────────────────────
    # Happy path
    # ─────────────────────────────────────────────────────────────────────

    def test_create_chantier_from_devis_success(self):
        """Test: creation reussie d'un chantier avec budget et lots."""
        # Arrange
        chantier_data = _make_chantier_data()
        budget_data = _make_budget_data()
        lot1_data = _make_lot_data(code_lot="LOT-01")
        lot2_data = _make_lot_data(code_lot="LOT-02", ordre=2)
        lots_data = [lot1_data, lot2_data]

        # Mock chantier repo
        self.mock_chantier_repo.get_last_code.return_value = "A041"
        mock_chantier = Mock(spec=Chantier)
        mock_chantier.id = 100
        mock_chantier.code = CodeChantier("A042")
        self.mock_chantier_repo.save.return_value = mock_chantier

        # Mock budget repo
        mock_budget = Mock(spec=Budget)
        mock_budget.id = 200
        self.mock_budget_repo.save.return_value = mock_budget

        # Act
        result = self.adapter.create_chantier_from_devis(
            chantier_data=chantier_data,
            budget_data=budget_data,
            lots_data=lots_data,
        )

        # Assert
        assert isinstance(result, ConversionChantierResult)
        assert result.chantier_id == 100
        assert result.code_chantier == "A042"
        assert result.budget_id == 200
        assert result.nb_lots_transferes == 2

        # Verifier les appels
        self.mock_chantier_repo.get_last_code.assert_called_once()
        self.mock_chantier_repo.save.assert_called_once()
        self.mock_budget_repo.save.assert_called_once()
        assert self.mock_lot_budgetaire_repo.save.call_count == 2

    def test_create_chantier_single_lot(self):
        """Test: creation avec un seul lot."""
        chantier_data = _make_chantier_data()
        budget_data = _make_budget_data()
        lot_data = _make_lot_data()

        self.mock_chantier_repo.get_last_code.return_value = "A001"
        mock_chantier = Mock(spec=Chantier)
        mock_chantier.id = 100
        mock_chantier.code = CodeChantier("A002")
        self.mock_chantier_repo.save.return_value = mock_chantier

        mock_budget = Mock(spec=Budget)
        mock_budget.id = 200
        self.mock_budget_repo.save.return_value = mock_budget

        result = self.adapter.create_chantier_from_devis(
            chantier_data=chantier_data,
            budget_data=budget_data,
            lots_data=[lot_data],
        )

        assert result.nb_lots_transferes == 1
        assert self.mock_lot_budgetaire_repo.save.call_count == 1

    def test_code_chantier_generation(self):
        """Test: le code chantier est genere correctement."""
        chantier_data = _make_chantier_data()
        budget_data = _make_budget_data()
        lot_data = _make_lot_data()

        self.mock_chantier_repo.get_last_code.return_value = "A099"

        # Capture du chantier sauvegarde
        saved_chantier = None
        def save_chantier(chantier):
            nonlocal saved_chantier
            saved_chantier = chantier
            chantier.id = 100
            return chantier

        self.mock_chantier_repo.save.side_effect = save_chantier

        mock_budget = Mock(spec=Budget)
        mock_budget.id = 200
        self.mock_budget_repo.save.return_value = mock_budget

        self.adapter.create_chantier_from_devis(
            chantier_data=chantier_data,
            budget_data=budget_data,
            lots_data=[lot_data],
        )

        # Verifier que le code a ete genere (A100 = A099 + 1)
        assert saved_chantier is not None
        assert str(saved_chantier.code) == "A100"

    # ─────────────────────────────────────────────────────────────────────
    # Sanitization (DEFAUT 3)
    # ─────────────────────────────────────────────────────────────────────

    def test_sanitize_chantier_nom(self):
        """Test: le nom du chantier est sanitize (HTML stripped)."""
        chantier_data = _make_chantier_data(
            nom="Chantier <script>alert('xss')</script>"
        )
        budget_data = _make_budget_data()
        lot_data = _make_lot_data()

        saved_chantier = None
        def save_chantier(chantier):
            nonlocal saved_chantier
            saved_chantier = chantier
            chantier.id = 100
            return chantier

        self.mock_chantier_repo.get_last_code.return_value = "A001"
        self.mock_chantier_repo.save.side_effect = save_chantier

        mock_budget = Mock(spec=Budget)
        mock_budget.id = 200
        self.mock_budget_repo.save.return_value = mock_budget

        self.adapter.create_chantier_from_devis(
            chantier_data=chantier_data,
            budget_data=budget_data,
            lots_data=[lot_data],
        )

        # Verifier que le HTML a ete supprime
        assert saved_chantier is not None
        assert "<script>" not in saved_chantier.nom
        assert saved_chantier.nom == "Chantier alert('xss')"

    def test_sanitize_chantier_adresse(self):
        """Test: l'adresse du chantier est sanitize (HTML stripped)."""
        chantier_data = _make_chantier_data(
            adresse="12 rue <b>Test</b>"
        )
        budget_data = _make_budget_data()
        lot_data = _make_lot_data()

        saved_chantier = None
        def save_chantier(chantier):
            nonlocal saved_chantier
            saved_chantier = chantier
            chantier.id = 100
            return chantier

        self.mock_chantier_repo.get_last_code.return_value = "A001"
        self.mock_chantier_repo.save.side_effect = save_chantier

        mock_budget = Mock(spec=Budget)
        mock_budget.id = 200
        self.mock_budget_repo.save.return_value = mock_budget

        self.adapter.create_chantier_from_devis(
            chantier_data=chantier_data,
            budget_data=budget_data,
            lots_data=[lot_data],
        )

        # Verifier que le HTML a ete supprime
        assert saved_chantier is not None
        assert "<b>" not in saved_chantier.adresse
        assert saved_chantier.adresse == "12 rue Test"

    def test_sanitize_chantier_description(self):
        """Test: la description du chantier est sanitize (HTML stripped)."""
        chantier_data = _make_chantier_data(
            description="Description <img src=x onerror=alert(1)>"
        )
        budget_data = _make_budget_data()
        lot_data = _make_lot_data()

        saved_chantier = None
        def save_chantier(chantier):
            nonlocal saved_chantier
            saved_chantier = chantier
            chantier.id = 100
            return chantier

        self.mock_chantier_repo.get_last_code.return_value = "A001"
        self.mock_chantier_repo.save.side_effect = save_chantier

        mock_budget = Mock(spec=Budget)
        mock_budget.id = 200
        self.mock_budget_repo.save.return_value = mock_budget

        self.adapter.create_chantier_from_devis(
            chantier_data=chantier_data,
            budget_data=budget_data,
            lots_data=[lot_data],
        )

        # Verifier que le HTML a ete supprime
        assert saved_chantier is not None
        assert "<img" not in saved_chantier.description
        assert saved_chantier.description == "Description"

    def test_sanitize_description_none(self):
        """Test: description None est geree correctement."""
        chantier_data = _make_chantier_data(description=None)
        budget_data = _make_budget_data()
        lot_data = _make_lot_data()

        saved_chantier = None
        def save_chantier(chantier):
            nonlocal saved_chantier
            saved_chantier = chantier
            chantier.id = 100
            return chantier

        self.mock_chantier_repo.get_last_code.return_value = "A001"
        self.mock_chantier_repo.save.side_effect = save_chantier

        mock_budget = Mock(spec=Budget)
        mock_budget.id = 200
        self.mock_budget_repo.save.return_value = mock_budget

        self.adapter.create_chantier_from_devis(
            chantier_data=chantier_data,
            budget_data=budget_data,
            lots_data=[lot_data],
        )

        assert saved_chantier is not None
        assert saved_chantier.description is None

    def test_sanitize_rejects_long_nom(self):
        """Test: un nom trop long leve une exception."""
        from shared.infrastructure.connectors.security import SecurityError

        long_nom = "A" * 300  # > 200 max
        chantier_data = _make_chantier_data(nom=long_nom)
        budget_data = _make_budget_data()
        lot_data = _make_lot_data()

        self.mock_chantier_repo.get_last_code.return_value = "A001"

        with pytest.raises(SecurityError, match="Texte trop long"):
            self.adapter.create_chantier_from_devis(
                chantier_data=chantier_data,
                budget_data=budget_data,
                lots_data=[lot_data],
            )

    # ─────────────────────────────────────────────────────────────────────
    # Chantier data mapping
    # ─────────────────────────────────────────────────────────────────────

    def test_chantier_statut_is_ouvert(self):
        """Test: le chantier est cree avec statut OUVERT."""
        chantier_data = _make_chantier_data()
        budget_data = _make_budget_data()
        lot_data = _make_lot_data()

        saved_chantier = None
        def save_chantier(chantier):
            nonlocal saved_chantier
            saved_chantier = chantier
            chantier.id = 100
            return chantier

        self.mock_chantier_repo.get_last_code.return_value = "A001"
        self.mock_chantier_repo.save.side_effect = save_chantier

        mock_budget = Mock(spec=Budget)
        mock_budget.id = 200
        self.mock_budget_repo.save.return_value = mock_budget

        self.adapter.create_chantier_from_devis(
            chantier_data=chantier_data,
            budget_data=budget_data,
            lots_data=[lot_data],
        )

        assert saved_chantier is not None
        assert saved_chantier.statut == StatutChantier.ouvert()

    def test_chantier_conducteur_ids_mapped(self):
        """Test: les conducteurs sont mappes correctement."""
        chantier_data = _make_chantier_data(conducteur_ids=[1, 2, 3])
        budget_data = _make_budget_data()
        lot_data = _make_lot_data()

        saved_chantier = None
        def save_chantier(chantier):
            nonlocal saved_chantier
            saved_chantier = chantier
            chantier.id = 100
            return chantier

        self.mock_chantier_repo.get_last_code.return_value = "A001"
        self.mock_chantier_repo.save.side_effect = save_chantier

        mock_budget = Mock(spec=Budget)
        mock_budget.id = 200
        self.mock_budget_repo.save.return_value = mock_budget

        self.adapter.create_chantier_from_devis(
            chantier_data=chantier_data,
            budget_data=budget_data,
            lots_data=[lot_data],
        )

        assert saved_chantier is not None
        assert saved_chantier.conducteur_ids == [1, 2, 3]

    # ─────────────────────────────────────────────────────────────────────
    # Budget data mapping
    # ─────────────────────────────────────────────────────────────────────

    def test_budget_linked_to_chantier(self):
        """Test: le budget est lie au chantier cree."""
        chantier_data = _make_chantier_data()
        budget_data = _make_budget_data()
        lot_data = _make_lot_data()

        mock_chantier = Mock(spec=Chantier)
        mock_chantier.id = 100
        mock_chantier.code = CodeChantier("A042")
        self.mock_chantier_repo.get_last_code.return_value = "A041"
        self.mock_chantier_repo.save.return_value = mock_chantier

        saved_budget = None
        def save_budget(budget):
            nonlocal saved_budget
            saved_budget = budget
            budget.id = 200
            return budget

        self.mock_budget_repo.save.side_effect = save_budget

        self.adapter.create_chantier_from_devis(
            chantier_data=chantier_data,
            budget_data=budget_data,
            lots_data=[lot_data],
        )

        assert saved_budget is not None
        assert saved_budget.chantier_id == 100

    def test_budget_montant_initial_mapped(self):
        """Test: le montant initial du budget est mappe correctement."""
        chantier_data = _make_chantier_data()
        budget_data = _make_budget_data(montant_initial_ht=Decimal("75000"))
        lot_data = _make_lot_data()

        mock_chantier = Mock(spec=Chantier)
        mock_chantier.id = 100
        mock_chantier.code = CodeChantier("A042")
        self.mock_chantier_repo.get_last_code.return_value = "A041"
        self.mock_chantier_repo.save.return_value = mock_chantier

        saved_budget = None
        def save_budget(budget):
            nonlocal saved_budget
            saved_budget = budget
            budget.id = 200
            return budget

        self.mock_budget_repo.save.side_effect = save_budget

        self.adapter.create_chantier_from_devis(
            chantier_data=chantier_data,
            budget_data=budget_data,
            lots_data=[lot_data],
        )

        assert saved_budget is not None
        assert saved_budget.montant_initial_ht == Decimal("75000")
        assert saved_budget.montant_avenants_ht == Decimal("0")

    # ─────────────────────────────────────────────────────────────────────
    # Lots data mapping
    # ─────────────────────────────────────────────────────────────────────

    def test_lots_linked_to_budget(self):
        """Test: les lots sont lies au budget cree."""
        chantier_data = _make_chantier_data()
        budget_data = _make_budget_data()
        lot_data = _make_lot_data()

        mock_chantier = Mock(spec=Chantier)
        mock_chantier.id = 100
        mock_chantier.code = CodeChantier("A042")
        self.mock_chantier_repo.get_last_code.return_value = "A041"
        self.mock_chantier_repo.save.return_value = mock_chantier

        mock_budget = Mock(spec=Budget)
        mock_budget.id = 200
        self.mock_budget_repo.save.return_value = mock_budget

        saved_lots = []
        def save_lot(lot):
            saved_lots.append(lot)
            return lot

        self.mock_lot_budgetaire_repo.save.side_effect = save_lot

        self.adapter.create_chantier_from_devis(
            chantier_data=chantier_data,
            budget_data=budget_data,
            lots_data=[lot_data],
        )

        assert len(saved_lots) == 1
        assert saved_lots[0].budget_id == 200

    def test_lots_count_matches_result(self):
        """Test: le nombre de lots crees correspond au resultat."""
        chantier_data = _make_chantier_data()
        budget_data = _make_budget_data()
        lots_data = [
            _make_lot_data(code_lot=f"LOT-{i:02d}", ordre=i)
            for i in range(1, 6)
        ]

        mock_chantier = Mock(spec=Chantier)
        mock_chantier.id = 100
        mock_chantier.code = CodeChantier("A042")
        self.mock_chantier_repo.get_last_code.return_value = "A041"
        self.mock_chantier_repo.save.return_value = mock_chantier

        mock_budget = Mock(spec=Budget)
        mock_budget.id = 200
        self.mock_budget_repo.save.return_value = mock_budget

        result = self.adapter.create_chantier_from_devis(
            chantier_data=chantier_data,
            budget_data=budget_data,
            lots_data=lots_data,
        )

        assert result.nb_lots_transferes == 5
        assert self.mock_lot_budgetaire_repo.save.call_count == 5
