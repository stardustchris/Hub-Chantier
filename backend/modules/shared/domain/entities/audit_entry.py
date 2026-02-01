"""Entité AuditEntry - Représente une entrée d'audit générique."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
from uuid import UUID, uuid4
import json


@dataclass
class AuditEntry:
    """
    Entité représentant une entrée d'audit générique pour tous les modules.

    Cette entité permet de tracer toutes les modifications effectuées sur
    les entités métier (devis, lots budgétaires, achats, budgets, etc.).

    L'audit trail est essentiel pour :
    - La traçabilité réglementaire (RGPD Article 30)
    - Le suivi des modifications (qui, quand, quoi, pourquoi)
    - L'analyse forensique en cas d'anomalie
    - La conformité avec les audits financiers

    Attributes:
        id: Identifiant unique UUID (compatible cross-module).
        entity_type: Type d'entité modifiée (ex: "devis", "lot_budgetaire", "achat").
        entity_id: ID de l'entité modifiée (string pour support UUID et int).
        action: Action effectuée (ex: "created", "updated", "deleted", "status_changed").
        field_name: Nom du champ modifié (optionnel, None pour création/suppression).
        old_value: Valeur avant modification (JSON serialized, optionnel).
        new_value: Valeur après modification (JSON serialized, optionnel).
        author_id: ID de l'utilisateur ayant effectué l'action.
        author_name: Nom complet de l'utilisateur (dénormalisé pour performance).
        timestamp: Date et heure de l'action (UTC).
        motif: Raison de la modification (optionnel).
        metadata: Métadonnées additionnelles au format dict (optionnel).
    """

    # Champs obligatoires
    entity_type: str
    entity_id: str
    action: str
    author_id: int
    author_name: str

    # Champs optionnels
    id: Optional[UUID] = None
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    motif: Optional[str] = None
    metadata: Optional[dict] = None

    def __post_init__(self) -> None:
        """Valide les données à la création."""
        # Génération UUID si absent
        if self.id is None:
            self.id = uuid4()

        # Validation entity_type
        if not self.entity_type or not self.entity_type.strip():
            raise ValueError("entity_type ne peut pas être vide")

        # Validation entity_id
        if not self.entity_id or not str(self.entity_id).strip():
            raise ValueError("entity_id ne peut pas être vide")

        # Validation action
        if not self.action or not self.action.strip():
            raise ValueError("action ne peut pas être vide")

        # Validation author_id
        if self.author_id <= 0:
            raise ValueError("author_id doit être un entier positif")

        # Validation author_name
        if not self.author_name or not self.author_name.strip():
            raise ValueError("author_name ne peut pas être vide")

        # Normalisation
        self.entity_type = self.entity_type.strip().lower()
        self.action = self.action.strip().lower()

    @staticmethod
    def serialize_value(value: Any) -> str:
        """
        Sérialise une valeur Python en JSON string.

        Cette méthode gère la conversion des types Python complexes
        (datetime, Decimal, UUID, etc.) en JSON.

        Args:
            value: Valeur à sérialiser.

        Returns:
            String JSON représentant la valeur.

        Example:
            >>> AuditEntry.serialize_value(datetime(2026, 2, 1, 10, 30))
            '2026-02-01T10:30:00'
            >>> AuditEntry.serialize_value(Decimal("125.50"))
            '125.50'
        """
        if value is None:
            return "null"

        # Types natifs JSON
        if isinstance(value, (str, int, float, bool)):
            return json.dumps(value, ensure_ascii=False)

        # datetime
        if isinstance(value, datetime):
            return value.isoformat()

        # UUID
        if isinstance(value, UUID):
            return str(value)

        # Decimal
        from decimal import Decimal
        if isinstance(value, Decimal):
            return str(value)

        # Enumération
        if hasattr(value, "value"):
            return json.dumps(value.value, ensure_ascii=False)

        # Dictionnaire ou liste (récursif)
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False, default=str)

        if isinstance(value, (list, tuple)):
            return json.dumps(list(value), ensure_ascii=False, default=str)

        # Fallback : conversion string
        return str(value)

    @staticmethod
    def create_for_creation(
        entity_type: str,
        entity_id: str,
        author_id: int,
        author_name: str,
        new_value: Any = None,
        motif: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> "AuditEntry":
        """
        Factory method pour création d'entité.

        Args:
            entity_type: Type d'entité créée.
            entity_id: ID de l'entité créée.
            author_id: ID de l'auteur.
            author_name: Nom de l'auteur.
            new_value: Valeur initiale de l'entité (optionnel).
            motif: Raison de la création (optionnel).
            metadata: Métadonnées additionnelles (optionnel).

        Returns:
            AuditEntry pour action "created".
        """
        return AuditEntry(
            entity_type=entity_type,
            entity_id=entity_id,
            action="created",
            author_id=author_id,
            author_name=author_name,
            field_name=None,
            old_value=None,
            new_value=AuditEntry.serialize_value(new_value) if new_value else None,
            motif=motif,
            metadata=metadata,
        )

    @staticmethod
    def create_for_update(
        entity_type: str,
        entity_id: str,
        field_name: str,
        old_value: Any,
        new_value: Any,
        author_id: int,
        author_name: str,
        motif: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> "AuditEntry":
        """
        Factory method pour mise à jour d'entité.

        Args:
            entity_type: Type d'entité modifiée.
            entity_id: ID de l'entité modifiée.
            field_name: Nom du champ modifié.
            old_value: Valeur avant modification.
            new_value: Valeur après modification.
            author_id: ID de l'auteur.
            author_name: Nom de l'auteur.
            motif: Raison de la modification (optionnel).
            metadata: Métadonnées additionnelles (optionnel).

        Returns:
            AuditEntry pour action "updated".
        """
        return AuditEntry(
            entity_type=entity_type,
            entity_id=entity_id,
            action="updated",
            field_name=field_name,
            old_value=AuditEntry.serialize_value(old_value),
            new_value=AuditEntry.serialize_value(new_value),
            author_id=author_id,
            author_name=author_name,
            motif=motif,
            metadata=metadata,
        )

    @staticmethod
    def create_for_deletion(
        entity_type: str,
        entity_id: str,
        author_id: int,
        author_name: str,
        old_value: Any = None,
        motif: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> "AuditEntry":
        """
        Factory method pour suppression d'entité.

        Args:
            entity_type: Type d'entité supprimée.
            entity_id: ID de l'entité supprimée.
            author_id: ID de l'auteur.
            author_name: Nom de l'auteur.
            old_value: Valeur avant suppression (optionnel).
            motif: Raison de la suppression (optionnel).
            metadata: Métadonnées additionnelles (optionnel).

        Returns:
            AuditEntry pour action "deleted".
        """
        return AuditEntry(
            entity_type=entity_type,
            entity_id=entity_id,
            action="deleted",
            author_id=author_id,
            author_name=author_name,
            field_name=None,
            old_value=AuditEntry.serialize_value(old_value) if old_value else None,
            new_value=None,
            motif=motif,
            metadata=metadata,
        )

    @staticmethod
    def create_for_status_change(
        entity_type: str,
        entity_id: str,
        old_status: str,
        new_status: str,
        author_id: int,
        author_name: str,
        motif: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> "AuditEntry":
        """
        Factory method pour changement de statut.

        Args:
            entity_type: Type d'entité modifiée.
            entity_id: ID de l'entité modifiée.
            old_status: Statut avant changement.
            new_status: Statut après changement.
            author_id: ID de l'auteur.
            author_name: Nom de l'auteur.
            motif: Raison du changement (optionnel).
            metadata: Métadonnées additionnelles (optionnel).

        Returns:
            AuditEntry pour action "status_changed".
        """
        return AuditEntry(
            entity_type=entity_type,
            entity_id=entity_id,
            action="status_changed",
            field_name="status",
            old_value=old_status,
            new_value=new_status,
            author_id=author_id,
            author_name=author_name,
            motif=motif,
            metadata=metadata,
        )

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID (entité)."""
        if not isinstance(other, AuditEntry):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))

    def __repr__(self) -> str:
        """Représentation string pour debug."""
        return (
            f"<AuditEntry(id={self.id}, entity_type='{self.entity_type}', "
            f"entity_id='{self.entity_id}', action='{self.action}', "
            f"timestamp={self.timestamp})>"
        )
