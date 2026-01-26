"""Tests unitaires pour SQLAlchemyInterventionRepository."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date, time, datetime

from modules.interventions.infrastructure.persistence.sqlalchemy_intervention_repository import (
    SQLAlchemyInterventionRepository,
)
from modules.interventions.domain.value_objects import (
    StatutIntervention,
    PrioriteIntervention,
    TypeIntervention,
)


class TestSave:
    """Tests de save."""

    def test_save_new_intervention(self):
        """Test sauvegarde nouvelle intervention."""
        mock_db = Mock()
        mock_intervention = Mock()
        mock_intervention.id = None
        mock_intervention.code = None
        mock_intervention.type_intervention = TypeIntervention.SAV
        mock_intervention.statut = StatutIntervention.A_PLANIFIER
        mock_intervention.priorite = PrioriteIntervention.NORMALE
        mock_intervention.client_nom = "Test Client"
        mock_intervention.client_adresse = "123 Rue Test"
        mock_intervention.client_telephone = "0123456789"
        mock_intervention.client_email = "test@test.com"
        mock_intervention.description = "Description test"
        mock_intervention.travaux_realises = None
        mock_intervention.anomalies = None
        mock_intervention.date_souhaitee = None
        mock_intervention.date_planifiee = None
        mock_intervention.heure_debut = None
        mock_intervention.heure_fin = None
        mock_intervention.heure_debut_reelle = None
        mock_intervention.heure_fin_reelle = None
        mock_intervention.chantier_origine_id = None
        mock_intervention.rapport_genere = False
        mock_intervention.rapport_url = None
        mock_intervention.created_by = 1
        mock_intervention.created_at = datetime.now()

        # Mock query pour generate_code
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 5

        repo = SQLAlchemyInterventionRepository(mock_db)

        # Mock flush pour assigner l'ID
        def flush_side_effect():
            pass

        mock_db.flush.side_effect = flush_side_effect

        result = repo.save(mock_intervention)

        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()

    def test_save_existing_intervention(self):
        """Test mise à jour intervention existante."""
        mock_db = Mock()
        mock_intervention = Mock()
        mock_intervention.id = 1
        mock_intervention.code = "INT-2026-0001"
        mock_intervention.type_intervention = TypeIntervention.SAV
        mock_intervention.statut = StatutIntervention.EN_COURS
        mock_intervention.priorite = PrioriteIntervention.URGENTE
        mock_intervention.client_nom = "Updated Client"
        mock_intervention.client_adresse = "456 Rue Update"
        mock_intervention.client_telephone = "9876543210"
        mock_intervention.client_email = "updated@test.com"
        mock_intervention.description = "Updated description"
        mock_intervention.travaux_realises = "Travaux effectués"
        mock_intervention.anomalies = None
        mock_intervention.date_souhaitee = date(2026, 1, 15)
        mock_intervention.date_planifiee = date(2026, 1, 20)
        mock_intervention.heure_debut = time(9, 0)
        mock_intervention.heure_fin = time(12, 0)
        mock_intervention.heure_debut_reelle = time(9, 15)
        mock_intervention.heure_fin_reelle = None
        mock_intervention.chantier_origine_id = 10
        mock_intervention.rapport_genere = False
        mock_intervention.rapport_url = None
        mock_intervention.deleted_at = None

        mock_model = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_model

        repo = SQLAlchemyInterventionRepository(mock_db)
        result = repo.save(mock_intervention)

        mock_db.flush.assert_called_once()
        assert mock_model.statut == StatutIntervention.EN_COURS


class TestGetById:
    """Tests de get_by_id."""

    def test_get_by_id_found(self):
        """Test récupération intervention trouvée."""
        mock_db = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.code = "INT-2026-0001"
        mock_model.type_intervention = TypeIntervention.SAV
        mock_model.statut = StatutIntervention.A_PLANIFIER
        mock_model.priorite = PrioriteIntervention.NORMALE
        mock_model.client_nom = "Test Client"
        mock_model.client_adresse = "123 Rue Test"
        mock_model.client_telephone = None
        mock_model.client_email = None
        mock_model.description = "Description"
        mock_model.travaux_realises = None
        mock_model.anomalies = None
        mock_model.date_souhaitee = None
        mock_model.date_planifiee = None
        mock_model.heure_debut = None
        mock_model.heure_fin = None
        mock_model.heure_debut_reelle = None
        mock_model.heure_fin_reelle = None
        mock_model.chantier_origine_id = None
        mock_model.rapport_genere = False
        mock_model.rapport_url = None
        mock_model.created_by = 1
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()
        mock_model.deleted_at = None
        mock_model.deleted_by = None

        mock_db.query.return_value.filter.return_value.first.return_value = mock_model

        repo = SQLAlchemyInterventionRepository(mock_db)
        result = repo.get_by_id(1)

        assert result is not None
        assert result.id == 1

    def test_get_by_id_not_found(self):
        """Test récupération intervention non trouvée."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        repo = SQLAlchemyInterventionRepository(mock_db)
        result = repo.get_by_id(999)

        assert result is None


