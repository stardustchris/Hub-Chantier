# Module Audit - Documentation

## Vue d'ensemble

Le module Audit est un système d'audit trail générique et mutualisé pour tous les modules de Hub Chantier. Il permet de tracer toutes les modifications effectuées sur les entités métier (devis, lots budgétaires, achats, budgets, etc.) avec un enregistrement complet de :

- **Qui** : Utilisateur ayant effectué l'action
- **Quand** : Timestamp précis (UTC)
- **Quoi** : Type d'entité et ID concerné
- **Action** : Type d'action (création, modification, suppression, changement de statut, etc.)
- **Détails** : Valeurs avant/après modification
- **Pourquoi** : Motif de la modification (optionnel)
- **Contexte** : Métadonnées additionnelles (optionnel)

## Architecture

Le module suit strictement la Clean Architecture avec 4 couches :

```
backend/modules/shared/
├── domain/
│   ├── entities/
│   │   └── audit_entry.py          # Entité AuditEntry
│   └── repositories/
│       └── audit_repository.py     # Interface repository
├── application/
│   ├── services/
│   │   └── audit_service.py        # Service applicatif
│   └── dtos/
│       └── audit_dtos.py           # DTOs
├── infrastructure/
│   ├── persistence/
│   │   ├── models.py               # Modèle SQLAlchemy AuditLogModel
│   │   └── sqlalchemy_audit_repository.py  # Implémentation repository
│   └── web/
│       ├── audit_routes.py         # Endpoints REST
│       └── dependencies.py         # Injection de dépendances FastAPI
└── README_AUDIT.md                 # Ce fichier
```

## Caractéristiques

### Table append-only

La table `audit_log` est **append-only** : les entrées ne sont jamais modifiées ou supprimées après création. Cela garantit l'intégrité de l'audit trail.

### Support UUID et int

Le champ `entity_id` est de type `string` pour supporter aussi bien les UUID (module Devis) que les entiers (modules existants).

### Optimisations performance

La table dispose de 8 index optimisés pour les requêtes fréquentes :
- `ix_audit_log_entity_type_entity_id` : Historique entité
- `ix_audit_log_entity_type_timestamp` : Feed d'activité par type
- `ix_audit_log_author_id_timestamp` : Actions utilisateur
- `ix_audit_log_action_timestamp` : Recherche par action
- Index simples sur `entity_type`, `action`, `author_id`, `timestamp`

### Sérialisation automatique

Les valeurs Python complexes (datetime, Decimal, UUID, enum, dict, list) sont automatiquement sérialisées en JSON :

```python
AuditEntry.serialize_value(datetime(2026, 2, 1, 10, 30))  # "2026-02-01T10:30:00"
AuditEntry.serialize_value(Decimal("125.50"))            # "125.50"
AuditEntry.serialize_value({"key": "value"})             # '{"key": "value"}'
```

## Utilisation

### 1. Injection du service

#### Dans un Use Case

```python
from modules.shared.application.services.audit_service import AuditService

class UpdateDevisUseCase:
    def __init__(
        self,
        devis_repo: DevisRepository,
        audit_service: AuditService,
    ):
        self.devis_repo = devis_repo
        self.audit_service = audit_service

    def execute(self, dto: UpdateDevisDTO) -> DevisDTO:
        # Récupérer l'entité existante
        devis = self.devis_repo.find_by_id(dto.devis_id)
        old_montant = devis.montant_ht

        # Effectuer la modification
        devis.montant_ht = dto.new_montant_ht
        updated_devis = self.devis_repo.save(devis)

        # Enregistrer dans l'audit trail
        self.audit_service.log_update(
            entity_type="devis",
            entity_id=str(devis.id),
            field_name="montant_ht",
            old_value=old_montant,
            new_value=dto.new_montant_ht,
            author_id=dto.user_id,
            author_name=dto.user_name,
            motif="Révision suite demande client",
        )

        return DevisDTO.from_entity(updated_devis)
```

#### Dans un endpoint FastAPI

