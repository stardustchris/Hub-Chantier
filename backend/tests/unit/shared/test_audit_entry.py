"""Tests unitaires pour l'entité AuditEntry."""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from modules.shared.domain.entities.audit_entry import AuditEntry


class TestAuditEntry:
    """Tests pour l'entité AuditEntry."""

    def test_create_audit_entry_valid(self):
        """Test création d'une entrée d'audit valide."""
        entry = AuditEntry(
            entity_type="devis",
            entity_id="123",
            action="created",
            author_id=1,
            author_name="Jean Dupont",
        )

        assert entry.entity_type == "devis"
        assert entry.entity_id == "123"
        assert entry.action == "created"
        assert entry.author_id == 1
        assert entry.author_name == "Jean Dupont"
        assert isinstance(entry.id, UUID)
        assert isinstance(entry.timestamp, datetime)

    def test_create_audit_entry_with_field_change(self):
        """Test création avec modification de champ."""
        entry = AuditEntry(
            entity_type="devis",
            entity_id="123",
            action="updated",
            field_name="montant_ht",
            old_value="10000.00",
            new_value="12000.00",
            author_id=1,
            author_name="Jean Dupont",
            motif="Révision suite demande client",
        )

        assert entry.field_name == "montant_ht"
        assert entry.old_value == "10000.00"
        assert entry.new_value == "12000.00"
        assert entry.motif == "Révision suite demande client"

    def test_create_audit_entry_with_metadata(self):
        """Test création avec métadonnées."""
        metadata = {"chantier_id": 456, "user_ip": "192.168.1.1"}

        entry = AuditEntry(
            entity_type="devis",
            entity_id="123",
            action="validated",
            author_id=1,
            author_name="Jean Dupont",
            metadata=metadata,
        )

        assert entry.metadata == metadata
        assert entry.metadata["chantier_id"] == 456

    def test_create_audit_entry_empty_entity_type_raises_error(self):
        """Test qu'un entity_type vide lève une erreur."""
        with pytest.raises(ValueError, match="entity_type ne peut pas être vide"):
            AuditEntry(
                entity_type="",
                entity_id="123",
                action="created",
                author_id=1,
                author_name="Jean Dupont",
            )

    def test_create_audit_entry_empty_entity_id_raises_error(self):
        """Test qu'un entity_id vide lève une erreur."""
        with pytest.raises(ValueError, match="entity_id ne peut pas être vide"):
            AuditEntry(
                entity_type="devis",
                entity_id="",
                action="created",
                author_id=1,
                author_name="Jean Dupont",
            )

    def test_create_audit_entry_empty_action_raises_error(self):
        """Test qu'une action vide lève une erreur."""
        with pytest.raises(ValueError, match="action ne peut pas être vide"):
            AuditEntry(
                entity_type="devis",
                entity_id="123",
                action="",
                author_id=1,
                author_name="Jean Dupont",
            )

    def test_create_audit_entry_invalid_author_id_raises_error(self):
        """Test qu'un author_id négatif lève une erreur."""
        with pytest.raises(ValueError, match="author_id doit être un entier positif"):
            AuditEntry(
                entity_type="devis",
                entity_id="123",
                action="created",
                author_id=0,
                author_name="Jean Dupont",
            )

    def test_create_audit_entry_empty_author_name_raises_error(self):
        """Test qu'un author_name vide lève une erreur."""
        with pytest.raises(ValueError, match="author_name ne peut pas être vide"):
            AuditEntry(
                entity_type="devis",
                entity_id="123",
                action="created",
                author_id=1,
                author_name="",
            )

    def test_serialize_value_string(self):
        """Test serialization d'une string."""
        value = "test"
        result = AuditEntry.serialize_value(value)
        assert result == '"test"'

    def test_serialize_value_int(self):
        """Test serialization d'un int."""
        value = 123
        result = AuditEntry.serialize_value(value)
        assert result == "123"

    def test_serialize_value_decimal(self):
        """Test serialization d'un Decimal."""
        value = Decimal("125.50")
        result = AuditEntry.serialize_value(value)
        assert result == "125.50"

    def test_serialize_value_datetime(self):
        """Test serialization d'un datetime."""
        value = datetime(2026, 2, 1, 10, 30, 0)
        result = AuditEntry.serialize_value(value)
        assert result == "2026-02-01T10:30:00"

    def test_serialize_value_none(self):
        """Test serialization de None."""
        result = AuditEntry.serialize_value(None)
        assert result == "null"

    def test_serialize_value_dict(self):
        """Test serialization d'un dict."""
        value = {"key": "value", "count": 42}
        result = AuditEntry.serialize_value(value)
        assert '"key"' in result
        assert '"value"' in result

    def test_factory_create_for_creation(self):
        """Test factory method pour création."""
        entry = AuditEntry.create_for_creation(
            entity_type="devis",
            entity_id="123",
            author_id=1,
            author_name="Jean Dupont",
            new_value={"montant_ht": 10000.00},
            motif="Nouveau devis",
        )

        assert entry.action == "created"
        assert entry.field_name is None
        assert entry.old_value is None
        assert entry.new_value is not None
        assert entry.motif == "Nouveau devis"

    def test_factory_create_for_update(self):
        """Test factory method pour mise à jour."""
        entry = AuditEntry.create_for_update(
            entity_type="devis",
            entity_id="123",
            field_name="montant_ht",
            old_value=10000.00,
            new_value=12000.00,
            author_id=1,
            author_name="Jean Dupont",
            motif="Révision",
        )

        assert entry.action == "updated"
        assert entry.field_name == "montant_ht"
        assert entry.old_value == "10000.0"
        assert entry.new_value == "12000.0"
        assert entry.motif == "Révision"

    def test_factory_create_for_deletion(self):
        """Test factory method pour suppression."""
        entry = AuditEntry.create_for_deletion(
            entity_type="devis",
            entity_id="123",
            author_id=1,
            author_name="Jean Dupont",
            old_value={"montant_ht": 10000.00},
            motif="Annulation devis",
        )

        assert entry.action == "deleted"
        assert entry.field_name is None
        assert entry.old_value is not None
        assert entry.new_value is None
        assert entry.motif == "Annulation devis"

    def test_factory_create_for_status_change(self):
        """Test factory method pour changement de statut."""
        entry = AuditEntry.create_for_status_change(
            entity_type="devis",
            entity_id="123",
            old_status="brouillon",
            new_status="valide",
            author_id=1,
            author_name="Jean Dupont",
            motif="Validation devis",
        )

        assert entry.action == "status_changed"
        assert entry.field_name == "status"
        assert entry.old_value == "brouillon"
        assert entry.new_value == "valide"
        assert entry.motif == "Validation devis"

    def test_equality_based_on_id(self):
        """Test égalité basée sur l'ID."""
        entry1 = AuditEntry(
            entity_type="devis",
            entity_id="123",
            action="created",
            author_id=1,
            author_name="Jean Dupont",
        )

        entry2 = AuditEntry(
            entity_type="devis",
            entity_id="123",
            action="created",
            author_id=1,
            author_name="Jean Dupont",
        )

        # Même ID
        entry2.id = entry1.id
        assert entry1 == entry2

        # ID différents
        entry2.id = UUID("550e8400-e29b-41d4-a716-446655440001")
        assert entry1 != entry2

    def test_hash_based_on_id(self):
        """Test hash basé sur l'ID."""
        entry1 = AuditEntry(
            entity_type="devis",
            entity_id="123",
            action="created",
            author_id=1,
            author_name="Jean Dupont",
        )

        entry2 = AuditEntry(
            entity_type="devis",
            entity_id="123",
            action="created",
            author_id=1,
            author_name="Jean Dupont",
        )

        entry2.id = entry1.id
        assert hash(entry1) == hash(entry2)

    def test_normalization_entity_type(self):
        """Test normalisation du entity_type en minuscules."""
        entry = AuditEntry(
            entity_type="DEVIS",
            entity_id="123",
            action="CREATED",
            author_id=1,
            author_name="Jean Dupont",
        )

        assert entry.entity_type == "devis"
        assert entry.action == "created"
