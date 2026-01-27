"""Tests unitaires pour les Value Objects du module pointages."""

import pytest

from modules.pointages.domain.value_objects import (
    StatutPointage,
    TypeVariablePaie,
    Duree,
)


class TestStatutPointage:
    """Tests pour StatutPointage."""

    def test_from_string_valid(self):
        """Test conversion depuis string valide."""
        assert StatutPointage.from_string("brouillon") == StatutPointage.BROUILLON
        assert StatutPointage.from_string("soumis") == StatutPointage.SOUMIS
        assert StatutPointage.from_string("valide") == StatutPointage.VALIDE
        assert StatutPointage.from_string("rejete") == StatutPointage.REJETE

    def test_from_string_case_insensitive(self):
        """Test conversion insensible à la casse."""
        assert StatutPointage.from_string("BROUILLON") == StatutPointage.BROUILLON
        assert StatutPointage.from_string("Soumis") == StatutPointage.SOUMIS

    def test_from_string_invalid(self):
        """Test conversion depuis string invalide."""
        with pytest.raises(ValueError):
            StatutPointage.from_string("invalid")

    def test_can_transition_brouillon_to_soumis(self):
        """Test transition brouillon -> soumis."""
        assert StatutPointage.BROUILLON.can_transition_to(StatutPointage.SOUMIS)
        assert not StatutPointage.BROUILLON.can_transition_to(StatutPointage.VALIDE)
        assert not StatutPointage.BROUILLON.can_transition_to(StatutPointage.REJETE)

    def test_can_transition_soumis_to_valide_or_rejete(self):
        """Test transition soumis -> valide ou rejete."""
        assert StatutPointage.SOUMIS.can_transition_to(StatutPointage.VALIDE)
        assert StatutPointage.SOUMIS.can_transition_to(StatutPointage.REJETE)
        assert not StatutPointage.SOUMIS.can_transition_to(StatutPointage.BROUILLON)

    def test_can_transition_rejete_to_brouillon(self):
        """Test transition rejete -> brouillon."""
        assert StatutPointage.REJETE.can_transition_to(StatutPointage.BROUILLON)
        assert not StatutPointage.REJETE.can_transition_to(StatutPointage.VALIDE)

    def test_valide_is_final(self):
        """Test que valide est un état final."""
        assert not StatutPointage.VALIDE.can_transition_to(StatutPointage.BROUILLON)
        assert not StatutPointage.VALIDE.can_transition_to(StatutPointage.SOUMIS)
        assert not StatutPointage.VALIDE.can_transition_to(StatutPointage.REJETE)

    def test_is_editable(self):
        """Test is_editable."""
        assert StatutPointage.BROUILLON.is_editable()
        assert StatutPointage.REJETE.is_editable()
        assert not StatutPointage.SOUMIS.is_editable()
        assert not StatutPointage.VALIDE.is_editable()

    def test_is_final(self):
        """Test is_final."""
        assert StatutPointage.VALIDE.is_final()
        assert not StatutPointage.BROUILLON.is_final()
        assert not StatutPointage.SOUMIS.is_final()
        assert not StatutPointage.REJETE.is_final()


class TestTypeVariablePaie:
    """Tests pour TypeVariablePaie."""

    def test_from_string_valid(self):
        """Test conversion depuis string valide."""
        assert TypeVariablePaie.from_string("heures_normales") == TypeVariablePaie.HEURES_NORMALES
        assert TypeVariablePaie.from_string("panier_repas") == TypeVariablePaie.PANIER_REPAS
        assert TypeVariablePaie.from_string("conges_payes") == TypeVariablePaie.CONGES_PAYES

    def test_from_string_invalid(self):
        """Test conversion depuis string invalide."""
        with pytest.raises(ValueError):
            TypeVariablePaie.from_string("invalid")

    def test_is_hours_type(self):
        """Test is_hours_type."""
        assert TypeVariablePaie.HEURES_NORMALES.is_hours_type()
        assert TypeVariablePaie.HEURES_SUPPLEMENTAIRES.is_hours_type()
        assert not TypeVariablePaie.PANIER_REPAS.is_hours_type()
        assert not TypeVariablePaie.CONGES_PAYES.is_hours_type()

    def test_is_allowance_type(self):
        """Test is_allowance_type."""
        assert TypeVariablePaie.PANIER_REPAS.is_allowance_type()
        assert TypeVariablePaie.INDEMNITE_TRANSPORT.is_allowance_type()
        assert not TypeVariablePaie.HEURES_NORMALES.is_allowance_type()
        assert not TypeVariablePaie.CONGES_PAYES.is_allowance_type()

    def test_is_absence_type(self):
        """Test is_absence_type."""
        assert TypeVariablePaie.CONGES_PAYES.is_absence_type()
        assert TypeVariablePaie.MALADIE.is_absence_type()
        assert not TypeVariablePaie.HEURES_NORMALES.is_absence_type()
        assert not TypeVariablePaie.PANIER_REPAS.is_absence_type()

    def test_libelle(self):
        """Test propriété libelle."""
        assert TypeVariablePaie.HEURES_NORMALES.libelle == "Heures normales"
        assert TypeVariablePaie.PANIER_REPAS.libelle == "Panier repas"


