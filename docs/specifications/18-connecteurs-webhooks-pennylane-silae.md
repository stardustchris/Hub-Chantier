## 18. CONNECTEURS WEBHOOKS (PENNYLANE & SILAE)

### 18.1 Vue d'ensemble

Le module Connecteurs Webhooks permet l'intégration temps réel avec les logiciels de comptabilité (Pennylane) et de paie (Silae). Il transforme automatiquement les événements métier de Hub Chantier en formats compatibles avec les APIs tierces et assure une traçabilité complète des données transmises. Conforme RGPD avec masquage des données personnelles et audit trail systématique.

### 18.2 Fonctionnalités

| ID | Fonctionnalité | Description | Statut |
|----|----------------|-------------|--------|
| CONN-01 | Connecteur Pennylane | Export automatique données comptables (achats, situations, paiements) | ✅ |
| CONN-02 | Connecteur Silae | Export automatique données paie (heures, variables) | ✅ |
| CONN-03 | Formatage données | Transformation événements Hub Chantier → format API cible | ✅ |
| CONN-04 | Validation sécurité | Protection XSS, injection SQL, validation codes/montants | ✅ |
| CONN-05 | Masquage RGPD | Codes employés masqués dans logs (EM**01) | ✅ |
| CONN-06 | Audit trail | Traçabilité complète transformations avec hash SHA-256 | ✅ |
| CONN-07 | Registry connecteurs | Découverte dynamique connecteurs disponibles | ✅ |
| CONN-08 | Tests unitaires | 97 tests, 94% couverture module security | ✅ |

### 18.3 Connecteur Pennylane (Comptabilité)

**Événements supportés** :
- `achat.created` → `POST /invoices/supplier` (factures fournisseurs)
- `situation_travaux.created` → `POST /invoices/customer` (factures clients)
- `paiement.created` → `POST /transactions` (transactions bancaires)

**Format de sortie (API Pennylane v1)** :
```json
{
  "date": "2026-01-31",
  "amount": 1500.00,
  "label": "Achat matériaux chantier MONTMELIAN",
  "category_id": "456",
  "invoice_number": "ACH-2026-001",
  "metadata": {
    "source": "hub-chantier",
    "event_id": "evt_abc123",
    "chantier_id": 12
  }
}
```

**Sécurité** :
- ✅ Protection XSS : tous les libellés sanitizés avec `bleach`
- ✅ Validation montants : montants négatifs rejetés
- ✅ Validation codes : numéros de facture validés par regex `^[A-Z0-9_-]{1,50}$`

### 18.4 Connecteur Silae (Paie)

**Événements supportés** :
- `feuille_heures.validated` → `POST /employees/hours`
- `pointage.validated` → `POST /employees/hours`

**Format de sortie (API Silae)** :
```json
{
  "employee_code": "EMP001",
  "period": "2026-01",
  "hours": [
    {
      "date": "2026-01-15",
      "type": "normal",
      "quantity": 8.0,
      "cost_center": "CHT001"
    },
    {
      "date": "2026-01-16",
      "type": "overtime",
      "quantity": 2.0,
      "cost_center": "CHT001"
    }
  ]
}
```

**Sécurité & RGPD** :
- ✅ Masquage employé : `EMP001` → `EM**01` dans tous les logs
- ✅ Hash SHA-256 : hash avec salt pour audit trail sans exposition données
- ✅ Audit trail : chaque transformation loggée avec timestamp, hash et métadonnées
- ✅ Validation codes : employe_code et chantier_code validés par regex
- ✅ Validation heures : types d'heures whitelistés (normal, overtime, night, sunday, holiday)

**Fonction d'agrégation** :
- Agrégation automatique de multiples pointages par (employé, période, date, chantier)
- Somme des quantités pour les heures du même type
- Format période validé : `YYYY-MM`

### 18.5 Architecture technique

**Structure** :
```
shared/infrastructure/connectors/
├── base_connector.py          # Interface abstraite (ABC)
├── registry.py                # Registry pattern + factory
├── security.py                # Fonctions sécurité (XSS, validation, RGPD)
├── pennylane/
│   ├── connector.py           # Implémentation Pennylane
│   └── formatters.py          # 3 formatters (supplier, customer, transaction)
└── silae/
    ├── connector.py           # Implémentation Silae
    └── formatters.py          # Formatter + agrégation pointages
```

**Design patterns** :
- Strategy Pattern (connecteurs interchangeables)
- Registry Pattern (découverte dynamique)
- Factory Pattern (`get_connector(name)`)
- Template Method (orchestration dans `transform_event()`)

