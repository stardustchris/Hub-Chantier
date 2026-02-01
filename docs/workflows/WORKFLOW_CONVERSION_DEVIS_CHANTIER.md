# Workflow Conversion Devis → Chantier - Hub Chantier

> Document créé le 1er février 2026
> Dernière mise à jour : 1er février 2026
> Spécification complète du workflow de conversion DEV-16
> Statut : **SPECIFICATION DETAILLEE** — Implémentation Phase 2 Module Devis

---

## TABLE DES MATIERES

1. [Vue d'ensemble](#1-vue-densemble)
2. [Prérequis et validations](#2-prerequis-et-validations)
3. [Workflow détaillé](#3-workflow-detaille)
4. [Transformation des entités](#4-transformation-des-entites)
5. [Gestion des variantes](#5-gestion-des-variantes)
6. [Audit et traçabilité](#6-audit-et-tracabilite)
7. [Rollback et gestion d'erreurs](#7-rollback-et-gestion-derreurs)
8. [Notifications](#8-notifications)
9. [Permissions et droits](#9-permissions-et-droits)
10. [Règles métier](#10-regles-metier)
11. [Événements domaine](#11-evenements-domaine)
12. [API REST](#12-api-rest)
13. [Scénarios de test](#13-scenarios-de-test)
14. [Architecture technique](#14-architecture-technique)
15. [Références](#15-references)

---

## 1. VUE D'ENSEMBLE

### Objectif de la conversion

La fonctionnalité **DEV-16 "Conversion en chantier"** transforme un devis accepté et signé en chantier opérationnel avec budget détaillé. Cette opération :

1. **Crée** un nouveau chantier dans le système
2. **Transfère** la structure budgétaire (lots + déboursés) vers le module Financier
3. **Archive** le devis en lecture seule
4. **Initialise** les entités liées (planning, documents, équipe)
5. **Notifie** les parties prenantes

### Contexte métier

**Phase commerciale (Devis)** :
- Chiffrage détaillé avec déboursés et marges
- Négociation client, variantes, révisions
- Signature électronique du client

**Phase opérationnelle (Chantier)** :
- Suivi budgétaire (engagé, réalisé, écarts)
- Achats fournisseurs, situations, facturation
- Planning, pointages, gestion équipe

**La conversion** est le **point de bascule irréversible** entre ces deux phases.

---

## 2. PREREQUIS ET VALIDATIONS

### Prérequis obligatoires

| Critère | Validation | Message d'erreur si KO |
|---------|------------|------------------------|
| **Statut devis** | `statut = "accepte"` | "Le devis doit être accepté pour être converti" |
| **Signature client** | `signature_client_at IS NOT NULL` | "La signature client est requise" |
| **Montant > 0** | `montant_total_ht > 0` | "Le montant du devis doit être supérieur à 0" |
| **Lots présents** | `COUNT(lots) >= 1` | "Le devis doit contenir au moins un lot" |
| **Client existant** | `client_id` valide | "Le client doit exister dans le système" |
| **Non déjà converti** | `chantier_id IS NULL` | "Ce devis a déjà été converti" |
| **Dates cohérentes** | `date_debut < date_fin` | "Les dates de début et fin sont incohérentes" |

### Validations optionnelles (warnings)

| Critère | Warning | Action recommandée |
|---------|---------|-------------------|
| **Conducteur assigné** | Aucun conducteur sur le devis | Assigner un conducteur après création |
| **Retenue de garantie** | Retenue = 0% | Vérifier si normal pour ce type de marché |
| **Déboursés manquants** | Lots sans déboursés détaillés | Analyse de rentabilité limitée |

---

## 3. WORKFLOW DETAILLE

### Étapes du workflow

```
┌────────────────────────────────────────────────────────────┐
│  ETAPE 1 : VALIDATIONS PREALABLES                          │
├────────────────────────────────────────────────────────────┤
│  • Vérifier statut = "accepte"                             │
│  • Vérifier signature client présente                      │
│  • Vérifier lots présents (≥ 1)                            │
│  • Vérifier non déjà converti                              │
│  • Vérifier cohérence dates                                │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│  ETAPE 2 : SELECTION VARIANTE ACTIVE                       │
├────────────────────────────────────────────────────────────┤
│  • Identifier la variante active (is_active = True)        │
│  • Si plusieurs variantes, prendre celle signée            │
│  • Récupérer tous les lots de la variante active           │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│  ETAPE 3 : CREATION DU CHANTIER                            │
├────────────────────────────────────────────────────────────┤
│  • Créer entité Chantier :                                 │
│    - code_chantier (auto-généré CHT-YYYY-NNN)             │
│    - nom = devis.nom_projet                                │
│    - client_id = devis.client_id                           │
│    - adresse = devis.adresse_travaux                       │
│    - date_debut = devis.date_debut_travaux                 │
│    - date_fin_prevue = devis.date_fin_travaux              │
│    - conducteur_id = devis.conducteur_id                   │
│    - statut = "EN_PREPARATION"                             │
│    - source_devis_id = devis.id                            │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│  ETAPE 4 : CREATION BUDGET GLOBAL                          │
├────────────────────────────────────────────────────────────┤
│  • Créer entité Budget :                                   │
│    - chantier_id = nouveau_chantier.id                     │
│    - montant_initial_ht = SUM(lots.total_prevu_ht)         │
│    - montant_revise_ht = montant_initial_ht                │
│    - retenue_garantie_pct = devis.retenue_garantie_pct     │
│    - seuil_alerte_pct = 80% (défaut)                       │
│    - seuil_validation_achat = 5000 EUR (défaut)            │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│  ETAPE 5 : TRANSFERT DES LOTS BUDGETAIRES                  │
├────────────────────────────────────────────────────────────┤
│  Pour chaque lot de la variante active :                   │
│  • UPDATE lot_budgetaire SET                               │
│      variante_devis_id = NULL                              │
│      budget_id = nouveau_budget.id                         │
│      (conservation déboursés et marges)                    │
│  • Initialiser :                                           │
│      engage = 0                                            │
│      realise = 0                                           │
│      reste_a_faire = total_prevu_ht                        │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│  ETAPE 6 : COPIE DES DOCUMENTS DEVIS → GED CHANTIER        │
├────────────────────────────────────────────────────────────┤
│  • Récupérer documents attachés au devis (plans, photos)  │
│  • Copier vers dossier GED du chantier                     │
│  • Conserver lien source (document.source_devis_id)        │
│  • Archiver PDF devis signé dans GED                       │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│  ETAPE 7 : CREATION PLANNING INITIAL (OPTIONNEL)           │
├────────────────────────────────────────────────────────────┤
│  • Si devis contient planning prévisionnel :               │
│    - Créer tâches dans Planning Opérationnel              │
│    - Lier tâches aux lots budgétaires (FIN-03)             │
│  • Sinon : Planning vide (à remplir manuellement)          │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│  ETAPE 8 : ARCHIVAGE DU DEVIS                              │
├────────────────────────────────────────────────────────────┤
│  • UPDATE devis SET                                        │
│      statut = "converti"                                   │
│      chantier_id = nouveau_chantier.id                     │
│      converti_at = NOW()                                   │
│      converti_by = current_user.id                         │
│  • Devis devient READ-ONLY (immutable)                     │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│  ETAPE 9 : JOURNALISATION AUDIT                            │
├────────────────────────────────────────────────────────────┤
│  • audit_service.log(                                      │
│      entity_type="devis",                                  │
│      entity_id=devis.id,                                   │
│      action="converted_to_chantier",                       │
│      metadata={                                            │
│        "chantier_id": nouveau_chantier.id,                 │
│        "montant_ht": devis.montant_total_ht,               │
│        "nb_lots_transferes": count(lots)                   │
│      }                                                     │
│    )                                                       │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│  ETAPE 10 : NOTIFICATIONS                                  │
├────────────────────────────────────────────────────────────┤
│  • Notifier conducteur assigné (push + email)              │
│  • Notifier tous les admins (push)                         │
│  • Email récapitulatif au client (optionnel)               │
│  • Publier événement DevisConvertiEvent                    │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│  ETAPE 11 : REPONSE API                                    │
├────────────────────────────────────────────────────────────┤
│  • Retourner :                                             │
│    - chantier_id (UUID)                                    │
│    - code_chantier (CHT-2026-042)                          │
│    - budget_id (int)                                       │
│    - nb_lots_transferes (int)                              │
│    - montant_total_ht (Decimal)                            │
│    - lien_chantier (/chantiers/{id})                       │
└────────────────────────────────────────────────────────────┘
```

---

## 4. TRANSFORMATION DES ENTITES

### Mapping Devis → Chantier

| Champ Devis | Champ Chantier | Transformation |
|-------------|----------------|----------------|
| `nom_projet` | `nom` | Copie directe |
| `client_id` | `client_id` | Référence conservée |
| `adresse_travaux` | `adresse` | Copie directe |
| `date_debut_travaux` | `date_debut` | Copie directe |
| `date_fin_travaux` | `date_fin_prevue` | Copie directe |
| `conducteur_id` | `conducteur_id` | Référence conservée |
| `description` | `description` | Copie directe |
| N/A | `statut` | "EN_PREPARATION" (défaut) |
| `id` | `source_devis_id` | Traçabilité |
| N/A | `code_chantier` | Auto-généré (CHT-YYYY-NNN) |

### Mapping Devis → Budget

| Champ Devis | Champ Budget | Transformation |
|-------------|--------------|----------------|
| N/A | `chantier_id` | Nouveau chantier.id |
| `SUM(lots.total_prevu_ht)` | `montant_initial_ht` | Somme calculée |
| `montant_initial_ht` | `montant_revise_ht` | Identique au départ |
| `retenue_garantie_pct` | `retenue_garantie_pct` | Copie directe |
| N/A | `seuil_alerte_pct` | 80% (défaut configurable) |
| N/A | `seuil_validation_achat` | 5000 EUR (défaut) |

### Mapping LotBudgetaire (phase devis → phase chantier)

| Champ (avant) | Champ (après) | Transformation |
|---------------|---------------|----------------|
| `variante_devis_id` | `variante_devis_id = NULL` | Déconnexion du devis |
| N/A | `budget_id` | Nouveau budget.id |
| `code_lot` | `code_lot` | Conservé |
| `libelle` | `libelle` | Conservé |
| `quantite_prevue` | `quantite_prevue` | Conservé |
| `prix_unitaire_ht` | `prix_unitaire_ht` | Conservé (prix après marge) |
| `total_prevu_ht` | `total_prevu_ht` | Conservé |
| `debourse_*` | `debourse_*` | **Conservé** (lecture seule) |
| `marge_pct` | `marge_pct` | **Conservé** (lecture seule) |
| N/A | `engage` | **0** (initialisé) |
| N/A | `realise` | **0** (initialisé) |
| N/A | `reste_a_faire` | **total_prevu_ht** (initialisé) |

**Point clé** : Les déboursés et marges du devis sont **conservés** dans `LotBudgetaire` pour permettre l'analyse de rentabilité (comparaison déboursé prévisionnel vs coûts réels).

---

## 5. GESTION DES VARIANTES

### Cas 1 : Devis sans variante

Si le devis n'a pas de variante explicite :
- Considérer la structure de lots principale comme la variante unique
- Transférer tous les lots liés directement au devis

### Cas 2 : Devis avec variantes (économique, standard, premium)

Si le devis contient plusieurs variantes :
1. **Identifier la variante active** : `variante.is_active = True`
2. **Vérifier unicité** : Une seule variante peut être active
3. **Transférer uniquement les lots de la variante active**
4. **Archiver les variantes non retenues** :
   - Les lots des variantes rejetées restent liés au devis
   - Statut `variante.statut = "non_retenue"`
   - Conservés pour historique commercial

**Règle métier** : La variante active est celle qui a été **signée par le client**.

---

## 6. AUDIT ET TRACABILITE

### Entrées d'audit créées

#### 1. Audit du devis

```python
audit_service.log(
    entity_type="devis",
    entity_id=str(devis.id),
    action="converted_to_chantier",
    author_id=current_user.id,
    author_name=current_user.full_name,
    metadata={
        "chantier_id": str(nouveau_chantier.id),
        "code_chantier": nouveau_chantier.code_chantier,
        "montant_ht": float(devis.montant_total_ht),
        "nb_lots_transferes": len(lots_transferes),
        "variante_retenue_id": str(variante_active.id) if variante_active else None
    },
    motif="Conversion automatique suite à acceptation et signature client"
)
```

#### 2. Audit du chantier créé

```python
audit_service.log(
    entity_type="chantier",
    entity_id=str(nouveau_chantier.id),
    action="created_from_devis",
    author_id=current_user.id,
    author_name=current_user.full_name,
    metadata={
        "source_devis_id": str(devis.id),
        "source_devis_numero": devis.numero,
        "montant_initial_ht": float(budget.montant_initial_ht)
    },
    motif="Création automatique depuis devis accepté"
)
```

#### 3. Audit de chaque lot transféré

Pour chaque lot :
```python
audit_service.log(
    entity_type="lot_budgetaire",
    entity_id=str(lot.id),
    action="transfered_to_chantier",
    field_name="budget_id",
    old_value=None,
    new_value=str(nouveau_budget.id),
    author_id=current_user.id,
    author_name=current_user.full_name,
    metadata={
        "source_devis_id": str(devis.id),
        "code_lot": lot.code_lot,
        "montant_ht": float(lot.total_prevu_ht)
    }
)
```

### Lien bidirectionnel

```
Devis.chantier_id  ←→  Chantier.source_devis_id
```

Permet de naviguer dans les deux sens pour consultation historique.

---

## 7. ROLLBACK ET GESTION D'ERREURS

### Stratégie de rollback

**Principe** : Toute la conversion se fait dans **une transaction unique** (ACID).

```python
async def convert_devis_to_chantier(devis_id: UUID):
    async with transaction():
        try:
            # Étapes 1-11
            chantier = create_chantier(...)
            budget = create_budget(...)
            transfer_lots(...)
            archive_devis(...)
            send_notifications(...)

            await transaction.commit()
            return chantier
        except Exception as e:
            await transaction.rollback()
            logger.error(f"Conversion failed: {e}")
            raise ConversionFailedException(str(e))
```

### Gestion des erreurs par étape

| Étape | Erreur possible | Action |
|-------|----------------|--------|
| **Validations** | Devis déjà converti | Retourner erreur 409 Conflict |
| **Variante** | Aucune variante active | Retourner erreur 400 Bad Request |
| **Création chantier** | Code chantier dupliqué | Regénérer code, retry |
| **Transfert lots** | Contrainte FK violée | Rollback complet |
| **Notifications** | Email fail | Log warning, continuer |

**Règle** : Échec de notification **NE BLOQUE PAS** la conversion (fire-and-forget).

---

## 8. NOTIFICATIONS

### Notification 1 : Conducteur assigné

**Canal** : Push + Email

**Destinataire** : `chantier.conducteur_id`

**Contenu** :
```
Titre : Nouveau chantier créé depuis devis
Message : Le devis [DEV-2026-042] a été converti en chantier [CHT-2026-015].
          Vous êtes assigné comme conducteur de travaux.
          Montant : 125 000 EUR HT
          Date début : 15 février 2026
Actions :
  - Voir le chantier
  - Consulter le budget
```

### Notification 2 : Administrateurs

**Canal** : Push

**Destinataires** : Tous les `role = "admin"`

**Contenu** :
```
Titre : Conversion devis → chantier
Message : Le devis [DEV-2026-042] a été converti en chantier [CHT-2026-015]
          par [Jean Dupont].
          Client : SARL Martin BTP
          Montant : 125 000 EUR HT
Actions :
  - Voir le chantier
```

### Notification 3 : Client (optionnelle)

**Canal** : Email

**Destinataire** : `client.email`

**Contenu** :
```
Objet : Votre projet démarre - [Nom projet]

Bonjour [Client],

Nous avons le plaisir de vous confirmer le démarrage de votre projet [Nom projet].

Votre conducteur de travaux :
  • Nom : [Conducteur]
  • Tél : [Téléphone]
  • Email : [Email]

Date de début : [Date]
Durée prévisionnelle : [X] semaines

Vous pouvez suivre l'avancement de votre chantier en temps réel via votre espace client :
[Lien espace client]

Cordialement,
L'équipe Greg Construction
```

---

## 9. PERMISSIONS ET DROITS

### Qui peut convertir un devis ?

| Rôle | Peut convertir | Conditions |
|------|----------------|------------|
| **Admin** | ✅ Oui | Tous les devis |
| **Conducteur** | ✅ Oui | Ses devis uniquement |
| **Commercial** | ❌ Non | Doit demander à Admin/Conducteur |
| **Chef chantier** | ❌ Non | N/A |
| **Compagnon** | ❌ Non | N/A |

### Permission détaillée

```python
def can_convert_devis(user: User, devis: Devis) -> bool:
    if user.role == Role.ADMIN:
        return True

    if user.role == Role.CONDUCTEUR:
        return devis.conducteur_id == user.id

    return False
```

---

## 10. REGLES METIER

1. **Unicité** : Un devis ne peut être converti qu'**une seule fois**
2. **Irréversibilité** : La conversion est **irréversible** (pas de "déconversion")
3. **Immutabilité** : Le devis converti devient **read-only**
4. **Conservation** : Tous les déboursés et marges sont **conservés** dans les lots
5. **Initialisation** : Les montants engagé/réalisé sont **à zéro** au départ
6. **Variante unique** : Seule la variante active est transférée
7. **Statut chantier** : Le chantier créé est en statut **"EN_PREPARATION"**
8. **Dates** : Les dates du devis sont copiées, modifiables ensuite
9. **Conducteur** : Le conducteur du devis devient conducteur du chantier (modifiable)
10. **Documents** : Les documents du devis sont copiés dans la GED du chantier

---

## 11. EVENEMENTS DOMAINE

### DevisConvertiEvent

**Publié** : Après commit transaction réussie

```python
@dataclass
class DevisConvertiEvent(DomainEvent):
    """Événement publié quand un devis est converti en chantier"""
    devis_id: UUID
    devis_numero: str
    chantier_id: UUID
    code_chantier: str
    budget_id: int
    montant_total_ht: Decimal
    nb_lots_transferes: int
    conducteur_id: int
    client_id: int
    converted_by: int
    converted_at: datetime
```

**Abonnés potentiels** :
- Module Planning : Créer planning initial
- Module Équipe : Assigner équipe par défaut
- Module Notifications : Notifier parties prenantes
- Module Analytics : Mise à jour statistiques commerciales

---

## 12. API REST

### POST /api/devis/{devis_id}/convert-to-chantier

**Description** : Convertit un devis accepté en chantier opérationnel

**Authentification** : Requise (Bearer token)

**Permissions** : Admin ou Conducteur assigné

**Request** :
```json
POST /api/devis/550e8400-e29b-41d4-a716-446655440000/convert-to-chantier
Authorization: Bearer {token}
Content-Type: application/json

{
  "notify_client": true,
  "notify_team": true,
  "create_initial_planning": false
}
```

**Response 201 Created** :
```json
{
  "success": true,
  "message": "Devis converti en chantier avec succès",
  "data": {
    "chantier": {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "code_chantier": "CHT-2026-015",
      "nom": "Immeuble Résidence Soleil",
      "client_id": 42,
      "client_nom": "SARL Martin BTP",
      "conducteur_id": 5,
      "conducteur_nom": "Jean Dupont",
      "statut": "EN_PREPARATION",
      "date_debut": "2026-02-15",
      "date_fin_prevue": "2026-08-30",
      "adresse": "15 rue de la Paix, 75002 Paris"
    },
    "budget": {
      "id": 123,
      "chantier_id": "660e8400-e29b-41d4-a716-446655440001",
      "montant_initial_ht": 125000.00,
      "montant_revise_ht": 125000.00,
      "retenue_garantie_pct": 5.0
    },
    "lots_transferes": {
      "count": 12,
      "total_ht": 125000.00
    },
    "devis": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "numero": "DEV-2026-042",
      "statut": "converti",
      "converti_at": "2026-02-01T14:35:22Z"
    },
    "links": {
      "chantier": "/chantiers/660e8400-e29b-41d4-a716-446655440001",
      "budget": "/chantiers/660e8400-e29b-41d4-a716-446655440001/budget",
      "devis": "/devis/550e8400-e29b-41d4-a716-446655440000"
    }
  }
}
```

**Response 400 Bad Request** :
```json
{
  "success": false,
  "error": "DEVIS_NOT_CONVERTIBLE",
  "message": "Le devis doit être accepté pour être converti",
  "details": {
    "current_status": "en_validation",
    "required_status": "accepte"
  }
}
```

**Response 409 Conflict** :
```json
{
  "success": false,
  "error": "DEVIS_ALREADY_CONVERTED",
  "message": "Ce devis a déjà été converti",
  "details": {
    "chantier_id": "660e8400-e29b-41d4-a716-446655440001",
    "code_chantier": "CHT-2026-015",
    "converted_at": "2026-01-28T10:15:00Z",
    "converted_by": "Jean Dupont"
  }
}
```

**Codes d'erreur** :

| Code HTTP | Error Code | Description |
|-----------|------------|-------------|
| 400 | `DEVIS_NOT_CONVERTIBLE` | Statut invalide (pas "accepte") |
| 400 | `SIGNATURE_MISSING` | Signature client manquante |
| 400 | `NO_LOTS` | Aucun lot dans le devis |
| 400 | `NO_ACTIVE_VARIANT` | Aucune variante active |
| 403 | `FORBIDDEN` | Utilisateur non autorisé |
| 404 | `DEVIS_NOT_FOUND` | Devis inexistant |
| 409 | `DEVIS_ALREADY_CONVERTED` | Déjà converti |
| 500 | `CONVERSION_FAILED` | Erreur interne |

---

## 13. SCENARIOS DE TEST

### Test 1 : Conversion nominale (happy path)

**Given** :
- Devis "DEV-2026-042" en statut "accepte"
- Signature client présente (01/02/2026 10:00)
- 12 lots budgétaires (total 125 000 EUR HT)
- Conducteur assigné (Jean Dupont, ID 5)
- Aucune variante (structure simple)

**When** :
- Admin appelle `POST /api/devis/{id}/convert-to-chantier`

**Then** :
- ✅ Chantier créé avec code "CHT-2026-015"
- ✅ Budget créé avec montant_initial_ht = 125 000 EUR
- ✅ 12 lots transférés (budget_id renseigné)
- ✅ Devis passe en statut "converti"
- ✅ Lien bidirectionnel créé (devis.chantier_id ↔ chantier.source_devis_id)
- ✅ 3 entrées d'audit créées (devis, chantier, 12x lots)
- ✅ Notification envoyée au conducteur
- ✅ Response 201 avec détails complets

### Test 2 : Devis déjà converti

**Given** :
- Devis "DEV-2026-041" déjà converti (chantier_id = CHT-2026-014)

**When** :
- Admin tente de convertir à nouveau

**Then** :
- ❌ Erreur 409 Conflict
- ❌ Message : "Ce devis a déjà été converti"
- ❌ Détails incluent chantier_id existant

### Test 3 : Devis non accepté

**Given** :
- Devis "DEV-2026-043" en statut "en_validation"

**When** :
- Admin tente de convertir

**Then** :
- ❌ Erreur 400 Bad Request
- ❌ Message : "Le devis doit être accepté pour être converti"

### Test 4 : Signature manquante

**Given** :
- Devis "DEV-2026-044" en statut "accepte"
- Mais signature_client_at = NULL

**When** :
- Admin tente de convertir

**Then** :
- ❌ Erreur 400 Bad Request
- ❌ Message : "La signature client est requise"

### Test 5 : Conversion avec variantes

**Given** :
- Devis "DEV-2026-045" avec 3 variantes :
  - Économique (8 lots, 95 000 EUR) - is_active = False
  - Standard (10 lots, 115 000 EUR) - is_active = True ← retenue
  - Premium (12 lots, 135 000 EUR) - is_active = False

**When** :
- Admin convertit

**Then** :
- ✅ Seuls les 10 lots de la variante "Standard" sont transférés
- ✅ Montant budget = 115 000 EUR
- ✅ Les 2 autres variantes restent liées au devis (archivées)

### Test 6 : Rollback sur erreur

**Given** :
- Devis valide "DEV-2026-046"
- Contrainte DB : code_chantier doit être unique
- Un chantier "CHT-2026-016" existe déjà

**When** :
- Générateur de code produit "CHT-2026-016" (collision)

**Then** :
- ❌ Transaction rollback
- ❌ Aucun chantier créé
- ❌ Aucun lot transféré
- ❌ Devis reste en statut "accepte"
- ❌ Erreur 500 avec message explicite

### Test 7 : Permission refusée

**Given** :
- Devis "DEV-2026-047" avec conducteur_id = 5 (Jean)
- Utilisateur connecté : Marie (conducteur_id = 7)

**When** :
- Marie tente de convertir

**Then** :
- ❌ Erreur 403 Forbidden
- ❌ Message : "Vous n'êtes pas autorisé à convertir ce devis"

---

## 14. ARCHITECTURE TECHNIQUE

### Use Case : ConvertDevisToChantierUseCase

**Localisation** : `backend/modules/devis/application/use_cases/convert_to_chantier_use_case.py`

**Responsabilités** :
1. Valider les prérequis
2. Orchestrer la création des entités (chantier, budget, transfert lots)
3. Publier l'événement domaine
4. Gérer la transaction

**Dépendances** :
- `DevisRepository` (lecture devis source)
- `ChantierRepository` (création chantier)
- `BudgetRepository` (création budget)
- `LotBudgetaireRepository` (transfert lots)
- `AuditService` (traçabilité)
- `EventBus` (publication événement)
- `NotificationService` (notifications)

### Diagramme de séquence

```
User → API → UseCase → Repositories → Database
                ↓
             EventBus → Subscribers
                ↓
          NotificationService → Email/Push
```

### Transaction management

```python
class ConvertDevisToChantierUseCase:
    async def execute(self, devis_id: UUID, options: ConvertOptionsDTO) -> ChantierDTO:
        # Validation préalable (hors transaction)
        devis = await self.devis_repo.find_by_id(devis_id)
        self._validate_convertible(devis)

        # Transaction atomique
        async with self.db.transaction():
            # Création entités
            chantier = await self._create_chantier(devis)
            budget = await self._create_budget(chantier, devis)
            lots = await self._transfer_lots(devis, budget)

            # Archivage devis
            await self._archive_devis(devis, chantier)

            # Audit
            await self._log_audit(devis, chantier, lots)

        # Post-transaction (fire-and-forget)
        await self._publish_event(devis, chantier, budget)
        await self._send_notifications(chantier, options)

        return ChantierDTO.from_entity(chantier)
```

---

## 15. REFERENCES

### Specifications CDC

- **DEV-16** : Conversion en chantier (Module 20, §20.2)
- **FIN-02** : Budget prévisionnel par lots (Module 17)
- **FIN-03** : Affectation budgets aux tâches (Module 17)
- **CHT-01** : Création chantier (Module 4)

### Entités Domain

- `Devis` : `backend/modules/devis/domain/entities/devis.py`
- `VarianteDevis` : `backend/modules/devis/domain/entities/variante_devis.py`
- `Chantier` : `backend/modules/chantiers/domain/entities/chantier.py`
- `Budget` : `backend/modules/financier/domain/entities/budget.py`
- `LotBudgetaire` : `backend/modules/shared/domain/entities/lot_budgetaire.py`

### Workflows liés

- [Workflow Gestion Financière](./WORKFLOW_GESTION_FINANCIERE.md)
- [Workflow Cycle de Vie Chantier](./WORKFLOW_CYCLE_VIE_CHANTIER.md)

---

**Version** : 1.0
**Date** : 1er février 2026
**Auteur** : Claude Code
**Statut** : ✅ Spécification détaillée complète