class TestDuree:
    """Tests pour Duree."""

    def test_creation_valid(self):
        """Test création avec valeurs valides."""
        d = Duree(heures=8, minutes=30)
        assert d.heures == 8
        assert d.minutes == 30

    def test_creation_invalid_heures(self):
        """Test création avec heures invalides."""
        with pytest.raises(ValueError):
            Duree(heures=1000, minutes=0)
        with pytest.raises(ValueError):
            Duree(heures=-1, minutes=0)

    def test_creation_invalid_minutes(self):
        """Test création avec minutes invalides."""
        with pytest.raises(ValueError):
            Duree(heures=8, minutes=60)
        with pytest.raises(ValueError):
            Duree(heures=8, minutes=-1)

    def test_zero(self):
        """Test factory zero."""
        d = Duree.zero()
        assert d.heures == 0
        assert d.minutes == 0
        assert d.is_zero()

    def test_from_minutes(self):
        """Test factory from_minutes."""
        d = Duree.from_minutes(90)
        assert d.heures == 1
        assert d.minutes == 30

    def test_from_decimal(self):
        """Test factory from_decimal."""
        d = Duree.from_decimal(7.5)
        assert d.heures == 7
        assert d.minutes == 30

    def test_from_string(self):
        """Test factory from_string."""
        d = Duree.from_string("08:30")
        assert d.heures == 8
        assert d.minutes == 30

        d2 = Duree.from_string("8:00")
        assert d2.heures == 8
        assert d2.minutes == 0

    def test_from_string_invalid(self):
        """Test from_string avec format invalide."""
        with pytest.raises(ValueError):
            Duree.from_string("invalid")
        with pytest.raises(ValueError):
            Duree.from_string("8-30")
        with pytest.raises(ValueError):
            Duree.from_string("")

    def test_total_minutes(self):
        """Test propriété total_minutes."""
        d = Duree(heures=8, minutes=30)
        assert d.total_minutes == 510

    def test_decimal(self):
        """Test propriété decimal."""
        d = Duree(heures=7, minutes=30)
        assert d.decimal == 7.5

    def test_str(self):
        """Test format string."""
        d = Duree(heures=8, minutes=5)
        assert str(d) == "08:05"

    def test_add(self):
        """Test addition."""
        d1 = Duree(heures=2, minutes=30)
        d2 = Duree(heures=1, minutes=45)
        result = d1 + d2
        assert result.heures == 4
        assert result.minutes == 15

    def test_sub(self):
        """Test soustraction."""
        d1 = Duree(heures=8, minutes=0)
        d2 = Duree(heures=2, minutes=30)
        result = d1 - d2
        assert result.heures == 5
        assert result.minutes == 30

    def test_sub_negative_raises(self):
        """Test soustraction avec résultat négatif."""
        d1 = Duree(heures=1, minutes=0)
        d2 = Duree(heures=2, minutes=0)
        with pytest.raises(ValueError):
            d1 - d2

    def test_comparisons(self):
        """Test comparaisons."""
        d1 = Duree(heures=2, minutes=0)
        d2 = Duree(heures=3, minutes=0)
        d3 = Duree(heures=2, minutes=0)

        assert d1 < d2
        assert d2 > d1
        assert d1 <= d3
        assert d1 >= d3
        assert d1 == d3

    def test_frozen(self):
        """Test immutabilité (frozen)."""
        d = Duree(heures=8, minutes=0)
        with pytest.raises(Exception):  # FrozenInstanceError ou AttributeError
            d.heures = 9
