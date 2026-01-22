"""Tests unitaires pour l'entite Affectation du module Planning.

Ce fichier teste :
- Creation avec valeurs valides
- Validation des contraintes (heure_fin > heure_debut)
- Methodes metier : modifier_horaires, ajouter_note, dupliquer
- Proprietes calculees : has_horaires, duree_minutes
"""

import pytest
from datetime import date, datetime

from modules.planning.domain.entities.affectation import Affectation
from modules.planning.domain.value_objects.heure_affectation import HeureAffectation
from modules.planning.domain.value_objects.type_affectation import TypeAffectation
from modules.planning.domain.value_objects.jour_semaine import JourSemaine


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def affectation_simple():
    """Fixture: affectation simple sans horaires."""
    return Affectation(
        utilisateur_id=1,
        chantier_id=2,
        date=date(2026, 1, 22),
        created_by=3,
    )


@pytest.fixture
def affectation_avec_horaires():
    """Fixture: affectation avec horaires definis."""
    return Affectation(
        utilisateur_id=1,
        chantier_id=2,
        date=date(2026, 1, 22),
        heure_debut=HeureAffectation(8, 0),
        heure_fin=HeureAffectation(17, 0),
        created_by=3,
    )


@pytest.fixture
def affectation_recurrente():
    """Fixture: affectation recurrente."""
    return Affectation(
        utilisateur_id=1,
        chantier_id=2,
        date=date(2026, 1, 22),
        type_affectation=TypeAffectation.RECURRENTE,
        jours_recurrence=[JourSemaine.LUNDI, JourSemaine.MERCREDI],
        created_by=3,
    )


# =============================================================================
# Tests Creation
# =============================================================================

class TestAffectationCreation:
    """Tests pour la creation d'une affectation."""

    def test_should_create_affectation_with_minimal_data(self):
        """Test: creation avec donnees minimales."""
        affectation = Affectation(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            created_by=3,
        )

        assert affectation.utilisateur_id == 1
        assert affectation.chantier_id == 2
        assert affectation.date == date(2026, 1, 22)
        assert affectation.created_by == 3
        assert affectation.id is None
        assert affectation.heure_debut is None
        assert affectation.heure_fin is None
        assert affectation.note is None
        assert affectation.type_affectation == TypeAffectation.UNIQUE

    def test_should_create_affectation_with_horaires(self):
        """Test: creation avec horaires definis."""
        heure_debut = HeureAffectation(8, 0)
        heure_fin = HeureAffectation(17, 0)

        affectation = Affectation(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            created_by=3,
        )

        assert affectation.heure_debut == heure_debut
        assert affectation.heure_fin == heure_fin

    def test_should_create_affectation_with_note(self):
        """Test: creation avec note."""
        affectation = Affectation(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            note="Apporter les outils specifiques",
            created_by=3,
        )

        assert affectation.note == "Apporter les outils specifiques"

    def test_should_trim_note_on_creation(self):
        """Test: la note est trimee a la creation."""
        affectation = Affectation(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            note="  Note avec espaces  ",
            created_by=3,
        )

        assert affectation.note == "Note avec espaces"

    def test_should_nullify_empty_note(self):
        """Test: note vide devient None."""
        affectation = Affectation(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            note="   ",
            created_by=3,
        )

        assert affectation.note is None

    def test_should_create_recurrente_affectation(self):
        """Test: creation affectation recurrente."""
        affectation = Affectation(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            type_affectation=TypeAffectation.RECURRENTE,
            jours_recurrence=[JourSemaine.LUNDI, JourSemaine.MERCREDI],
            created_by=3,
        )

        assert affectation.type_affectation == TypeAffectation.RECURRENTE
        assert affectation.jours_recurrence == [JourSemaine.LUNDI, JourSemaine.MERCREDI]

    def test_should_set_created_at_and_updated_at(self):
        """Test: dates de creation/modification initialisees."""
        before = datetime.now()
        affectation = Affectation(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            created_by=3,
        )
        after = datetime.now()

        assert before <= affectation.created_at <= after
        assert before <= affectation.updated_at <= after


