"""Tests unitaires pour SQLAlchemyBesoinChargeRepository.

Note: Les tests d'integration dans tests/integration/test_planning_charge_api.py
couvrent la fonctionnalite complete du repository avec une vraie base de donnees.
Ces tests unitaires se concentrent sur la logique metier testable sans DB.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.planning.infrastructure.persistence import (
    SQLAlchemyBesoinChargeRepository,
    BesoinChargeModel,
)
from modules.planning.domain.entities import BesoinCharge
from modules.planning.domain.value_objects import Semaine, TypeMetier


class TestSQLAlchemyBesoinChargeRepository:
    """Tests pour le repository SQLAlchemy des besoins de charge."""

    @pytest.fixture
    def mock_session(self):
        """Mock de session SQLAlchemy."""
        return Mock()

    @pytest.fixture
    def repository(self, mock_session):
        """Cree un repository avec session mockee."""
        return SQLAlchemyBesoinChargeRepository(mock_session)

    def test_repository_initialization(self, repository, mock_session):
        """Test que le repository est correctement initialise."""
        assert repository.session is mock_session

    def test_to_model_creates_model_new_entity(self, repository, mock_session):
        """Test que _to_model cree un model pour nouvelle entite."""
        entity = BesoinCharge(
            chantier_id=10,
            semaine=Semaine(annee=2026, numero=4),
            type_metier=TypeMetier.MACON,
            besoin_heures=35.0,
            note="Test",
            created_by=1,
        )

        # Mock query().get() pour retourner None (nouveau)
        mock_query = Mock()
        mock_query.get.return_value = None
        mock_session.query.return_value = mock_query

        # Executer
        model = repository._to_model(entity)

        # Verifier
        assert model.chantier_id == 10
        assert model.semaine_annee == 2026
        assert model.semaine_numero == 4
        assert model.type_metier == "macon"
        assert model.besoin_heures == 35.0

    def test_to_model_updates_existing_model(self, repository, mock_session):
        """Test que _to_model met a jour un model existant."""
        # Entite avec ID (existant)
        entity = BesoinCharge(
            id=1,
            chantier_id=10,
            semaine=Semaine(annee=2026, numero=4),
            type_metier=TypeMetier.MACON,
            besoin_heures=70.0,  # Modifie
            note="Updated",
            created_by=1,
        )

        # Mock du model existant
        existing_model = BesoinChargeModel()
        existing_model.id = 1
        existing_model.chantier_id = 10
        existing_model.semaine_annee = 2026
        existing_model.semaine_numero = 4
        existing_model.type_metier = "macon"
        existing_model.besoin_heures = 35.0  # Ancienne valeur
        existing_model.note = "Original"
        existing_model.created_by = 1

        mock_query = Mock()
        mock_query.get.return_value = existing_model
        mock_session.query.return_value = mock_query

        # Executer
        model = repository._to_model(entity)

        # Verifier que les valeurs ont ete mises a jour
        assert model.besoin_heures == 70.0
        assert model.note == "Updated"


class TestBesoinChargeModelMapping:
    """Tests pour le mapping TypeMetier."""

    def test_type_metier_string_to_enum(self):
        """Test conversion string vers enum TypeMetier."""
        assert TypeMetier("macon") == TypeMetier.MACON
        assert TypeMetier("coffreur") == TypeMetier.COFFREUR
        assert TypeMetier("ferrailleur") == TypeMetier.FERRAILLEUR
        assert TypeMetier("grutier") == TypeMetier.GRUTIER
        assert TypeMetier("charpentier") == TypeMetier.CHARPENTIER
        assert TypeMetier("couvreur") == TypeMetier.COUVREUR
        assert TypeMetier("electricien") == TypeMetier.ELECTRICIEN
        assert TypeMetier("employe") == TypeMetier.EMPLOYE
        assert TypeMetier("sous_traitant") == TypeMetier.SOUS_TRAITANT

    def test_type_metier_enum_to_string(self):
        """Test conversion enum TypeMetier vers string."""
        assert TypeMetier.MACON.value == "macon"
        assert TypeMetier.COFFREUR.value == "coffreur"
        assert TypeMetier.FERRAILLEUR.value == "ferrailleur"
        assert TypeMetier.GRUTIER.value == "grutier"
        assert TypeMetier.CHARPENTIER.value == "charpentier"
        assert TypeMetier.COUVREUR.value == "couvreur"
        assert TypeMetier.ELECTRICIEN.value == "electricien"
        assert TypeMetier.EMPLOYE.value == "employe"
        assert TypeMetier.SOUS_TRAITANT.value == "sous_traitant"

    def test_type_metier_all_values(self):
        """Test que tous les types de metier sont valides."""
        # Verifie qu'il y a 9 types de metiers definis
        all_values = [t.value for t in TypeMetier]
        assert "macon" in all_values
        assert "coffreur" in all_values
        assert "ferrailleur" in all_values
        assert "grutier" in all_values
        assert "charpentier" in all_values
        assert "couvreur" in all_values
        assert "electricien" in all_values
        assert "employe" in all_values
        assert "sous_traitant" in all_values

    def test_semaine_value_object(self):
        """Test du value object Semaine."""
        semaine = Semaine(annee=2026, numero=4)

        assert semaine.annee == 2026
        assert semaine.numero == 4
        assert semaine.code == "S04-2026"

    def test_semaine_comparison(self):
        """Test comparaison de semaines."""
        s1 = Semaine(annee=2026, numero=4)
        s2 = Semaine(annee=2026, numero=5)
        s3 = Semaine(annee=2026, numero=4)

        assert s1 < s2
        assert s2 > s1
        assert s1 == s3
        assert s1 <= s3
        assert s1 <= s2

    def test_semaine_next(self):
        """Test semaine suivante."""
        s1 = Semaine(annee=2026, numero=4)
        s2 = s1.next()

        assert s2.annee == 2026
        assert s2.numero == 5

    def test_semaine_next_cross_year(self):
        """Test semaine suivante qui passe a l'annee suivante."""
        # Semaine 52 de 2025
        s1 = Semaine(annee=2025, numero=52)
        s2 = s1.next()

        # Devrait passer a semaine 1 de 2026
        assert s2.annee == 2026
        assert s2.numero == 1

    def test_semaine_from_date(self):
        """Test creation de semaine depuis une date."""
        from datetime import date

        # 20 janvier 2026 est un lundi de la semaine 4
        d = date(2026, 1, 20)
        semaine = Semaine.from_date(d)

        assert semaine.annee == 2026
        assert semaine.numero == 4

    def test_semaine_date_range(self):
        """Test plage de dates d'une semaine."""
        semaine = Semaine(annee=2026, numero=4)
        debut, fin = semaine.date_range()

        # Semaine 4 de 2026: 19-25 janvier
        from datetime import date
        assert debut == date(2026, 1, 19)
        assert fin == date(2026, 1, 25)
