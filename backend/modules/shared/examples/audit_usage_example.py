"""Exemples d'utilisation du module Audit.

Ce fichier montre comment utiliser le module audit dans différents contextes.

IMPORTANT: Ce fichier est un exemple, pas du code de production.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

# ──────────────────────────────────────────────────────────────────────────────
# Exemple 1: Utilisation dans un Use Case (backend)
# ──────────────────────────────────────────────────────────────────────────────


class UpdateDevisUseCase:
    """Exemple d'un use case utilisant le service d'audit."""

    def __init__(self, devis_repo, audit_service):
        self.devis_repo = devis_repo
        self.audit_service = audit_service

    def execute(self, devis_id: str, new_montant_ht: Decimal, user_id: int, user_name: str):
        """Met à jour le montant d'un devis et enregistre dans l'audit trail."""
        # 1. Récupérer le devis existant
        devis = self.devis_repo.find_by_id(devis_id)
        if not devis:
            raise ValueError(f"Devis {devis_id} non trouvé")

        # 2. Sauvegarder l'ancienne valeur
        old_montant = devis.montant_ht

        # 3. Effectuer la modification
        devis.montant_ht = new_montant_ht
        updated_devis = self.devis_repo.save(devis)

        # 4. Enregistrer dans l'audit trail
        self.audit_service.log_update(
            entity_type="devis",
            entity_id=str(devis.id),
            field_name="montant_ht",
            old_value=old_montant,
            new_value=new_montant_ht,
            author_id=user_id,
            author_name=user_name,
            motif="Révision suite demande client",
            metadata={"chantier_id": devis.chantier_id},
        )

        return updated_devis


# ──────────────────────────────────────────────────────────────────────────────
# Exemple 2: Enregistrement de différents types d'actions
# ──────────────────────────────────────────────────────────────────────────────


def example_audit_actions(audit_service):
    """Exemples d'enregistrement de différentes actions."""

    # Action 1: Création d'un devis
    audit_service.log_creation(
        entity_type="devis",
        entity_id=str(uuid4()),
        author_id=1,
        author_name="Jean Dupont",
        new_value={
            "numero": "DEV-2026-001",
            "montant_ht": 10000.00,
            "statut": "brouillon",
        },
        motif="Nouveau devis pour rénovation bureau",
    )

    # Action 2: Modification d'un champ
    audit_service.log_update(
        entity_type="lot_budgetaire",
        entity_id="123",
        field_name="montant_prevu_ht",
        old_value=Decimal("8500.00"),
        new_value=Decimal("9200.00"),
        author_id=1,
        author_name="Jean Dupont",
        motif="Ajustement suite avenant #4",
        metadata={"avenant_id": 4},
    )

    # Action 3: Changement de statut
    audit_service.log_status_change(
        entity_type="devis",
        entity_id=str(uuid4()),
        old_status="brouillon",
        new_status="valide",
        author_id=2,
        author_name="Marie Martin",
        motif="Validation après révision technique",
    )

    # Action 4: Suppression
    audit_service.log_deletion(
        entity_type="achat",
        entity_id="789",
        author_id=1,
        author_name="Jean Dupont",
        old_value={"montant_ht": 1500.00, "fournisseur": "ABC Matériaux"},
        motif="Commande annulée par le fournisseur",
    )

    # Action 5: Action personnalisée
    audit_service.log(
        entity_type="devis",
        entity_id=str(uuid4()),
        action="signed",
        author_id=3,
        author_name="Client ABC",
        motif="Signature électronique devis",
        metadata={
            "ip_address": "192.168.1.100",
            "signature_timestamp": datetime.utcnow().isoformat(),
        },
    )


# ──────────────────────────────────────────────────────────────────────────────
# Exemple 3: Consultation de l'historique
# ──────────────────────────────────────────────────────────────────────────────


def example_query_history(audit_service, devis_id: str):
    """Exemples de consultation de l'historique."""

    # Récupérer l'historique complet d'un devis
    response = audit_service.get_history(
        entity_type="devis",
        entity_id=devis_id,
        limit=50,
        offset=0,
    )

    print(f"Historique du devis {devis_id}:")
    print(f"  Total: {response.total} entrées")
    print(f"  Affichées: {len(response.entries)}")
    print(f"  Encore des entrées? {response.has_more}")

    for entry in response.entries:
        print(f"  - {entry.timestamp} | {entry.action} | par {entry.author_name}")
        if entry.field_name:
            print(f"    Champ: {entry.field_name}")
            print(f"    Avant: {entry.old_value}")
            print(f"    Après: {entry.new_value}")
        if entry.motif:
            print(f"    Motif: {entry.motif}")


def example_query_user_actions(audit_service, user_id: int):
    """Exemples de consultation des actions d'un utilisateur."""

    # Actions des 7 derniers jours
    end = datetime.utcnow()
    start = end - timedelta(days=7)

    actions = audit_service.get_user_actions(
        author_id=user_id,
        start_date=start,
        end_date=end,
        entity_type="devis",
        limit=100,
    )

    print(f"Actions de l'utilisateur {user_id} sur les devis (7 derniers jours):")
    for action in actions:
        print(f"  - {action.timestamp} | {action.action} | Devis {action.entity_id}")


