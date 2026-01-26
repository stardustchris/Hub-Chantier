"""Tests unitaires pour SQLAlchemyTacheRepository."""

import pytest
from datetime import date, datetime
from unittest.mock import Mock, MagicMock, patch

from modules.taches.infrastructure.persistence.sqlalchemy_tache_repository import (
    SQLAlchemyTacheRepository,
)
from modules.taches.domain.entities import Tache
from modules.taches.domain.value_objects import StatutTache, UniteMesure


class TestSQLAlchemyTacheRepository:
    """Tests pour SQLAlchemyTacheRepository."""

    @pytest.fixture
    def mock_session(self):
        """Session SQLAlchemy mock."""
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        session.first.return_value = None
        session.all.return_value = []
        session.count.return_value = 0
        return session

    @pytest.fixture
    def repository(self, mock_session):
        """Instance du repository."""
        return SQLAlchemyTacheRepository(mock_session)


class TestFindById:
    """Tests pour find_by_id."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyTacheRepository(mock_session)

    def test_trouve_tache_existante(self, repository, mock_session):
        """Trouve une tache existante par ID."""
        mock_entity = Mock()
        mock_entity.id = 1
        mock_entity.chantier_id = 10
        mock_entity.titre = "Tache test"

        mock_model = Mock()
        mock_model.to_entity.return_value = mock_entity

        mock_session.first.return_value = mock_model

        result = repository.find_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.titre == "Tache test"

    def test_retourne_none_si_non_trouve(self, repository, mock_session):
        """Retourne None si tache non trouvee."""
        mock_session.first.return_value = None

        result = repository.find_by_id(999)
        assert result is None


class TestFindByChantier:
    """Tests pour find_by_chantier."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        session.order_by.return_value = session
        session.offset.return_value = session
        session.limit.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyTacheRepository(mock_session)

    def test_trouve_taches_racines_chantier(self, repository, mock_session):
        """Trouve les taches racines d'un chantier."""
        mock_entity = Mock()
        mock_entity.id = 1
        mock_entity.parent_id = None

        mock_model = Mock()
        mock_model.to_entity.return_value = mock_entity

        mock_session.all.return_value = [mock_model]

        result = repository.find_by_chantier(10)

        assert len(result) == 1
        assert result[0].parent_id is None

    def test_pagination(self, repository, mock_session):
        """Gere la pagination."""
        mock_session.all.return_value = []

        repository.find_by_chantier(10, skip=20, limit=10)

        mock_session.offset.assert_called_with(20)
        mock_session.limit.assert_called_with(10)


class TestFindChildren:
    """Tests pour find_children."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        session.order_by.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyTacheRepository(mock_session)

    def test_trouve_sous_taches(self, repository, mock_session):
        """Trouve les sous-taches d'une tache."""
        mock_entity1 = Mock()
        mock_entity1.id = 2
        mock_entity1.parent_id = 1

        mock_entity2 = Mock()
        mock_entity2.id = 3
        mock_entity2.parent_id = 1

        mock_model1 = Mock()
        mock_model1.to_entity.return_value = mock_entity1
        mock_model2 = Mock()
        mock_model2.to_entity.return_value = mock_entity2

        mock_session.all.return_value = [mock_model1, mock_model2]

        result = repository.find_children(1)

        assert len(result) == 2
        assert all(r.parent_id == 1 for r in result)


class TestSave:
    """Tests pour save."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyTacheRepository(mock_session)

    def test_cree_nouvelle_tache(self, repository, mock_session):
        """Cree une nouvelle tache."""
        tache = Mock()
        tache.id = None  # Nouvelle
        tache.chantier_id = 10
        tache.titre = "Nouvelle tache"
        tache.description = "Description"
        tache.parent_id = None
        tache.ordre = 1
        tache.statut = StatutTache.A_FAIRE
        tache.date_echeance = date(2024, 2, 15)
        tache.unite_mesure = UniteMesure.M2  # Metres carres
        tache.quantite_estimee = 100.0
        tache.quantite_realisee = 0.0
        tache.heures_estimees = 40
        tache.heures_realisees = 0
        tache.template_id = None
        tache.created_at = datetime.now()
        tache.updated_at = datetime.now()

        mock_saved_entity = Mock()
        mock_saved_entity.id = 42

        mock_model = Mock()
        mock_model.to_entity.return_value = mock_saved_entity

        with patch(
            "modules.taches.infrastructure.persistence.sqlalchemy_tache_repository.TacheModel"
        ) as MockTacheModel:
            MockTacheModel.from_entity.return_value = mock_model
            result = repository.save(tache)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_met_a_jour_tache_existante(self, repository, mock_session):
        """Met a jour une tache existante."""
        tache = Mock()
        tache.id = 42  # Existante
        tache.chantier_id = 10
        tache.titre = "Tache mise a jour"
        tache.description = "Nouvelle description"
        tache.parent_id = None
        tache.ordre = 2
        tache.statut = StatutTache.TERMINE  # Termine
        tache.date_echeance = date(2024, 2, 20)
        tache.unite_mesure = UniteMesure.M2  # Metres carres
        tache.quantite_estimee = 150.0
        tache.quantite_realisee = 50.0
        tache.heures_estimees = 60
        tache.heures_realisees = 20
        tache.template_id = None
        tache.updated_at = datetime.now()

        mock_model = Mock()
        mock_model.id = 42
        mock_model.to_entity.return_value = tache

        mock_session.first.return_value = mock_model

        result = repository.save(tache)

        mock_session.commit.assert_called_once()
        assert mock_model.titre == "Tache mise a jour"
        assert mock_model.statut == "termine"


class TestDelete:
    """Tests pour delete."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyTacheRepository(mock_session)

    def test_supprime_tache_existante(self, repository, mock_session):
        """Supprime une tache existante."""
        mock_model = Mock()
        mock_model.id = 1
        mock_session.first.return_value = mock_model

        # Pas d'enfants
        mock_session.all.return_value = []

        result = repository.delete(1)

        assert result is True
        mock_session.delete.assert_called_with(mock_model)
        mock_session.commit.assert_called_once()

    def test_supprime_avec_sous_taches(self, repository, mock_session):
        """Supprime une tache avec ses sous-taches."""
        mock_model = Mock()
        mock_model.id = 1

        mock_child = Mock()
        mock_child.id = 2

        # Premier appel: tache parente, deuxieme: enfants, etc.
        mock_session.first.side_effect = [mock_model]
        mock_session.all.side_effect = [[mock_child], []]  # Enfant puis pas d'enfants

        result = repository.delete(1)

        assert result is True
        # Supprime l'enfant et le parent
        assert mock_session.delete.call_count >= 1

    def test_retourne_false_si_non_trouve(self, repository, mock_session):
        """Retourne False si tache non trouvee."""
        mock_session.first.return_value = None

        result = repository.delete(999)

        assert result is False
        mock_session.delete.assert_not_called()


