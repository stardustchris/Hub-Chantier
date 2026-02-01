"""Tests unitaires pour l'entite JournalDevis.

DEV-18: Historique modifications - Journal complet des changements.
"""

import pytest
from datetime import datetime

from modules.devis.domain.entities.journal_devis import JournalDevis


class TestJournalDevisCreation:
    """Tests pour la creation d'une entree de journal."""

    def test_create_journal_valid(self):
        """Test: creation d'une entree de journal valide."""
        now = datetime.utcnow()
        entry = JournalDevis(
            id=1,
            devis_id=10,
            action="creation",
            auteur_id=5,
            details_json={"message": "Devis cree"},
            created_at=now,
        )
        assert entry.id == 1
        assert entry.devis_id == 10
        assert entry.action == "creation"
        assert entry.auteur_id == 5
        assert entry.details_json == {"message": "Devis cree"}
        assert entry.created_at == now

    def test_create_journal_minimal(self):
        """Test: creation d'une entree avec le minimum requis."""
        entry = JournalDevis(
            devis_id=1,
            action="modification",
            auteur_id=1,
        )
        assert entry.devis_id == 1
        assert entry.action == "modification"
        assert entry.auteur_id == 1
        assert entry.details_json is None

    def test_create_journal_devis_id_zero(self):
        """Test: erreur si devis_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            JournalDevis(devis_id=0, action="test", auteur_id=1)
        assert "devis" in str(exc_info.value).lower()

    def test_create_journal_devis_id_negatif(self):
        """Test: erreur si devis_id est negatif."""
        with pytest.raises(ValueError):
            JournalDevis(devis_id=-1, action="test", auteur_id=1)

    def test_create_journal_action_vide(self):
        """Test: erreur si action vide."""
        with pytest.raises(ValueError) as exc_info:
            JournalDevis(devis_id=1, action="", auteur_id=1)
        assert "action" in str(exc_info.value).lower()

    def test_create_journal_action_espaces(self):
        """Test: erreur si action uniquement espaces."""
        with pytest.raises(ValueError):
            JournalDevis(devis_id=1, action="   ", auteur_id=1)

    def test_create_journal_auteur_id_zero(self):
        """Test: erreur si auteur_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            JournalDevis(devis_id=1, action="test", auteur_id=0)
        assert "auteur" in str(exc_info.value).lower()

    def test_create_journal_auteur_id_negatif(self):
        """Test: erreur si auteur_id est negatif."""
        with pytest.raises(ValueError):
            JournalDevis(devis_id=1, action="test", auteur_id=-1)


class TestJournalDevisActions:
    """Tests pour les differentes actions du journal."""

    def test_action_creation(self):
        """Test: entree de journal pour creation."""
        entry = JournalDevis(
            devis_id=1,
            action="creation",
            auteur_id=1,
            details_json={"numero": "DEV-2026-001"},
        )
        assert entry.action == "creation"

    def test_action_modification(self):
        """Test: entree de journal pour modification."""
        entry = JournalDevis(
            devis_id=1,
            action="modification",
            auteur_id=1,
            details_json={"champs": ["client_nom", "objet"]},
        )
        assert entry.action == "modification"

    def test_action_transition_statut(self):
        """Test: entree de journal pour transition de statut."""
        entry = JournalDevis(
            devis_id=1,
            action="transition_statut",
            auteur_id=1,
            details_json={
                "de": "brouillon",
                "vers": "en_validation",
            },
        )
        assert entry.action == "transition_statut"
        assert entry.details_json["de"] == "brouillon"
        assert entry.details_json["vers"] == "en_validation"

    def test_action_suppression(self):
        """Test: entree de journal pour suppression."""
        entry = JournalDevis(
            devis_id=1,
            action="suppression",
            auteur_id=1,
        )
        assert entry.action == "suppression"


class TestJournalDevisToDict:
    """Tests pour la conversion en dictionnaire."""

    def test_to_dict_complet(self):
        """Test: conversion en dictionnaire avec tous les champs."""
        now = datetime.utcnow()
        entry = JournalDevis(
            id=1,
            devis_id=10,
            action="creation",
            auteur_id=5,
            details_json={"numero": "DEV-001"},
            created_at=now,
        )
        d = entry.to_dict()
        assert d["id"] == 1
        assert d["devis_id"] == 10
        assert d["action"] == "creation"
        assert d["auteur_id"] == 5
        assert d["details_json"] == {"numero": "DEV-001"}
        assert d["created_at"] == now.isoformat()

    def test_to_dict_sans_details(self):
        """Test: conversion en dictionnaire sans details_json."""
        entry = JournalDevis(
            id=1,
            devis_id=10,
            action="test",
            auteur_id=1,
        )
        d = entry.to_dict()
        assert d["details_json"] is None

    def test_to_dict_sans_created_at(self):
        """Test: conversion en dictionnaire sans created_at."""
        entry = JournalDevis(
            id=1,
            devis_id=10,
            action="test",
            auteur_id=1,
        )
        d = entry.to_dict()
        assert d["created_at"] is None
