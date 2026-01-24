"""Tests unitaires pour les providers du module planning_charge."""

import pytest
from unittest.mock import Mock

from modules.planning_charge.infrastructure.providers import (
    SQLAlchemyChantierProvider,
    SQLAlchemyAffectationProvider,
    SQLAlchemyUtilisateurProvider,
)
from modules.planning_charge.domain.value_objects import Semaine


class TestSQLAlchemyChantierProvider:
    """Tests pour le provider des chantiers."""

    @pytest.fixture
    def mock_session(self):
        """Fixture pour la session mock."""
        return Mock()

    @pytest.fixture
    def provider(self, mock_session):
        """Fixture pour le provider."""
        return SQLAlchemyChantierProvider(mock_session)

    def test_get_chantiers_by_ids_empty_list(self, provider):
        """Test get_chantiers_by_ids avec liste vide retourne liste vide."""
        result = provider.get_chantiers_by_ids([])
        assert result == []

    def test_provider_initialization(self, provider, mock_session):
        """Test que le provider est correctement initialise."""
        assert provider.session is mock_session


class TestSQLAlchemyAffectationProvider:
    """Tests pour le provider des affectations."""

    @pytest.fixture
    def mock_session(self):
        """Fixture pour la session mock."""
        return Mock()

    @pytest.fixture
    def provider(self, mock_session):
        """Fixture pour le provider."""
        return SQLAlchemyAffectationProvider(mock_session)

    def test_get_heures_planifiees_par_chantier_et_semaine_empty(self, provider):
        """Test avec liste de chantiers vide retourne dict vide."""
        semaine = Semaine(annee=2026, numero=4)
        result = provider.get_heures_planifiees_par_chantier_et_semaine([], semaine, semaine)
        assert result == {}

    def test_map_metier_to_type_known_macon(self, provider):
        """Test mapping metier macon."""
        assert provider._map_metier_to_type("Macon") == "macon"
        assert provider._map_metier_to_type("Maçon") == "macon"
        assert provider._map_metier_to_type("MACON") == "macon"

    def test_map_metier_to_type_known_coffreur(self, provider):
        """Test mapping metier coffreur."""
        assert provider._map_metier_to_type("Coffreur") == "coffreur"
        assert provider._map_metier_to_type("COFFREUR") == "coffreur"

    def test_map_metier_to_type_known_ferrailleur(self, provider):
        """Test mapping metier ferrailleur."""
        assert provider._map_metier_to_type("Ferrailleur") == "ferrailleur"

    def test_map_metier_to_type_known_grutier(self, provider):
        """Test mapping metier grutier."""
        assert provider._map_metier_to_type("Grutier") == "grutier"

    def test_map_metier_to_type_known_charpentier(self, provider):
        """Test mapping metier charpentier."""
        assert provider._map_metier_to_type("Charpentier") == "charpentier"

    def test_map_metier_to_type_known_couvreur(self, provider):
        """Test mapping metier couvreur."""
        assert provider._map_metier_to_type("Couvreur") == "couvreur"

    def test_map_metier_to_type_known_electricien(self, provider):
        """Test mapping metier electricien."""
        assert provider._map_metier_to_type("Electricien") == "electricien"
        assert provider._map_metier_to_type("électricien") == "electricien"

    def test_map_metier_to_type_unknown(self, provider):
        """Test mapping metier inconnu retourne employe."""
        assert provider._map_metier_to_type("AutreMetier") == "employe"
        assert provider._map_metier_to_type("Technicien") == "employe"

    def test_map_metier_to_type_empty(self, provider):
        """Test mapping metier vide retourne employe."""
        assert provider._map_metier_to_type("") == "employe"

    def test_map_metier_to_type_none(self, provider):
        """Test mapping metier None retourne employe."""
        assert provider._map_metier_to_type(None) == "employe"

    def test_generate_semaines_same_week(self, provider):
        """Test generation de semaines pour une seule semaine."""
        debut = Semaine(annee=2026, numero=4)
        fin = Semaine(annee=2026, numero=4)

        result = provider._generate_semaines(debut, fin)

        assert len(result) == 1
        assert result[0].numero == 4
        assert result[0].annee == 2026

    def test_generate_semaines_multiple_weeks(self, provider):
        """Test generation de semaines pour plusieurs semaines."""
        debut = Semaine(annee=2026, numero=4)
        fin = Semaine(annee=2026, numero=6)

        result = provider._generate_semaines(debut, fin)

        assert len(result) == 3
        assert result[0].numero == 4
        assert result[1].numero == 5
        assert result[2].numero == 6

    def test_generate_semaines_cross_year(self, provider):
        """Test generation de semaines qui traverse une annee."""
        debut = Semaine(annee=2025, numero=52)
        fin = Semaine(annee=2026, numero=2)

        result = provider._generate_semaines(debut, fin)

        # S52-2025 -> S01-2026 -> S02-2026 = 3 semaines
        assert len(result) == 3
        assert result[0].annee == 2025
        assert result[0].numero == 52
        assert result[1].annee == 2026
        assert result[1].numero == 1
        assert result[2].annee == 2026
        assert result[2].numero == 2

    def test_provider_constants(self, provider):
        """Test les constantes du provider."""
        assert provider.HEURES_PAR_JOUR == 7.0
        assert provider.HEURES_PAR_SEMAINE == 35.0


