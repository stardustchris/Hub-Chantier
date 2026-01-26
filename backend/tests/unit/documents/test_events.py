"""Tests unitaires pour les événements du module Documents."""

import pytest
from datetime import datetime
from dataclasses import FrozenInstanceError

from modules.documents.domain.events.document_events import (
    DocumentEvent,
    DocumentUploaded,
    DocumentDeleted,
    DocumentMoved,
    DocumentRenamed,
    DossierEvent,
    DossierCreated,
    DossierDeleted,
    AutorisationEvent,
    AutorisationAccordee,
    AutorisationRevoquee,
)


class TestDocumentEvent:
    """Tests pour DocumentEvent."""

    def test_create_document_event(self):
        """Test création événement document."""
        now = datetime.now()
        event = DocumentEvent(
            document_id=1,
            chantier_id=2,
            timestamp=now,
        )

        assert event.document_id == 1
        assert event.chantier_id == 2
        assert event.timestamp == now

    def test_document_event_is_frozen(self):
        """Test que l'événement est immuable."""
        event = DocumentEvent(
            document_id=1,
            chantier_id=2,
            timestamp=datetime.now(),
        )

        with pytest.raises(FrozenInstanceError):
            event.document_id = 10

    def test_document_event_equality(self):
        """Test égalité des événements."""
        now = datetime.now()
        event1 = DocumentEvent(document_id=1, chantier_id=2, timestamp=now)
        event2 = DocumentEvent(document_id=1, chantier_id=2, timestamp=now)

        assert event1 == event2

    def test_document_event_inequality(self):
        """Test inégalité des événements."""
        now = datetime.now()
        event1 = DocumentEvent(document_id=1, chantier_id=2, timestamp=now)
        event2 = DocumentEvent(document_id=2, chantier_id=2, timestamp=now)

        assert event1 != event2


class TestDocumentUploaded:
    """Tests pour DocumentUploaded."""

    def test_create_document_uploaded(self):
        """Test création événement upload."""
        now = datetime.now()
        event = DocumentUploaded(
            document_id=1,
            chantier_id=2,
            timestamp=now,
            nom="rapport.pdf",
            dossier_id=3,
            uploaded_by=4,
            taille=1024,
        )

        assert event.document_id == 1
        assert event.chantier_id == 2
        assert event.nom == "rapport.pdf"
        assert event.dossier_id == 3
        assert event.uploaded_by == 4
        assert event.taille == 1024

    def test_document_uploaded_inherits_from_document_event(self):
        """Test que DocumentUploaded hérite de DocumentEvent."""
        event = DocumentUploaded(
            document_id=1,
            chantier_id=2,
            timestamp=datetime.now(),
            nom="test.pdf",
            dossier_id=3,
            uploaded_by=4,
            taille=512,
        )

        assert isinstance(event, DocumentEvent)

    def test_document_uploaded_is_frozen(self):
        """Test que l'événement est immuable."""
        event = DocumentUploaded(
            document_id=1,
            chantier_id=2,
            timestamp=datetime.now(),
            nom="test.pdf",
            dossier_id=3,
            uploaded_by=4,
            taille=512,
        )

        with pytest.raises(FrozenInstanceError):
            event.nom = "autre.pdf"


class TestDocumentDeleted:
    """Tests pour DocumentDeleted."""

    def test_create_document_deleted(self):
        """Test création événement suppression."""
        now = datetime.now()
        event = DocumentDeleted(
            document_id=1,
            chantier_id=2,
            timestamp=now,
            nom="ancien.pdf",
            deleted_by=5,
        )

        assert event.document_id == 1
        assert event.chantier_id == 2
        assert event.nom == "ancien.pdf"
        assert event.deleted_by == 5

    def test_document_deleted_inherits_from_document_event(self):
        """Test que DocumentDeleted hérite de DocumentEvent."""
        event = DocumentDeleted(
            document_id=1,
            chantier_id=2,
            timestamp=datetime.now(),
            nom="test.pdf",
            deleted_by=5,
        )

        assert isinstance(event, DocumentEvent)


class TestDocumentMoved:
    """Tests pour DocumentMoved."""

    def test_create_document_moved(self):
        """Test création événement déplacement."""
        now = datetime.now()
        event = DocumentMoved(
            document_id=1,
            chantier_id=2,
            timestamp=now,
            ancien_dossier_id=10,
            nouveau_dossier_id=20,
            moved_by=3,
        )

        assert event.document_id == 1
        assert event.ancien_dossier_id == 10
        assert event.nouveau_dossier_id == 20
        assert event.moved_by == 3

    def test_document_moved_inherits_from_document_event(self):
        """Test que DocumentMoved hérite de DocumentEvent."""
        event = DocumentMoved(
            document_id=1,
            chantier_id=2,
            timestamp=datetime.now(),
            ancien_dossier_id=10,
            nouveau_dossier_id=20,
            moved_by=3,
        )

        assert isinstance(event, DocumentEvent)


class TestDocumentRenamed:
    """Tests pour DocumentRenamed."""

    def test_create_document_renamed(self):
        """Test création événement renommage."""
        now = datetime.now()
        event = DocumentRenamed(
            document_id=1,
            chantier_id=2,
            timestamp=now,
            ancien_nom="old.pdf",
            nouveau_nom="new.pdf",
            renamed_by=4,
        )

        assert event.document_id == 1
        assert event.ancien_nom == "old.pdf"
        assert event.nouveau_nom == "new.pdf"
        assert event.renamed_by == 4

    def test_document_renamed_inherits_from_document_event(self):
        """Test que DocumentRenamed hérite de DocumentEvent."""
        event = DocumentRenamed(
            document_id=1,
            chantier_id=2,
            timestamp=datetime.now(),
            ancien_nom="old.pdf",
            nouveau_nom="new.pdf",
            renamed_by=4,
        )

        assert isinstance(event, DocumentEvent)


