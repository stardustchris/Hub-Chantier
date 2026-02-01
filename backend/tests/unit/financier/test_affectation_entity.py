"""Tests unitaires pour l'entite AffectationTacheLot du module Financier."""

import pytest
from datetime import datetime
from decimal import Decimal

from modules.financier.domain.entities import AffectationTacheLot


class TestAffectationTacheLot:
    """Tests pour l'entite AffectationTacheLot."""

    def _make_affectation(self, **kwargs):
        """Cree une affectation valide avec valeurs par defaut."""
        defaults = {
            "chantier_id": 1,
            "tache_id": 10,
            "lot_budgetaire_id": 20,
            "pourcentage_affectation": Decimal("100"),
        }
        defaults.update(kwargs)
        return AffectationTacheLot(**defaults)

    # -- Creation valide -------------------------------------------------------

    def test_create_affectation_valid(self):
        """Test: creation d'une affectation valide avec tous les champs."""
        affectation = self._make_affectation(
            id=1,
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
            pourcentage_affectation=Decimal("75"),
            created_at=datetime(2026, 1, 15),
            created_by=3,
        )
        assert affectation.id == 1
        assert affectation.chantier_id == 5
        assert affectation.tache_id == 10
        assert affectation.lot_budgetaire_id == 20
        assert affectation.pourcentage_affectation == Decimal("75")
        assert affectation.created_at == datetime(2026, 1, 15)
        assert affectation.created_by == 3

    def test_create_affectation_defaults(self):
        """Test: les valeurs par defaut sont correctement initialisees."""
        affectation = self._make_affectation()
        assert affectation.id is None
        assert affectation.pourcentage_affectation == Decimal("100")
        assert affectation.created_at is None
        assert affectation.created_by is None

    def test_create_affectation_pourcentage_zero(self):
        """Test: pourcentage a 0 est autorise."""
        affectation = self._make_affectation(pourcentage_affectation=Decimal("0"))
        assert affectation.pourcentage_affectation == Decimal("0")

    def test_create_affectation_pourcentage_100(self):
        """Test: pourcentage a 100 est autorise."""
        affectation = self._make_affectation(pourcentage_affectation=Decimal("100"))
        assert affectation.pourcentage_affectation == Decimal("100")

    def test_create_affectation_pourcentage_decimal(self):
        """Test: pourcentage avec decimales (ex: 33.33) est autorise."""
        affectation = self._make_affectation(pourcentage_affectation=Decimal("33.33"))
        assert affectation.pourcentage_affectation == Decimal("33.33")

    # -- __post_init__ validation -----------------------------------------------

    def test_create_affectation_chantier_id_zero(self):
        """Test: erreur si chantier_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            self._make_affectation(chantier_id=0)
        assert "chantier" in str(exc_info.value).lower()

    def test_create_affectation_chantier_id_negatif(self):
        """Test: erreur si chantier_id est negatif."""
        with pytest.raises(ValueError):
            self._make_affectation(chantier_id=-1)

    def test_create_affectation_tache_id_zero(self):
        """Test: erreur si tache_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            self._make_affectation(tache_id=0)
        assert "tache" in str(exc_info.value).lower()

    def test_create_affectation_tache_id_negatif(self):
        """Test: erreur si tache_id est negatif."""
        with pytest.raises(ValueError):
            self._make_affectation(tache_id=-1)

    def test_create_affectation_lot_id_zero(self):
        """Test: erreur si lot_budgetaire_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            self._make_affectation(lot_budgetaire_id=0)
        assert "lot" in str(exc_info.value).lower()

    def test_create_affectation_lot_id_negatif(self):
        """Test: erreur si lot_budgetaire_id est negatif."""
        with pytest.raises(ValueError):
            self._make_affectation(lot_budgetaire_id=-1)

    def test_create_affectation_pourcentage_negatif(self):
        """Test: erreur si pourcentage est negatif."""
        with pytest.raises(ValueError) as exc_info:
            self._make_affectation(pourcentage_affectation=Decimal("-1"))
        assert "pourcentage" in str(exc_info.value).lower()

    def test_create_affectation_pourcentage_superieur_100(self):
        """Test: erreur si pourcentage depasse 100."""
        with pytest.raises(ValueError) as exc_info:
            self._make_affectation(pourcentage_affectation=Decimal("101"))
        assert "pourcentage" in str(exc_info.value).lower()

    def test_create_affectation_pourcentage_tres_superieur(self):
        """Test: erreur si pourcentage est 200."""
        with pytest.raises(ValueError):
            self._make_affectation(pourcentage_affectation=Decimal("200"))

    # -- to_dict() -------------------------------------------------------

    def test_to_dict_structure(self):
        """Test: to_dict retourne la structure correcte."""
        now = datetime(2026, 1, 15, 10, 30, 0)
        affectation = self._make_affectation(
            id=1,
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
            pourcentage_affectation=Decimal("75"),
            created_at=now,
            created_by=3,
        )
        d = affectation.to_dict()
        assert d["id"] == 1
        assert d["chantier_id"] == 5
        assert d["tache_id"] == 10
        assert d["lot_budgetaire_id"] == 20
        assert d["pourcentage_affectation"] == "75"
        assert d["created_at"] == now.isoformat()
        assert d["created_by"] == 3

    def test_to_dict_none_dates(self):
        """Test: to_dict gere les dates None."""
        affectation = self._make_affectation(id=1)
        d = affectation.to_dict()
        assert d["created_at"] is None

    def test_to_dict_pourcentage_decimal(self):
        """Test: to_dict convertit le pourcentage decimal en string."""
        affectation = self._make_affectation(
            pourcentage_affectation=Decimal("33.33"),
        )
        d = affectation.to_dict()
        assert d["pourcentage_affectation"] == "33.33"

    # -- __eq__ et __hash__ -------------------------------------------------------

    def test_eq_same_id(self):
        """Test: deux affectations avec le meme ID sont egales."""
        a1 = self._make_affectation(id=1)
        a2 = self._make_affectation(id=1)
        assert a1 == a2

    def test_eq_different_id(self):
        """Test: deux affectations avec des IDs differents ne sont pas egales."""
        a1 = self._make_affectation(id=1)
        a2 = self._make_affectation(id=2)
        assert a1 != a2

    def test_eq_none_id(self):
        """Test: deux affectations sans ID ne sont pas egales."""
        a1 = self._make_affectation()
        a2 = self._make_affectation()
        assert a1 != a2

    def test_eq_one_none_id(self):
        """Test: une affectation avec ID et une sans ID ne sont pas egales."""
        a1 = self._make_affectation(id=1)
        a2 = self._make_affectation()
        assert a1 != a2

    def test_eq_different_type(self):
        """Test: une affectation n'est pas egale a un autre type."""
        a1 = self._make_affectation(id=1)
        assert a1 != "not an affectation"

    def test_hash_with_id(self):
        """Test: le hash est base sur l'ID."""
        a1 = self._make_affectation(id=1)
        a2 = self._make_affectation(id=1)
        assert hash(a1) == hash(a2)

    def test_hash_different_ids(self):
        """Test: des IDs differents donnent des hashes differents."""
        a1 = self._make_affectation(id=1)
        a2 = self._make_affectation(id=2)
        assert hash(a1) != hash(a2)

    def test_hash_none_id(self):
        """Test: le hash fonctionne sans ID (base sur id(self))."""
        a1 = self._make_affectation()
        # Ne doit pas lever d'exception
        h = hash(a1)
        assert isinstance(h, int)

    def test_can_be_used_in_set(self):
        """Test: les affectations avec ID peuvent etre utilisees dans un set."""
        a1 = self._make_affectation(id=1)
        a2 = self._make_affectation(id=1)
        a3 = self._make_affectation(id=2)
        s = {a1, a2, a3}
        assert len(s) == 2