```python
from fastapi import Depends
from modules.shared.infrastructure.web.dependencies import get_audit_service

@router.get("/audit/history/devis/{devis_id}")
def get_devis_history(
    devis_id: str,
    service: AuditService = Depends(get_audit_service),
):
    return service.get_history(
        entity_type="devis",
        entity_id=devis_id,
        limit=50,
    )
```

### 2. Enregistrement d'entrées d'audit

#### Création d'entité

```python
audit_service.log_creation(
    entity_type="devis",
    entity_id="550e8400-e29b-41d4-a716-446655440000",
    author_id=1,
    author_name="Jean Dupont",
    new_value={"montant_ht": 10000.00, "statut": "brouillon"},
    motif="Nouveau devis pour client ABC",
)
```

#### Modification de champ

```python
audit_service.log_update(
    entity_type="lot_budgetaire",
    entity_id="123",
    field_name="montant_prevu_ht",
    old_value=Decimal("8500.00"),
    new_value=Decimal("9200.00"),
    author_id=1,
    author_name="Jean Dupont",
    motif="Ajustement suite avenant",
    metadata={"avenant_id": 456},
)
```

#### Suppression d'entité

```python
audit_service.log_deletion(
    entity_type="achat",
    entity_id="789",
    author_id=1,
    author_name="Jean Dupont",
    old_value={"montant_ht": 1500.00, "fournisseur_id": 42},
    motif="Commande annulée par le fournisseur",
)
```

#### Changement de statut

```python
audit_service.log_status_change(
    entity_type="devis",
    entity_id="550e8400-e29b-41d4-a716-446655440000",
    old_status="brouillon",
    new_status="valide",
    author_id=1,
    author_name="Jean Dupont",
    motif="Validation après révision",
)
```

#### Enregistrement générique

```python
audit_service.log(
    entity_type="devis",
    entity_id="550e8400-e29b-41d4-a716-446655440000",
    action="validated",
    author_id=1,
    author_name="Jean Dupont",
    motif="Devis validé par la direction",
    metadata={"validation_level": "direction", "montant_ht": 45000.00},
)
```

### 3. Consultation de l'historique

#### Historique complet d'une entité

```python
response = audit_service.get_history(
    entity_type="devis",
    entity_id="550e8400-e29b-41d4-a716-446655440000",
    limit=50,
    offset=0,
)

print(f"Total: {response.total} entrées")
print(f"Affichées: {len(response.entries)}")
print(f"Encore des entrées? {response.has_more}")

for entry in response.entries:
    print(f"{entry.timestamp} - {entry.action} par {entry.author_name}")
```

#### Actions d'un utilisateur

```python
from datetime import datetime, timedelta

end = datetime.utcnow()
start = end - timedelta(days=7)

actions = audit_service.get_user_actions(
    author_id=1,
    start_date=start,
    end_date=end,
    entity_type="devis",
    limit=100,
)

print(f"L'utilisateur a effectué {len(actions)} actions sur des devis cette semaine")
```

#### Feed d'activité récent

```python
recent = audit_service.get_recent_entries(
    entity_type="devis",
    action="created",
    limit=10,
)

for entry in recent:
    print(f"Nouveau devis {entry.entity_id} créé par {entry.author_name}")
```

#### Recherche avancée

```python
response = audit_service.search(
    entity_type="devis",
    action="updated",
    author_id=1,
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 1, 31),
    limit=100,
    offset=0,
)

print(f"Trouvé {response.total} modifications de devis en janvier")
```

## Endpoints REST

Le module expose 4 endpoints REST :

### GET /api/audit/history/{entity_type}/{entity_id}

Récupère l'historique d'une entité.

**Paramètres :**
- `entity_type` (path) : Type d'entité (ex: "devis", "lot_budgetaire")
- `entity_id` (path) : ID de l'entité
- `limit` (query, optionnel) : Nombre maximum d'entrées (défaut: 50, max: 200)
- `offset` (query, optionnel) : Décalage pour pagination (défaut: 0)

**Exemple :**
```bash
GET /api/audit/history/devis/550e8400-e29b-41d4-a716-446655440000?limit=20
```

