"""Tests unitaires pour les Use Cases du journal d'audit.

DEV-18: Historique modifications.
Couche Application - journal_use_cases.py
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from modules.devis.domain.entities.journal_devis import JournalDevis
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.journal_use_cases import (
    LogJournalDevisUseCase,
    GetJournalDevisUseCase,
)
from modules.devis.application.dtos.journal_dtos import JournalDevisDTO


def _make_journal(**kwargs):
    """Cree une entree de journal valide."""
    defaults = {
        "id": 1,
        "devis_id": 1,
        "action": "creation",
        "details_json": {"message": "Devis cree"},
        "auteur_id": 1,
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return JournalDevis(**defaults)


class TestLogJournalDevisUseCase:
    """Tests pour l'enregistrement d'entrees de journal."""

    def setup_method(self):
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = LogJournalDevisUseCase(
            journal_repository=self.mock_journal_repo,
        )

    def test_log_journal_success(self):
        """Test: enregistrement reussi."""
        saved_entry = _make_journal()
        self.mock_journal_repo.save.return_value = saved_entry

        result = self.use_case.execute(
            devis_id=1,
            action="creation",
            details="Devis cree",
            auteur_id=1,
        )

        assert isinstance(result, JournalDevisDTO)
        assert result.devis_id == 1
        assert result.action == "creation"
        self.mock_journal_repo.save.assert_called_once()

    def test_log_journal_entry_structure(self):
        """Test: structure de l'entree sauvegardee."""
        self.mock_journal_repo.save.return_value = _make_journal()

        self.use_case.execute(
            devis_id=5,
            action="modification",
            details="Client modifie",
            auteur_id=3,
        )

        journal_saved = self.mock_journal_repo.save.call_args[0][0]
        assert isinstance(journal_saved, JournalDevis)
        assert journal_saved.devis_id == 5
        assert journal_saved.action == "modification"
        assert journal_saved.details_json == {"message": "Client modifie"}
        assert journal_saved.auteur_id == 3
        assert journal_saved.created_at is not None

    def test_log_journal_different_actions(self):
        """Test: differents types d'actions."""
        self.mock_journal_repo.save.return_value = _make_journal(action="suppression")

        result = self.use_case.execute(
            devis_id=1,
            action="suppression",
            details="Devis supprime",
            auteur_id=2,
        )

        assert result.action == "suppression"


class TestGetJournalDevisUseCase:
    """Tests pour la consultation du journal."""

    def setup_method(self):
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = GetJournalDevisUseCase(
            journal_repository=self.mock_journal_repo,
        )

    def test_get_journal_success(self):
        """Test: recuperation avec pagination."""
        entries = [
            _make_journal(id=1, action="creation"),
            _make_journal(id=2, action="modification"),
            _make_journal(id=3, action="soumission"),
        ]
        self.mock_journal_repo.find_by_devis.return_value = entries
        self.mock_journal_repo.count_by_devis.return_value = 3

        result = self.use_case.execute(devis_id=1)

        assert len(result["items"]) == 3
        assert result["total"] == 3
        assert result["limit"] == 100
        assert result["offset"] == 0

    def test_get_journal_empty(self):
        """Test: journal vide pour un devis."""
        self.mock_journal_repo.find_by_devis.return_value = []
        self.mock_journal_repo.count_by_devis.return_value = 0

        result = self.use_case.execute(devis_id=999)

        assert len(result["items"]) == 0
        assert result["total"] == 0

    def test_get_journal_pagination(self):
        """Test: pagination personnalisee."""
        self.mock_journal_repo.find_by_devis.return_value = []
        self.mock_journal_repo.count_by_devis.return_value = 50

        result = self.use_case.execute(devis_id=1, limit=10, offset=20)

        assert result["limit"] == 10
        assert result["offset"] == 20
        self.mock_journal_repo.find_by_devis.assert_called_once_with(
            devis_id=1,
            limit=10,
            offset=20,
        )

    def test_get_journal_returns_dtos(self):
        """Test: les items sont des JournalDevisDTO."""
        entries = [_make_journal()]
        self.mock_journal_repo.find_by_devis.return_value = entries
        self.mock_journal_repo.count_by_devis.return_value = 1

        result = self.use_case.execute(devis_id=1)

        assert len(result["items"]) == 1
        assert isinstance(result["items"][0], JournalDevisDTO)
        assert result["items"][0].details == "Devis cree"

    def test_get_journal_default_pagination(self):
        """Test: pagination par defaut."""
        self.mock_journal_repo.find_by_devis.return_value = []
        self.mock_journal_repo.count_by_devis.return_value = 0

        self.use_case.execute(devis_id=1)

        self.mock_journal_repo.find_by_devis.assert_called_once_with(
            devis_id=1,
            limit=100,
            offset=0,
        )
