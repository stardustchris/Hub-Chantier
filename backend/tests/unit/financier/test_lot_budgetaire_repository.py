"""Tests unitaires pour le repository LotBudgetaire."""

import pytest
from decimal import Decimal
from uuid import uuid4
from unittest.mock import Mock

from modules.financier.domain.entities import LotBudgetaire
from modules.financier.domain.value_objects import UniteMesure
from modules.financier.infrastructure.persistence.sqlalchemy_lot_budgetaire_repository import (
    SQLAlchemyLotBudgetaireRepository,
)
from modules.financier.infrastructure.persistence.models import LotBudgetaireModel


class TestFindByDevisId:
    """Tests pour la méthode find_by_devis_id du repository."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_session = Mock()
        self.repository = SQLAlchemyLotBudgetaireRepository(self.mock_session)

    def test_find_by_devis_id_with_existing_devis(self):
        """Test: find_by_devis_id avec devis existant retourne les lots."""
        # Arrange
        devis_id = uuid4()
        mock_lot1 = LotBudgetaireModel(
            id=1,
            devis_id=str(devis_id),
            code_lot="GO-01",
            libelle="Gros oeuvre",
            unite="m2",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
            ordre=1,
            deleted_at=None,
        )
        mock_lot2 = LotBudgetaireModel(
            id=2,
            devis_id=str(devis_id),
            code_lot="SEC-01",
            libelle="Second oeuvre",
            unite="m2",
            quantite_prevue=Decimal("80"),
            prix_unitaire_ht=Decimal("40"),
            ordre=2,
            deleted_at=None,
        )

        # Mock de la query SQLAlchemy
        mock_query = Mock()
        mock_filter1 = Mock()
        mock_filter2 = Mock()
        mock_order = Mock()

        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter1
        mock_filter1.filter.return_value = mock_filter2
        mock_filter2.order_by.return_value = mock_order
        mock_order.all.return_value = [mock_lot1, mock_lot2]

        # Act
        result = self.repository.find_by_devis_id(devis_id)

        # Assert
        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].code_lot == "GO-01"
        assert result[0].devis_id == devis_id
        assert result[1].id == 2
        assert result[1].code_lot == "SEC-01"
        assert result[1].devis_id == devis_id

        # Vérifier que la query a été appelée avec le bon UUID
        self.mock_session.query.assert_called_once()

    def test_find_by_devis_id_with_nonexistent_devis(self):
        """Test: find_by_devis_id avec devis inexistant retourne liste vide."""
        # Arrange
        devis_id = uuid4()

        # Mock de la query SQLAlchemy
        mock_query = Mock()
        mock_filter1 = Mock()
        mock_filter2 = Mock()
        mock_order = Mock()

        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter1
        mock_filter1.filter.return_value = mock_filter2
        mock_filter2.order_by.return_value = mock_order
        mock_order.all.return_value = []

        # Act
        result = self.repository.find_by_devis_id(devis_id)

        # Assert
        assert len(result) == 0
        assert result == []

    def test_find_by_devis_id_excludes_deleted(self):
        """Test: find_by_devis_id exclut les lots supprimés."""
        # Arrange
        devis_id = uuid4()
        mock_lot_active = LotBudgetaireModel(
            id=1,
            devis_id=str(devis_id),
            code_lot="GO-01",
            libelle="Gros oeuvre",
            unite="m2",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
            ordre=1,
            deleted_at=None,
        )

        # Mock de la query SQLAlchemy
        mock_query = Mock()
        mock_filter1 = Mock()
        mock_filter2 = Mock()
        mock_order = Mock()

        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter1
        mock_filter1.filter.return_value = mock_filter2
        mock_filter2.order_by.return_value = mock_order
        mock_order.all.return_value = [mock_lot_active]

        # Act
        result = self.repository.find_by_devis_id(devis_id)

        # Assert
        assert len(result) == 1
        assert result[0].id == 1
        # Vérifier que le filtre deleted_at.is_(None) a été appliqué
        assert mock_filter1.filter.called

    def test_find_by_devis_id_ordered_by_ordre_and_code(self):
        """Test: find_by_devis_id retourne les lots triés par ordre et code."""
        # Arrange
        devis_id = uuid4()
        mock_lot1 = LotBudgetaireModel(
            id=1,
            devis_id=str(devis_id),
            code_lot="GO-01",
            libelle="Gros oeuvre",
            unite="m2",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
            ordre=1,
            deleted_at=None,
        )
        mock_lot2 = LotBudgetaireModel(
            id=2,
            devis_id=str(devis_id),
            code_lot="GO-02",
            libelle="Fondations",
            unite="m2",
            quantite_prevue=Decimal("80"),
            prix_unitaire_ht=Decimal("60"),
            ordre=1,
            deleted_at=None,
        )

        # Mock de la query SQLAlchemy
        mock_query = Mock()
        mock_filter1 = Mock()
        mock_filter2 = Mock()
        mock_order = Mock()

        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter1
        mock_filter1.filter.return_value = mock_filter2
        mock_filter2.order_by.return_value = mock_order
        mock_order.all.return_value = [mock_lot1, mock_lot2]

        # Act
        result = self.repository.find_by_devis_id(devis_id)

        # Assert
        assert len(result) == 2
        # Vérifier que order_by a été appelé
        assert mock_filter2.order_by.called


class TestCountByDevisId:
    """Tests pour la méthode count_by_devis_id du repository."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_session = Mock()
        self.repository = SQLAlchemyLotBudgetaireRepository(self.mock_session)

    def test_count_by_devis_id_with_lots(self):
        """Test: count_by_devis_id retourne le nombre de lots."""
        # Arrange
        devis_id = uuid4()

        # Mock de la query SQLAlchemy
        mock_query = Mock()
        mock_filter1 = Mock()
        mock_filter2 = Mock()

        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter1
        mock_filter1.filter.return_value = mock_filter2
        mock_filter2.count.return_value = 5

        # Act
        result = self.repository.count_by_devis_id(devis_id)

        # Assert
        assert result == 5
        self.mock_session.query.assert_called_once()
        mock_filter2.count.assert_called_once()

    def test_count_by_devis_id_with_no_lots(self):
        """Test: count_by_devis_id retourne 0 si pas de lots."""
        # Arrange
        devis_id = uuid4()

        # Mock de la query SQLAlchemy
        mock_query = Mock()
        mock_filter1 = Mock()
        mock_filter2 = Mock()

        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter1
        mock_filter1.filter.return_value = mock_filter2
        mock_filter2.count.return_value = 0

        # Act
        result = self.repository.count_by_devis_id(devis_id)

        # Assert
        assert result == 0

    def test_count_by_devis_id_excludes_deleted(self):
        """Test: count_by_devis_id exclut les lots supprimés."""
        # Arrange
        devis_id = uuid4()

        # Mock de la query SQLAlchemy
        mock_query = Mock()
        mock_filter1 = Mock()
        mock_filter2 = Mock()

        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter1
        mock_filter1.filter.return_value = mock_filter2
        mock_filter2.count.return_value = 3

        # Act
        result = self.repository.count_by_devis_id(devis_id)

        # Assert
        assert result == 3
        # Vérifier que le filtre deleted_at.is_(None) a été appliqué
        assert mock_filter1.filter.called
