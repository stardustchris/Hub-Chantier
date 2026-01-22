"""Tests unitaires pour les Value Objects du module Planning.

Ce fichier teste :
- HeureAffectation : heure au format HH:MM
- TypeAffectation : enum unique/recurrente
- JourSemaine : jours de la semaine pour recurrence
"""

import pytest

from modules.planning.domain.value_objects.heure_affectation import HeureAffectation
from modules.planning.domain.value_objects.type_affectation import TypeAffectation
from modules.planning.domain.value_objects.jour_semaine import JourSemaine


# =============================================================================
# Tests HeureAffectation
# =============================================================================

class TestHeureAffectation:
    """Tests pour le Value Object HeureAffectation."""

    # --- Creation valide ---

    def test_should_create_heure_when_valid_values(self):
        """Test: creation reussie avec heure et minute valides."""
        heure = HeureAffectation(heure=8, minute=30)

        assert heure.heure == 8
        assert heure.minute == 30

    def test_should_create_heure_when_midnight(self):
        """Test: creation reussie pour minuit (00:00)."""
        heure = HeureAffectation(heure=0, minute=0)

        assert heure.heure == 0
        assert heure.minute == 0

    def test_should_create_heure_when_end_of_day(self):
        """Test: creation reussie pour 23:59."""
        heure = HeureAffectation(heure=23, minute=59)

        assert heure.heure == 23
        assert heure.minute == 59

    # --- Creation invalide ---

    def test_should_raise_when_heure_negative(self):
        """Test: echec si heure negative."""
        with pytest.raises(ValueError) as exc_info:
            HeureAffectation(heure=-1, minute=0)

        assert "heure doit etre comprise entre 0 et 23" in str(exc_info.value)

    def test_should_raise_when_heure_too_large(self):
        """Test: echec si heure > 23."""
        with pytest.raises(ValueError) as exc_info:
            HeureAffectation(heure=24, minute=0)

        assert "heure doit etre comprise entre 0 et 23" in str(exc_info.value)

    def test_should_raise_when_minute_negative(self):
        """Test: echec si minute negative."""
        with pytest.raises(ValueError) as exc_info:
            HeureAffectation(heure=8, minute=-1)

        assert "minute doit etre comprise entre 0 et 59" in str(exc_info.value)

    def test_should_raise_when_minute_too_large(self):
        """Test: echec si minute > 59."""
        with pytest.raises(ValueError) as exc_info:
            HeureAffectation(heure=8, minute=60)

        assert "minute doit etre comprise entre 0 et 59" in str(exc_info.value)

    def test_should_raise_when_heure_not_integer(self):
        """Test: echec si heure n'est pas un entier."""
        with pytest.raises(ValueError) as exc_info:
            HeureAffectation(heure="8", minute=0)

        assert "doivent etre des entiers" in str(exc_info.value)

    def test_should_raise_when_minute_not_integer(self):
        """Test: echec si minute n'est pas un entier."""
        with pytest.raises(ValueError) as exc_info:
            HeureAffectation(heure=8, minute="30")

        assert "doivent etre des entiers" in str(exc_info.value)

    # --- Methode __str__ / to_string ---

    def test_should_format_to_string_with_padding(self):
        """Test: formatage avec zero padding pour heures/minutes < 10."""
        heure = HeureAffectation(heure=8, minute=5)

        assert str(heure) == "08:05"
        assert heure.to_string() == "08:05"

    def test_should_format_to_string_without_padding(self):
        """Test: formatage pour heures/minutes >= 10."""
        heure = HeureAffectation(heure=14, minute=30)

        assert str(heure) == "14:30"

    # --- Methode from_string ---

    def test_should_create_from_string_valid_format(self):
        """Test: creation depuis string au format HH:MM."""
        heure = HeureAffectation.from_string("08:30")

        assert heure.heure == 8
        assert heure.minute == 30

    def test_should_create_from_string_single_digit_hour(self):
        """Test: creation depuis string avec heure a un chiffre."""
        heure = HeureAffectation.from_string("8:30")

        assert heure.heure == 8
        assert heure.minute == 30

    def test_should_create_from_string_with_spaces(self):
        """Test: creation depuis string avec espaces autour."""
        heure = HeureAffectation.from_string("  08:30  ")

        assert heure.heure == 8
        assert heure.minute == 30

    def test_should_raise_when_from_string_empty(self):
        """Test: echec depuis string vide."""
        with pytest.raises(ValueError) as exc_info:
            HeureAffectation.from_string("")

        assert "chaine non vide" in str(exc_info.value)

    def test_should_raise_when_from_string_invalid_format(self):
        """Test: echec depuis string sans separateur."""
        with pytest.raises(ValueError) as exc_info:
            HeureAffectation.from_string("0830")

        assert "Format invalide" in str(exc_info.value)

    def test_should_raise_when_from_string_non_numeric(self):
        """Test: echec depuis string avec caracteres non numeriques."""
        with pytest.raises(ValueError) as exc_info:
            HeureAffectation.from_string("ab:cd")

        assert "doivent etre des nombres" in str(exc_info.value)

    def test_should_raise_when_from_string_invalid_hour(self):
        """Test: echec depuis string avec heure invalide."""
        with pytest.raises(ValueError) as exc_info:
            HeureAffectation.from_string("25:00")

        assert "heure doit etre comprise" in str(exc_info.value)

    # --- Comparaison ---

    def test_should_compare_less_than(self):
        """Test: comparaison inferieur."""
        h1 = HeureAffectation(8, 0)
        h2 = HeureAffectation(9, 0)

        assert h1 < h2
        assert not h2 < h1

    def test_should_compare_less_than_same_hour(self):
        """Test: comparaison inferieur meme heure."""
        h1 = HeureAffectation(8, 0)
        h2 = HeureAffectation(8, 30)

        assert h1 < h2

    def test_should_compare_less_than_or_equal(self):
        """Test: comparaison inferieur ou egal."""
        h1 = HeureAffectation(8, 0)
        h2 = HeureAffectation(8, 0)

        assert h1 <= h2
        assert h2 <= h1

    def test_should_compare_greater_than(self):
        """Test: comparaison superieur."""
        h1 = HeureAffectation(17, 0)
        h2 = HeureAffectation(8, 0)

        assert h1 > h2

    def test_should_compare_greater_than_or_equal(self):
        """Test: comparaison superieur ou egal."""
        h1 = HeureAffectation(17, 0)
        h2 = HeureAffectation(17, 0)

        assert h1 >= h2

    def test_should_compare_equal(self):
        """Test: egalite de deux heures identiques."""
        h1 = HeureAffectation(8, 30)
        h2 = HeureAffectation(8, 30)

        assert h1 == h2

    def test_should_compare_not_equal(self):
        """Test: inegalite de deux heures differentes."""
        h1 = HeureAffectation(8, 30)
        h2 = HeureAffectation(8, 31)

        assert h1 != h2

    # --- Conversion en minutes ---

    def test_should_convert_to_minutes(self):
        """Test: conversion en minutes depuis minuit."""
        heure = HeureAffectation(8, 30)

        assert heure.to_minutes() == 510  # 8*60 + 30

    def test_should_convert_midnight_to_zero_minutes(self):
        """Test: minuit = 0 minutes."""
        heure = HeureAffectation(0, 0)

        assert heure.to_minutes() == 0

    # --- Calcul de duree ---

    def test_should_calculate_duration_to_other_heure(self):
        """Test: calcul de duree vers une autre heure."""
        debut = HeureAffectation(8, 0)
        fin = HeureAffectation(17, 0)

        assert debut.duree_vers(fin) == 540  # 9h * 60

    def test_should_calculate_negative_duration_when_reversed(self):
        """Test: duree negative si fin < debut."""
        debut = HeureAffectation(17, 0)
        fin = HeureAffectation(8, 0)

        assert debut.duree_vers(fin) == -540

    # --- Factory methods ---

    def test_should_create_debut_journee(self):
        """Test: creation heure de debut de journee standard."""
        heure = HeureAffectation.debut_journee()

        assert heure.heure == 8
        assert heure.minute == 0

    def test_should_create_fin_journee(self):
        """Test: creation heure de fin de journee standard."""
        heure = HeureAffectation.fin_journee()

        assert heure.heure == 17
        assert heure.minute == 0

    def test_should_create_midi(self):
        """Test: creation heure de midi."""
        heure = HeureAffectation.midi()

        assert heure.heure == 12
        assert heure.minute == 0

    # --- Immutabilite ---

    def test_should_be_immutable(self):
        """Test: HeureAffectation est immutable (frozen dataclass)."""
        heure = HeureAffectation(8, 30)

        with pytest.raises(AttributeError):
            heure.heure = 9


