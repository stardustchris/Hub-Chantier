"""Tests unitaires pour le gel financier (GAP #5).

Verifie que la fonction _check_chantier_not_closed interdit les
operations financieres sur un chantier ferme.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from fastapi import HTTPException

from modules.chantiers.domain.value_objects.statut_chantier import (
    StatutChantier,
)
from modules.financier.infrastructure.web.financier_routes import (
    _check_chantier_not_closed,
)


class TestCheckChantierNotClosed:
    """Tests pour le helper _check_chantier_not_closed."""

    @patch(
        "modules.chantiers.infrastructure.persistence.SQLAlchemyChantierRepository"
    )
    def test_chantier_ferme_raises_403(self, MockRepo):
        """Test GAP #5: un chantier ferme leve HTTPException 403."""
        # Arrange
        mock_chantier = MagicMock()
        mock_chantier.statut = StatutChantier.ferme()
        MockRepo.return_value.find_by_id.return_value = mock_chantier

        mock_db = MagicMock()

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            _check_chantier_not_closed(chantier_id=1, db=mock_db)

        assert exc_info.value.status_code == 403
        assert "ferme" in exc_info.value.detail.lower()

    @patch(
        "modules.chantiers.infrastructure.persistence.SQLAlchemyChantierRepository"
    )
    def test_chantier_ouvert_passes(self, MockRepo):
        """Test GAP #5: un chantier ouvert ne leve pas d'exception."""
        # Arrange
        mock_chantier = MagicMock()
        mock_chantier.statut = StatutChantier.ouvert()
        MockRepo.return_value.find_by_id.return_value = mock_chantier

        mock_db = MagicMock()

        # Act - ne doit pas lever d'exception
        _check_chantier_not_closed(chantier_id=1, db=mock_db)

    @patch(
        "modules.chantiers.infrastructure.persistence.SQLAlchemyChantierRepository"
    )
    def test_chantier_en_cours_passes(self, MockRepo):
        """Test GAP #5: un chantier en_cours ne leve pas d'exception."""
        # Arrange
        mock_chantier = MagicMock()
        mock_chantier.statut = StatutChantier.en_cours()
        MockRepo.return_value.find_by_id.return_value = mock_chantier

        mock_db = MagicMock()

        # Act - ne doit pas lever d'exception
        _check_chantier_not_closed(chantier_id=1, db=mock_db)

    @patch(
        "modules.chantiers.infrastructure.persistence.SQLAlchemyChantierRepository"
    )
    def test_chantier_receptionne_passes(self, MockRepo):
        """Test GAP #5: un chantier receptionne ne leve pas d'exception.

        Un chantier receptionne peut encore avoir des operations financieres
        (dernieres factures, etc.).
        """
        # Arrange
        mock_chantier = MagicMock()
        mock_chantier.statut = StatutChantier.receptionne()
        MockRepo.return_value.find_by_id.return_value = mock_chantier

        mock_db = MagicMock()

        # Act - ne doit pas lever d'exception
        _check_chantier_not_closed(chantier_id=1, db=mock_db)

    @patch(
        "modules.chantiers.infrastructure.persistence.SQLAlchemyChantierRepository"
    )
    def test_chantier_not_found_passes(self, MockRepo):
        """Test GAP #5: chantier non trouve ne leve pas d'exception.

        Si le chantier n'existe pas dans le repo, on ne bloque pas
        (la validation sera faite par le use case en aval).
        """
        # Arrange
        MockRepo.return_value.find_by_id.return_value = None

        mock_db = MagicMock()

        # Act - ne doit pas lever d'exception
        _check_chantier_not_closed(chantier_id=999, db=mock_db)