class TestGetByCode:
    """Tests de get_by_code."""

    def test_get_by_code_found(self):
        """Test récupération par code."""
        mock_db = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.code = "INT-2026-0001"
        mock_model.type_intervention = TypeIntervention.SAV
        mock_model.statut = StatutIntervention.A_PLANIFIER
        mock_model.priorite = PrioriteIntervention.NORMALE
        mock_model.client_nom = "Test"
        mock_model.client_adresse = "Adresse"
        mock_model.client_telephone = None
        mock_model.client_email = None
        mock_model.description = "Desc"
        mock_model.travaux_realises = None
        mock_model.anomalies = None
        mock_model.date_souhaitee = None
        mock_model.date_planifiee = None
        mock_model.heure_debut = None
        mock_model.heure_fin = None
        mock_model.heure_debut_reelle = None
        mock_model.heure_fin_reelle = None
        mock_model.chantier_origine_id = None
        mock_model.rapport_genere = False
        mock_model.rapport_url = None
        mock_model.created_by = 1
        mock_model.created_at = datetime.now()
        mock_model.updated_at = None
        mock_model.deleted_at = None
        mock_model.deleted_by = None

        mock_db.query.return_value.filter.return_value.first.return_value = mock_model

        repo = SQLAlchemyInterventionRepository(mock_db)
        result = repo.get_by_code("INT-2026-0001")

        assert result is not None
        assert result.code == "INT-2026-0001"

    def test_get_by_code_not_found(self):
        """Test récupération par code non trouvé."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        repo = SQLAlchemyInterventionRepository(mock_db)
        result = repo.get_by_code("INT-9999-9999")

        assert result is None


class TestListAll:
    """Tests de list_all."""

    def test_list_all_no_filters(self):
        """Test liste sans filtres."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyInterventionRepository(mock_db)
        result = repo.list_all()

        assert result == []

    def test_list_all_with_statut_filter(self):
        """Test liste avec filtre statut."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyInterventionRepository(mock_db)
        repo.list_all(statut=StatutIntervention.EN_COURS)

        # Vérifie que filter a été appelé plusieurs fois
        assert mock_query.filter.call_count >= 1


class TestCount:
    """Tests de count."""

    def test_count_all(self):
        """Test comptage total."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 42

        repo = SQLAlchemyInterventionRepository(mock_db)
        result = repo.count()

        assert result == 42

    def test_count_with_filters(self):
        """Test comptage avec filtres."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 10

        repo = SQLAlchemyInterventionRepository(mock_db)
        result = repo.count(
            statut=StatutIntervention.PLANIFIEE,
            priorite=PrioriteIntervention.URGENTE,
        )

        assert result == 10

    def test_count_returns_zero_when_none(self):
        """Test comptage retourne 0 si None."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = None

        repo = SQLAlchemyInterventionRepository(mock_db)
        result = repo.count()

        assert result == 0


class TestDelete:
    """Tests de delete."""

    def test_delete_success(self):
        """Test suppression réussie."""
        mock_db = Mock()
        mock_model = Mock()
        mock_model.deleted_at = None
        mock_db.query.return_value.filter.return_value.first.return_value = mock_model

        repo = SQLAlchemyInterventionRepository(mock_db)
        result = repo.delete(1, deleted_by=5)

        assert result is True
        assert mock_model.deleted_at is not None
        assert mock_model.deleted_by == 5

    def test_delete_not_found(self):
        """Test suppression élément non trouvé."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        repo = SQLAlchemyInterventionRepository(mock_db)
        result = repo.delete(999, deleted_by=5)

        assert result is False


class TestGenerateCode:
    """Tests de generate_code."""

    def test_generate_code_first_of_year(self):
        """Test génération premier code de l'année."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 0

        repo = SQLAlchemyInterventionRepository(mock_db)
        code = repo.generate_code()

        year = datetime.utcnow().year
        assert code == f"INT-{year}-0001"

    def test_generate_code_increments(self):
        """Test génération code incrémenté."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 42

        repo = SQLAlchemyInterventionRepository(mock_db)
        code = repo.generate_code()

        year = datetime.utcnow().year
        assert code == f"INT-{year}-0043"


class TestListByDateRange:
    """Tests de list_by_date_range."""

    def test_list_by_date_range_empty(self):
        """Test liste vide pour période."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyInterventionRepository(mock_db)
        result = repo.list_by_date_range(
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        assert result == []