### 18.6 Module de sécurité

Fichier : `shared/infrastructure/connectors/security.py`

**Fonctions exportées** :

| Fonction | Description | Usage |
|----------|-------------|-------|
| `sanitize_text()` | Protection XSS avec bleach | Sanitizer tous libellés, noms, descriptions |
| `validate_code()` | Validation regex codes | Valider employe_code, chantier_code, invoice_number |
| `validate_amount()` | Validation montants | Rejeter négatifs, NaN, hors bornes |
| `mask_employee_code()` | Masquage RGPD | Masquer codes employés dans logs (EM**01) |
| `hash_employee_code()` | Hash SHA-256 | Hash avec salt pour audit trail |
| `audit_log_employee_data()` | Audit trail RGPD | Logger transformations données employé |

**Exception custom** : `SecurityError(message, field)` pour violations de sécurité

### 18.7 Tests et qualité

**Tests unitaires** :
- 97 tests au total
- 44 tests pour `security.py` (94% couverture)
- 11 tests pour `pennylane/connector.py`
- 13 tests pour `silae/connector.py`
- 11 tests pour `silae/formatters.py` (agrégation)
- 10 tests pour `registry.py`

**Validations agents** :
- ✅ **architect-reviewer** : 9.6/10 - 0 violation Clean Architecture
- ✅ **test-automator** : 94% couverture (objectif 90% dépassé)
- ✅ **code-reviewer** : 9.0/10 - APPROVED
- ✅ **security-auditor** : PASS - 0 finding CRITICAL/HIGH

**Conformité** :
- ✅ RGPD compliant (masquage + audit trail)
- ✅ OWASP Top 10 (protection XSS, injection, logging sécurisé)
- ⚠️ ISO 27001/27002 : PARTIAL (recommandation : documenter retention logs)

### 18.8 Utilisation

**Récupérer un connecteur** :
```python
from shared.infrastructure.connectors import get_connector

connector = get_connector("pennylane")  # ou "silae"
```

**Transformer un événement** :
```python
from shared.infrastructure.event_bus.domain_event import DomainEvent

event = DomainEvent(
    event_type="achat.created",
    data={
        "date": "2026-01-31",
        "montant": 1500.00,
        "libelle": "Achat matériaux",
        "numero_facture": "ACH-2026-001"
    }
)

payload = connector.transform_event(event)
# {
#   "endpoint": "/invoices/supplier",
#   "data": {...},
#   "metadata": {...}
# }
```

### 18.9 Matrice des droits

| Action | Admin | Conducteur | Chef chantier | Compagnon |
|--------|-------|------------|---------------|-----------|
| Configurer connecteurs | ✅ | ❌ | ❌ | ❌ |
| Voir logs audit | ✅ | ✅ (lecture) | ❌ | ❌ |
| Déclencher export manuel | ✅ | ✅ | ❌ | ❌ |
| Voir historique exports | ✅ | ✅ (ses chantiers) | ❌ | ❌ |

### 18.10 Dépendances

| Package | Version | Usage |
|---------|---------|-------|
| bleach | >= 6.1.0 | Protection XSS (sanitization HTML) |

### 18.11 Intégrations avec autres modules

| Module | Événement | Connecteur | Format |
|--------|-----------|------------|--------|
| Financier | `achat.created` | Pennylane | Facture fournisseur |
| Financier | `situation_travaux.created` | Pennylane | Facture client |
| Financier | `paiement.created` | Pennylane | Transaction bancaire |
| Feuilles Heures | `feuille_heures.validated` | Silae | Heures employé période |
| Pointages | `pointage.validated` | Silae | Heures employé journalières |

### 18.12 Roadmap

**Phase 1 (Actuelle - ✅ Complète)** :
- ✅ Connecteur Pennylane (achats, situations, paiements)
- ✅ Connecteur Silae (heures, variables paie)
- ✅ Module de sécurité (XSS, RGPD, injection)
- ✅ Tests unitaires >= 90%

**Phase 2 (Prévue)** :
- ⏳ Dashboard monitoring des livraisons webhook
- ⏳ Retry avancé avec exponential backoff configurable
- ⏳ Connecteur Sage (comptabilité)
- ⏳ Connecteur QuickBooks (comptabilité)

**Phase 3 (Future)** :
- 🔮 Webhooks bidirectionnels (import depuis ERP)
- 🔮 Mapping personnalisé par utilisateur
- 🔮 Interface graphique configuration connecteurs

---