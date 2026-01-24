"""Tests unitaires pour les repositories du module Logistique.

H12: Amélioration de la couverture de tests à 85%.
"""

import pytest
from datetime import date, time, datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from modules.logistique.domain.entities import Ressource, Reservation
from modules.logistique.domain.value_objects import (
    CategorieRessource,
    StatutReservation,
    PlageHoraire,
)
from modules.logistique.infrastructure.persistence.sqlalchemy_ressource_repository import (
    SQLAlchemyRessourceRepository,
)
from modules.logistique.infrastructure.persistence.sqlalchemy_reservation_repository import (
    SQLAlchemyReservationRepository,
)


class TestSQLAlchemyRessourceRepository:
    """Tests pour SQLAlchemyRessourceRepository."""

    @pytest.fixture
    def mock_session(self):
        """Mock de la session SQLAlchemy."""
        return MagicMock()

    @pytest.fixture
    def repository(self, mock_session):
        """Repository avec session mockée."""
        return SQLAlchemyRessourceRepository(mock_session)

    @pytest.fixture
    def mock_ressource_model(self):
        """Mock d'un modèle Ressource."""
        model = MagicMock()
        model.id = 1
        model.nom = "Grue 50T"
        model.code = "GRU001"
        model.categorie = CategorieRessource.ENGIN_LEVAGE
        model.photo_url = "http://example.com/grue.jpg"
        model.couleur = "#FF5733"
        model.heure_debut_defaut = time(8, 0)
        model.heure_fin_defaut = time(18, 0)
        model.validation_requise = True
        model.actif = True
        model.description = "Grue de levage"
        model.created_at = datetime.now()
        model.updated_at = None
        model.created_by = 1
        model.deleted_at = None
        model.deleted_by = None
        return model

    def test_to_entity_converts_model_correctly(self, repository, mock_ressource_model):
        """Test: conversion modèle vers entité."""
        entity = repository._to_entity(mock_ressource_model)

        assert entity.id == 1
        assert entity.nom == "Grue 50T"
        assert entity.code == "GRU001"
        assert entity.categorie == CategorieRessource.ENGIN_LEVAGE
        assert entity.couleur == "#FF5733"
        assert entity.validation_requise is True
        assert entity.actif is True
        assert entity.deleted_at is None

    def test_find_by_id_returns_entity(self, repository, mock_session, mock_ressource_model):
        """Test: find_by_id retourne une entité."""
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            mock_ressource_model
        )

        result = repository.find_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.code == "GRU001"

    def test_find_by_id_returns_none_when_not_found(self, repository, mock_session):
        """Test: find_by_id retourne None si non trouvé."""
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            None
        )

        result = repository.find_by_id(999)

        assert result is None

    def test_find_by_code_returns_entity(self, repository, mock_session, mock_ressource_model):
        """Test: find_by_code retourne une entité."""
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            mock_ressource_model
        )

        result = repository.find_by_code("GRU001")

        assert result is not None
        assert result.code == "GRU001"

    def test_find_by_code_returns_none_when_not_found(self, repository, mock_session):
        """Test: find_by_code retourne None si non trouvé."""
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            None
        )

        result = repository.find_by_code("NOTFOUND")

        assert result is None

    def test_find_all_returns_list(self, repository, mock_session, mock_ressource_model):
        """Test: find_all retourne une liste."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_ressource_model]

        result = repository.find_all()

        assert len(result) == 1
        assert result[0].code == "GRU001"

    def test_find_all_with_categorie_filter(self, repository, mock_session, mock_ressource_model):
        """Test: find_all avec filtre catégorie."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_ressource_model]

        result = repository.find_all(categorie=CategorieRessource.ENGIN_LEVAGE)

        assert len(result) == 1

    def test_count_returns_number(self, repository, mock_session):
        """Test: count retourne un nombre."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5

        result = repository.count()

        assert result == 5

    def test_delete_soft_deletes_ressource(self, repository, mock_session, mock_ressource_model):
        """Test: delete fait un soft delete."""
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            mock_ressource_model
        )

        result = repository.delete(1, deleted_by=10)

        assert result is True
        assert mock_ressource_model.deleted_at is not None
        assert mock_ressource_model.deleted_by == 10
        mock_session.flush.assert_called_once()

    def test_delete_returns_false_when_not_found(self, repository, mock_session):
        """Test: delete retourne False si non trouvé."""
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            None
        )

        result = repository.delete(999)

        assert result is False

    def test_save_creates_new_ressource(self, repository, mock_session):
        """Test: save crée une nouvelle ressource."""
        ressource = Ressource(
            nom="Nouvelle Grue",
            code="GRU002",
            categorie=CategorieRessource.ENGIN_LEVAGE,
            plage_horaire_defaut=PlageHoraire(time(8, 0), time(18, 0)),
        )

        mock_model = MagicMock()
        mock_model.id = 2
        mock_model.nom = "Nouvelle Grue"
        mock_model.code = "GRU002"
        mock_model.categorie = CategorieRessource.ENGIN_LEVAGE
        mock_model.photo_url = None
        mock_model.couleur = "#3B82F6"
        mock_model.heure_debut_defaut = time(8, 0)
        mock_model.heure_fin_defaut = time(18, 0)
        mock_model.validation_requise = True
        mock_model.actif = True
        mock_model.description = None
        mock_model.created_at = datetime.now()
        mock_model.updated_at = None
        mock_model.created_by = None
        mock_model.deleted_at = None
        mock_model.deleted_by = None

        with patch.object(repository, "_to_model", return_value=mock_model):
            mock_session.add = MagicMock()
            mock_session.flush = MagicMock()

            result = repository.save(ressource)

            mock_session.add.assert_called_once()
            mock_session.flush.assert_called_once()


class TestSQLAlchemyReservationRepository:
    """Tests pour SQLAlchemyReservationRepository."""

    @pytest.fixture
    def mock_session(self):
        """Mock de la session SQLAlchemy."""
        return MagicMock()

    @pytest.fixture
    def repository(self, mock_session):
        """Repository avec session mockée."""
        return SQLAlchemyReservationRepository(mock_session)

    @pytest.fixture
    def mock_reservation_model(self):
        """Mock d'un modèle Reservation."""
        model = MagicMock()
        model.id = 1
        model.ressource_id = 1
        model.chantier_id = 100
        model.demandeur_id = 10
        model.date_reservation = date.today()
        model.heure_debut = time(9, 0)
        model.heure_fin = time(12, 0)
        model.statut = StatutReservation.EN_ATTENTE
        model.motif_refus = None
        model.commentaire = "Test"
        model.valideur_id = None
        model.validated_at = None
        model.created_at = datetime.now()
        model.updated_at = None
        model.deleted_at = None
        model.deleted_by = None
        return model

    def test_to_entity_converts_model_correctly(self, repository, mock_reservation_model):
        """Test: conversion modèle vers entité."""
        entity = repository._to_entity(mock_reservation_model)

        assert entity.id == 1
        assert entity.ressource_id == 1
        assert entity.chantier_id == 100
        assert entity.demandeur_id == 10
        assert entity.statut == StatutReservation.EN_ATTENTE
        assert entity.deleted_at is None

    def test_find_by_id_returns_entity(self, repository, mock_session, mock_reservation_model):
        """Test: find_by_id retourne une entité."""
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            mock_reservation_model
        )

        result = repository.find_by_id(1)

        assert result is not None
        assert result.id == 1

    def test_find_by_id_returns_none_when_not_found(self, repository, mock_session):
        """Test: find_by_id retourne None si non trouvé."""
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            None
        )

        result = repository.find_by_id(999)

        assert result is None

    def test_find_en_attente_validation_returns_list(
        self, repository, mock_session, mock_reservation_model
    ):
        """Test: find_en_attente_validation retourne une liste."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_reservation_model]

        result = repository.find_en_attente_validation()

        assert len(result) == 1
        assert result[0].statut == StatutReservation.EN_ATTENTE

    def test_count_en_attente_returns_number(self, repository, mock_session):
        """Test: count_en_attente retourne un nombre."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 3

        result = repository.count_en_attente()

        assert result == 3

    def test_delete_soft_deletes_reservation(
        self, repository, mock_session, mock_reservation_model
    ):
        """Test: delete fait un soft delete."""
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            mock_reservation_model
        )

        result = repository.delete(1, deleted_by=10)

        assert result is True
        assert mock_reservation_model.deleted_at is not None
        assert mock_reservation_model.deleted_by == 10
        mock_session.flush.assert_called_once()

    def test_delete_returns_false_when_not_found(self, repository, mock_session):
        """Test: delete retourne False si non trouvé."""
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            None
        )

        result = repository.delete(999)

        assert result is False

    def test_find_by_ressource_and_date_range(
        self, repository, mock_session, mock_reservation_model
    ):
        """Test: find_by_ressource_and_date_range retourne une liste."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [mock_reservation_model]

        result = repository.find_by_ressource_and_date_range(
            ressource_id=1,
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=7),
        )

        assert len(result) == 1

    def test_find_by_chantier(self, repository, mock_session, mock_reservation_model):
        """Test: find_by_chantier retourne une liste."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_reservation_model]

        result = repository.find_by_chantier(chantier_id=100)

        assert len(result) == 1
        assert result[0].chantier_id == 100

    def test_find_by_demandeur(self, repository, mock_session, mock_reservation_model):
        """Test: find_by_demandeur retourne une liste."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_reservation_model]

        result = repository.find_by_demandeur(demandeur_id=10)

        assert len(result) == 1
        assert result[0].demandeur_id == 10

    def test_count_by_ressource(self, repository, mock_session):
        """Test: count_by_ressource retourne un nombre."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5

        result = repository.count_by_ressource(ressource_id=1)

        assert result == 5

    def test_find_conflits_returns_conflicting_reservations(
        self, repository, mock_session, mock_reservation_model
    ):
        """Test: find_conflits retourne les réservations en conflit."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_reservation_model]

        reservation = Reservation(
            id=2,
            ressource_id=1,
            chantier_id=100,
            demandeur_id=10,
            date_reservation=date.today(),
            heure_debut=time(10, 0),
            heure_fin=time(11, 0),
            statut=StatutReservation.EN_ATTENTE,
        )

        result = repository.find_conflits(reservation)

        assert len(result) == 1

    def test_find_historique_ressource(self, repository, mock_session, mock_reservation_model):
        """Test: find_historique_ressource retourne l'historique."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_reservation_model]

        result = repository.find_historique_ressource(ressource_id=1)

        assert len(result) == 1
