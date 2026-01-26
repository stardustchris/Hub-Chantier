"""Tests unitaires pour ContactChantier value object."""

import pytest
from dataclasses import FrozenInstanceError

from modules.chantiers.domain.value_objects.contact_chantier import ContactChantier


class TestContactChantier:
    """Tests pour ContactChantier."""

    def test_create_with_nom_only(self):
        """Test création avec nom uniquement."""
        contact = ContactChantier(nom="Jean Dupont")

        assert contact.nom == "Jean Dupont"
        assert contact.profession is None
        assert contact.telephone is None

    def test_create_with_all_fields(self):
        """Test création avec tous les champs."""
        contact = ContactChantier(
            nom="Marie Martin",
            profession="Chef de chantier",
            telephone="0612345678",
        )

        assert contact.nom == "Marie Martin"
        assert contact.profession == "Chef de chantier"
        assert contact.telephone == "0612345678"

    def test_nom_normalization(self):
        """Test normalisation du nom (title case)."""
        contact = ContactChantier(nom="jean dupont")

        assert contact.nom == "Jean Dupont"

    def test_nom_strip(self):
        """Test suppression des espaces autour du nom."""
        contact = ContactChantier(nom="  Jean Dupont  ")

        assert contact.nom == "Jean Dupont"

    def test_empty_nom_raises(self):
        """Test erreur si nom vide."""
        with pytest.raises(ValueError, match="Le nom du contact ne peut pas être vide"):
            ContactChantier(nom="")

    def test_whitespace_nom_raises(self):
        """Test erreur si nom uniquement espaces."""
        with pytest.raises(ValueError, match="Le nom du contact ne peut pas être vide"):
            ContactChantier(nom="   ")

    def test_profession_normalization(self):
        """Test normalisation de la profession."""
        contact = ContactChantier(nom="Test", profession="  Conducteur  ")

        assert contact.profession == "Conducteur"

    def test_empty_profession_becomes_none(self):
        """Test profession vide devient None."""
        contact = ContactChantier(nom="Test", profession="   ")

        assert contact.profession is None

    def test_telephone_cleaning(self):
        """Test nettoyage du numéro de téléphone."""
        contact = ContactChantier(nom="Test", telephone="06 12 34 56 78")

        assert contact.telephone == "0612345678"

    def test_telephone_with_dots(self):
        """Test téléphone avec des points."""
        contact = ContactChantier(nom="Test", telephone="06.12.34.56.78")

        assert contact.telephone == "0612345678"

    def test_telephone_international_preserved(self):
        """Test téléphone international préservé."""
        contact = ContactChantier(nom="Test", telephone="+33612345678")

        assert contact.telephone == "+33612345678"

    def test_empty_telephone_becomes_none(self):
        """Test téléphone vide devient None."""
        contact = ContactChantier(nom="Test", telephone="   ")

        assert contact.telephone is None

    def test_frozen_immutability(self):
        """Test que ContactChantier est immutable."""
        contact = ContactChantier(nom="Test")

        with pytest.raises(FrozenInstanceError):
            contact.nom = "Autre"

    def test_str_with_nom_only(self):
        """Test __str__ avec nom uniquement."""
        contact = ContactChantier(nom="Jean Dupont")

        assert str(contact) == "Jean Dupont"

    def test_str_with_profession(self):
        """Test __str__ avec profession."""
        contact = ContactChantier(nom="Jean Dupont", profession="Conducteur")

        assert str(contact) == "Jean Dupont (Conducteur)"

    def test_str_with_all_fields(self):
        """Test __str__ avec tous les champs."""
        contact = ContactChantier(
            nom="Jean Dupont",
            profession="Conducteur",
            telephone="0612345678",
        )

        result = str(contact)
        assert "Jean Dupont" in result
        assert "(Conducteur)" in result
        assert "06 12 34 56 78" in result

    def test_formatted_phone_french(self):
        """Test formatage téléphone français."""
        contact = ContactChantier(nom="Test", telephone="0612345678")

        assert contact.formatted_phone == "06 12 34 56 78"

    def test_formatted_phone_international_french(self):
        """Test formatage téléphone international français."""
        contact = ContactChantier(nom="Test", telephone="+33612345678")

        assert contact.formatted_phone == "+33 6 12 34 56 78"

    def test_formatted_phone_other_international(self):
        """Test formatage téléphone international autre."""
        contact = ContactChantier(nom="Test", telephone="+14155551234")

        assert contact.formatted_phone == "+14155551234"

    def test_formatted_phone_none(self):
        """Test formatted_phone sans téléphone."""
        contact = ContactChantier(nom="Test")

        assert contact.formatted_phone is None

    def test_callable_phone(self):
        """Test URL tel: pour click-to-call."""
        contact = ContactChantier(nom="Test", telephone="0612345678")

        assert contact.callable_phone == "tel:0612345678"

    def test_callable_phone_none(self):
        """Test callable_phone sans téléphone."""
        contact = ContactChantier(nom="Test")

        assert contact.callable_phone is None

    def test_to_dict(self):
        """Test conversion en dictionnaire."""
        contact = ContactChantier(
            nom="Jean Dupont",
            profession="Conducteur",
            telephone="0612345678",
        )

        result = contact.to_dict()

        assert result == {
            "nom": "Jean Dupont",
            "profession": "Conducteur",
            "telephone": "0612345678",
        }

    def test_to_dict_with_none_values(self):
        """Test to_dict avec valeurs None."""
        contact = ContactChantier(nom="Jean Dupont")

        result = contact.to_dict()

        assert result == {
            "nom": "Jean Dupont",
            "profession": None,
            "telephone": None,
        }

    def test_from_dict(self):
        """Test création depuis dictionnaire."""
        data = {
            "nom": "Jean Dupont",
            "profession": "Conducteur",
            "telephone": "0612345678",
        }

        contact = ContactChantier.from_dict(data)

        assert contact.nom == "Jean Dupont"
        assert contact.profession == "Conducteur"
        assert contact.telephone == "0612345678"

    def test_from_dict_without_optional(self):
        """Test from_dict sans champs optionnels."""
        data = {"nom": "Jean Dupont"}

        contact = ContactChantier.from_dict(data)

        assert contact.nom == "Jean Dupont"
        assert contact.profession is None
        assert contact.telephone is None

    def test_from_dict_missing_nom_raises(self):
        """Test from_dict sans nom lève ValueError."""
        data = {"profession": "Conducteur"}

        with pytest.raises(ValueError, match="Dictionnaire doit contenir 'nom'"):
            ContactChantier.from_dict(data)