class TestDossierEvent:
    """Tests pour DossierEvent."""

    def test_create_dossier_event(self):
        """Test création événement dossier."""
        now = datetime.now()
        event = DossierEvent(
            dossier_id=1,
            chantier_id=2,
            timestamp=now,
        )

        assert event.dossier_id == 1
        assert event.chantier_id == 2
        assert event.timestamp == now

    def test_dossier_event_is_frozen(self):
        """Test que l'événement est immuable."""
        event = DossierEvent(
            dossier_id=1,
            chantier_id=2,
            timestamp=datetime.now(),
        )

        with pytest.raises(FrozenInstanceError):
            event.dossier_id = 10


class TestDossierCreated:
    """Tests pour DossierCreated."""

    def test_create_dossier_created(self):
        """Test création événement création dossier."""
        now = datetime.now()
        event = DossierCreated(
            dossier_id=1,
            chantier_id=2,
            timestamp=now,
            nom="Plans",
            parent_id=None,
            created_by=3,
        )

        assert event.dossier_id == 1
        assert event.nom == "Plans"
        assert event.parent_id is None
        assert event.created_by == 3

    def test_create_dossier_created_with_parent(self):
        """Test création événement avec parent."""
        event = DossierCreated(
            dossier_id=1,
            chantier_id=2,
            timestamp=datetime.now(),
            nom="Sous-dossier",
            parent_id=10,
            created_by=3,
        )

        assert event.parent_id == 10

    def test_dossier_created_inherits_from_dossier_event(self):
        """Test que DossierCreated hérite de DossierEvent."""
        event = DossierCreated(
            dossier_id=1,
            chantier_id=2,
            timestamp=datetime.now(),
            nom="Test",
            parent_id=None,
            created_by=3,
        )

        assert isinstance(event, DossierEvent)


class TestDossierDeleted:
    """Tests pour DossierDeleted."""

    def test_create_dossier_deleted(self):
        """Test création événement suppression dossier."""
        now = datetime.now()
        event = DossierDeleted(
            dossier_id=1,
            chantier_id=2,
            timestamp=now,
            nom="Ancien dossier",
            deleted_by=5,
        )

        assert event.dossier_id == 1
        assert event.nom == "Ancien dossier"
        assert event.deleted_by == 5

    def test_dossier_deleted_inherits_from_dossier_event(self):
        """Test que DossierDeleted hérite de DossierEvent."""
        event = DossierDeleted(
            dossier_id=1,
            chantier_id=2,
            timestamp=datetime.now(),
            nom="Test",
            deleted_by=5,
        )

        assert isinstance(event, DossierEvent)


class TestAutorisationEvent:
    """Tests pour AutorisationEvent."""

    def test_create_autorisation_event(self):
        """Test création événement autorisation."""
        now = datetime.now()
        event = AutorisationEvent(
            autorisation_id=1,
            timestamp=now,
        )

        assert event.autorisation_id == 1
        assert event.timestamp == now

    def test_autorisation_event_is_frozen(self):
        """Test que l'événement est immuable."""
        event = AutorisationEvent(
            autorisation_id=1,
            timestamp=datetime.now(),
        )

        with pytest.raises(FrozenInstanceError):
            event.autorisation_id = 10


class TestAutorisationAccordee:
    """Tests pour AutorisationAccordee."""

    def test_create_autorisation_accordee(self):
        """Test création événement autorisation accordée."""
        now = datetime.now()
        event = AutorisationAccordee(
            autorisation_id=1,
            timestamp=now,
            user_id=2,
            cible_type="dossier",
            cible_id=3,
            accorde_par=4,
        )

        assert event.autorisation_id == 1
        assert event.user_id == 2
        assert event.cible_type == "dossier"
        assert event.cible_id == 3
        assert event.accorde_par == 4

    def test_autorisation_accordee_document(self):
        """Test événement autorisation sur document."""
        event = AutorisationAccordee(
            autorisation_id=1,
            timestamp=datetime.now(),
            user_id=2,
            cible_type="document",
            cible_id=5,
            accorde_par=4,
        )

        assert event.cible_type == "document"
        assert event.cible_id == 5

    def test_autorisation_accordee_inherits_from_autorisation_event(self):
        """Test que AutorisationAccordee hérite de AutorisationEvent."""
        event = AutorisationAccordee(
            autorisation_id=1,
            timestamp=datetime.now(),
            user_id=2,
            cible_type="dossier",
            cible_id=3,
            accorde_par=4,
        )

        assert isinstance(event, AutorisationEvent)


class TestAutorisationRevoquee:
    """Tests pour AutorisationRevoquee."""

    def test_create_autorisation_revoquee(self):
        """Test création événement autorisation révoquée."""
        now = datetime.now()
        event = AutorisationRevoquee(
            autorisation_id=1,
            timestamp=now,
            user_id=2,
            cible_type="dossier",
            cible_id=3,
            revoque_par=5,
        )

        assert event.autorisation_id == 1
        assert event.user_id == 2
        assert event.cible_type == "dossier"
        assert event.cible_id == 3
        assert event.revoque_par == 5

    def test_autorisation_revoquee_inherits_from_autorisation_event(self):
        """Test que AutorisationRevoquee hérite de AutorisationEvent."""
        event = AutorisationRevoquee(
            autorisation_id=1,
            timestamp=datetime.now(),
            user_id=2,
            cible_type="document",
            cible_id=3,
            revoque_par=5,
        )

        assert isinstance(event, AutorisationEvent)
