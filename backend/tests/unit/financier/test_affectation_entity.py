"""Tests unitaires pour l'entite AffectationBudgetTache.

FIN-03: Affectation budgets aux taches - tests de l'entite domain.
"""

import pytest
from datetime import datetime
from decimal import Decimal

from modules.financier.domain.entities.affectation_budget_tache import (
    AffectationBudgetTache,
)


class TestAffectationBudgetTacheCreation:
    """Tests de creation de l'entite AffectationBudgetTache."""

    def test_create_valid_affectation(self):
        """Test: creation avec des valeurs valides."""
        aff = AffectationBudgetTache(
            lot_budgetaire_id=1,
            tache_id=10,
            pourcentage_allocation=Decimal("50"),
        )
        assert aff.lot_budgetaire_id == 1
        assert aff.tache_id == 10
        assert aff.pourcentage_allocation == Decimal("50")
        assert aff.id is None
        assert aff.created_at is None
        assert aff.updated_at is None

    def test_create_with_all_fields(self):
        """Test: creation avec tous les champs."""
        now = datetime(2026, 1, 15, 10, 30)
        aff = AffectationBudgetTache(
            lot_budgetaire_id=2,
            tache_id=20,
            pourcentage_allocation=Decimal("75.5"),
            id=100,
            created_at=now,
            updated_at=now,
        )
        assert aff.id == 100
        assert aff.created_at == now
        assert aff.updated_at == now

    def test_create_with_zero_allocation(self):
        """Test: allocation a 0% est valide."""
        aff = AffectationBudgetTache(
            lot_budgetaire_id=1,
            tache_id=10,
            pourcentage_allocation=Decimal("0"),
        )
        assert aff.pourcentage_allocation == Decimal("0")

    def test_create_with_100_allocation(self):
        """Test: allocation a 100% est valide."""
        aff = AffectationBudgetTache(
            lot_budgetaire_id=1,
            tache_id=10,
            pourcentage_allocation=Decimal("100"),
        )
        assert aff.pourcentage_allocation == Decimal("100")


class TestAffectationBudgetTacheValidation:
    """Tests de validation de l'entite."""

    def test_invalid_lot_budgetaire_id_zero(self):
        """Test: ValueError si lot_budgetaire_id = 0."""
        with pytest.raises(ValueError, match="lot budgetaire"):
            AffectationBudgetTache(
                lot_budgetaire_id=0,
                tache_id=10,
                pourcentage_allocation=Decimal("50"),
            )

    def test_invalid_lot_budgetaire_id_negative(self):
        """Test: ValueError si lot_budgetaire_id < 0."""
        with pytest.raises(ValueError, match="lot budgetaire"):
            AffectationBudgetTache(
                lot_budgetaire_id=-1,
                tache_id=10,
                pourcentage_allocation=Decimal("50"),
            )

    def test_invalid_tache_id_zero(self):
        """Test: ValueError si tache_id = 0."""
        with pytest.raises(ValueError, match="tache"):
            AffectationBudgetTache(
                lot_budgetaire_id=1,
                tache_id=0,
                pourcentage_allocation=Decimal("50"),
            )

    def test_invalid_tache_id_negative(self):
        """Test: ValueError si tache_id < 0."""
        with pytest.raises(ValueError, match="tache"):
            AffectationBudgetTache(
                lot_budgetaire_id=1,
                tache_id=-5,
                pourcentage_allocation=Decimal("50"),
            )

    def test_invalid_pourcentage_negative(self):
        """Test: ValueError si pourcentage < 0."""
        with pytest.raises(ValueError, match="pourcentage"):
            AffectationBudgetTache(
                lot_budgetaire_id=1,
                tache_id=10,
                pourcentage_allocation=Decimal("-1"),
            )

    def test_invalid_pourcentage_over_100(self):
        """Test: ValueError si pourcentage > 100."""
        with pytest.raises(ValueError, match="pourcentage"):
            AffectationBudgetTache(
                lot_budgetaire_id=1,
                tache_id=10,
                pourcentage_allocation=Decimal("101"),
            )

    def test_invalid_pourcentage_way_over_100(self):
        """Test: ValueError si pourcentage tres superieur a 100."""
        with pytest.raises(ValueError, match="pourcentage"):
            AffectationBudgetTache(
                lot_budgetaire_id=1,
                tache_id=10,
                pourcentage_allocation=Decimal("200"),
            )