# =============================================================================
# Tests Validation
# =============================================================================

class TestAffectationValidation:
    """Tests pour la validation des contraintes."""

    def test_should_raise_when_utilisateur_id_zero(self):
        """Test: echec si utilisateur_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            Affectation(
                utilisateur_id=0,
                chantier_id=2,
                date=date(2026, 1, 22),
                created_by=3,
            )

        assert "ID utilisateur doit etre positif" in str(exc_info.value)

    def test_should_raise_when_utilisateur_id_negative(self):
        """Test: echec si utilisateur_id est negatif."""
        with pytest.raises(ValueError) as exc_info:
            Affectation(
                utilisateur_id=-1,
                chantier_id=2,
                date=date(2026, 1, 22),
                created_by=3,
            )

        assert "ID utilisateur doit etre positif" in str(exc_info.value)

    def test_should_raise_when_chantier_id_invalid(self):
        """Test: echec si chantier_id invalide."""
        with pytest.raises(ValueError) as exc_info:
            Affectation(
                utilisateur_id=1,
                chantier_id=0,
                date=date(2026, 1, 22),
                created_by=3,
            )

        assert "ID chantier doit etre positif" in str(exc_info.value)

    def test_should_raise_when_created_by_invalid(self):
        """Test: echec si created_by invalide."""
        with pytest.raises(ValueError) as exc_info:
            Affectation(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                created_by=0,
            )

        assert "ID du createur doit etre positif" in str(exc_info.value)

    def test_should_raise_when_heure_fin_before_heure_debut(self):
        """Test: echec si heure_fin <= heure_debut."""
        with pytest.raises(ValueError) as exc_info:
            Affectation(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                heure_debut=HeureAffectation(17, 0),
                heure_fin=HeureAffectation(8, 0),
                created_by=3,
            )

        assert "heure de fin" in str(exc_info.value).lower()
        assert "posterieure" in str(exc_info.value)

    def test_should_raise_when_heure_fin_equals_heure_debut(self):
        """Test: echec si heure_fin == heure_debut."""
        with pytest.raises(ValueError) as exc_info:
            Affectation(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                heure_debut=HeureAffectation(8, 0),
                heure_fin=HeureAffectation(8, 0),
                created_by=3,
            )

        assert "heure de fin" in str(exc_info.value).lower()

    def test_should_raise_when_recurrente_without_jours(self):
        """Test: echec si type recurrent sans jours de recurrence."""
        with pytest.raises(ValueError) as exc_info:
            Affectation(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                type_affectation=TypeAffectation.RECURRENTE,
                jours_recurrence=None,
                created_by=3,
            )

        assert "jours de recurrence" in str(exc_info.value)

    def test_should_raise_when_recurrente_with_empty_jours(self):
        """Test: echec si type recurrent avec liste de jours vide."""
        with pytest.raises(ValueError) as exc_info:
            Affectation(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                type_affectation=TypeAffectation.RECURRENTE,
                jours_recurrence=[],
                created_by=3,
            )

        assert "jours de recurrence" in str(exc_info.value)

    def test_should_ignore_jours_recurrence_for_unique(self):
        """Test: jours_recurrence ignoree pour affectation unique."""
        affectation = Affectation(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            type_affectation=TypeAffectation.UNIQUE,
            jours_recurrence=[JourSemaine.LUNDI],  # Devrait etre ignore
            created_by=3,
        )

        assert affectation.jours_recurrence is None


# =============================================================================
# Tests Proprietes calculees
# =============================================================================

class TestAffectationProperties:
    """Tests pour les proprietes calculees."""

    def test_should_have_horaires_when_both_defined(self, affectation_avec_horaires):
        """Test: has_horaires True si debut ET fin definis."""
        assert affectation_avec_horaires.has_horaires is True

    def test_should_not_have_horaires_when_none(self, affectation_simple):
        """Test: has_horaires False si pas d'horaires."""
        assert affectation_simple.has_horaires is False

    def test_should_not_have_horaires_when_only_debut(self):
        """Test: has_horaires False si seulement debut."""
        affectation = Affectation(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            heure_debut=HeureAffectation(8, 0),
            created_by=3,
        )

        assert affectation.has_horaires is False

    def test_should_calculate_duree_minutes(self, affectation_avec_horaires):
        """Test: calcul de la duree en minutes."""
        # 8h -> 17h = 9h = 540 minutes
        assert affectation_avec_horaires.duree_minutes == 540

    def test_should_return_none_duree_when_no_horaires(self, affectation_simple):
        """Test: duree_minutes None si pas d'horaires."""
        assert affectation_simple.duree_minutes is None

    def test_should_calculate_duree_heures(self, affectation_avec_horaires):
        """Test: calcul de la duree en heures."""
        # 8h -> 17h = 9h
        assert affectation_avec_horaires.duree_heures == 9.0

    def test_should_return_none_duree_heures_when_no_horaires(self, affectation_simple):
        """Test: duree_heures None si pas d'horaires."""
        assert affectation_simple.duree_heures is None

    def test_should_identify_recurrente(self, affectation_recurrente):
        """Test: is_recurrente True pour affectation recurrente."""
        assert affectation_recurrente.is_recurrente is True

    def test_should_identify_not_recurrente(self, affectation_simple):
        """Test: is_recurrente False pour affectation unique."""
        assert affectation_simple.is_recurrente is False

    def test_should_have_note_when_defined(self):
        """Test: has_note True si note definie."""
        affectation = Affectation(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            note="Une note",
            created_by=3,
        )

        assert affectation.has_note is True

    def test_should_not_have_note_when_none(self, affectation_simple):
        """Test: has_note False si pas de note."""
        assert affectation_simple.has_note is False

    def test_should_format_horaires_str(self, affectation_avec_horaires):
        """Test: formatage des horaires en string."""
        assert affectation_avec_horaires.horaires_str() == "08:00 - 17:00"

    def test_should_return_none_horaires_str_when_no_horaires(self, affectation_simple):
        """Test: horaires_str() retourne None si pas d'horaires."""
        assert affectation_simple.horaires_str() is None