# =============================================================================
# Tests TypeAffectation
# =============================================================================

class TestTypeAffectation:
    """Tests pour l'enum TypeAffectation."""

    def test_should_have_unique_value(self):
        """Test: valeur UNIQUE."""
        assert TypeAffectation.UNIQUE.value == "unique"

    def test_should_have_recurrente_value(self):
        """Test: valeur RECURRENTE."""
        assert TypeAffectation.RECURRENTE.value == "recurrente"

    def test_should_convert_to_string(self):
        """Test: conversion en string."""
        assert str(TypeAffectation.UNIQUE) == "unique"
        assert str(TypeAffectation.RECURRENTE) == "recurrente"

    def test_should_check_is_recurrente(self):
        """Test: methode is_recurrente()."""
        assert TypeAffectation.RECURRENTE.is_recurrente() is True
        assert TypeAffectation.UNIQUE.is_recurrente() is False

    def test_should_check_is_unique(self):
        """Test: methode is_unique()."""
        assert TypeAffectation.UNIQUE.is_unique() is True
        assert TypeAffectation.RECURRENTE.is_unique() is False

    def test_should_create_from_string_lowercase(self):
        """Test: creation depuis string minuscule."""
        assert TypeAffectation.from_string("unique") == TypeAffectation.UNIQUE
        assert TypeAffectation.from_string("recurrente") == TypeAffectation.RECURRENTE

    def test_should_create_from_string_uppercase(self):
        """Test: creation depuis string majuscule."""
        assert TypeAffectation.from_string("UNIQUE") == TypeAffectation.UNIQUE
        assert TypeAffectation.from_string("RECURRENTE") == TypeAffectation.RECURRENTE

    def test_should_create_from_string_with_spaces(self):
        """Test: creation depuis string avec espaces."""
        assert TypeAffectation.from_string("  unique  ") == TypeAffectation.UNIQUE

    def test_should_raise_when_from_string_invalid(self):
        """Test: echec depuis string invalide."""
        with pytest.raises(ValueError) as exc_info:
            TypeAffectation.from_string("invalide")

        assert "Type d'affectation invalide" in str(exc_info.value)

    def test_should_return_default(self):
        """Test: type par defaut est UNIQUE."""
        assert TypeAffectation.default() == TypeAffectation.UNIQUE


