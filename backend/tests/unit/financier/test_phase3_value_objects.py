"""Tests unitaires pour les Value Objects Phase 3 du module Financier."""

import pytest
from decimal import Decimal

from modules.financier.domain.value_objects.avancement_tache import AvancementTache


class TestAvancementTache:
    """Tests pour le value object AvancementTache."""

    def _make_avancement(self, **kwargs):
        """Cree un avancement valide avec valeurs par defaut."""
        defaults = {
            "tache_id": 1,
            "titre": "Terrassement zone A",
            "statut": "en_cours",
            "heures_estimees": Decimal("40"),
            "heures_realisees": Decimal("25"),
            "quantite_estimee": Decimal("100"),
            "quantite_realisee": Decimal("60"),
            "progression_pct": Decimal("60"),
        }
        defaults.update(kwargs)
        return AvancementTache(**defaults)

    # -- Creation valide -------------------------------------------------------

    def test_create_avancement_valid(self):
        """Test: creation d'un avancement valide avec tous les champs."""
        avancement = self._make_avancement()
        assert avancement.tache_id == 1
        assert avancement.titre == "Terrassement zone A"
        assert avancement.statut == "en_cours"
        assert avancement.heures_estimees == Decimal("40")
        assert avancement.heures_realisees == Decimal("25")
        assert avancement.quantite_estimee == Decimal("100")
        assert avancement.quantite_realisee == Decimal("60")
        assert avancement.progression_pct == Decimal("60")

    def test_create_avancement_heures_estimees_none(self):
        """Test: heures_estimees peut etre None."""
        avancement = self._make_avancement(heures_estimees=None)
        assert avancement.heures_estimees is None

    def test_create_avancement_quantite_estimee_none(self):
        """Test: quantite_estimee peut etre None."""
        avancement = self._make_avancement(quantite_estimee=None)
        assert avancement.quantite_estimee is None

    def test_create_avancement_zero_progression(self):
        """Test: progression a 0% est valide."""
        avancement = self._make_avancement(
            progression_pct=Decimal("0"),
            heures_realisees=Decimal("0"),
            quantite_realisee=Decimal("0"),
        )
        assert avancement.progression_pct == Decimal("0")

    def test_create_avancement_complete(self):
        """Test: progression a 100% est valide."""
        avancement = self._make_avancement(
            progression_pct=Decimal("100"),
            heures_realisees=Decimal("40"),
            quantite_realisee=Decimal("100"),
            statut="terminee",
        )
        assert avancement.progression_pct == Decimal("100")
        assert avancement.statut == "terminee"

    # -- Immutabilite (frozen=True) -----------------------------------------------

    def test_frozen_cannot_modify_titre(self):
        """Test: impossible de modifier un champ (frozen dataclass)."""
        avancement = self._make_avancement()
        with pytest.raises(AttributeError):
            avancement.titre = "Nouveau titre"

    def test_frozen_cannot_modify_progression(self):
        """Test: impossible de modifier la progression."""
        avancement = self._make_avancement()
        with pytest.raises(AttributeError):
            avancement.progression_pct = Decimal("99")

    def test_frozen_cannot_modify_statut(self):
        """Test: impossible de modifier le statut."""
        avancement = self._make_avancement()
        with pytest.raises(AttributeError):
            avancement.statut = "terminee"

    # -- Egalite (frozen dataclass => auto __eq__) --------------------------------

    def test_eq_same_values(self):
        """Test: deux avancements avec les memes valeurs sont egaux."""
        a1 = self._make_avancement()
        a2 = self._make_avancement()
        assert a1 == a2

    def test_eq_different_values(self):
        """Test: deux avancements avec des valeurs differentes ne sont pas egaux."""
        a1 = self._make_avancement(tache_id=1)
        a2 = self._make_avancement(tache_id=2)
        assert a1 != a2

    def test_eq_different_progression(self):
        """Test: deux avancements avec des progressions differentes ne sont pas egaux."""
        a1 = self._make_avancement(progression_pct=Decimal("60"))
        a2 = self._make_avancement(progression_pct=Decimal("80"))
        assert a1 != a2

    # -- Hash (frozen dataclass => auto __hash__) ----------------------------------

    def test_hash_same_values(self):
        """Test: deux avancements identiques ont le meme hash."""
        a1 = self._make_avancement()
        a2 = self._make_avancement()
        assert hash(a1) == hash(a2)

    def test_hash_can_be_used_in_set(self):
        """Test: les avancements peuvent etre utilises dans un set."""
        a1 = self._make_avancement(tache_id=1)
        a2 = self._make_avancement(tache_id=1)
        a3 = self._make_avancement(tache_id=2)
        s = {a1, a2, a3}
        assert len(s) == 2

    # -- Differents statuts -----------------------------------------------

    def test_statut_a_faire(self):
        """Test: statut 'a_faire' est valide."""
        avancement = self._make_avancement(statut="a_faire")
        assert avancement.statut == "a_faire"

    def test_statut_en_cours(self):
        """Test: statut 'en_cours' est valide."""
        avancement = self._make_avancement(statut="en_cours")
        assert avancement.statut == "en_cours"

    def test_statut_terminee(self):
        """Test: statut 'terminee' est valide."""
        avancement = self._make_avancement(statut="terminee")
        assert avancement.statut == "terminee"
