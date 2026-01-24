"""Tests unitaires pour le value object Semaine."""

import pytest
from datetime import date

from modules.planning_charge.domain.value_objects import Semaine


class TestSemaine:
    """Tests pour le value object Semaine."""

    def test_create_valid_semaine(self):
        """Test creation d'une semaine valide."""
        semaine = Semaine(annee=2026, numero=4)
        assert semaine.annee == 2026
        assert semaine.numero == 4

    def test_create_invalid_annee_low(self):
        """Test erreur si annee trop basse."""
        with pytest.raises(ValueError, match="Annee invalide"):
            Semaine(annee=2019, numero=1)

    def test_create_invalid_annee_high(self):
        """Test erreur si annee trop haute."""
        with pytest.raises(ValueError, match="Annee invalide"):
            Semaine(annee=2101, numero=1)

    def test_create_invalid_numero_low(self):
        """Test erreur si numero trop bas."""
        with pytest.raises(ValueError, match="Numero de semaine invalide"):
            Semaine(annee=2026, numero=0)

    def test_create_invalid_numero_high(self):
        """Test erreur si numero trop haut."""
        with pytest.raises(ValueError, match="Numero de semaine invalide"):
            Semaine(annee=2026, numero=54)

    def test_str_format(self):
        """Test le format string SXX - YYYY."""
        semaine = Semaine(annee=2026, numero=4)
        assert str(semaine) == "S04 - 2026"

    def test_code_format(self):
        """Test le format code SXX-YYYY."""
        semaine = Semaine(annee=2026, numero=30)
        assert semaine.code == "S30-2026"

    def test_from_date(self):
        """Test creation depuis une date."""
        # Le 27 janvier 2026 est dans la semaine 5 de 2026
        d = date(2026, 1, 27)
        semaine = Semaine.from_date(d)
        assert semaine.annee == 2026
        assert semaine.numero == 5

    def test_from_code_valid(self):
        """Test creation depuis un code valide."""
        semaine = Semaine.from_code("S04-2026")
        assert semaine.annee == 2026
        assert semaine.numero == 4

    def test_from_code_with_spaces(self):
        """Test creation depuis un code avec espaces."""
        semaine = Semaine.from_code("S04 - 2026")
        assert semaine.annee == 2026
        assert semaine.numero == 4

    def test_from_code_invalid(self):
        """Test erreur si code invalide."""
        with pytest.raises(ValueError, match="Format invalide"):
            Semaine.from_code("INVALID")

    def test_current(self):
        """Test semaine courante."""
        semaine = Semaine.current()
        today = date.today()
        assert semaine.annee >= 2024

    def test_date_range(self):
        """Test plage de dates de la semaine."""
        semaine = Semaine(annee=2026, numero=4)
        lundi, dimanche = semaine.date_range()
        assert lundi.weekday() == 0  # Lundi
        assert dimanche.weekday() == 6  # Dimanche
        assert (dimanche - lundi).days == 6

    def test_lundi_property(self):
        """Test propriete lundi."""
        semaine = Semaine(annee=2026, numero=4)
        assert semaine.lundi.weekday() == 0

    def test_dimanche_property(self):
        """Test propriete dimanche."""
        semaine = Semaine(annee=2026, numero=4)
        assert semaine.dimanche.weekday() == 6

    def test_next(self):
        """Test semaine suivante."""
        semaine = Semaine(annee=2026, numero=4)
        suivante = semaine.next()
        assert suivante.numero == 5
        assert suivante.annee == 2026

    def test_next_cross_year(self):
        """Test passage a l'annee suivante."""
        semaine = Semaine(annee=2025, numero=52)
        suivante = semaine.next()
        assert suivante.annee == 2026
        assert suivante.numero == 1

    def test_previous(self):
        """Test semaine precedente."""
        semaine = Semaine(annee=2026, numero=4)
        precedente = semaine.previous()
        assert precedente.numero == 3
        assert precedente.annee == 2026

    def test_previous_cross_year(self):
        """Test retour a l'annee precedente."""
        semaine = Semaine(annee=2026, numero=1)
        precedente = semaine.previous()
        assert precedente.annee == 2025

    def test_comparison_lt(self):
        """Test comparaison inferieur."""
        s1 = Semaine(annee=2026, numero=4)
        s2 = Semaine(annee=2026, numero=5)
        assert s1 < s2

    def test_comparison_lt_different_years(self):
        """Test comparaison inferieur annees differentes."""
        s1 = Semaine(annee=2025, numero=52)
        s2 = Semaine(annee=2026, numero=1)
        assert s1 < s2

    def test_comparison_gt(self):
        """Test comparaison superieur."""
        s1 = Semaine(annee=2026, numero=10)
        s2 = Semaine(annee=2026, numero=5)
        assert s1 > s2

    def test_comparison_eq(self):
        """Test egalite."""
        s1 = Semaine(annee=2026, numero=4)
        s2 = Semaine(annee=2026, numero=4)
        assert s1 == s2

    def test_comparison_le(self):
        """Test comparaison inferieur ou egal."""
        s1 = Semaine(annee=2026, numero=4)
        s2 = Semaine(annee=2026, numero=4)
        s3 = Semaine(annee=2026, numero=5)
        assert s1 <= s2
        assert s1 <= s3

    def test_comparison_ge(self):
        """Test comparaison superieur ou egal."""
        s1 = Semaine(annee=2026, numero=5)
        s2 = Semaine(annee=2026, numero=5)
        s3 = Semaine(annee=2026, numero=4)
        assert s1 >= s2
        assert s1 >= s3

    def test_immutable(self):
        """Test que Semaine est immutable (frozen)."""
        semaine = Semaine(annee=2026, numero=4)
        with pytest.raises(AttributeError):
            semaine.annee = 2027