# =============================================================================
# Tests Methodes metier
# =============================================================================

class TestAffectationModifierHoraires:
    """Tests pour la methode modifier_horaires."""

    def test_should_modify_horaires(self, affectation_simple):
        """Test: modification des horaires."""
        new_debut = HeureAffectation(9, 0)
        new_fin = HeureAffectation(18, 0)

        affectation_simple.modifier_horaires(new_debut, new_fin)

        assert affectation_simple.heure_debut == new_debut
        assert affectation_simple.heure_fin == new_fin

    def test_should_update_timestamp_when_modifying_horaires(self, affectation_simple):
        """Test: updated_at mis a jour lors de la modification."""
        before = affectation_simple.updated_at
        affectation_simple.modifier_horaires(
            HeureAffectation(9, 0),
            HeureAffectation(18, 0),
        )

        assert affectation_simple.updated_at >= before

    def test_should_clear_horaires(self, affectation_avec_horaires):
        """Test: suppression des horaires (mise a None)."""
        affectation_avec_horaires.modifier_horaires(None, None)

        assert affectation_avec_horaires.heure_debut is None
        assert affectation_avec_horaires.heure_fin is None

    def test_should_raise_when_invalid_horaires_on_modify(self, affectation_simple):
        """Test: echec si heure_fin <= heure_debut lors de la modification."""
        with pytest.raises(ValueError) as exc_info:
            affectation_simple.modifier_horaires(
                HeureAffectation(17, 0),
                HeureAffectation(8, 0),
            )

        assert "heure de fin" in str(exc_info.value).lower()