# =============================================================================
# Tests JourSemaine
# =============================================================================

class TestJourSemaine:
    """Tests pour l'enum JourSemaine."""

    # --- Valeurs ---

    def test_should_have_correct_values(self):
        """Test: valeurs des jours de la semaine (0-6)."""
        assert JourSemaine.LUNDI.value == 0
        assert JourSemaine.MARDI.value == 1
        assert JourSemaine.MERCREDI.value == 2
        assert JourSemaine.JEUDI.value == 3
        assert JourSemaine.VENDREDI.value == 4
        assert JourSemaine.SAMEDI.value == 5
        assert JourSemaine.DIMANCHE.value == 6

    # --- Noms ---

    def test_should_return_nom_francais(self):
        """Test: noms des jours en francais."""
        assert JourSemaine.LUNDI.nom_francais() == "Lundi"
        assert JourSemaine.MARDI.nom_francais() == "Mardi"
        assert JourSemaine.MERCREDI.nom_francais() == "Mercredi"
        assert JourSemaine.JEUDI.nom_francais() == "Jeudi"
        assert JourSemaine.VENDREDI.nom_francais() == "Vendredi"
        assert JourSemaine.SAMEDI.nom_francais() == "Samedi"
        assert JourSemaine.DIMANCHE.nom_francais() == "Dimanche"

    def test_should_return_nom_court(self):
        """Test: abreviations des jours."""
        assert JourSemaine.LUNDI.nom_court() == "Lun"
        assert JourSemaine.MARDI.nom_court() == "Mar"
        assert JourSemaine.MERCREDI.nom_court() == "Mer"
        assert JourSemaine.JEUDI.nom_court() == "Jeu"
        assert JourSemaine.VENDREDI.nom_court() == "Ven"
        assert JourSemaine.SAMEDI.nom_court() == "Sam"
        assert JourSemaine.DIMANCHE.nom_court() == "Dim"

    def test_should_convert_to_string_as_nom_francais(self):
        """Test: __str__ retourne le nom en francais."""
        assert str(JourSemaine.LUNDI) == "Lundi"

    # --- Weekend / Semaine ---

    def test_should_identify_weekend_days(self):
        """Test: identification des jours de weekend."""
        assert JourSemaine.SAMEDI.is_weekend() is True
        assert JourSemaine.DIMANCHE.is_weekend() is True

    def test_should_identify_weekdays(self):
        """Test: identification des jours de semaine."""
        assert JourSemaine.LUNDI.is_weekend() is False
        assert JourSemaine.MARDI.is_weekend() is False
        assert JourSemaine.MERCREDI.is_weekend() is False
        assert JourSemaine.JEUDI.is_weekend() is False
        assert JourSemaine.VENDREDI.is_weekend() is False

    def test_should_identify_semaine_days(self):
        """Test: is_semaine() est l'inverse de is_weekend()."""
        assert JourSemaine.LUNDI.is_semaine() is True
        assert JourSemaine.SAMEDI.is_semaine() is False

    # --- Creation depuis int ---

    def test_should_create_from_int(self):
        """Test: creation depuis entier (0-6)."""
        assert JourSemaine.from_int(0) == JourSemaine.LUNDI
        assert JourSemaine.from_int(4) == JourSemaine.VENDREDI
        assert JourSemaine.from_int(6) == JourSemaine.DIMANCHE

    def test_should_raise_when_from_int_negative(self):
        """Test: echec depuis entier negatif."""
        with pytest.raises(ValueError) as exc_info:
            JourSemaine.from_int(-1)

        assert "Jour invalide" in str(exc_info.value)

    def test_should_raise_when_from_int_too_large(self):
        """Test: echec depuis entier > 6."""
        with pytest.raises(ValueError) as exc_info:
            JourSemaine.from_int(7)

        assert "Jour invalide" in str(exc_info.value)

    # --- Creation depuis string ---

    def test_should_create_from_string_full_name(self):
        """Test: creation depuis nom complet."""
        assert JourSemaine.from_string("lundi") == JourSemaine.LUNDI
        assert JourSemaine.from_string("vendredi") == JourSemaine.VENDREDI

    def test_should_create_from_string_short_name(self):
        """Test: creation depuis abreviation."""
        assert JourSemaine.from_string("lun") == JourSemaine.LUNDI
        assert JourSemaine.from_string("ven") == JourSemaine.VENDREDI

    def test_should_create_from_string_case_insensitive(self):
        """Test: creation insensible a la casse."""
        assert JourSemaine.from_string("LUNDI") == JourSemaine.LUNDI
        assert JourSemaine.from_string("Lundi") == JourSemaine.LUNDI

    def test_should_raise_when_from_string_invalid(self):
        """Test: echec depuis string invalide."""
        with pytest.raises(ValueError) as exc_info:
            JourSemaine.from_string("invalid")

        assert "Jour invalide" in str(exc_info.value)

    # --- Listes de jours ---

    def test_should_return_jours_semaine(self):
        """Test: liste des jours ouvrables (lundi-vendredi)."""
        jours = JourSemaine.jours_semaine()

        assert len(jours) == 5
        assert JourSemaine.LUNDI in jours
        assert JourSemaine.VENDREDI in jours
        assert JourSemaine.SAMEDI not in jours
        assert JourSemaine.DIMANCHE not in jours

    def test_should_return_weekend(self):
        """Test: liste des jours de weekend."""
        jours = JourSemaine.weekend()

        assert len(jours) == 2
        assert JourSemaine.SAMEDI in jours
        assert JourSemaine.DIMANCHE in jours

    def test_should_return_tous(self):
        """Test: liste de tous les jours."""
        jours = JourSemaine.tous()

        assert len(jours) == 7
        assert JourSemaine.LUNDI in jours
        assert JourSemaine.DIMANCHE in jours