class TestAffectationBudgetTacheEquality:
    """Tests d'egalite et de hash."""

    def test_equality_by_id(self):
        """Test: egalite basee sur l'ID."""
        a1 = AffectationBudgetTache(
            lot_budgetaire_id=1, tache_id=10,
            pourcentage_allocation=Decimal("50"), id=1,
        )
        a2 = AffectationBudgetTache(
            lot_budgetaire_id=2, tache_id=20,
            pourcentage_allocation=Decimal("75"), id=1,
        )
        assert a1 == a2

    def test_inequality_different_ids(self):
        """Test: inegalite si IDs differents."""
        a1 = AffectationBudgetTache(
            lot_budgetaire_id=1, tache_id=10,
            pourcentage_allocation=Decimal("50"), id=1,
        )
        a2 = AffectationBudgetTache(
            lot_budgetaire_id=1, tache_id=10,
            pourcentage_allocation=Decimal("50"), id=2,
        )
        assert a1 != a2

    def test_inequality_none_ids(self):
        """Test: inegalite si un des IDs est None."""
        a1 = AffectationBudgetTache(
            lot_budgetaire_id=1, tache_id=10,
            pourcentage_allocation=Decimal("50"), id=1,
        )
        a2 = AffectationBudgetTache(
            lot_budgetaire_id=1, tache_id=10,
            pourcentage_allocation=Decimal("50"),
        )
        assert a1 != a2

    def test_inequality_both_none_ids(self):
        """Test: inegalite si les deux IDs sont None."""
        a1 = AffectationBudgetTache(
            lot_budgetaire_id=1, tache_id=10,
            pourcentage_allocation=Decimal("50"),
        )
        a2 = AffectationBudgetTache(
            lot_budgetaire_id=1, tache_id=10,
            pourcentage_allocation=Decimal("50"),
        )
        assert a1 != a2

    def test_inequality_with_other_type(self):
        """Test: inegalite avec un type different."""
        a = AffectationBudgetTache(
            lot_budgetaire_id=1, tache_id=10,
            pourcentage_allocation=Decimal("50"), id=1,
        )
        assert a != "not an affectation"

    def test_hash_with_id(self):
        """Test: hash base sur l'ID."""
        a = AffectationBudgetTache(
            lot_budgetaire_id=1, tache_id=10,
            pourcentage_allocation=Decimal("50"), id=42,
        )
        assert hash(a) == hash(42)

    def test_hash_without_id(self):
        """Test: hash base sur id(self) si pas d'ID."""
        a = AffectationBudgetTache(
            lot_budgetaire_id=1, tache_id=10,
            pourcentage_allocation=Decimal("50"),
        )
        # Doit fonctionner sans erreur
        assert isinstance(hash(a), int)


class TestAffectationBudgetTacheToDict:
    """Tests pour la methode to_dict."""

    def test_to_dict_complete(self):
        """Test: to_dict avec tous les champs."""
        now = datetime(2026, 2, 1, 14, 0)
        aff = AffectationBudgetTache(
            lot_budgetaire_id=1,
            tache_id=10,
            pourcentage_allocation=Decimal("50"),
            id=42,
            created_at=now,
            updated_at=now,
        )
        d = aff.to_dict()
        assert d["id"] == 42
        assert d["lot_budgetaire_id"] == 1
        assert d["tache_id"] == 10
        assert d["pourcentage_allocation"] == "50"
        assert d["created_at"] == now.isoformat()
        assert d["updated_at"] == now.isoformat()

    def test_to_dict_none_dates(self):
        """Test: to_dict avec dates None."""
        aff = AffectationBudgetTache(
            lot_budgetaire_id=1,
            tache_id=10,
            pourcentage_allocation=Decimal("25.5"),
        )
        d = aff.to_dict()
        assert d["id"] is None
        assert d["created_at"] is None
        assert d["updated_at"] is None
        assert d["pourcentage_allocation"] == "25.5"