class TestAffectationNotes:
    """Tests pour les methodes de gestion des notes."""

    def test_should_add_note(self, affectation_simple):
        """Test: ajout d'une note."""
        affectation_simple.ajouter_note("Nouvelle note")

        assert affectation_simple.note == "Nouvelle note"

    def test_should_update_timestamp_when_adding_note(self, affectation_simple):
        """Test: updated_at mis a jour lors de l'ajout de note."""
        before = affectation_simple.updated_at
        affectation_simple.ajouter_note("Note")

        assert affectation_simple.updated_at >= before

    def test_should_trim_note(self, affectation_simple):
        """Test: note trimee a l'ajout."""
        affectation_simple.ajouter_note("  Note avec espaces  ")

        assert affectation_simple.note == "Note avec espaces"

    def test_should_nullify_empty_note_on_add(self, affectation_simple):
        """Test: note vide devient None."""
        affectation_simple.ajouter_note("   ")

        assert affectation_simple.note is None

    def test_should_delete_note(self):
        """Test: suppression d'une note."""
        affectation = Affectation(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            note="Note existante",
            created_by=3,
        )

        affectation.supprimer_note()

        assert affectation.note is None


class TestAffectationDupliquer:
    """Tests pour la methode dupliquer."""

    def test_should_duplicate_to_new_date(self, affectation_avec_horaires):
        """Test: duplication vers une nouvelle date."""
        nouvelle_date = date(2026, 1, 23)

        copie = affectation_avec_horaires.dupliquer(nouvelle_date)

        assert copie.id is None  # Nouvel ID
        assert copie.date == nouvelle_date
        assert copie.utilisateur_id == affectation_avec_horaires.utilisateur_id
        assert copie.chantier_id == affectation_avec_horaires.chantier_id

    def test_should_copy_horaires_on_duplicate(self, affectation_avec_horaires):
        """Test: horaires copies lors de la duplication."""
        copie = affectation_avec_horaires.dupliquer(date(2026, 1, 23))

        assert copie.heure_debut == affectation_avec_horaires.heure_debut
        assert copie.heure_fin == affectation_avec_horaires.heure_fin

    def test_should_copy_note_on_duplicate(self):
        """Test: note copiee lors de la duplication."""
        affectation = Affectation(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            note="Note importante",
            created_by=3,
        )

        copie = affectation.dupliquer(date(2026, 1, 23))

        assert copie.note == "Note importante"

    def test_should_set_type_unique_on_duplicate(self, affectation_recurrente):
        """Test: type devient UNIQUE apres duplication."""
        copie = affectation_recurrente.dupliquer(date(2026, 1, 23))

        assert copie.type_affectation == TypeAffectation.UNIQUE
        assert copie.jours_recurrence is None


class TestAffectationConversion:
    """Tests pour les methodes de conversion de type."""

    def test_should_convert_to_unique(self, affectation_recurrente):
        """Test: conversion en type unique."""
        affectation_recurrente.convertir_en_unique()

        assert affectation_recurrente.type_affectation == TypeAffectation.UNIQUE
        assert affectation_recurrente.jours_recurrence is None

    def test_should_convert_to_recurrente(self, affectation_simple):
        """Test: conversion en type recurrent."""
        jours = [JourSemaine.LUNDI, JourSemaine.MERCREDI, JourSemaine.VENDREDI]

        affectation_simple.convertir_en_recurrente(jours)

        assert affectation_simple.type_affectation == TypeAffectation.RECURRENTE
        assert affectation_simple.jours_recurrence == jours

    def test_should_raise_when_convert_recurrente_empty_jours(self, affectation_simple):
        """Test: echec si conversion recurrente avec liste vide."""
        with pytest.raises(ValueError) as exc_info:
            affectation_simple.convertir_en_recurrente([])

        assert "ne peut pas etre vide" in str(exc_info.value)


