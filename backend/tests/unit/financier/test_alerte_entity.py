"""Tests unitaires pour l'entite AlerteDepassement du module Financier."""

import pytest
from datetime import datetime
from decimal import Decimal

from modules.financier.domain.entities import AlerteDepassement


class TestAlerteDepassement:
    """Tests pour l'entite AlerteDepassement."""

    def _make_alerte(self, **kwargs):
        """Cree une alerte valide avec valeurs par defaut."""
        defaults = {
            "chantier_id": 1,
            "budget_id": 10,
            "type_alerte": "seuil_engage",
            "message": "Depassement du seuil a 85%",
            "pourcentage_atteint": Decimal("85.5"),
            "seuil_configure": Decimal("80"),
            "montant_budget_ht": Decimal("500000"),
            "montant_atteint_ht": Decimal("427500"),
        }
        defaults.update(kwargs)
        return AlerteDepassement(**defaults)

    # -- Creation valide -------------------------------------------------------

    def test_create_alerte_valid(self):
        """Test: creation d'une alerte valide."""
        alerte = self._make_alerte(id=1)
        assert alerte.id == 1
        assert alerte.chantier_id == 1
        assert alerte.budget_id == 10
        assert alerte.type_alerte == "seuil_engage"
        assert alerte.message == "Depassement du seuil a 85%"
        assert alerte.pourcentage_atteint == Decimal("85.5")
        assert alerte.seuil_configure == Decimal("80")
        assert alerte.montant_budget_ht == Decimal("500000")
        assert alerte.montant_atteint_ht == Decimal("427500")
        assert alerte.est_acquittee is False
        assert alerte.acquittee_par is None
        assert alerte.acquittee_at is None

    def test_create_alerte_type_seuil_realise(self):
        """Test: creation d'une alerte de type seuil_realise."""
        alerte = self._make_alerte(type_alerte="seuil_realise")
        assert alerte.type_alerte == "seuil_realise"

    def test_create_alerte_type_depassement_lot(self):
        """Test: creation d'une alerte de type depassement_lot."""
        alerte = self._make_alerte(type_alerte="depassement_lot")
        assert alerte.type_alerte == "depassement_lot"

    # -- __post_init__ validation -----------------------------------------------

    def test_create_alerte_chantier_id_zero(self):
        """Test: erreur si chantier_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            self._make_alerte(chantier_id=0)
        assert "chantier" in str(exc_info.value).lower()

    def test_create_alerte_chantier_id_negatif(self):
        """Test: erreur si chantier_id est negatif."""
        with pytest.raises(ValueError):
            self._make_alerte(chantier_id=-1)

    def test_create_alerte_budget_id_zero(self):
        """Test: erreur si budget_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            self._make_alerte(budget_id=0)
        assert "budget" in str(exc_info.value).lower()

    def test_create_alerte_budget_id_negatif(self):
        """Test: erreur si budget_id est negatif."""
        with pytest.raises(ValueError):
            self._make_alerte(budget_id=-1)

    # -- acquitter() -------------------------------------------------------

    def test_acquitter_success(self):
        """Test: acquittement reussi d'une alerte."""
        alerte = self._make_alerte()
        alerte.acquitter(user_id=5)
        assert alerte.est_acquittee is True
        assert alerte.acquittee_par == 5
        assert alerte.acquittee_at is not None
        assert isinstance(alerte.acquittee_at, datetime)

    def test_acquitter_deja_acquittee(self):
        """Test: erreur si alerte deja acquittee."""
        alerte = self._make_alerte()
        alerte.acquitter(user_id=5)
        with pytest.raises(ValueError) as exc_info:
            alerte.acquitter(user_id=10)
        assert "acquittee" in str(exc_info.value).lower() or "acquittée" in str(exc_info.value).lower()

    # -- to_dict() -------------------------------------------------------

    def test_to_dict_structure(self):
        """Test: to_dict retourne la structure correcte."""
        now = datetime.utcnow()
        alerte = self._make_alerte(id=1, created_at=now)
        d = alerte.to_dict()
        assert d["id"] == 1
        assert d["chantier_id"] == 1
        assert d["budget_id"] == 10
        assert d["type_alerte"] == "seuil_engage"
        assert d["message"] == "Depassement du seuil a 85%"
        assert d["pourcentage_atteint"] == "85.5"
        assert d["seuil_configure"] == "80"
        assert d["montant_budget_ht"] == "500000"
        assert d["montant_atteint_ht"] == "427500"
        assert d["est_acquittee"] is False
        assert d["acquittee_par"] is None
        assert d["acquittee_at"] is None
        assert d["created_at"] == now.isoformat()

    def test_to_dict_apres_acquittement(self):
        """Test: to_dict apres acquittement."""
        alerte = self._make_alerte(id=1, created_at=datetime.utcnow())
        alerte.acquitter(user_id=5)
        d = alerte.to_dict()
        assert d["est_acquittee"] is True
        assert d["acquittee_par"] == 5
        assert d["acquittee_at"] is not None

    def test_to_dict_none_dates(self):
        """Test: to_dict gere les dates None."""
        alerte = self._make_alerte(id=1)
        d = alerte.to_dict()
        assert d["created_at"] is None
        assert d["acquittee_at"] is None
