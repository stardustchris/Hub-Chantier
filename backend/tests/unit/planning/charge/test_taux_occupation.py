"""Tests unitaires pour le value object TauxOccupation."""

import pytest

from modules.planning.domain.value_objects import TauxOccupation, NiveauOccupation


class TestNiveauOccupation:
    """Tests pour l'enum NiveauOccupation."""

    def test_all_niveaux_have_couleur(self):
        """Test que chaque niveau a une couleur."""
        for niveau in NiveauOccupation:
            assert niveau.couleur.startswith("#")

    def test_all_niveaux_have_label(self):
        """Test que chaque niveau a un label."""
        for niveau in NiveauOccupation:
            assert len(niveau.label) > 0

    def test_alerte_for_surcharge_and_critique(self):
        """Test que seuls surcharge et critique declenchent une alerte."""
        assert not NiveauOccupation.SOUS_CHARGE.alerte
        assert not NiveauOccupation.NORMAL.alerte
        assert not NiveauOccupation.HAUTE.alerte
        assert NiveauOccupation.SURCHARGE.alerte
        assert NiveauOccupation.CRITIQUE.alerte


class TestTauxOccupation:
    """Tests pour le value object TauxOccupation."""

    def test_create_valid_taux(self):
        """Test creation d'un taux valide."""
        taux = TauxOccupation(valeur=50.0)
        assert taux.valeur == 50.0

    def test_create_zero_taux(self):
        """Test creation d'un taux nul."""
        taux = TauxOccupation(valeur=0.0)
        assert taux.valeur == 0.0

    def test_create_negative_taux_raises(self):
        """Test erreur si taux negatif."""
        with pytest.raises(ValueError, match="taux doit etre >= 0"):
            TauxOccupation(valeur=-10.0)

    def test_str_format(self):
        """Test format string."""
        taux = TauxOccupation(valeur=85.5)
        assert str(taux) == "85.5%"

    def test_niveau_sous_charge(self):
        """Test niveau sous-charge (< 70%)."""
        taux = TauxOccupation(valeur=50.0)
        assert taux.niveau == NiveauOccupation.SOUS_CHARGE

    def test_niveau_normal(self):
        """Test niveau normal (70-90%)."""
        taux = TauxOccupation(valeur=80.0)
        assert taux.niveau == NiveauOccupation.NORMAL

    def test_niveau_haute(self):
        """Test niveau haute (90-100%)."""
        taux = TauxOccupation(valeur=95.0)
        assert taux.niveau == NiveauOccupation.HAUTE

    def test_niveau_surcharge(self):
        """Test niveau surcharge (== 100%)."""
        taux = TauxOccupation(valeur=100.0)
        assert taux.niveau == NiveauOccupation.SURCHARGE

    def test_niveau_critique(self):
        """Test niveau critique (> 100%)."""
        taux = TauxOccupation(valeur=120.0)
        assert taux.niveau == NiveauOccupation.CRITIQUE

    def test_couleur_property(self):
        """Test couleur selon niveau."""
        taux_bas = TauxOccupation(valeur=50.0)
        taux_haut = TauxOccupation(valeur=105.0)
        assert taux_bas.couleur == "#27AE60"  # Vert
        assert taux_haut.couleur == "#C0392B"  # Rouge fonce

    def test_alerte_property(self):
        """Test alerte pour surcharge."""
        taux_ok = TauxOccupation(valeur=85.0)
        taux_surcharge = TauxOccupation(valeur=100.0)
        assert not taux_ok.alerte
        assert taux_surcharge.alerte

    def test_calculer_normal(self):
        """Test calcul de taux normal."""
        taux = TauxOccupation.calculer(planifie=35.0, capacite=70.0)
        assert taux.valeur == 50.0

    def test_calculer_zero_capacite_with_planifie(self):
        """Test calcul avec capacite nulle et planifie > 0."""
        taux = TauxOccupation.calculer(planifie=10.0, capacite=0.0)
        assert taux.valeur == 200.0  # Critique

    def test_calculer_zero_both(self):
        """Test calcul avec les deux a zero."""
        taux = TauxOccupation.calculer(planifie=0.0, capacite=0.0)
        assert taux.valeur == 0.0

    def test_zero_class_method(self):
        """Test methode zero()."""
        taux = TauxOccupation.zero()
        assert taux.valeur == 0.0

    def test_label_property(self):
        """Test label du niveau."""
        taux = TauxOccupation(valeur=80.0)
        assert taux.label == "Normal"

    def test_seuils_cdc(self):
        """Test des seuils selon CDC Section 6.4."""
        # < 70% = Sous-charge
        assert TauxOccupation(valeur=69.9).niveau == NiveauOccupation.SOUS_CHARGE
        # 70% = Normal
        assert TauxOccupation(valeur=70.0).niveau == NiveauOccupation.NORMAL
        # 89.9% = Normal
        assert TauxOccupation(valeur=89.9).niveau == NiveauOccupation.NORMAL
        # 90% = Haute
        assert TauxOccupation(valeur=90.0).niveau == NiveauOccupation.HAUTE
        # 99.9% = Haute
        assert TauxOccupation(valeur=99.9).niveau == NiveauOccupation.HAUTE
        # 100% = Surcharge
        assert TauxOccupation(valeur=100.0).niveau == NiveauOccupation.SURCHARGE
        # 100.1% = Critique
        assert TauxOccupation(valeur=100.1).niveau == NiveauOccupation.CRITIQUE
