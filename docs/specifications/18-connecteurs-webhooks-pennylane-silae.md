## 18. CONNECTEURS WEBHOOKS (PENNYLANE & SILAE)

### 18.1 Vue d'ensemble

Le module Connecteurs Webhooks permet l'intégration temps réel avec les logiciels de comptabilité (Pennylane) et de paie (Silae). Il transforme automatiquement les événements métier de Hub Chantier en formats compatibles avec les APIs tierces et assure une traçabilité complète des données transmises. Conforme RGPD avec masquage des données personnelles et audit trail systématique.

### 18.2 Fonctionnalités

| ID | Fonctionnalité | Description | Statut |
|----|----------------|-------------|--------|
| CONN-01 | Connecteur Pennylane Outbound | Export automatique données comptables (achats, situations, paiements) | ✅ |
| CONN-02 | Connecteur Silae | Export automatique données paie (heures, variables) | ✅ |
| CONN-03 | Formatage données | Transformation événements Hub Chantier → format API cible | ✅ |
| CONN-04 | Validation sécurité | Protection XSS, injection SQL, validation codes/montants | ✅ |
| CONN-05 | Masquage RGPD | Codes employés masqués dans logs (EM**01) | ✅ |
| CONN-06 | Audit trail | Traçabilité complète transformations avec hash SHA-256 | ✅ |
| CONN-07 | Registry connecteurs | Découverte dynamique connecteurs disponibles | ✅ |
| CONN-08 | Tests unitaires | 97 tests, 94% couverture module security | ✅ |
| **CONN-10** | **Sync factures fournisseurs** | Import factures payées depuis Pennylane (polling 15 min) | ✅ |
| **CONN-11** | **Sync encaissements clients** | Mise à jour statut paiement FactureClient | ✅ |
| **CONN-12** | **Import fournisseurs** | Création automatique fiches fournisseurs depuis Pennylane | ✅ |
| **CONN-13** | **Matching intelligent** | Fournisseur + Chantier + Montant ±10% + Fenêtre 30j | ✅ |
| **CONN-14** | **Table mapping analytique** | Correspondance code_analytique_pennylane ↔ chantier_id | ✅ |
| **CONN-15** | **Dashboard réconciliation** | File d'attente achats non matchés + validation manuelle | ✅ |
| **CONN-16** | **Alertes dépassement** | Notification si facture > 110% prévisionnel | ⏳ |
| **CONN-17** | **Import historique** | Commande one-shot pour importer factures existantes | ⏳ |

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

### 18.12 Intégration Pennylane Inbound (Import Données Comptables)

> **Objectif** : Importer les factures payées depuis Pennylane pour calculer la rentabilité réelle des chantiers (Budget vs Réalisé).

#### 18.12.1 Architecture : Polling (Synchronisation Périodique)

**Pourquoi pas de webhooks ?**
- L'API Pennylane ne propose **pas de webhooks natifs** (confirmé via documentation officielle)
- Les "webhooks Pennylane" trouvés en ligne passent par Zapier/Pipedream (services tiers payants)
- L'API est explicitement "request-based" et non "event-based"

**Architecture retenue** :
```
┌─────────────────┐     Toutes les 15 min      ┌──────────────────┐
│  HUB CHANTIER   │ ──────────────────────────>│   PENNYLANE      │
│                 │  GET /supplier_invoices    │                  │
│ • Scheduler     │  ?is_paid=true             │ • Factures       │
│ • Sync Service  │  &updated_since=...        │ • Fournisseurs   │
│                 │<──────────────────────────│                  │
│ • Matching      │  JSON Response             │                  │
│ • Budget update │                            │                  │
└─────────────────┘                            └──────────────────┘
```

**Coût API Pennylane** : **Gratuit** (inclus dans abonnement Essentiel 24€+/mois)
- Rate limit : 5 requêtes/seconde
- Consommation estimée : ~100 appels/jour << limite 432 000/jour

#### 18.12.2 Fonctionnalités Import Pennylane

| ID | Fonctionnalité | Description | Statut |
|----|----------------|-------------|--------|
| CONN-10 | Sync factures fournisseurs | Import factures payées avec matching achats prévisionnels | ⏳ |
| CONN-11 | Sync encaissements clients | Mise à jour statut paiement FactureClient | ⏳ |
| CONN-12 | Import fournisseurs | Création automatique fiches fournisseurs depuis Pennylane | ⏳ |
| CONN-13 | Matching intelligent | Fournisseur + Chantier + Montant ±10% + Fenêtre temporelle | ⏳ |
| CONN-14 | Table mapping analytique | Correspondance code_analytique_pennylane ↔ chantier_id | ⏳ |
| CONN-15 | Dashboard réconciliation | File d'attente achats non matchés à valider manuellement | ⏳ |
| CONN-16 | Alertes dépassement | Notification si facture > 110% prévisionnel | ⏳ |
| CONN-17 | Import historique | Commande one-shot pour importer factures existantes | ⏳ |

#### 18.12.3 Enrichissement Entités

**Achat** (nouveaux champs) :
- `montant_ht_reel` : Montant facture réelle (Pennylane)
- `date_facture_reelle` : Date facture Pennylane
- `pennylane_invoice_id` : ID externe pour idempotence
- `source_donnee` : "HUB" | "PENNYLANE"

**FactureClient** (nouveaux champs) :
- `date_paiement_reel` : Date encaissement constaté
- `montant_encaisse` : Montant réellement encaissé
- `pennylane_invoice_id` : ID externe

