"""Tests unitaires pour l'entite BesoinCharge."""

import pytest
from datetime import datetime

from modules.planning.domain.entities import BesoinCharge
from modules.planning.domain.value_objects import Semaine, TypeMetier


class TestBesoinCharge:
    """Tests pour l'entite BesoinCharge."""

    @pytest.fixture
    def valid_besoin(self):
        """Fixture pour un besoin valide."""
        return BesoinCharge(
            chantier_id=1,
            semaine=Semaine(annee=2026, numero=4),
            type_metier=TypeMetier.MACON,
            besoin_heures=35.0,
            created_by=1,
        )

    def test_create_valid_besoin(self, valid_besoin):
        """Test creation d'un besoin valide."""
        assert valid_besoin.chantier_id == 1
        assert valid_besoin.semaine.numero == 4
        assert valid_besoin.type_metier == TypeMetier.MACON
        assert valid_besoin.besoin_heures == 35.0
        assert valid_besoin.id is None

    def test_create_with_note(self):
        """Test creation avec note."""
        besoin = BesoinCharge(
            chantier_id=1,
            semaine=Semaine(annee=2026, numero=4),
            type_metier=TypeMetier.MACON,
            besoin_heures=35.0,
            note="Besoin urgent pour dalle",
            created_by=1,
        )
        assert besoin.note == "Besoin urgent pour dalle"

    def test_create_invalid_chantier_id(self):
        """Test erreur si chantier_id <= 0."""
        with pytest.raises(ValueError, match="ID du chantier doit etre positif"):
            BesoinCharge(
                chantier_id=0,
                semaine=Semaine(annee=2026, numero=4),
                type_metier=TypeMetier.MACON,
                besoin_heures=35.0,
                created_by=1,
            )

    def test_create_invalid_created_by(self):
        """Test erreur si created_by <= 0."""
        with pytest.raises(ValueError, match="ID du createur doit etre positif"):
            BesoinCharge(
                chantier_id=1,
                semaine=Semaine(annee=2026, numero=4),
                type_metier=TypeMetier.MACON,
                besoin_heures=35.0,
                created_by=0,
            )

    def test_create_negative_heures(self):
        """Test erreur si heures negatives."""
        with pytest.raises(ValueError, match="besoin en heures doit etre >= 0"):
            BesoinCharge(
                chantier_id=1,
                semaine=Semaine(annee=2026, numero=4),
                type_metier=TypeMetier.MACON,
                besoin_heures=-10.0,
                created_by=1,
            )

    def test_besoin_jours_homme_property(self, valid_besoin):
        """Test conversion en jours/homme."""
        assert valid_besoin.besoin_jours_homme == 5.0  # 35h / 7h

    def test_besoin_jours_homme_zero(self):
        """Test J/H avec 0 heures."""
        besoin = BesoinCharge(
            chantier_id=1,
            semaine=Semaine(annee=2026, numero=4),
            type_metier=TypeMetier.MACON,
            besoin_heures=0.0,
            created_by=1,
        )
        assert besoin.besoin_jours_homme == 0.0

    def test_has_note_true(self):
        """Test has_note avec note."""
        besoin = BesoinCharge(
            chantier_id=1,
            semaine=Semaine(annee=2026, numero=4),
            type_metier=TypeMetier.MACON,
            besoin_heures=35.0,
            note="Note test",
            created_by=1,
        )
        assert besoin.has_note is True

    def test_has_note_false(self, valid_besoin):
        """Test has_note sans note."""
        assert valid_besoin.has_note is False

    def test_code_unique(self, valid_besoin):
        """Test code unique."""
        expected = "1-S04-2026-macon"
        assert valid_besoin.code_unique == expected

    def test_modifier_besoin(self, valid_besoin):
        """Test modification du besoin en heures."""
        old_updated = valid_besoin.updated_at
        valid_besoin.modifier_besoin(70.0)
        assert valid_besoin.besoin_heures == 70.0
        assert valid_besoin.updated_at >= old_updated

    def test_modifier_besoin_negative(self, valid_besoin):
        """Test erreur si modification negative."""
        with pytest.raises(ValueError):
            valid_besoin.modifier_besoin(-10.0)

    def test_ajouter_note(self, valid_besoin):
        """Test ajout de note."""
        valid_besoin.ajouter_note("Nouvelle note")
        assert valid_besoin.note == "Nouvelle note"

    def test_ajouter_note_empty(self, valid_besoin):
        """Test ajout de note vide."""
        valid_besoin.ajouter_note("  ")
        assert valid_besoin.note is None

    def test_supprimer_note(self):
        """Test suppression de note."""
        besoin = BesoinCharge(
            chantier_id=1,
            semaine=Semaine(annee=2026, numero=4),
            type_metier=TypeMetier.MACON,
            besoin_heures=35.0,
            note="A supprimer",
            created_by=1,
        )
        besoin.supprimer_note()
        assert besoin.note is None

    def test_changer_type_metier(self, valid_besoin):
        """Test changement de type metier."""
        valid_besoin.changer_type_metier(TypeMetier.COFFREUR)
        assert valid_besoin.type_metier == TypeMetier.COFFREUR

    def test_est_pour_semaine_true(self, valid_besoin):
        """Test est_pour_semaine avec la bonne semaine."""
        semaine = Semaine(annee=2026, numero=4)
        assert valid_besoin.est_pour_semaine(semaine) is True

    def test_est_pour_semaine_false(self, valid_besoin):
        """Test est_pour_semaine avec une autre semaine."""
        semaine = Semaine(annee=2026, numero=5)
        assert valid_besoin.est_pour_semaine(semaine) is False

    def test_est_pour_chantier_true(self, valid_besoin):
        """Test est_pour_chantier avec le bon chantier."""
        assert valid_besoin.est_pour_chantier(1) is True

    def test_est_pour_chantier_false(self, valid_besoin):
        """Test est_pour_chantier avec un autre chantier."""
        assert valid_besoin.est_pour_chantier(2) is False

    def test_equality_same_id(self):
        """Test egalite avec meme ID."""
        besoin1 = BesoinCharge(
            id=1,
            chantier_id=1,
            semaine=Semaine(annee=2026, numero=4),
            type_metier=TypeMetier.MACON,
            besoin_heures=35.0,
            created_by=1,
        )
        besoin2 = BesoinCharge(
            id=1,
            chantier_id=2,  # Chantier different
            semaine=Semaine(annee=2026, numero=5),  # Semaine differente
            type_metier=TypeMetier.COFFREUR,  # Type different
            besoin_heures=70.0,  # Heures differentes
            created_by=2,
        )
        assert besoin1 == besoin2

    def test_equality_different_id(self):
        """Test non-egalite avec IDs differents."""
        besoin1 = BesoinCharge(
            id=1,
            chantier_id=1,
            semaine=Semaine(annee=2026, numero=4),
            type_metier=TypeMetier.MACON,
            besoin_heures=35.0,
            created_by=1,
        )
        besoin2 = BesoinCharge(
            id=2,
            chantier_id=1,
            semaine=Semaine(annee=2026, numero=4),
            type_metier=TypeMetier.MACON,
            besoin_heures=35.0,
            created_by=1,
        )
        assert besoin1 != besoin2

    def test_equality_none_id(self):
        """Test non-egalite si un ID est None."""
        besoin1 = BesoinCharge(
            id=1,
            chantier_id=1,
            semaine=Semaine(annee=2026, numero=4),
            type_metier=TypeMetier.MACON,
            besoin_heures=35.0,
            created_by=1,
        )
        besoin2 = BesoinCharge(
            chantier_id=1,
            semaine=Semaine(annee=2026, numero=4),
            type_metier=TypeMetier.MACON,
            besoin_heures=35.0,
            created_by=1,
        )
        assert besoin1 != besoin2

    def test_hash(self, valid_besoin):
        """Test hash pour utilisation dans set/dict."""
        valid_besoin.id = 1
        besoin_set = {valid_besoin}
        assert valid_besoin in besoin_set

    def test_str(self, valid_besoin):
        """Test representation string."""
        result = str(valid_besoin)
        assert "Chantier 1" in result
        assert "S04 - 2026" in result
        assert "Macon" in result
        assert "35.0h" in result

    def test_repr(self, valid_besoin):
        """Test representation technique."""
        result = repr(valid_besoin)
        assert "BesoinCharge" in result
        assert "chantier_id=1" in result

    def test_note_normalized(self):
        """Test que la note est normalisee (strip)."""
        besoin = BesoinCharge(
            chantier_id=1,
            semaine=Semaine(annee=2026, numero=4),
            type_metier=TypeMetier.MACON,
            besoin_heures=35.0,
            note="  Note avec espaces  ",
            created_by=1,
        )
        assert besoin.note == "Note avec espaces"

    def test_timestamps_set(self, valid_besoin):
        """Test que les timestamps sont initialises."""
        assert isinstance(valid_besoin.created_at, datetime)
        assert isinstance(valid_besoin.updated_at, datetime)