class TestCountByChantier:
    """Tests pour count_by_chantier."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyTacheRepository(mock_session)

    def test_compte_taches_chantier(self, repository, mock_session):
        """Compte les taches d'un chantier."""
        mock_session.scalar.return_value = 15

        result = repository.count_by_chantier(10)

        assert result == 15


class TestSearch:
    """Tests pour search."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        session.order_by.return_value = session
        session.offset.return_value = session
        session.limit.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyTacheRepository(mock_session)

    def test_recherche_par_texte(self, repository, mock_session):
        """Recherche par texte dans titre et description."""
        mock_session.count.return_value = 3
        mock_session.all.return_value = []

        taches, total = repository.search(10, query="peinture")

        assert total == 3
        # Le filtre ilike est applique
        mock_session.filter.assert_called()

    def test_recherche_par_statut(self, repository, mock_session):
        """Recherche par statut."""
        mock_session.count.return_value = 5
        mock_session.all.return_value = []

        taches, total = repository.search(10, statut=StatutTache.A_FAIRE)

        assert total == 5

    def test_recherche_combinee(self, repository, mock_session):
        """Recherche avec texte et statut."""
        mock_session.count.return_value = 2
        mock_session.all.return_value = []

        taches, total = repository.search(
            10, query="electricite", statut=StatutTache.A_FAIRE
        )

        assert total == 2


class TestReorder:
    """Tests pour reorder."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyTacheRepository(mock_session)

    def test_reordonne_tache(self, repository, mock_session):
        """Reordonne une tache."""
        mock_model = Mock()
        mock_model.ordre = 1
        mock_session.first.return_value = mock_model

        repository.reorder(1, 5)

        assert mock_model.ordre == 5
        mock_session.commit.assert_called_once()

    def test_ignore_si_tache_non_trouvee(self, repository, mock_session):
        """Ignore si tache non trouvee."""
        mock_session.first.return_value = None

        repository.reorder(999, 5)

        mock_session.commit.assert_not_called()


class TestFindByTemplate:
    """Tests pour find_by_template."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyTacheRepository(mock_session)

    def test_trouve_taches_depuis_template(self, repository, mock_session):
        """Trouve les taches creees depuis un template."""
        mock_entity = Mock()
        mock_entity.template_id = 5

        mock_model = Mock()
        mock_model.to_entity.return_value = mock_entity

        mock_session.all.return_value = [mock_model]

        result = repository.find_by_template(5)

        assert len(result) == 1
        assert result[0].template_id == 5


class TestGetStatsChantier:
    """Tests pour get_stats_chantier."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyTacheRepository(mock_session)

    def test_calcule_statistiques(self, repository, mock_session):
        """Calcule les statistiques d'un chantier."""
        # Total: 20, Terminees: 15, En retard: 2, Heures: (200, 150)
        mock_session.scalar.side_effect = [20, 15, 2]
        mock_session.first.return_value = (200, 150)

        stats = repository.get_stats_chantier(10)

        assert stats["total"] == 20
        assert stats["terminees"] == 15
        assert stats["en_cours"] == 5  # 20 - 15
        assert stats["en_retard"] == 2
        assert stats["heures_estimees_total"] == 200
        assert stats["heures_realisees_total"] == 150

    def test_statistiques_vides(self, repository, mock_session):
        """Statistiques pour chantier vide."""
        mock_session.scalar.side_effect = [0, 0, 0]
        mock_session.first.return_value = (None, None)

        stats = repository.get_stats_chantier(10)

        assert stats["total"] == 0
        assert stats["terminees"] == 0
        assert stats["en_cours"] == 0
        assert stats["en_retard"] == 0
        assert stats["heures_estimees_total"] == 0
        assert stats["heures_realisees_total"] == 0