### GET /api/audit/user/{user_id}

Récupère les actions d'un utilisateur.

**Paramètres :**
- `user_id` (path) : ID de l'utilisateur
- `start_date` (query, optionnel) : Date de début (ISO 8601)
- `end_date` (query, optionnel) : Date de fin (ISO 8601)
- `entity_type` (query, optionnel) : Filtrer par type d'entité
- `limit` (query, optionnel) : Nombre maximum d'entrées (défaut: 100, max: 500)
- `offset` (query, optionnel) : Décalage pour pagination

**Exemple :**
```bash
GET /api/audit/user/1?entity_type=devis&start_date=2026-01-01T00:00:00Z&limit=50
```

### GET /api/audit/recent

Récupère les entrées d'audit récentes.

**Paramètres :**
- `entity_type` (query, optionnel) : Filtrer par type d'entité
- `action` (query, optionnel) : Filtrer par type d'action
- `limit` (query, optionnel) : Nombre maximum d'entrées (défaut: 50, max: 200)

**Exemple :**
```bash
GET /api/audit/recent?entity_type=devis&action=created&limit=10
```

### GET /api/audit/search

Recherche avancée dans l'audit.

**Paramètres :**
- `entity_type` (query, optionnel) : Filtrer par type d'entité
- `entity_id` (query, optionnel) : Filtrer par ID d'entité
- `action` (query, optionnel) : Filtrer par type d'action
- `author_id` (query, optionnel) : Filtrer par auteur
- `start_date` (query, optionnel) : Date de début (ISO 8601)
- `end_date` (query, optionnel) : Date de fin (ISO 8601)
- `limit` (query, optionnel) : Nombre maximum d'entrées (défaut: 100, max: 500)
- `offset` (query, optionnel) : Décalage pour pagination

**Exemple :**
```bash
GET /api/audit/search?entity_type=devis&action=updated&author_id=1&limit=100
```

## Tests

Les tests unitaires sont disponibles dans :

- `/backend/tests/unit/shared/test_audit_entry.py` : Tests de l'entité AuditEntry
- `/backend/tests/unit/shared/test_audit_service.py` : Tests du service AuditService

Exécution des tests :

```bash
cd backend
pytest tests/unit/shared/ -v
```

## Migration

La migration Alembic pour créer la table `audit_log` :

```bash
cd backend
alembic upgrade head
```

Fichier de migration : `/backend/migrations/versions/20260201_1700_add_audit_log_table.py`

## Types d'actions recommandés

Pour homogénéité entre les modules, voici les actions recommandées :

- `created` : Création d'entité
- `updated` : Modification de champ
- `deleted` : Suppression d'entité
- `status_changed` : Changement de statut
- `validated` : Validation
- `rejected` : Refus/Rejet
- `sent` : Envoi (email, etc.)
- `signed` : Signature
- `approved` : Approbation
- `canceled` : Annulation

## Conformité RGPD

Le module d'audit contribue à la conformité RGPD :

- **Article 30** : Registre des activités de traitement
- **Article 5(1)(a)** : Traçabilité et transparence
- **Article 32** : Sécurité du traitement (audit trail)

Le champ `author_name` est dénormalisé (duplication) pour permettre la consultation de l'historique même après suppression d'un utilisateur (droit à l'oubli Article 17).

## Bonnes pratiques

1. **Toujours enregistrer les modifications sensibles** : montants, statuts, validations
2. **Ajouter un motif pour les actions importantes** : facilite l'audit et la compréhension
3. **Utiliser les factory methods** : `log_creation()`, `log_update()`, `log_deletion()`, `log_status_change()`
4. **Métadonnées pour contexte supplémentaire** : IDs liés, adresse IP, etc.
5. **Pagination pour grandes listes** : éviter de charger tout l'historique en mémoire
6. **Filtrer par période pour recherches** : améliore les performances

## Support

Pour toute question ou problème sur le module Audit, consulter :

- Cette documentation
- Les tests unitaires (exemples d'utilisation)
- Le code source (docstrings détaillées)