class TestSQLAlchemyUtilisateurProvider:
    """Tests pour le provider des utilisateurs."""

    @pytest.fixture
    def mock_session(self):
        """Fixture pour la session mock."""
        return Mock()

    @pytest.fixture
    def provider(self, mock_session):
        """Fixture pour le provider."""
        return SQLAlchemyUtilisateurProvider(mock_session)

    def test_map_metier_to_type_macon(self, provider):
        """Test mapping metier macon."""
        assert provider._map_metier_to_type("macon") == "macon"
        assert provider._map_metier_to_type("Maçon") == "macon"
        assert provider._map_metier_to_type("MACON") == "macon"

    def test_map_metier_to_type_coffreur(self, provider):
        """Test mapping metier coffreur."""
        assert provider._map_metier_to_type("Coffreur") == "coffreur"

    def test_map_metier_to_type_ferrailleur(self, provider):
        """Test mapping metier ferrailleur."""
        assert provider._map_metier_to_type("Ferrailleur") == "ferrailleur"

    def test_map_metier_to_type_grutier(self, provider):
        """Test mapping metier grutier."""
        assert provider._map_metier_to_type("Grutier") == "grutier"

    def test_map_metier_to_type_charpentier(self, provider):
        """Test mapping metier charpentier."""
        assert provider._map_metier_to_type("Charpentier") == "charpentier"

    def test_map_metier_to_type_couvreur(self, provider):
        """Test mapping metier couvreur."""
        assert provider._map_metier_to_type("Couvreur") == "couvreur"

    def test_map_metier_to_type_electricien(self, provider):
        """Test mapping metier electricien."""
        assert provider._map_metier_to_type("Electricien") == "electricien"
        assert provider._map_metier_to_type("électricien") == "electricien"

    def test_map_metier_to_type_sous_traitant(self, provider):
        """Test mapping metier sous-traitant."""
        assert provider._map_metier_to_type("Sous-traitant") == "sous_traitant"
        assert provider._map_metier_to_type("sous traitant") == "sous_traitant"
        assert provider._map_metier_to_type("prestataire") == "sous_traitant"

    def test_map_metier_to_type_unknown(self, provider):
        """Test mapping metier inconnu retourne employe."""
        assert provider._map_metier_to_type("AutreMetier") == "employe"
        assert provider._map_metier_to_type("inconnu") == "employe"

    def test_map_metier_to_type_none(self, provider):
        """Test mapping metier None retourne employe."""
        assert provider._map_metier_to_type(None) == "employe"

    def test_map_metier_to_type_empty(self, provider):
        """Test mapping metier vide retourne employe."""
        assert provider._map_metier_to_type("") == "employe"

    def test_provider_constant(self, provider):
        """Test la constante du provider."""
        assert provider.HEURES_PAR_SEMAINE == 35.0
