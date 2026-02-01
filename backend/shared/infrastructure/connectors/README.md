# Connecteurs d'Intégration

Ce module fournit des connecteurs pour intégrer Hub Chantier avec des systèmes tiers (comptabilité, paie, etc.).

## Architecture

```
connectors/
├── __init__.py                 # Exports publics
├── base_connector.py           # Interface abstraite BaseConnector
├── registry.py                 # Registre des connecteurs disponibles
├── pennylane/                  # Connecteur Pennylane (comptabilité)
│   ├── __init__.py
│   ├── connector.py
│   └── formatters.py
└── silae/                      # Connecteur Silae (paie)
    ├── __init__.py
    ├── connector.py
    └── formatters.py
```

## Connecteurs Disponibles

### Pennylane (Comptabilité)

Transforme les événements financiers en appels API Pennylane v1.

**Événements supportés:**
- `achat.created` → POST `/invoices/supplier` (factures fournisseurs)
- `situation_travaux.created` → POST `/invoices/customer` (factures clients)
- `paiement.created` → POST `/transactions` (transactions bancaires)

### Silae (Paie)

Transforme les événements RH en appels API Silae.

**Événements supportés:**
- `feuille_heures.validated` → POST `/employees/hours` (heures validées)
- `pointage.validated` → POST `/employees/hours` (pointages validés)

## Utilisation

### Récupérer un connecteur

```python
from shared.infrastructure.connectors import get_connector

# Récupérer le connecteur Pennylane
connector = get_connector("pennylane")

# Récupérer le connecteur Silae
connector = get_connector("silae")
```

### Transformer un événement

```python
from shared.infrastructure.event_bus.domain_event import DomainEvent
from shared.infrastructure.connectors import get_connector

# Créer un événement
event = DomainEvent(
    event_type="achat.created",
    aggregate_id="123",
    data={
        "date": "2026-01-31",
        "montant": 1500.00,
        "libelle": "Achat matériaux chantier X",
        "numero_facture": "F-2026-001"
    }
)

# Transformer l'événement
connector = get_connector("pennylane")
payload = connector.transform_event(event)

# Résultat:
# {
#     "endpoint": "/invoices/supplier",
#     "data": {
#         "date": "2026-01-31",
#         "amount": 1500.00,
#         "label": "Achat matériaux chantier X",
#         "invoice_number": "F-2026-001",
#         "external_id": "123"
#     },
#     "metadata": {
#         "source": "hub-chantier",
#         "event_id": "...",
#         "event_type": "achat.created",
#         "occurred_at": "2026-01-31T12:00:00",
#         "connector": "pennylane"
#     }
# }
```

### Lister les connecteurs disponibles

```python
from shared.infrastructure.connectors.registry import list_connectors

connectors = list_connectors()
# {
#     "pennylane": ["achat.created", "situation_travaux.created", "paiement.created"],
#     "silae": ["feuille_heures.validated", "pointage.validated"]
# }
```

### Trouver le connecteur pour un événement

```python
from shared.infrastructure.connectors.registry import find_connector_for_event

connector_name = find_connector_for_event("achat.created")
# "pennylane"

connector_name = find_connector_for_event("feuille_heures.validated")
# "silae"

connector_name = find_connector_for_event("user.created")
# None (aucun connecteur ne supporte cet événement)
```

## Exemples par Événement

### Pennylane - Achat (Facture Fournisseur)

```python
event = DomainEvent(
    event_type="achat.created",
    data={
        "date": "2026-01-31",
        "montant": 1500.00,
        "libelle": "Achat matériaux",
        "numero_facture": "F-2026-001",  # Optionnel
        "category_id": "CAT-123"         # Optionnel
    }
)
```

### Pennylane - Situation de Travaux (Facture Client)

```python
event = DomainEvent(
    event_type="situation_travaux.created",
    data={
        "date": "2026-01-31",
        "montant": 25000.00,
        "libelle": "Situation #1",
        "numero": 1,                     # Optionnel
        "chantier_nom": "Chantier ABC"   # Optionnel
    }
)
```