**Fournisseur** (nouveaux champs) :
- `pennylane_supplier_id` : ID externe
- `delai_paiement_jours` : Délai paiement par défaut
- `iban` / `bic` : Coordonnées bancaires (optionnel)
- `source_donnee` : "HUB" | "PENNYLANE"

#### 18.12.4 Workflow Synchronisation

```
Job PennylaneSyncJob (toutes les 15 min)
│
├─ 1. Récupérer last_sync_timestamp
│
├─ 2. GET /supplier_invoices?is_paid=true&updated_since=<timestamp>
│
├─ 3. Pour chaque facture non importée :
│   │
│   ├─ 3a. Find/Create Fournisseur (par SIRET)
│   │
│   ├─ 3b. Find Chantier (par code analytique via table mapping)
│   │
│   ├─ 3c. Matching intelligent Achat existant :
│   │   • Même fournisseur + même chantier
│   │   • Montant dans tolérance ±10%
│   │   • Statut COMMANDE ou LIVRE
│   │   • Fenêtre temporelle < 30 jours
│   │
│   ├─ 3d. Si match trouvé :
│   │   → Update Achat.montant_ht_reel
│   │   → Update Achat.statut = FACTURE
│   │
│   └─ 3e. Si pas de match :
│       → Créer PendingReconciliation (file d'attente)
│       → Alerter conducteur travaux
│
├─ 4. Mettre à jour Budget.total_realise_ht
│
└─ 5. Enregistrer sync_timestamp
```

#### 18.12.5 Dashboard Réconciliation

Page `/financier/reconciliation` :

```
┌─────────────────────────────────────────────────────────────┐
│ Réconciliation Pennylane                    [Sync manuelle] │
├─────────────────────────────────────────────────────────────┤
│ ✅ Matchés automatiquement (42)                             │
│ ⚠️  À vérifier (7)                                          │
│ ❌ Non matchés (3)                                          │
├─────────────────────────────────────────────────────────────┤
│ Facture ACME #F2026-0234 - 5 200€                           │
│ Code analytique: MONTMELIAN                                 │
│ ┌────────────────────────────────────────┐                  │
│ │ Match suggéré: Achat #A-2026-089       │ [Valider]       │
│ │ Prévisionnel: 5 000€ | Écart: +4%      │ [Réaffecter]    │
│ └────────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

#### 18.12.6 Alertes Intelligentes

| Alerte | Trigger | Destinataire |
|--------|---------|--------------|
| Dépassement budget | Facture > 110% prévisionnel | Chef de chantier |
| Facture non prévue | Aucun Achat matching | Conducteur travaux |
| Fournisseur inconnu | SIRET absent de Hub | Admin |
| Code analytique inconnu | Mapping non trouvé | Admin |

#### 18.12.7 Tables SQL Additionnelles

```sql
-- Table de mapping codes analytiques
CREATE TABLE pennylane_mapping_analytique (
    id SERIAL PRIMARY KEY,
    code_analytique VARCHAR(50) UNIQUE NOT NULL,
    chantier_id INTEGER REFERENCES chantiers(id),
    created_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER REFERENCES utilisateurs(id)
);

-- Table de suivi synchronisation
CREATE TABLE pennylane_sync_log (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    records_processed INTEGER DEFAULT 0,
    records_created INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_pending INTEGER DEFAULT 0,
    error_message TEXT,
    status VARCHAR(20) DEFAULT 'running'
);

-- File d'attente réconciliation
CREATE TABLE pennylane_pending_reconciliation (
    id SERIAL PRIMARY KEY,
    pennylane_invoice_id VARCHAR(255) UNIQUE NOT NULL,
    supplier_name VARCHAR(255),
    supplier_siret VARCHAR(14),
    amount_ht DECIMAL(15,2),
    code_analytique VARCHAR(50),
    invoice_date DATE,
    suggested_achat_id INTEGER REFERENCES achats(id),
    status VARCHAR(20) DEFAULT 'pending',
    resolved_by INTEGER REFERENCES utilisateurs(id),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 18.13 Roadmap

**Phase 1 (✅ Complète)** :
- ✅ Connecteur Pennylane Outbound (achats, situations, paiements)
- ✅ Connecteur Silae (heures, variables paie)
- ✅ Module de sécurité (XSS, RGPD, injection)
- ✅ Tests unitaires >= 90%

**Phase 2 (⏳ En cours)** :
- ⏳ **Import Pennylane Inbound** (CONN-10 à CONN-17)
- ⏳ Dashboard monitoring des livraisons
- ⏳ Retry avancé avec exponential backoff

**Phase 3 (Prévue)** :
- 🔮 Génération factures depuis devis (`/create_from_quote`)
- 🔮 Rapprochement bancaire automatique (DSO)
- 🔮 Prévisionnel trésorerie enrichi
- 🔮 Connecteur Sage / QuickBooks

**Phase 4 (Future)** :
- 🔮 Export FEC automatisé
- 🔮 Suivi TVA construction (autoliquidation)
- 🔮 Interface graphique configuration connecteurs

### 18.14 Références

- [Documentation API Pennylane](https://pennylane.readme.io/)
- [Rate Limiting API v2](https://pennylane.readme.io/docs/rate-limiting-1)
- [Data Sharing Pennylane](https://data-sharing.pennylane.com/)
- [Plan d'intégration détaillé](/.claude/plans/twinkly-shimmying-rose.md)

---