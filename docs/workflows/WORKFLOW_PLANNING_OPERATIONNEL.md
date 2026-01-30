# Workflow Planning Opérationnel

**Date** : 30 janvier 2026
**Auteur** : Claude Sonnet 4.5
**Module** : `backend/modules/planning/`
**Référence CDC** : Section 5 - Planning Opérationnel (PLN-01 à PLN-28)

---

## 🎯 Objectif

Le Planning Opérationnel est le **cœur métier** de Hub Chantier. Il permet de planifier et gérer les affectations des compagnons aux chantiers sur une base hebdomadaire, avec une synchronisation automatique vers les feuilles d'heures.

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Acteurs](#acteurs)
3. [Concepts Métier](#concepts-métier)
4. [Workflows Détaillés](#workflows-détaillés)
5. [Règles Métier](#règles-métier)
6. [Interactions Modules](#interactions-modules)
7. [Architecture Technique](#architecture-technique)
8. [Scénarios de Test](#scénarios-de-test)
9. [Points d'Attention](#points-dattention)

---

## 1. Vue d'Ensemble

### 1.1 Qu'est-ce qu'une Affectation ?

Une **Affectation** lie un **compagnon** à un **chantier** pour une **date** donnée, avec :
- Horaires optionnels (heure début/fin)
- Heures prévues (pour calcul charge)
- Note privée visible uniquement par le compagnon
- Type : **UNIQUE** (ponctuelle) ou **RÉCURRENTE** (hebdomadaire)

### 1.2 Fonctionnalités Principales

| Fonctionnalité | Code CDC | Description |
|----------------|----------|-------------|
| **Création affectation** | PLN-04 | Affecter un compagnon à un chantier |
| **Modification** | PLN-05 | Changer dates, horaires, chantier |
| **Suppression** | PLN-06 | Retirer une affectation |
| **Drag & Drop** | PLN-27 | Déplacer visuellement les blocs |
| **Récurrence** | PLN-07 | Répéter sur plusieurs jours |
| **Duplication** | PLN-08 | Dupliquer une semaine sur une autre |
| **Gestion absences** | PLN-09 | Affecter à chantiers système (CONGES, MALADIE, RTT, FORMATION) |
| **Notes privées** | PLN-25 | Commentaires visibles par l'affecté uniquement |
| **Synchronisation FDH** | FDH-10 | Création automatique pointages depuis planning |

---

## 2. Acteurs

### 2.1 Rôles et Permissions

| Rôle | Vue Planning | Créer Affectation | Modifier | Supprimer | Voir Tous Utilisateurs |
|------|--------------|-------------------|----------|-----------|------------------------|
| **Admin** | ✅ Tous | ✅ Oui | ✅ Toutes | ✅ Toutes | ✅ Oui |
| **Conducteur de travaux** | ✅ Tous | ✅ Oui | ✅ Toutes | ✅ Toutes | ✅ Oui |
| **Chef de chantier** | ⚠️ Ses chantiers uniquement | ✅ Oui (ses chantiers) | ✅ Ses chantiers | ✅ Ses chantiers | ⚠️ Uniquement affectés à ses chantiers |
| **Compagnon** | ⚠️ Son planning uniquement | ❌ Non | ❌ Non | ❌ Non | ❌ Non |

### 2.2 Permissions Détaillées

**Admin / Conducteur** :
- Voient **TOUT** le planning (tous utilisateurs, tous chantiers)
- Peuvent affecter **n'importe qui** à **n'importe quel chantier**
- Peuvent gérer les affectations récurrentes
- Peuvent dupliquer des semaines complètes

**Chef de Chantier** :
- Voient uniquement les affectations sur **leurs chantiers**
- Peuvent affecter des compagnons sur **leurs chantiers uniquement**
- Ne voient que les utilisateurs déjà affectés à leurs chantiers
- Peuvent gérer absences de leurs équipes

**Compagnon** :
- Voient **uniquement leur propre planning**
- Mode **lecture seule** (consultation uniquement)
- Peuvent voir leurs notes privées
- Reçoivent notifications d'affectation

---

## 3. Concepts Métier

### 3.1 Types d'Affectation

#### **Affectation UNIQUE** (par défaut)
```
Utilisateur : Sébastien ACHKAR
Chantier    : 2025-03-TOURNON-COMMERCIAL
Date        : 2026-01-30
Horaires    : 08:00 - 17:00 (optionnel)
Heures      : 8h00
Note        : "Apporter matériel électrique"
```

#### **Affectation RÉCURRENTE**
```
Utilisateur : Carlos DE OLIVEIRA COVAS
Chantier    : 2025-04-CHIGNIN-AGRICOLE
Date début  : 2026-02-03 (lundi)
Récurrence  : Lundi, Mardi, Mercredi, Jeudi, Vendredi
Horaires    : 07:30 - 16:30
Heures/jour : 8h00
```

Génère automatiquement 5 affectations (une par jour spécifié).

---

### 3.2 Chantiers Spéciaux (Absences)

Hub Chantier gère les absences via des **chantiers système** :

| Code | Nom | Usage | Impact Paie |
|------|-----|-------|-------------|
| **CONGES** | Congés payés | Vacances planifiées | ✅ Payé |
| **MALADIE** | Arrêt maladie | Absence maladie/accident | ⚠️ Variable selon convention |
| **FORMATION** | Formation | Formation professionnelle | ✅ Payé |
| **RTT** | RTT | Réduction temps travail | ✅ Payé |

**Règles** :
- Ces chantiers sont **toujours disponibles** (statut = `ouvert`)
- Pas d'heures prévues requises
- Apparaissent dans le planning avec couleur spécifique
- **Bloquent** la création de pointages réels (FDH-10)

---

### 3.3 Horaires et Heures Prévues

#### Horaires (Optionnels)
- **Heure début** : Format HH:MM (ex: 08:00)
- **Heure fin** : Format HH:MM (ex: 17:00)
- Validation : heure_fin > heure_debut

**Usage** : Information indicative, n'impacte PAS les calculs.

#### Heures Prévues (Importantes)
- **Durée planifiée** pour la journée
- Format : Decimal (ex: 8.0, 7.5)
- **Utilisé pour** :
  - Calcul de charge (Planning de Charge)
  - Pré-remplissage feuilles d'heures (FDH-10)
  - Comparaison prévu vs réalisé

**Valeur par défaut** : 8h00 (journée complète)

---

## 4. Workflows Détaillés

### 4.1 Création d'une Affectation UNIQUE

#### Acteur
Chef de chantier, Conducteur, ou Admin

#### Étapes

**1. Accès au Planning**
```
GET /api/planning?date_debut=2026-01-27&date_fin=2026-02-02
```
- Charge le planning de la semaine
- Applique les filtres de rôle automatiquement

**2. Sélection du Compagnon et Chantier**
- Drag & Drop d'un compagnon sur un chantier (UI)
- OU clic "Ajouter affectation"

**3. Saisie des Informations**
```json
{
  "utilisateur_id": 15,
  "chantier_id": 42,
  "date": "2026-01-30",
  "heure_debut": "08:00",
  "heure_fin": "17:00",
  "heures_prevues": 8.0,
  "note": "Travaux de maçonnerie",
  "type_affectation": "UNIQUE"
}
```

**4. Validation Backend**

**Use Case** : `CreateAffectationUseCase`

**Validations** :
- ✅ Utilisateur existe et est actif
- ✅ Chantier existe et n'est pas fermé/archivé
- ✅ Date >= aujourd'hui (optionnel selon règle métier)
- ✅ heure_fin > heure_debut
- ✅ heures_prevues > 0
- ✅ Pas de double affectation (même utilisateur, même date, chantier différent)

**5. Création en Base**
```sql
INSERT INTO affectations (
  utilisateur_id, chantier_id, date,
  heure_debut, heure_fin, heures_prevues,
  note, type_affectation, created_by, created_at
) VALUES (
  15, 42, '2026-01-30',
  '08:00', '17:00', 8.0,
  'Travaux de maçonnerie', 'UNIQUE', 1, NOW()
);
```

**6. Event Publié**
```python
AffectationCreatedEvent(
    affectation_id=123,
    utilisateur_id=15,
    chantier_id=42,
    date=date(2026, 1, 30),
)
```

**7. Notification**
- **Push notification** au compagnon : "Vous êtes affecté au chantier TOURNON-COMMERCIAL le 30/01/2026"
- Email (optionnel selon paramètres)

**8. Réponse API**
```json
{
  "id": 123,
  "utilisateur_id": 15,
  "utilisateur_nom": "Sébastien ACHKAR",
  "utilisateur_couleur": "#3B82F6",
  "chantier_id": 42,
  "chantier_nom": "Bâtiment commercial Tournon",
  "chantier_couleur": "#10B981",
  "date": "2026-01-30",
  "heure_debut": "08:00",
  "heure_fin": "17:00",
  "heures_prevues": 8.0,
  "note": "Travaux de maçonnerie",
  "type_affectation": "UNIQUE"
}
```

---

### 4.2 Création d'une Affectation RÉCURRENTE

#### Cas d'Usage
Affecter un compagnon à un chantier **toute la semaine** (Lun-Ven).

#### Étapes

**1. Saisie avec Récurrence**
```json
{
  "utilisateur_id": 20,
  "chantier_id": 50,
  "date": "2026-02-03",  // Lundi de la semaine
  "heure_debut": "07:30",
  "heure_fin": "16:30",
  "heures_prevues": 8.0,
  "type_affectation": "RECURRENTE",
  "jours_recurrence": ["LUNDI", "MARDI", "MERCREDI", "JEUDI", "VENDREDI"]
}
```

**2. Génération Automatique**

Le Use Case crée **5 affectations distinctes** (une par jour) :

```sql
INSERT INTO affectations VALUES
  (utilisateur=20, chantier=50, date='2026-02-03', ...),  -- Lundi
  (utilisateur=20, chantier=50, date='2026-02-04', ...),  -- Mardi
  (utilisateur=20, chantier=50, date='2026-02-05', ...),  -- Mercredi
  (utilisateur=20, chantier=50, date='2026-02-06', ...),  -- Jeudi
  (utilisateur=20, chantier=50, date='2026-02-07', ...);  -- Vendredi
```

**3. Particularités**
- Chaque affectation est **indépendante** (peut être modifiée/supprimée individuellement)
- Pas de lien "parent/enfant" en base
- Si modification d'une seule journée → modifier l'affectation spécifique uniquement

---

### 4.3 Modification d'une Affectation

#### Use Case
`UpdateAffectationUseCase`

#### Scénarios

**A. Changer le Chantier**
```json
PATCH /api/planning/affectations/123
{
  "chantier_id": 55
}
```

**B. Modifier les Horaires**
```json
PATCH /api/planning/affectations/123
{
  "heure_debut": "09:00",
  "heure_fin": "18:00",
  "heures_prevues": 8.0
}
```

**C. Ajouter/Modifier la Note**
```json
PATCH /api/planning/affectations/123
{
  "note": "Nouveau commentaire"
}
```

**Validations** :
- ✅ L'affectation existe
- ✅ L'utilisateur a les droits (chef du chantier OU admin/conducteur)
- ✅ Le nouveau chantier existe (si changement)
- ✅ heures_prevues > 0
- ✅ heure_fin > heure_debut

**Event** :
```python
AffectationUpdatedEvent(
    affectation_id=123,
    utilisateur_id=15,
    ancien_chantier_id=42,
    nouveau_chantier_id=55,
    date=date(2026, 1, 30),
)
```

---

### 4.4 Suppression d'une Affectation

#### Use Case
`DeleteAffectationUseCase`

#### Étapes

**1. Demande de Suppression**
```
DELETE /api/planning/affectations/123
```

**2. Validations**
- ✅ L'affectation existe
- ✅ L'utilisateur a les droits
- ⚠️ **IMPORTANT** : Vérifier si des pointages existent déjà pour cette affectation (FDH-10)

**3. Cas d'Usage : Affectation avec Pointages**

Si des pointages existent déjà (affectation dans le passé ou partiellement saisie) :

**Option A** : **Bloquer** la suppression (recommandé)
```json
{
  "error": "Impossible de supprimer : des heures ont déjà été saisies pour cette affectation",
  "pointages_count": 1
}
```

**Option B** : **Soft Delete** (marquer comme supprimée sans effacer)
```sql
UPDATE affectations
SET deleted_at = NOW()
WHERE id = 123;
```

**4. Suppression Réelle** (si aucun pointage)
```sql
DELETE FROM affectations WHERE id = 123;
```

**5. Event**
```python
AffectationDeletedEvent(
    affectation_id=123,
    utilisateur_id=15,
    chantier_id=42,
    date=date(2026, 1, 30),
)
```

---

### 4.5 Drag & Drop (Déplacement Visuel)

#### Fonctionnalité UI
Permet de déplacer visuellement un bloc d'affectation :
- **Verticalement** : Changer de chantier
- **Horizontalement** : Changer de date
- **Resize** : Modifier la durée (heures_prevues)

#### Backend Use Cases

**A. Déplacer vers un Autre Chantier (même date)**
→ `UpdateAffectationUseCase` avec `chantier_id` différent

**B. Déplacer vers un Autre Jour (même chantier)**
→ `UpdateAffectationUseCase` avec `date` différente

**C. Resize (Modifier Durée)**
→ `ResizeAffectationUseCase` avec nouvelles `heure_debut`/`heure_fin`/`heures_prevues`

**Validations Spécifiques** :
- ✅ Pas de conflit (double affectation)
- ✅ Date cible >= aujourd'hui (optionnel)
- ✅ Chantier cible ouvert/en cours

---

### 4.6 Duplication de Semaine

#### Cas d'Usage
Copier toutes les affectations de la **semaine N** vers la **semaine N+1**.

#### Use Case
`DuplicateAffectationsUseCase`

#### Étapes

**1. Requête**
```
POST /api/planning/duplicate
{
  "semaine_source": "2026-01-27",  // Lundi semaine source
  "semaine_cible": "2026-02-03",   // Lundi semaine cible
  "utilisateur_ids": [15, 20, 25]  // Optionnel : filtrer par utilisateurs
}
```

**2. Récupération Affectations Source**
```sql
SELECT * FROM affectations
WHERE date >= '2026-01-27'
  AND date <= '2026-02-02'
  AND (utilisateur_ids IS NULL OR utilisateur_id IN (15, 20, 25));
```

**3. Création Affectations Cibles**

Pour chaque affectation source :
- Calculer le décalage de jours (ex: +7 jours)
- Créer nouvelle affectation avec `date_cible = date_source + 7 jours`
- Conserver : chantier, horaires, heures_prevues, note

**4. Gestion Conflits**

Si affectation existe déjà pour (utilisateur, date_cible) :
- **Option A** : Ignorer (ne pas dupliquer)
- **Option B** : Écraser (supprimer existante)
- **Option C** : Erreur (bloquer duplication)

**Recommandation** : Option A (ignorer conflits)

**5. Réponse**
```json
{
  "affectations_dupliquees": 23,
  "affectations_ignorees": 2,
  "conflits": [
    {
      "utilisateur_id": 15,
      "date": "2026-02-03",
      "raison": "Affectation existante"
    }
  ]
}
```

---

### 4.7 Gestion des Absences

#### Scénario : Planifier des Congés

**1. Sélection Chantier Système**
```json
{
  "utilisateur_id": 15,
  "chantier_id": 1,  // CONGES
  "date": "2026-03-10",
  "type_affectation": "RECURRENTE",
  "jours_recurrence": ["LUNDI", "MARDI", "MERCREDI", "JEUDI", "VENDREDI"]
}
```

**2. Validation Spécifique**
- ⚠️ **Bloquer** si des affectations "réelles" existent déjà sur ces dates
- Message : "Impossible d'affecter à CONGES : le compagnon est déjà affecté au chantier X"

**3. Impact Synchronisation FDH**
- ❌ **AUCUN pointage** n'est créé automatiquement (FDH-10)
- Raison : Les absences ne génèrent pas d'heures de travail

**4. Affichage Planning**
- Couleur spécifique (ex: orange pour CONGES, rouge pour MALADIE)
- Badge "Absence" visible

---

## 5. Règles Métier

### 5.1 Règles de Validation

| Règle | Code | Validation |
|-------|------|------------|
| **Unicité** | RG-PLN-001 | Un utilisateur ne peut être affecté qu'à **un seul chantier** par jour |
| **Chronologie Horaires** | RG-PLN-002 | `heure_fin` DOIT être > `heure_debut` |
| **Heures Positives** | RG-PLN-003 | `heures_prevues` DOIT être > 0 |
| **Chantier Actif** | RG-PLN-004 | Impossible d'affecter à un chantier `fermé` ou `deleted_at != NULL` |
| **Utilisateur Actif** | RG-PLN-005 | Impossible d'affecter un utilisateur désactivé (`is_active = false`) |
| **Récurrence Cohérente** | RG-PLN-006 | Affectation RÉCURRENTE DOIT avoir `jours_recurrence` renseigné |
| **Conflit Absences** | RG-PLN-007 | Impossible d'affecter à un chantier système si affectation réelle existe |

---

### 5.2 Règles de Permissions

| Règle | Code | Description |
|-------|------|-------------|
| **Vue Globale** | RG-PERM-001 | Admin/Conducteur voient TOUT le planning |
| **Vue Restreinte Chef** | RG-PERM-002 | Chef voit uniquement ses chantiers (via `chantiers.chef_chantier_ids`) |
| **Vue Personnelle** | RG-PERM-003 | Compagnon voit uniquement son propre planning (`utilisateur_id = current_user_id`) |
| **Création Restreinte** | RG-PERM-004 | Chef peut affecter UNIQUEMENT sur ses chantiers |
| **Lecture Seule** | RG-PERM-005 | Compagnon en **lecture seule** (aucune action CREATE/UPDATE/DELETE) |

---

### 5.3 Règles de Calcul

#### Calcul Heures Prévues (Défaut)

Si `heures_prevues` n'est pas renseignée :

```python
if heure_debut and heure_fin:
    heures_prevues = heure_fin - heure_debut  # Ex: 17:00 - 08:00 = 9.0h
else:
    heures_prevues = 8.0  # Valeur par défaut (journée standard)
```

#### Calcul Charge Hebdomadaire

```python
charge_semaine = sum(affectation.heures_prevues for affectation in affectations_utilisateur)
```

---

## 6. Interactions Modules

### 6.1 Planning → Pointages (FDH-10)

**Synchronisation Automatique** : Lors de la consultation d'une feuille d'heures, les pointages sont créés automatiquement depuis le planning.

#### Use Case
`BulkCreateFromPlanningUseCase` (module pointages)

#### Déclencheur
Lorsqu'un compagnon ouvre sa feuille d'heures pour une semaine :
```
GET /api/pointages/feuilles-heures/utilisateur/15/semaine/2026-01-27
```

#### Processus

**1. Récupération Affectations**
```sql
SELECT * FROM affectations
WHERE utilisateur_id = 15
  AND date >= '2026-01-27'
  AND date <= '2026-02-02'
  AND chantier_id NOT IN (SELECT id FROM chantiers WHERE code IN ('CONGES', 'MALADIE', 'RTT', 'FORMATION'));
```

**2. Création Pointages**

Pour chaque affectation (si pointage n'existe pas déjà) :
```sql
INSERT INTO pointages (
  utilisateur_id, chantier_id, date_pointage,
  heures_normales, heures_supplementaires,
  statut, created_by
) VALUES (
  15, 42, '2026-01-30',
  affectation.heures_prevues, 0,  -- Pré-rempli avec heures prévues
  'BROUILLON', 15
);
```

**3. Règles Importantes**
- ❌ **AUCUN pointage** pour chantiers système (CONGES, MALADIE, etc.)
- ✅ Statut initial : **BROUILLON** (modifiable par le compagnon)
- ✅ `heures_normales` pré-rempli avec `affectation.heures_prevues`
- ✅ Idempotence : Si pointage existe déjà → ne pas recréer

---

### 6.2 Planning → Planning de Charge

**Calcul de Charge** : Le module `planning_charge` agrège les `heures_prevues` par métier.

#### Flux

**1. Récupération Affectations par Métier**
```sql
SELECT
  u.metier,
  SUM(a.heures_prevues) as total_heures,
  a.date
FROM affectations a
JOIN users u ON a.utilisateur_id = u.id
WHERE a.date >= '2026-01-27'
  AND a.date <= '2026-02-02'
GROUP BY u.metier, a.date;
```

**2. Calcul Capacité Disponible**
```sql
SELECT
  metier,
  COUNT(*) as nb_compagnons,
  COUNT(*) * 40 as capacite_hebdo  -- 40h/semaine standard
FROM users
WHERE role = 'COMPAGNON'
  AND is_active = true
GROUP BY metier;
```

**3. Calcul Taux Occupation**
```python
taux_occupation = (total_heures_affectees / capacite_hebdo) * 100
```

**4. Alertes**
- 🟢 Taux < 80% : Sous-charge (disponibilité)
- 🟡 Taux 80-100% : Charge optimale
- 🔴 Taux > 100% : Surcharge (besoin intérim/recrutement)

---

### 6.3 Planning → Chantiers

**Récupération Infos Chantier** pour enrichissement DTOs :

```python
chantier_info = get_chantier_info(chantier_id)
# Retourne : { "nom": "...", "couleur": "#...", "statut": "..." }
```

**Filtrage Chantiers Disponibles** :
```sql
SELECT * FROM chantiers
WHERE statut IN ('ouvert', 'en_cours')
  AND deleted_at IS NULL
ORDER BY nom;
```

---

### 6.4 Planning → Auth (Utilisateurs)

**Récupération Infos Utilisateur** :

```python
user_info = get_user_info(utilisateur_id)
# Retourne : { "nom": "Prénom NOM", "couleur": "#...", "metier": "Maçon" }
```

**Filtrage Utilisateurs Disponibles** (Chef de Chantier) :
```sql
-- Récupérer uniquement les utilisateurs déjà affectés aux chantiers du chef
SELECT DISTINCT u.*
FROM users u
JOIN affectations a ON u.id = a.utilisateur_id
WHERE a.chantier_id IN (
  SELECT id FROM chantiers
  WHERE chef_chantier_ids LIKE '%"' || :chef_id || '"%'
);
```

---

### 6.5 Planning → Notifications

**Events Déclenchant Notifications** :

| Event | Notification | Destinataire |
|-------|--------------|--------------|
| `AffectationCreatedEvent` | "Vous êtes affecté au chantier X le Y" | Compagnon concerné |
| `AffectationUpdatedEvent` | "Votre affectation au chantier X a été modifiée" | Compagnon concerné |
| `AffectationDeletedEvent` | "Votre affectation au chantier X le Y a été annulée" | Compagnon concerné |

**Canaux** :
- 📱 Push notification (prioritaire)
- 📧 Email (optionnel selon préférences)

---

## 7. Architecture Technique

### 7.1 Structure Clean Architecture

```
┌─────────────────────────────────────────┐
│ INFRASTRUCTURE                           │
│ • SQLAlchemyAffectationRepository       │
│ • Persistence avec modèles SQLAlchemy   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ APPLICATION (Use Cases)                  │
│ • CreateAffectationUseCase              │
│ • UpdateAffectationUseCase              │
│ • DeleteAffectationUseCase              │
│ • GetPlanningUseCase                    │
│ • DuplicateAffectationsUseCase          │
│ • ResizeAffectationUseCase              │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ DOMAIN                                   │
│ • Affectation (Entity)                  │
│ • HeureAffectation (Value Object)       │
│ • TypeAffectation (UNIQUE/RECURRENTE)   │
│ • JourSemaine (LUNDI, MARDI, ...)       │
│ • AffectationRepository (Interface)     │
│ • Events (Created, Updated, Deleted)    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ ADAPTERS (Controllers)                   │
│ • PlanningController                     │
│ • Conversion Entity ↔ DTO               │
│ • Gestion permissions (rôles)           │
└─────────────────────────────────────────┘
```

---

### 7.2 Entité Domain `Affectation`

**Fichier** : `backend/modules/planning/domain/entities/affectation.py`

```python
@dataclass
class Affectation:
    utilisateur_id: int
    chantier_id: int
    date: date
    created_by: int

    id: Optional[int] = None
    heure_debut: Optional[HeureAffectation] = None
    heure_fin: Optional[HeureAffectation] = None
    heures_prevues: float = 8.0
    note: Optional[str] = None
    type_affectation: TypeAffectation = TypeAffectation.UNIQUE
    jours_recurrence: Optional[List[JourSemaine]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        # Validation IDs positifs
        # Validation heure_fin > heure_debut
        # Validation cohérence type/récurrence
```

---

### 7.3 Use Case Pattern (Exemple : CreateAffectation)

**Fichier** : `backend/modules/planning/application/use_cases/create_affectation.py`

```python
class CreateAffectationUseCase:
    def __init__(
        self,
        affectation_repo: AffectationRepository,
        event_publisher: Optional[Callable] = None,
    ):
        self.affectation_repo = affectation_repo
        self.event_publisher = event_publisher

    def execute(
        self,
        dto: CreateAffectationDTO,
        created_by: int,
    ) -> AffectationDTO:
        # 1. Validation règles métier
        self._validate(dto)

        # 2. Vérification conflits
        if self._has_conflict(dto):
            raise AffectationConflictError(...)

        # 3. Création entité domain
        affectation = Affectation(
            utilisateur_id=dto.utilisateur_id,
            chantier_id=dto.chantier_id,
            date=dto.date,
            heure_debut=dto.heure_debut,
            heure_fin=dto.heure_fin,
            heures_prevues=dto.heures_prevues,
            note=dto.note,
            type_affectation=dto.type_affectation,
            jours_recurrence=dto.jours_recurrence,
            created_by=created_by,
        )

        # 4. Persistence
        if dto.type_affectation == TypeAffectation.RECURRENTE:
            affectations = self._create_recurrence(affectation, dto.jours_recurrence)
        else:
            affectations = [self.affectation_repo.save(affectation)]

        # 5. Event
        if self.event_publisher:
            for aff in affectations:
                event = AffectationCreatedEvent(
                    affectation_id=aff.id,
                    utilisateur_id=aff.utilisateur_id,
                    chantier_id=aff.chantier_id,
                    date=aff.date,
                )
                self.event_publisher(event)

        # 6. Retour DTO
        return [AffectationDTO.from_entity(aff) for aff in affectations]
```

---

### 7.4 Repository Interface

**Fichier** : `backend/modules/planning/domain/repositories/affectation_repository.py`

```python
class AffectationRepository(ABC):
    @abstractmethod
    def save(self, affectation: Affectation) -> Affectation:
        """Sauvegarde une affectation."""
        pass

    @abstractmethod
    def find_by_id(self, affectation_id: int) -> Optional[Affectation]:
        """Récupère une affectation par son ID."""
        pass

    @abstractmethod
    def find_by_date_range(
        self, date_debut: date, date_fin: date
    ) -> List[Affectation]:
        """Récupère les affectations sur une période."""
        pass

    @abstractmethod
    def find_by_utilisateur_and_date(
        self, utilisateur_id: int, date: date
    ) -> Optional[Affectation]:
        """Vérifie si une affectation existe déjà pour un utilisateur et une date."""
        pass

    @abstractmethod
    def delete(self, affectation_id: int) -> None:
        """Supprime une affectation."""
        pass
```

---

## 8. Scénarios de Test

### 8.1 Tests Unitaires (Use Cases)

#### Test : Création Affectation Unique Valide

```python
def test_create_affectation_unique_success():
    # Arrange
    dto = CreateAffectationDTO(
        utilisateur_id=15,
        chantier_id=42,
        date=date(2026, 1, 30),
        heures_prevues=8.0,
        type_affectation=TypeAffectation.UNIQUE,
    )
    use_case = CreateAffectationUseCase(mock_repo)

    # Act
    result = use_case.execute(dto, created_by=1)

    # Assert
    assert result.utilisateur_id == 15
    assert result.chantier_id == 42
    assert mock_repo.save.called_once()
```

#### Test : Détection Conflit Double Affectation

```python
def test_create_affectation_conflict_error():
    # Arrange
    mock_repo.find_by_utilisateur_and_date.return_value = existing_affectation
    dto = CreateAffectationDTO(
        utilisateur_id=15,
        chantier_id=50,  # Chantier différent
        date=date(2026, 1, 30),  # Même date
    )
    use_case = CreateAffectationUseCase(mock_repo)

    # Act & Assert
    with pytest.raises(AffectationConflictError) as exc:
        use_case.execute(dto, created_by=1)

    assert "déjà affecté" in str(exc.value)
```

#### Test : Création Récurrence Génère N Affectations

```python
def test_create_affectation_recurrence_generates_5_affectations():
    # Arrange
    dto = CreateAffectationDTO(
        utilisateur_id=20,
        chantier_id=42,
        date=date(2026, 2, 3),  # Lundi
        type_affectation=TypeAffectation.RECURRENTE,
        jours_recurrence=[
            JourSemaine.LUNDI,
            JourSemaine.MARDI,
            JourSemaine.MERCREDI,
            JourSemaine.JEUDI,
            JourSemaine.VENDREDI,
        ],
    )
    use_case = CreateAffectationUseCase(mock_repo)

    # Act
    results = use_case.execute(dto, created_by=1)

    # Assert
    assert len(results) == 5
    assert results[0].date == date(2026, 2, 3)  # Lundi
    assert results[4].date == date(2026, 2, 7)  # Vendredi
```

---

### 8.2 Tests d'Intégration (API)

#### Test : GET Planning avec Filtre Rôle Chef

```python
def test_get_planning_chef_sees_only_his_chantiers():
    # Arrange
    client.auth_as(user_id=5, role="chef_chantier")

    # Act
    response = client.get("/api/planning?date_debut=2026-01-27&date_fin=2026-02-02")

    # Assert
    assert response.status_code == 200
    affectations = response.json()

    # Vérifier que TOUS les chantiers retournés sont bien ceux du chef
    chef_chantiers = [10, 20, 30]  # Chantiers du chef ID=5
    for aff in affectations:
        assert aff["chantier_id"] in chef_chantiers
```

#### Test : POST Création Affectation Envoie Notification

```python
def test_create_affectation_sends_notification():
    # Arrange
    mock_notification_service = Mock()
    dto = {
        "utilisateur_id": 15,
        "chantier_id": 42,
        "date": "2026-01-30",
    }

    # Act
    response = client.post("/api/planning/affectations", json=dto)

    # Assert
    assert response.status_code == 201
    assert mock_notification_service.send_push.called_once_with(
        user_id=15,
        title="Nouvelle affectation",
        message=contains("Tournon"),
    )
```

---

### 8.3 Tests End-to-End (Scénarios Utilisateur)

#### Scénario : Chef Planifie sa Semaine Complète

```gherkin
Feature: Planification hebdomadaire par Chef de Chantier

Scenario: Affecter 3 compagnons sur un chantier pour toute la semaine
  Given je suis connecté en tant que Chef de Chantier (ID=5)
  And le chantier "TOURNON-COMMERCIAL" (ID=42) est affecté à moi
  And les compagnons [15, 20, 25] sont disponibles

  When je crée une affectation RÉCURRENTE pour le compagnon 15
    | chantier_id      | 42                        |
    | date             | 2026-02-03                |
    | type_affectation | RECURRENTE                |
    | jours_recurrence | Lun, Mar, Mer, Jeu, Ven   |
    | heures_prevues   | 8.0                       |

  And je crée une affectation RÉCURRENTE pour le compagnon 20
    | chantier_id      | 42                        |
    | date             | 2026-02-03                |
    | type_affectation | RECURRENTE                |
    | jours_recurrence | Lun, Mar, Mer, Jeu, Ven   |
    | heures_prevues   | 8.0                       |

  And je crée une affectation RÉCURRENTE pour le compagnon 25
    | chantier_id      | 42                        |
    | date             | 2026-02-03                |
    | type_affectation | RECURRENTE                |
    | jours_recurrence | Lun, Mar, Mer             |
    | heures_prevues   | 8.0                       |

  Then le planning affiche :
    | Utilisateur | Lun | Mar | Mer | Jeu | Ven |
    | Compagnon 15 | ✅  | ✅  | ✅  | ✅  | ✅  |
    | Compagnon 20 | ✅  | ✅  | ✅  | ✅  | ✅  |
    | Compagnon 25 | ✅  | ✅  | ✅  | ❌  | ❌  |

  And 13 affectations ont été créées au total
  And 3 notifications push ont été envoyées
```

---

## 9. Points d'Attention

### 9.1 Performance

#### Problème N+1 - Enrichissement

**Symptôme** : Lors du chargement du planning, une requête SQL par affectation pour récupérer les infos utilisateur/chantier.

**Solution Implémentée** :

```python
# ❌ MAUVAIS (N+1)
for affectation in affectations:
    user_info = get_user_info(affectation.utilisateur_id)  # 1 requête par affectation
    chantier_info = get_chantier_info(affectation.chantier_id)

# ✅ BON (Batch avec cache)
user_ids = {a.utilisateur_id for a in affectations}
chantier_ids = {a.chantier_id for a in affectations}

user_cache = {uid: get_user_info(uid) for uid in user_ids}  # N requêtes au lieu de M
chantier_cache = {cid: get_chantier_info(cid) for cid in chantier_ids}

for affectation in affectations:
    affectation.user_info = user_cache.get(affectation.utilisateur_id)
    affectation.chantier_info = chantier_cache.get(affectation.chantier_id)
```

**Fichier** : `get_planning.py` ligne 180+

---

### 9.2 Gestion des Conflits

#### Double Affectation Accidentelle

**Risque** : Deux chefs affectent le même compagnon sur deux chantiers différents à la même date.

**Solution** :
- Validation **AVANT insertion** dans le Use Case
- Contrainte unique en base : `UNIQUE(utilisateur_id, date)` (recommandé)
- Message d'erreur explicite

---

### 9.3 Synchronisation Planning ↔ Pointages

#### Cohérence des Données

**Problème** : Si une affectation est supprimée APRÈS création du pointage, que se passe-t-il ?

**Scénarios** :

**Cas 1** : Affectation future (pas encore de pointage)
→ ✅ Suppression simple OK

**Cas 2** : Affectation passée avec pointage BROUILLON
→ ⚠️ Supprimer affectation OU pointage ? **Recommandation** : Soft delete affectation, conserver pointage

**Cas 3** : Affectation passée avec pointage VALIDÉ
→ ❌ **BLOQUER** la suppression (heures déjà validées/payées)

**Règle Métier Recommandée** :
```python
if pointage.statut in [StatutPointage.VALIDE, StatutPointage.SOUMIS]:
    raise CannotDeleteAffectationError(
        "Impossible de supprimer : des heures validées existent"
    )
```

---

### 9.4 Permissions Complexes (Chef de Chantier)

#### Récupération Chantiers du Chef

**Modèle Chantier** :
```python
class Chantier:
    chef_chantier_ids: List[int]  # JSON array [5, 10, 15]
```

**Requête SQL** :
```sql
SELECT * FROM chantiers
WHERE chef_chantier_ids LIKE '%"5"%'  -- Chef ID = 5
  AND deleted_at IS NULL;
```

**⚠️ Attention** : `LIKE` sur JSON pas optimal. Alternatives :
- PostgreSQL : `chef_chantier_ids @> '[5]'::jsonb`
- SQLite : Utiliser JSON_EXTRACT

---

### 9.5 Mode Offline (Frontend)

**Problématique** : Comment gérer les affectations créées offline ?

**Solution Recommandée** :
1. Stockage local (IndexedDB) des affectations créées offline
2. Flag `pending_sync = true`
3. Synchronisation automatique au retour de connexion
4. Gestion conflits (affectation créée entre temps par autre utilisateur)

**Non implémenté actuellement** - Évolution future.

---

## 📊 Métriques & KPIs

### KPIs Métier

| Métrique | Définition | Objectif |
|----------|------------|----------|
| **Taux d'occupation** | (Heures affectées / Heures disponibles) * 100 | 85-95% |
| **Délai planification** | Temps moyen entre création chantier et première affectation | < 2 jours |
| **Taux modification** | Nb modifications / Nb créations | < 20% |
| **Conflits détectés** | Nb tentatives double affectation | 0 (validation stricte) |

### KPIs Techniques

| Métrique | Définition | Objectif |
|----------|------------|----------|
| **Temps réponse GET planning** | API `/api/planning?date_debut=...` | < 500ms (50 affectations) |
| **Temps création affectation** | POST `/api/planning/affectations` | < 200ms |
| **Nombre requêtes SQL** | Par chargement planning | < 10 (avec cache) |

---

## 🔗 Références

### Documentation Liée

- `WORKFLOW_FEUILLES_HEURES.md` - Synchronisation FDH-10
- `WORKFLOW_PLANNING_CHARGE.md` - Calcul capacitaire (à créer)
- `docs/SPECIFICATIONS.md` - Section 5 (PLN-01 à PLN-28)

### Fichiers Clés

**Domain** :
- `backend/modules/planning/domain/entities/affectation.py`
- `backend/modules/planning/domain/value_objects/type_affectation.py`
- `backend/modules/planning/domain/repositories/affectation_repository.py`

**Application** :
- `backend/modules/planning/application/use_cases/create_affectation.py`
- `backend/modules/planning/application/use_cases/get_planning.py`
- `backend/modules/planning/application/use_cases/duplicate_affectations.py`

**Infrastructure** :
- `backend/modules/planning/infrastructure/persistence/sqlalchemy_affectation_repository.py`

**Frontend** :
- `frontend/src/pages/PlanningPage.tsx`
- `frontend/src/components/planning/WeekView.tsx`

---

## ✅ Conclusion

Le **Planning Opérationnel** est le workflow le plus complexe de Hub Chantier car il :
- Centralise les affectations de toutes les équipes
- Interagit avec 6 autres modules (Pointages, Planning Charge, Chantiers, Auth, Notifications, GED)
- Gère des règles métier strictes (unicité, permissions, récurrence)
- Doit garantir une performance élevée (chargement planning < 500ms)
- Synchronise automatiquement avec les feuilles d'heures (FDH-10)

**Architecture Clean** : Le module respecte scrupuleusement les principes de Clean Architecture et sert de **référence** pour les autres modules.

**Prochaines évolutions** :
- Mode offline (synchronisation)
- Optimisation requêtes SQL (PostgreSQL JSONB)
- Alertes proactives (surcharge détectée)
- Vue calendrier mensuelle (en plus de hebdomadaire)

---

**Dernière mise à jour** : 30 janvier 2026
**Version** : 1.0