### Pennylane - Paiement (Transaction)

```python
event = DomainEvent(
    event_type="paiement.created",
    data={
        "date": "2026-01-31",
        "montant": 5000.00,
        "libelle": "Paiement facture",
        "type": "virement"  # virement, cheque, especes, cb
    }
)
```

### Silae - Feuille d'Heures

```python
event = DomainEvent(
    event_type="feuille_heures.validated",
    data={
        "employe_code": "EMP001",
        "periode": "2026-01",
        "heures": [
            {
                "date": "2026-01-15",
                "type": "normal",  # normal, supplementaire, nuit, dimanche, ferie
                "quantite": 8.0,
                "chantier_code": "CHT001"  # Optionnel
            },
            {
                "date": "2026-01-16",
                "type": "supplementaire",
                "quantite": 2.0
            }
        ]
    }
)
```

## Gestion d'Erreurs

Tous les connecteurs lèvent une `ConnectorError` en cas de problème :

```python
from shared.infrastructure.connectors.base_connector import ConnectorError

try:
    payload = connector.transform_event(event)
except ConnectorError as e:
    print(f"Erreur connecteur: {e}")
    print(f"Connecteur: {e.connector_name}")
    print(f"Événement: {e.event_type}")
```

**Cas d'erreurs:**
- Événement non supporté par le connecteur
- Champs requis manquants dans les données
- Format de données invalide
- Erreur inattendue lors de la transformation

## Intégration avec WebhookDeliveryService

Les connecteurs sont conçus pour être utilisés avec `WebhookDeliveryService`:

```python
from shared.infrastructure.webhooks.webhook_service import WebhookDeliveryService
from shared.infrastructure.connectors import get_connector

# 1. Transformer l'événement via le connecteur
connector = get_connector("pennylane")
payload = connector.transform_event(event)

# 2. Le payload contient:
#    - endpoint: "/invoices/supplier"
#    - data: {...}  (données formatées pour Pennylane)
#    - metadata: {...}

# 3. WebhookDeliveryService fait la livraison HTTP
#    - POST à l'URL du webhook configuré
#    - Avec le payload transformé
#    - Signature HMAC pour sécurité
#    - Retry automatique en cas d'échec
```

## Créer un Nouveau Connecteur

Pour ajouter un connecteur pour un nouveau système:

1. **Créer le dossier du connecteur:**
   ```
   connectors/nouveau_systeme/
   ├── __init__.py
   ├── connector.py
   └── formatters.py
   ```

2. **Implémenter le connecteur:**
   ```python
   from ..base_connector import BaseConnector

   class NouveauSystemeConnector(BaseConnector):
       def __init__(self):
           super().__init__(
               name="nouveau_systeme",
               supported_events=["event.type1", "event.type2"]
           )

       def format_data(self, event: DomainEvent) -> dict:
           # Logique de transformation
           ...

       def get_api_endpoint(self, event_type: str) -> str:
           # Retourner l'endpoint API
           ...
   ```

3. **Enregistrer dans le registre:**
   ```python
   # Dans registry.py
   from .nouveau_systeme.connector import NouveauSystemeConnector

   CONNECTOR_REGISTRY = {
       "pennylane": PennylaneConnector,
       "silae": SilaeConnector,
       "nouveau_systeme": NouveauSystemeConnector,  # Ajouter ici
   }
   ```

4. **Créer les tests:**
   ```
   tests/unit/shared/infrastructure/connectors/test_nouveau_systeme_connector.py
   ```

## Tests

Exécuter les tests:

```bash
pytest backend/tests/unit/shared/infrastructure/connectors/ -v --cov=shared/infrastructure/connectors
```

**Couverture actuelle:** 96% (53 tests)

## Références

- **Architecture:** Clean Architecture (4 layers)
- **Standards:** PEP 8, type hints complets, docstrings Google style
- **Documentation API:**
  - [Pennylane API v1](https://pennylane.com/api)
  - [Silae API](https://silae.fr/documentation)