class TestAffectationChangements:
    """Tests pour les methodes de changement."""

    def test_should_change_chantier(self, affectation_simple):
        """Test: changement de chantier."""
        affectation_simple.changer_chantier(99)

        assert affectation_simple.chantier_id == 99

    def test_should_raise_when_change_chantier_invalid(self, affectation_simple):
        """Test: echec si nouveau chantier_id invalide."""
        with pytest.raises(ValueError):
            affectation_simple.changer_chantier(0)

    def test_should_change_utilisateur(self, affectation_simple):
        """Test: changement d'utilisateur."""
        affectation_simple.changer_utilisateur(99)

        assert affectation_simple.utilisateur_id == 99

    def test_should_raise_when_change_utilisateur_invalid(self, affectation_simple):
        """Test: echec si nouvel utilisateur_id invalide."""
        with pytest.raises(ValueError):
            affectation_simple.changer_utilisateur(0)

    def test_should_change_date(self, affectation_simple):
        """Test: changement de date."""
        nouvelle_date = date(2026, 2, 15)
        affectation_simple.changer_date(nouvelle_date)

        assert affectation_simple.date == nouvelle_date


class TestAffectationJours:
    """Tests pour la methode est_pour_jour."""

    def test_should_return_true_for_unique_affectation(self, affectation_simple):
        """Test: affectation unique s'applique toujours."""
        assert affectation_simple.est_pour_jour(JourSemaine.LUNDI) is True
        assert affectation_simple.est_pour_jour(JourSemaine.SAMEDI) is True

    def test_should_return_true_when_jour_in_recurrence(self, affectation_recurrente):
        """Test: True si jour dans les jours de recurrence."""
        # jours_recurrence = [LUNDI, MERCREDI]
        assert affectation_recurrente.est_pour_jour(JourSemaine.LUNDI) is True
        assert affectation_recurrente.est_pour_jour(JourSemaine.MERCREDI) is True

    def test_should_return_false_when_jour_not_in_recurrence(self, affectation_recurrente):
        """Test: False si jour pas dans les jours de recurrence."""
        # jours_recurrence = [LUNDI, MERCREDI]
        assert affectation_recurrente.est_pour_jour(JourSemaine.MARDI) is False
        assert affectation_recurrente.est_pour_jour(JourSemaine.VENDREDI) is False


# =============================================================================
# Tests Egalite et Hash
# =============================================================================

class TestAffectationEquality:
    """Tests pour l'egalite et le hash."""

    def test_should_be_equal_when_same_id(self):
        """Test: egalite basee sur l'ID."""
        aff1 = Affectation(
            id=1,
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            created_by=3,
        )
        aff2 = Affectation(
            id=1,
            utilisateur_id=99,  # Differents attributs
            chantier_id=99,
            date=date(2026, 12, 31),
            created_by=99,
        )

        assert aff1 == aff2

    def test_should_not_be_equal_when_different_id(self):
        """Test: pas d'egalite si IDs differents."""
        aff1 = Affectation(
            id=1,
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            created_by=3,
        )
        aff2 = Affectation(
            id=2,
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            created_by=3,
        )

        assert aff1 != aff2

    def test_should_not_be_equal_when_id_is_none(self, affectation_simple):
        """Test: pas d'egalite si un des IDs est None."""
        aff2 = Affectation(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            created_by=3,
        )

        assert affectation_simple != aff2

    def test_should_have_same_hash_when_same_id(self):
        """Test: meme hash si meme ID."""
        aff1 = Affectation(
            id=1,
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            created_by=3,
        )
        aff2 = Affectation(
            id=1,
            utilisateur_id=99,
            chantier_id=99,
            date=date(2026, 12, 31),
            created_by=99,
        )

        assert hash(aff1) == hash(aff2)


# =============================================================================
# Tests Representation
# =============================================================================

class TestAffectationRepresentation:
    """Tests pour les methodes de representation."""

    def test_should_format_str_for_unique(self, affectation_simple):
        """Test: __str__ pour affectation unique."""
        result = str(affectation_simple)

        assert "unique" in result
        assert "User 1" in result
        assert "Chantier 2" in result

    def test_should_format_str_with_horaires(self, affectation_avec_horaires):
        """Test: __str__ inclut les horaires."""
        result = str(affectation_avec_horaires)

        assert "08:00" in result
        assert "17:00" in result

    def test_should_format_repr(self, affectation_simple):
        """Test: __repr__ inclut les details techniques."""
        result = repr(affectation_simple)

        assert "Affectation(" in result
        assert "utilisateur_id=1" in result
        assert "chantier_id=2" in result
