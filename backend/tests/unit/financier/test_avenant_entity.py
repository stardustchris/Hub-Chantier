"""Tests unitaires pour l'entite AvenantBudgetaire du module Financier."""

import pytest
from datetime import datetime
from decimal import Decimal

from modules.financier.domain.entities import AvenantBudgetaire


class TestAvenantBudgetaire:
    """Tests pour l'entite AvenantBudgetaire."""

    def _make_avenant(self, **kwargs):
        """Cree un avenant valide avec valeurs par defaut."""
        defaults = {
            "budget_id": 1,
            "numero": "AVN-2026-01",
            "motif": "Travaux supplementaires",
            "montant_ht": Decimal("25000"),
        }
        defaults.update(kwargs)
        return AvenantBudgetaire(**defaults)

    # -- Creation valide -------------------------------------------------------

    def test_create_avenant_valid(self):
        """Test: creation d'un avenant valide."""
        avenant = self._make_avenant(
            id=1,
            budget_id=10,
            impact_description="Ajout de travaux de terrassement",
        )
        assert avenant.id == 1
        assert avenant.budget_id == 10
        assert avenant.numero == "AVN-2026-01"
        assert avenant.motif == "Travaux supplementaires"
        assert avenant.montant_ht == Decimal("25000")
        assert avenant.impact_description == "Ajout de travaux de terrassement"
        assert avenant.statut == "brouillon"
        assert avenant.validated_by is None
        assert avenant.validated_at is None

    def test_create_avenant_negatif_montant(self):
        """Test: montant negatif autorise (reduction de budget)."""
        avenant = self._make_avenant(montant_ht=Decimal("-10000"))
        assert avenant.montant_ht == Decimal("-10000")

    def test_create_avenant_montant_zero(self):
        """Test: montant a zero est autorise."""
        avenant = self._make_avenant(montant_ht=Decimal("0"))
        assert avenant.montant_ht == Decimal("0")

    # -- __post_init__ validation -----------------------------------------------

    def test_create_avenant_motif_vide(self):
        """Test: erreur si motif vide."""
        with pytest.raises(ValueError) as exc_info:
            self._make_avenant(motif="")
        assert "motif" in str(exc_info.value).lower()

    def test_create_avenant_motif_espaces(self):
        """Test: erreur si motif uniquement espaces."""
        with pytest.raises(ValueError):
            self._make_avenant(motif="   ")

    def test_create_avenant_numero_vide(self):
        """Test: erreur si numero vide."""
        with pytest.raises(ValueError) as exc_info:
            self._make_avenant(numero="")
        assert "numéro" in str(exc_info.value).lower() or "numero" in str(exc_info.value).lower()

    def test_create_avenant_numero_espaces(self):
        """Test: erreur si numero uniquement espaces."""
        with pytest.raises(ValueError):
            self._make_avenant(numero="   ")

    def test_create_avenant_budget_id_zero(self):
        """Test: erreur si budget_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            self._make_avenant(budget_id=0)
        assert "budget" in str(exc_info.value).lower()

    def test_create_avenant_budget_id_negatif(self):
        """Test: erreur si budget_id est negatif."""
        with pytest.raises(ValueError):
            self._make_avenant(budget_id=-1)

    # -- valider() -------------------------------------------------------

    def test_valider_success(self):
        """Test: validation reussie d'un avenant brouillon."""
        avenant = self._make_avenant()
        avenant.valider(validated_by=5)
        assert avenant.statut == "valide"
        assert avenant.validated_by == 5
        assert avenant.validated_at is not None
        assert isinstance(avenant.validated_at, datetime)
        assert avenant.updated_at is not None

    def test_valider_deja_valide(self):
        """Test: erreur si on valide un avenant deja valide."""
        avenant = self._make_avenant()
        avenant.valider(validated_by=5)
        with pytest.raises(ValueError) as exc_info:
            avenant.valider(validated_by=10)
        assert "déjà validé" in str(exc_info.value).lower() or "deja valide" in str(exc_info.value).lower()

    # -- Properties -------------------------------------------------------

    def test_est_valide_brouillon(self):
        """Test: est_valide est False pour un brouillon."""
        avenant = self._make_avenant()
        assert avenant.est_valide is False

    def test_est_valide_apres_validation(self):
        """Test: est_valide est True apres validation."""
        avenant = self._make_avenant()
        avenant.valider(validated_by=5)
        assert avenant.est_valide is True

    def test_est_supprime_false(self):
        """Test: est_supprime est False par defaut."""
        avenant = self._make_avenant()
        assert avenant.est_supprime is False

    def test_est_supprime_true(self):
        """Test: est_supprime est True si deleted_at est defini."""
        avenant = self._make_avenant(deleted_at=datetime.utcnow(), deleted_by=1)
        assert avenant.est_supprime is True

    # -- to_dict() -------------------------------------------------------

    def test_to_dict_structure(self):
        """Test: to_dict retourne la structure correcte."""
        now = datetime.utcnow()
        avenant = self._make_avenant(
            id=1,
            budget_id=10,
            impact_description="Test impact",
            created_by=5,
            created_at=now,
        )
        d = avenant.to_dict()
        assert d["id"] == 1
        assert d["budget_id"] == 10
        assert d["numero"] == "AVN-2026-01"
        assert d["motif"] == "Travaux supplementaires"
        assert d["montant_ht"] == "25000"
        assert d["impact_description"] == "Test impact"
        assert d["statut"] == "brouillon"
        assert d["created_by"] == 5
        assert d["validated_by"] is None
        assert d["validated_at"] is None
        assert d["created_at"] == now.isoformat()

    def test_to_dict_with_validation(self):
        """Test: to_dict inclut les champs de validation apres validation."""
        avenant = self._make_avenant(id=1, created_at=datetime.utcnow())
        avenant.valider(validated_by=5)
        d = avenant.to_dict()
        assert d["statut"] == "valide"
        assert d["validated_by"] == 5
        assert d["validated_at"] is not None
        assert d["updated_at"] is not None

    def test_to_dict_none_dates(self):
        """Test: to_dict gere les dates None."""
        avenant = self._make_avenant(id=1)
        d = avenant.to_dict()
        assert d["validated_at"] is None
        assert d["created_at"] is None
        assert d["updated_at"] is None