def example_query_recent_entries(audit_service):
    """Exemples de feed d'activité récent."""

    # 10 dernières créations de devis
    recent_devis = audit_service.get_recent_entries(
        entity_type="devis",
        action="created",
        limit=10,
    )

    print("Derniers devis créés:")
    for entry in recent_devis:
        print(f"  - Devis {entry.entity_id} créé par {entry.author_name} le {entry.timestamp}")


def example_search_audit(audit_service):
    """Exemples de recherche avancée."""

    # Toutes les modifications de devis en janvier 2026
    response = audit_service.search(
        entity_type="devis",
        action="updated",
        start_date=datetime(2026, 1, 1),
        end_date=datetime(2026, 1, 31, 23, 59, 59),
        limit=100,
        offset=0,
    )

    print(f"Modifications de devis en janvier 2026: {response.total}")

    # Toutes les actions d'un utilisateur spécifique sur un devis spécifique
    response = audit_service.search(
        entity_type="devis",
        entity_id="550e8400-e29b-41d4-a716-446655440000",
        author_id=1,
        limit=50,
    )

    print(f"Actions de l'utilisateur 1 sur ce devis: {response.total}")


# ──────────────────────────────────────────────────────────────────────────────
# Exemple 4: Utilisation avec FastAPI (injection de dépendances)
# ──────────────────────────────────────────────────────────────────────────────


"""
from fastapi import APIRouter, Depends
from modules.shared.infrastructure.web.dependencies import get_audit_service

router = APIRouter()

@router.get("/devis/{devis_id}/history")
def get_devis_history(
    devis_id: str,
    limit: int = 50,
    offset: int = 0,
    audit_service = Depends(get_audit_service),
):
    '''Récupère l'historique d'un devis.'''
    response = audit_service.get_history(
        entity_type="devis",
        entity_id=devis_id,
        limit=limit,
        offset=offset,
    )

    return {
        "entries": [
            {
                "id": entry.id,
                "action": entry.action,
                "field_name": entry.field_name,
                "old_value": entry.old_value,
                "new_value": entry.new_value,
                "author_name": entry.author_name,
                "timestamp": entry.timestamp,
                "motif": entry.motif,
            }
            for entry in response.entries
        ],
        "total": response.total,
        "has_more": response.has_more,
    }
"""


# ──────────────────────────────────────────────────────────────────────────────
# Exemple 5: Helper pour diff automatique d'objets
# ──────────────────────────────────────────────────────────────────────────────


def log_entity_changes(audit_service, entity_type: str, entity_id: str, old_entity, new_entity, user_id: int, user_name: str):
    """
    Helper pour enregistrer automatiquement toutes les modifications entre deux versions d'une entité.

    Args:
        audit_service: Service d'audit
        entity_type: Type de l'entité
        entity_id: ID de l'entité
        old_entity: Version avant modification
        new_entity: Version après modification
        user_id: ID utilisateur
        user_name: Nom utilisateur
    """
    # Récupérer tous les champs de l'entité
    old_dict = old_entity.__dict__ if hasattr(old_entity, "__dict__") else old_entity
    new_dict = new_entity.__dict__ if hasattr(new_entity, "__dict__") else new_entity

    # Comparer et enregistrer les différences
    for field_name, new_value in new_dict.items():
        # Ignorer les champs système
        if field_name.startswith("_"):
            continue

        old_value = old_dict.get(field_name)

        # Si la valeur a changé
        if old_value != new_value:
            audit_service.log_update(
                entity_type=entity_type,
                entity_id=entity_id,
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                author_id=user_id,
                author_name=user_name,
            )


# ──────────────────────────────────────────────────────────────────────────────
# Exemple 6: Intégration dans un Domain Event Handler
# ──────────────────────────────────────────────────────────────────────────────


"""
from modules.shared.domain.events import DomainEvent

class DevisValidatedEvent(DomainEvent):
    '''Event déclenché quand un devis est validé.'''
    def __init__(self, devis_id: str, montant_ht: Decimal, user_id: int, user_name: str):
        super().__init__()
        self.devis_id = devis_id
        self.montant_ht = montant_ht
        self.user_id = user_id
        self.user_name = user_name


class AuditEventHandler:
    '''Handler qui enregistre les events dans l'audit trail.'''

    def __init__(self, audit_service):
        self.audit_service = audit_service

    def handle_devis_validated(self, event: DevisValidatedEvent):
        '''Enregistre la validation du devis dans l'audit.'''
        self.audit_service.log(
            entity_type="devis",
            entity_id=event.devis_id,
            action="validated",
            author_id=event.user_id,
            author_name=event.user_name,
            metadata={
                "montant_ht": str(event.montant_ht),
                "event_timestamp": event.occurred_at.isoformat(),
            },
        )
"""


# ──────────────────────────────────────────────────────────────────────────────
# Point d'entrée pour tester les exemples
# ──────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    print("Ce fichier contient des exemples d'utilisation du module Audit.")
    print("Consultez le code source pour voir les différents exemples.")
    print("Pour utiliser le module Audit dans votre code, importez:")
    print("  from modules.shared.application.services.audit_service import AuditService")
    print("  from modules.shared.infrastructure.web.dependencies import get_audit_service")
