# Workflow : Cycle de Vie d'un Chantier

**Complexité** : ⭐⭐⭐⭐
**Module** : `backend/modules/chantiers`
**Date** : 30 janvier 2026
**Statut** : ✅ Documenté

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Acteurs et permissions](#2-acteurs-et-permissions)
3. [États et transitions](#3-états-et-transitions)
4. [Workflows détaillés](#4-workflows-détaillés)
5. [Règles métier](#5-règles-métier)
6. [Interactions avec autres modules](#6-interactions-avec-autres-modules)
7. [Architecture technique](#7-architecture-technique)
8. [Scénarios de test](#8-scénarios-de-test)
9. [Points d'attention](#9-points-dattention)

---

## 1. Vue d'ensemble

### 1.1 Définition

Le **Cycle de Vie d'un Chantier** représente l'ensemble des phases par lesquelles passe un chantier depuis sa création jusqu'à sa clôture définitive. Ce workflow gère :

- La création d'un nouveau chantier
- Les changements de statut selon les règles métier
- L'assignation et le retrait des responsables
- Les modifications des informations du chantier
- La clôture et l'archivage

### 1.2 Objectifs métier

| Objectif | Description |
|----------|-------------|
| **Traçabilité** | Suivre toutes les phases d'un chantier de bout en bout |
| **Contrôle** | Empêcher les transitions illégales de statut |
| **Responsabilisation** | Assigner clairement les conducteurs et chefs de chantier |
| **Planification** | Gérer les dates prévisionnelles et réelles |
| **Intégration** | Synchroniser avec planning, pointages, documents |

### 1.3 Périmètre fonctionnel

**Inclus** :
- Création chantier avec génération automatique de code
- Machine à états (OUVERT → EN_COURS → RECEPTIONNE → FERME)
- Assignation/retrait conducteurs et chefs de chantier
- Modification informations (adresse, dates, description, etc.)
- Suppression (soft delete) avec cascade

**Exclus** :
- Gestion documentaire (GED) → module `documents`
- Planification équipes → module `planning`
- Pointages et feuilles d'heures → module `pointages`
- Formulaires et signalements → modules `formulaires`, `signalements`

### 1.4 Références CDC

| CDC ID | Fonctionnalité | Implémenté |
|--------|----------------|------------|
| CHT-01 | Fiche Chantier Complète | ✅ |
| CHT-02 | Code Couleur | ✅ |
| CHT-03 | Localisation GPS | ✅ |
| CHT-04 | Photo de Couverture | ✅ |
| CHT-05 | Conducteur de Travaux | ✅ |
| CHT-06 | Chef de Chantier | ✅ |
| CHT-07 | Contact Principal | ✅ |
| CHT-19 | Identifiant Unique | ✅ |
| CHT-20 | Dates Prévisionnelles | ✅ |
| CHT-21 | Statuts de Chantier | ✅ |

---

## 2. Acteurs et permissions

### 2.1 Rôles

| Rôle | Permissions | Restrictions |
|------|-------------|--------------|
| **Admin** | Toutes opérations | - |
| **Conducteur** | Créer, modifier, démarrer, fermer | Uniquement ses chantiers |
| **Chef de chantier** | Modifier, consulter | Uniquement chantiers assignés |
| **Compagnon** | Consulter | Chantiers où il a affectations |
| **Client (externe)** | Consulter | Chantiers avec accès partagé |

### 2.2 Permissions détaillées

```python
# backend/modules/chantiers/domain/entities/chantier.py

PERMISSIONS = {
    "ADMIN": ["create", "read", "update", "delete", "change_statut", "assign_responsable"],
    "CONDUCTEUR": ["create", "read", "update", "change_statut", "assign_responsable"],
    "CHEF_CHANTIER": ["read", "update"],
    "COMPAGNON": ["read"],
    "CLIENT": ["read"],
}
```

**Règles supplémentaires** :
- Un conducteur ne peut modifier que les chantiers où il est assigné
- Un chef de chantier ne peut modifier que les chantiers où il est assigné
- Les transitions de statut vers `FERME` nécessitent validation admin
- La suppression nécessite validation admin

---

## 3. États et transitions

### 3.1 Machine à états

```
┌─────────┐
│ OUVERT  │ (Initial)
└────┬────┘
     │
     ├─────► demarrer() ────► ┌───────────┐
     │                         │ EN_COURS  │
     │                         └─────┬─────┘
     │                               │
     │                               ├─────► receptionner() ────► ┌──────────────┐
     │                               │                             │ RECEPTIONNE  │
     │                               │                             └──────┬───────┘
     │                               │                                    │
     └───────────────────────────────┴────────────────────────────────────┴────► fermer() ────► ┌────────┐
                                                                                                  │ FERME  │
                                                                                                  └────────┘
                                                                                                  (Terminal)
```

### 3.2 Définition des statuts

**Fichier** : `backend/modules/chantiers/domain/value_objects/statut_chantier.py:12-24`

| Statut | Description | Transitions autorisées |
|--------|-------------|------------------------|
| **OUVERT** | Chantier créé, non démarré | → EN_COURS, → FERME |
| **EN_COURS** | Chantier actif, travaux en cours | → RECEPTIONNE, → FERME |
| **RECEPTIONNE** | Travaux terminés, réception client effectuée | → EN_COURS, → FERME |
| **FERME** | Chantier clôturé définitivement | (aucune) |

### 3.3 Règles de transition

**Fichier** : `backend/modules/chantiers/domain/value_objects/statut_chantier.py:26-34`

```python
TRANSITIONS = {
    "ouvert": ["en_cours", "ferme"],
    "en_cours": ["receptionne", "ferme"],
    "receptionne": ["en_cours", "ferme"],
    "ferme": [],
}
```

**Validation** :

```python
def can_transition_to(self, nouveau_statut: "StatutChantier") -> bool:
    """Vérifie si la transition est autorisée."""
    return nouveau_statut.value in TRANSITIONS.get(self.value, [])
```

### 3.4 Propriétés métier

**Fichier** : `backend/modules/chantiers/domain/value_objects/statut_chantier.py:56-75`

| Propriété | Description | Valeurs |
|-----------|-------------|---------|
| `is_active()` | Chantier actif (pointages autorisés) | OUVERT, EN_COURS, RECEPTIONNE |
| `allows_modifications()` | Modifications autorisées | OUVERT, EN_COURS |
| `is_closed()` | Chantier fermé | FERME |

**Utilisation** :

```python
# Vérifier si on peut pointer des heures
if chantier.statut.is_active():
    # Autoriser création pointages
    pass

# Vérifier si on peut modifier le chantier
if not chantier.statut.allows_modifications():
    raise ValueError("Impossible de modifier un chantier fermé")
```

---

## 4. Workflows détaillés

### 4.1 Création d'un chantier

**Use Case** : `CreateChantierUseCase`
**Fichier** : `backend/modules/chantiers/application/use_cases/create_chantier.py:63-91`

#### 4.1.1 Flux nominal

```
┌──────────┐     ┌─────────────────┐     ┌──────────────┐     ┌──────────────┐     ┌─────────┐
│ Frontend │────►│ ChantierController│────►│ CreateChantier│────►│ ChantierRepo │────►│ Database│
└──────────┘     └─────────────────┘     │   UseCase      │     └──────────────┘     └─────────┘
                                          └────────────────┘
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │ EventPublisher│
                                          └──────────────┘
                                          (ChantierCreatedEvent)
```

**Étapes** :

1. **Validation DTO** (ligne 78)
   - Nom obligatoire
   - Adresse obligatoire
   - Dates cohérentes (fin >= début)

2. **Génération code** (lignes 93-102)
   ```python
   if dto.code:
       # Code fourni → vérifier unicité
       code = CodeChantier(dto.code)
       if self.chantier_repo.exists_by_code(code):
           raise CodeChantierAlreadyExistsError(dto.code)
   else:
       # Auto-génération (A001, A002, ..., A999, B001, ...)
       last_code = self.chantier_repo.get_last_code()
       code = CodeChantier.generate_next(last_code)
   ```

3. **Parsing coordonnées GPS** (lignes 104-113)
   - Si latitude + longitude fournis → CoordonneesGPS
   - Sinon → None

4. **Parsing contact** (lignes 115-122)
   - Si nom + téléphone fournis → ContactChantier
   - Sinon → None

5. **Validation dates** (lignes 124-141)
   ```python
   if date_debut and date_fin and date_fin < date_debut:
       raise InvalidDatesError("Date fin < date début")
   ```

6. **Création entité** (lignes 149-175)
   ```python
   chantier = Chantier(
       code=code,
       nom=dto.nom,
       adresse=dto.adresse,
       statut=StatutChantier.ouvert(),  # ← TOUJOURS "OUVERT" à la création
       couleur=couleur or Couleur.default(),
       coordonnees_gps=coordonnees_gps,
       contact=contact,
       date_debut=date_debut,
       date_fin=date_fin,
       conducteur_ids=list(dto.conducteur_ids or []),
       chef_chantier_ids=list(dto.chef_chantier_ids or []),
   )
   ```

7. **Sauvegarde** (ligne 88)
   ```python
   chantier = self.chantier_repo.save(chantier)
   ```

8. **Publication event** (lignes 177-188)
   ```python
   event = ChantierCreatedEvent(
       chantier_id=chantier.id,
       code=str(chantier.code),
       nom=chantier.nom,
       statut="ouvert",
       conducteur_ids=tuple(chantier.conducteur_ids),
       chef_chantier_ids=tuple(chantier.chef_chantier_ids),
   )
   self.event_publisher(event)
   ```

#### 4.1.2 Exemple de création

**Requête HTTP** :

```http
POST /api/chantiers
Content-Type: application/json
Authorization: Bearer <token>

{
  "nom": "Rénovation Mairie - Montmélian",
  "adresse": "123 Avenue de la République, 73800 Montmélian",
  "description": "Rénovation complète de la façade et des bureaux",
  "code": "2026-01-MONTMELIAN",
  "couleur": "#3B82F6",
  "latitude": 45.5036,
  "longitude": 6.0565,
  "contact_nom": "M. Jean DUPONT",
  "contact_telephone": "04 79 XX XX XX",
  "heures_estimees": 450.0,
  "date_debut": "2026-02-01",
  "date_fin": "2026-05-31",
  "conducteur_ids": [3],
  "chef_chantier_ids": [7]
}
```

**Réponse** :

```json
{
  "id": 28,
  "code": "2026-01-MONTMELIAN",
  "nom": "Rénovation Mairie - Montmélian",
  "adresse": "123 Avenue de la République, 73800 Montmélian",
  "statut": "ouvert",
  "couleur": "#3B82F6",
  "coordonnees_gps": {
    "latitude": 45.5036,
    "longitude": 6.0565
  },
  "contact": {
    "nom": "M. Jean DUPONT",
    "telephone": "04 79 XX XX XX"
  },
  "heures_estimees": 450.0,
  "date_debut": "2026-02-01",
  "date_fin": "2026-05-31",
  "conducteur_ids": [3],
  "chef_chantier_ids": [7],
  "created_at": "2026-01-30T14:23:00Z",
  "updated_at": "2026-01-30T14:23:00Z"
}
```

#### 4.1.3 Cas d'erreur

| Erreur | Code HTTP | Message |
|--------|-----------|---------|
| Code déjà existant | 409 Conflict | `Le code chantier 2026-01-MONTMELIAN est déjà utilisé` |
| Date fin < date début | 400 Bad Request | `La date de fin ne peut pas être antérieure à la date de début` |
| Nom vide | 400 Bad Request | `Le nom du chantier est obligatoire` |
| Format code invalide | 400 Bad Request | `Format de code chantier invalide: XYZ` |

---

### 4.2 Démarrage d'un chantier (OUVERT → EN_COURS)

**Use Case** : `ChangeStatutUseCase.demarrer()`
**Fichier** : `backend/modules/chantiers/application/use_cases/change_statut.py:102-112`

#### 4.2.1 Flux nominal

```
┌──────────┐     ┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│ Frontend │────►│ ChantierController│────►│ ChangeStatut │────►│ ChantierRepo │
└──────────┘     └─────────────────┘     │   UseCase     │     └──────────────┘
      │                                   └───────┬──────┘
      │                                           │
      │                                           ▼
      │                                   chantier.change_statut(EN_COURS)
      │                                           │
      │                                           ▼
      │                                   ┌──────────────┐
      │                                   │ Validation   │
      │                                   │ transition   │
      │                                   └──────┬───────┘
      │                                          │
      │                                          ▼ OK
      │                                   ┌──────────────┐
      │                                   │ Save + Event │
      │                                   └──────────────┘
      │                                   (ChantierStatutChangedEvent)
      │
      └─────────────────► Réponse ChantierDTO
```

**Étapes** :

1. **Récupération chantier** (lignes 71-73)
   ```python
   chantier = self.chantier_repo.find_by_id(chantier_id)
   if not chantier:
       raise ChantierNotFoundError(chantier_id)
   ```

2. **Validation transition** (lignes 82-85)
   ```python
   try:
       chantier.change_statut(StatutChantier.en_cours())
   except ValueError as e:
       raise TransitionNonAutoriseeError("ouvert", "en_cours") from e
   ```

3. **Sauvegarde** (ligne 88)
   ```python
   chantier = self.chantier_repo.save(chantier)
   ```

4. **Publication event** (lignes 91-98)
   ```python
   event = ChantierStatutChangedEvent(
       chantier_id=chantier.id,
       code=str(chantier.code),
       ancien_statut="ouvert",
       nouveau_statut="en_cours",
   )
   self.event_publisher(event)
   ```

#### 4.2.2 Exemple de démarrage

**Requête HTTP** :

```http
PATCH /api/chantiers/28/statut
Content-Type: application/json
Authorization: Bearer <token>

{
  "nouveau_statut": "en_cours"
}
```

**Ou via raccourci** :

```http
POST /api/chantiers/28/demarrer
Authorization: Bearer <token>
```

**Réponse** :

```json
{
  "id": 28,
  "code": "2026-01-MONTMELIAN",
  "statut": "en_cours",
  "updated_at": "2026-02-01T08:00:00Z"
}
```

#### 4.2.3 Effets de bord

Quand un chantier passe EN_COURS :

1. **Planning** : Affectations deviennent actives
2. **Pointages** : Compagnons peuvent pointer
3. **Notifications** : Email aux conducteurs et chefs de chantier
4. **Dashboard** : Chantier apparaît dans "Chantiers actifs"

---

### 4.3 Réception d'un chantier (EN_COURS → RECEPTIONNE)

**Use Case** : `ChangeStatutUseCase.receptionner()`
**Fichier** : `backend/modules/chantiers/application/use_cases/change_statut.py:114-124`

#### 4.3.1 Prérequis métier

Avant de réceptionner un chantier, vérifier :

- [ ] Tous les formulaires obligatoires remplis
- [ ] Tous les documents finaux uploadés (DOE, PV réception, etc.)
- [ ] Pas de signalements ouverts critiques
- [ ] Heures pointées validées
- [ ] Photos finales prises

**Note** : Ces vérifications sont actuellement manuelles (conducteur). Une future évolution pourrait ajouter des règles automatiques.

#### 4.3.2 Flux nominal

**Requête HTTP** :

```http
POST /api/chantiers/28/receptionner
Authorization: Bearer <token>
```

**Réponse** :

```json
{
  "id": 28,
  "code": "2026-01-MONTMELIAN",
  "statut": "receptionne",
  "updated_at": "2026-05-31T17:00:00Z"
}
```

#### 4.3.3 Effets de bord

Quand un chantier passe RECEPTIONNE :

1. **Planning** : Affectations futures bloquées
2. **Pointages** : Pointages encore possibles (corrections)
3. **Documents** : PV de réception généré (si configuré)
4. **Notifications** : Email admin + conducteur
5. **Dashboard** : Chantier apparaît dans "Chantiers réceptionnés"

---

### 4.4 Réouverture d'un chantier (RECEPTIONNE → EN_COURS)

**Use Case** : `ChangeStatutUseCase.execute()`
**Fichier** : `backend/modules/chantiers/application/use_cases/change_statut.py:54-100`

#### 4.4.1 Cas d'usage

Un chantier réceptionné peut être réouvert en cas de :

- Travaux supplémentaires demandés par le client
- Réserves à lever après réception
- Garantie / SAV nécessitant intervention

#### 4.4.2 Flux nominal

**Requête HTTP** :

```http
PATCH /api/chantiers/28/statut
Content-Type: application/json
Authorization: Bearer <token>

{
  "nouveau_statut": "en_cours"
}
```

**Réponse** :

```json
{
  "id": 28,
  "code": "2026-01-MONTMELIAN",
  "statut": "en_cours",
  "updated_at": "2026-06-15T09:00:00Z"
}
```

**⚠️ Attention** : Transition rare, nécessite validation admin en production.

---

### 4.5 Clôture définitive (* → FERME)

**Use Case** : `ChangeStatutUseCase.fermer()`
**Fichier** : `backend/modules/chantiers/application/use_cases/change_statut.py:126-136`

#### 4.5.1 Prérequis métier

Avant de fermer un chantier, vérifier :

- [ ] Chantier réceptionné (recommandé)
- [ ] Toutes les factures émises
- [ ] Tous les documents archivés
- [ ] Pas de litiges en cours
- [ ] Validation direction/comptabilité

#### 4.5.2 Flux nominal

**Requête HTTP** :

```http
POST /api/chantiers/28/fermer
Authorization: Bearer <token>
```

**Réponse** :

```json
{
  "id": 28,
  "code": "2026-01-MONTMELIAN",
  "statut": "ferme",
  "updated_at": "2026-07-01T10:00:00Z"
}
```

#### 4.5.3 Effets de bord

Quand un chantier passe FERME :

1. **Planning** : ❌ Aucune affectation possible
2. **Pointages** : ❌ Aucun pointage possible
3. **Modifications** : ❌ Chantier en lecture seule
4. **Documents** : ✅ Consultation uniquement
5. **Archivage** : ✅ Données archivées (backup)
6. **Dashboard** : Chantier dans "Historique"

**⚠️ ATTENTION** : Transition **irréversible**. Aucun retour arrière possible.

---

### 4.6 Assignation responsables

**Use Case** : `AssignResponsableUseCase`
**Fichier** : `backend/modules/chantiers/application/use_cases/assign_responsable.py:49-98`

#### 4.6.1 Assignation conducteur

**Requête HTTP** :

```http
POST /api/chantiers/28/responsables
Content-Type: application/json
Authorization: Bearer <token>

{
  "user_id": 3,
  "role_type": "conducteur"
}
```

**Réponse** :

```json
{
  "id": 28,
  "conducteur_ids": [3],
  "chef_chantier_ids": [7]
}
```

**Event publié** :

```python
ConducteurAssigneEvent(
    chantier_id=28,
    code="2026-01-MONTMELIAN",
    conducteur_id=3,
)
```

#### 4.6.2 Assignation chef de chantier

**Requête HTTP** :

```http
POST /api/chantiers/28/responsables
Content-Type: application/json
Authorization: Bearer <token>

{
  "user_id": 9,
  "role_type": "chef_chantier"
}
```

**Réponse** :

```json
{
  "id": 28,
  "conducteur_ids": [3],
  "chef_chantier_ids": [7, 9]
}
```

**Event publié** :

```python
ChefChantierAssigneEvent(
    chantier_id=28,
    code="2026-01-MONTMELIAN",
    chef_id=9,
)
```

#### 4.6.3 Retrait responsables

**Retrait conducteur** :

```http
DELETE /api/chantiers/28/responsables/conducteur/3
Authorization: Bearer <token>
```

**Retrait chef de chantier** :

```http
DELETE /api/chantiers/28/responsables/chef/7
Authorization: Bearer <token>
```

**Fichier** : `assign_responsable.py:132-168`

---

### 4.7 Modification chantier

**Use Case** : `UpdateChantierUseCase`
**Fichier** : `backend/modules/chantiers/application/use_cases/update_chantier.py`

#### 4.7.1 Champs modifiables

| Champ | Modifiable si statut | Validation |
|-------|---------------------|------------|
| `nom` | OUVERT, EN_COURS, RECEPTIONNE | Non vide |
| `adresse` | OUVERT, EN_COURS, RECEPTIONNE | Non vide |
| `description` | OUVERT, EN_COURS, RECEPTIONNE | - |
| `couleur` | OUVERT, EN_COURS, RECEPTIONNE | Format hexa |
| `photo_couverture` | OUVERT, EN_COURS, RECEPTIONNE | URL valide |
| `coordonnees_gps` | OUVERT, EN_COURS, RECEPTIONNE | Lat/Lon valides |
| `contact` | OUVERT, EN_COURS, RECEPTIONNE | - |
| `heures_estimees` | OUVERT, EN_COURS | > 0 |
| `date_debut` | OUVERT | - |
| `date_fin` | OUVERT, EN_COURS | >= date_debut |

**Règle** : Un chantier **FERME** n'est jamais modifiable.

#### 4.7.2 Exemple de modification

**Requête HTTP** :

```http
PATCH /api/chantiers/28
Content-Type: application/json
Authorization: Bearer <token>

{
  "description": "Rénovation complète de la façade, bureaux et salle du conseil",
  "heures_estimees": 520.0,
  "date_fin": "2026-06-15"
}
```

**Réponse** :

```json
{
  "id": 28,
  "code": "2026-01-MONTMELIAN",
  "description": "Rénovation complète de la façade, bureaux et salle du conseil",
  "heures_estimees": 520.0,
  "date_fin": "2026-06-15",
  "updated_at": "2026-03-10T11:30:00Z"
}
```

---

### 4.8 Suppression chantier

**Use Case** : `DeleteChantierUseCase`
**Fichier** : `backend/modules/chantiers/application/use_cases/delete_chantier.py`

#### 4.8.1 Stratégie de suppression

**Soft Delete** (recommandé) :

- Marquage `deleted_at = NOW()`
- Données conservées en base
- Chantier invisible dans listes
- Récupération possible

**Hard Delete** (déconseillé) :

- Suppression physique en base
- CASCADE sur toutes les tables liées
- **Irréversible**
- Perte de traçabilité

#### 4.8.2 Données supprimées en cascade

Lors d'une suppression HARD DELETE :

```sql
DELETE FROM chantiers WHERE id = 28;
-- CASCADE supprime aussi :
-- - affectations (planning)
-- - pointages
-- - dossiers
-- - formulaires_remplis
-- - signalements
-- - interventions
```

**⚠️ ATTENTION** : Perte définitive de toutes les données du chantier.

#### 4.8.3 Recommandation

✅ **Préférer SOFT DELETE** :

- Conserver historique
- Récupération possible
- Audit trail
- Conformité RGPD (anonymisation ultérieure)

❌ **Éviter HARD DELETE** sauf :

- Chantier de test
- Erreur de saisie immédiate
- Demande RGPD explicite

---

## 5. Règles métier

### 5.1 Règles de statut

| Règle | Description | Fichier |
|-------|-------------|---------|
| **RG-CHT-01** | Un chantier créé est toujours OUVERT | `create_chantier.py:164` |
| **RG-CHT-02** | Seules les transitions définies sont autorisées | `statut_chantier.py:26-34` |
| **RG-CHT-03** | Un chantier FERME ne peut plus changer de statut | `statut_chantier.py:27` |
| **RG-CHT-04** | Un chantier FERME ne peut plus être modifié | `chantier.py:__post_init__` |

### 5.2 Règles de code

| Règle | Description | Fichier |
|-------|-------------|---------|
| **RG-CHT-10** | Code unique par chantier | `create_chantier.py:97` |
| **RG-CHT-11** | Format : `LETTRE+3CHIFFRES` ou `AAAA-NN-NOM` | `code_chantier.py:26` |
| **RG-CHT-12** | Auto-génération si code non fourni | `create_chantier.py:100-102` |
| **RG-CHT-13** | Codes spéciaux pour absences (CONGES, MALADIE, etc.) | `code_chantier.py:29` |

### 5.3 Règles de dates

| Règle | Description | Fichier |
|-------|-------------|---------|
| **RG-CHT-20** | `date_fin` >= `date_debut` | `create_chantier.py:136-139` |
| **RG-CHT-21** | Dates optionnelles à la création | `create_chantier.py:124-141` |
| **RG-CHT-22** | `date_debut` modifiable si OUVERT uniquement | `update_chantier.py` |
| **RG-CHT-23** | `date_fin` modifiable si OUVERT ou EN_COURS | `update_chantier.py` |

### 5.4 Règles de responsables

| Règle | Description | Fichier |
|-------|-------------|---------|
| **RG-CHT-30** | Un chantier peut avoir plusieurs conducteurs | `chantier.py:62` |
| **RG-CHT-31** | Un chantier peut avoir plusieurs chefs de chantier | `chantier.py:63` |
| **RG-CHT-32** | Un conducteur ne peut être assigné 2x | `chantier.py:assigner_conducteur` |
| **RG-CHT-33** | Un chef ne peut être assigné 2x | `chantier.py:assigner_chef_chantier` |

### 5.5 Règles de validation entité

**Fichier** : `backend/modules/chantiers/domain/entities/chantier.py:81-104`

```python
def __post_init__(self) -> None:
    """Validation de l'entité à la création."""

    # RG-CHT-40 : Nom obligatoire et non vide
    if not self.nom or not self.nom.strip():
        raise ValueError("Le nom du chantier est obligatoire")

    # RG-CHT-41 : Adresse obligatoire et non vide
    if not self.adresse or not self.adresse.strip():
        raise ValueError("L'adresse du chantier est obligatoire")

    # RG-CHT-42 : Code obligatoire
    if not self.code:
        raise ValueError("Le code chantier est obligatoire")

    # RG-CHT-43 : Statut obligatoire
    if not self.statut:
        raise ValueError("Le statut est obligatoire")

    # RG-CHT-44 : Dates cohérentes
    if self.date_debut and self.date_fin:
        if self.date_fin < self.date_debut:
            raise ValueError("La date de fin doit être >= date de début")
```

---

## 6. Interactions avec autres modules

### 6.1 Planning (Affectations)

**Direction** : Chantier → Planning

| Event | Impact Planning |
|-------|----------------|
| `ChantierCreatedEvent` | Chantier disponible pour affectations |
| `ChantierStatutChangedEvent(EN_COURS)` | Affectations activées |
| `ChantierStatutChangedEvent(FERME)` | Affectations bloquées |
| `ChantierDeletedEvent` | Affectations supprimées (cascade) |

**Règle** : On ne peut affecter un compagnon que sur un chantier **is_active()** (OUVERT, EN_COURS, RECEPTIONNE).

**Fichier** : `backend/modules/planning/domain/entities/affectation.py`

```python
# Validation lors de création affectation
if not chantier.statut.is_active():
    raise ValueError(f"Impossible d'affecter sur chantier {chantier.statut}")
```

### 6.2 Pointages (Feuilles d'heures)

**Direction** : Chantier → Pointages

| Event | Impact Pointages |
|-------|-----------------|
| `ChantierStatutChangedEvent(EN_COURS)` | Pointages autorisés |
| `ChantierStatutChangedEvent(FERME)` | Pointages bloqués |
| `ChantierDeletedEvent` | Pointages supprimés (cascade) |

**Règle** : On ne peut pointer que sur un chantier **is_active()**.

**Fichier** : `backend/modules/pointages/domain/entities/pointage.py`

```python
# Validation lors de création pointage
if not chantier.statut.is_active():
    raise ValueError(f"Impossible de pointer sur chantier {chantier.statut}")
```

### 6.3 Documents (GED)

**Direction** : Chantier ↔ Documents

| Event | Impact Documents |
|-------|-----------------|
| `ChantierCreatedEvent` | Dossier racine créé |
| `ChantierStatutChangedEvent(RECEPTIONNE)` | PV réception généré (si configuré) |
| `ChantierStatutChangedEvent(FERME)` | Documents en lecture seule |
| `ChantierDeletedEvent` | Documents archivés ou supprimés |

**Fichier** : `backend/modules/documents/domain/entities/dossier.py`

### 6.4 Formulaires

**Direction** : Chantier → Formulaires

| Event | Impact Formulaires |
|-------|-------------------|
| `ChantierCreatedEvent` | Formulaires obligatoires assignés |
| `ChantierStatutChangedEvent(FERME)` | Formulaires en lecture seule |
| `ChantierDeletedEvent` | Formulaires supprimés (cascade) |

### 6.5 Signalements

**Direction** : Chantier → Signalements

| Event | Impact Signalements |
|-------|---------------------|
| `ChantierStatutChangedEvent(RECEPTIONNE)` | Vérification signalements ouverts |
| `ChantierStatutChangedEvent(FERME)` | Signalements archivés |
| `ChantierDeletedEvent` | Signalements supprimés (cascade) |

**Règle** : Un chantier avec signalements critiques ouverts ne devrait pas être réceptionné (validation manuelle).

### 6.6 Schéma d'interactions

```
                              ┌─────────────┐
                              │  Chantier   │
                              └──────┬──────┘
                                     │
                 ┌───────────────────┼───────────────────┐
                 │                   │                   │
                 ▼                   ▼                   ▼
         ┌───────────┐       ┌───────────┐      ┌───────────┐
         │ Planning  │       │ Pointages │      │ Documents │
         │           │       │           │      │           │
         │ Affectations│     │ FdH       │      │ Dossiers  │
         └───────────┘       └───────────┘      └───────────┘
                 │                   │                   │
                 └───────────────────┼───────────────────┘
                                     │
                                     ▼
                              ┌─────────────┐
                              │  Dashboard  │
                              └─────────────┘
                              (Indicateurs KPI)
```

---

## 7. Architecture technique

### 7.1 Structure des fichiers

```
backend/modules/chantiers/
│
├── domain/                              # Couche Domain
│   ├── entities/
│   │   └── chantier.py                 # Entity Chantier (règles métier)
│   ├── value_objects/
│   │   ├── code_chantier.py            # VO CodeChantier
│   │   ├── statut_chantier.py          # VO StatutChantier (machine à états)
│   │   ├── coordonnees_gps.py          # VO CoordonneesGPS
│   │   └── contact_chantier.py         # VO ContactChantier
│   ├── repositories.py                  # Interface Repository
│   └── events/
│       ├── chantier_created.py
│       ├── chantier_updated.py
│       ├── chantier_statut_changed.py
│       └── chantier_deleted.py
│
├── application/                         # Couche Application
│   ├── use_cases/
│   │   ├── create_chantier.py          # UC Création
│   │   ├── update_chantier.py          # UC Modification
│   │   ├── change_statut.py            # UC Changement statut
│   │   ├── assign_responsable.py       # UC Assignation responsables
│   │   ├── delete_chantier.py          # UC Suppression
│   │   ├── get_chantier.py             # UC Lecture unique
│   │   └── list_chantiers.py           # UC Lecture liste
│   └── dtos/
│       ├── create_chantier_dto.py
│       ├── update_chantier_dto.py
│       ├── change_statut_dto.py
│       ├── assign_responsable_dto.py
│       └── chantier_dto.py             # DTO sortie
│
├── adapters/                            # Couche Adapters
│   └── controllers/
│       └── chantier_controller.py      # Controller FastAPI
│
└── infrastructure/                      # Couche Infrastructure
    ├── persistence/
    │   ├── models.py                   # SQLAlchemy Model
    │   └── sqlalchemy_chantier_repository.py
    └── web/
        └── chantier_routes.py          # Routes FastAPI
```

### 7.2 Clean Architecture - Dépendances

```
┌──────────────────────────────────────────────────┐
│                   Domain                         │
│  (Entities, VOs, Repository Interface, Events)   │
│                                                   │
│  - Aucune dépendance externe                     │
│  - Règles métier pures                           │
└────────────────────┬─────────────────────────────┘
                     │
                     │ depends on
                     │
┌────────────────────▼─────────────────────────────┐
│                Application                       │
│         (Use Cases, DTOs, Services)              │
│                                                   │
│  - Dépend uniquement de Domain                   │
│  - Orchestration logique métier                  │
└────────────────────┬─────────────────────────────┘
                     │
                     │ depends on
                     │
┌────────────────────▼─────────────────────────────┐
│                 Adapters                         │
│            (Controllers, Presenters)             │
│                                                   │
│  - Dépend de Application + Domain                │
│  - Convertit Use Case → HTTP/JSON                │
└────────────────────┬─────────────────────────────┘
                     │
                     │ depends on
                     │
┌────────────────────▼─────────────────────────────┐
│              Infrastructure                      │
│      (Persistence, Web, External Services)       │
│                                                   │
│  - Implémente interfaces du Domain               │
│  - SQLAlchemy, FastAPI, PostgreSQL               │
└──────────────────────────────────────────────────┘
```

**Règle d'or** : Les dépendances vont **TOUJOURS vers l'intérieur**.

### 7.3 Entité Chantier (Domain)

**Fichier** : `backend/modules/chantiers/domain/entities/chantier.py:17-79`

```python
@dataclass
class Chantier:
    """
    Entité Chantier - Représente un chantier de construction.

    Attributes:
        id: Identifiant unique (généré par la DB).
        code: Code unique du chantier (ex: A001, 2026-01-MONTMELIAN).
        nom: Nom du chantier.
        adresse: Adresse du chantier.
        statut: Statut actuel (OUVERT, EN_COURS, RECEPTIONNE, FERME).
        couleur: Couleur pour l'affichage (hexa).
        coordonnees_gps: Coordonnées GPS (lat/lon).
        photo_couverture: URL de la photo de couverture.
        contact: Contact principal (nom + téléphone).
        heures_estimees: Heures de travail estimées.
        date_debut: Date de début prévisionnelle.
        date_fin: Date de fin prévisionnelle.
        description: Description du chantier.
        conducteur_ids: Liste des IDs conducteurs.
        chef_chantier_ids: Liste des IDs chefs de chantier.
        created_at: Date de création.
        updated_at: Date de dernière modification.
    """

    # Identifiant
    code: CodeChantier

    # Informations principales
    nom: str
    adresse: str
    statut: StatutChantier

    # Optionnels
    couleur: Couleur = field(default_factory=Couleur.default)
    coordonnees_gps: Optional[CoordonneesGPS] = None
    photo_couverture: Optional[str] = None
    contact: Optional[ContactChantier] = None

    # Planning
    heures_estimees: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None

    # Description
    description: Optional[str] = None

    # Responsables
    conducteur_ids: list[int] = field(default_factory=list)
    chef_chantier_ids: list[int] = field(default_factory=list)

    # Métadonnées
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### 7.4 Méthodes métier de l'entité

**Fichier** : `backend/modules/chantiers/domain/entities/chantier.py:106-180`

```python
def change_statut(self, nouveau_statut: StatutChantier) -> None:
    """Change le statut du chantier (avec validation)."""
    if not self.statut.can_transition_to(nouveau_statut):
        raise ValueError(
            f"Transition non autorisée: {self.statut} → {nouveau_statut}"
        )
    self.statut = nouveau_statut

def demarrer(self) -> None:
    """Raccourci : passe en statut EN_COURS."""
    self.change_statut(StatutChantier.en_cours())

def receptionner(self) -> None:
    """Raccourci : passe en statut RECEPTIONNE."""
    self.change_statut(StatutChantier.receptionne())

def fermer(self) -> None:
    """Raccourci : passe en statut FERME."""
    self.change_statut(StatutChantier.ferme())

def assigner_conducteur(self, user_id: int) -> None:
    """Assigne un conducteur (si pas déjà assigné)."""
    if user_id not in self.conducteur_ids:
        self.conducteur_ids.append(user_id)

def retirer_conducteur(self, user_id: int) -> None:
    """Retire un conducteur."""
    if user_id in self.conducteur_ids:
        self.conducteur_ids.remove(user_id)

def assigner_chef_chantier(self, user_id: int) -> None:
    """Assigne un chef de chantier (si pas déjà assigné)."""
    if user_id not in self.chef_chantier_ids:
        self.chef_chantier_ids.append(user_id)

def retirer_chef_chantier(self, user_id: int) -> None:
    """Retire un chef de chantier."""
    if user_id in self.chef_chantier_ids:
        self.chef_chantier_ids.remove(user_id)
```

### 7.5 Repository (Interface)

**Fichier** : `backend/modules/chantiers/domain/repositories.py`

```python
from abc import ABC, abstractmethod
from typing import Optional, List
from .entities import Chantier
from .value_objects import CodeChantier, StatutChantier

class ChantierRepository(ABC):
    """Interface du repository chantier."""

    @abstractmethod
    def save(self, chantier: Chantier) -> Chantier:
        """Sauvegarde un chantier (create ou update)."""
        pass

    @abstractmethod
    def find_by_id(self, chantier_id: int) -> Optional[Chantier]:
        """Trouve un chantier par ID."""
        pass

    @abstractmethod
    def find_by_code(self, code: CodeChantier) -> Optional[Chantier]:
        """Trouve un chantier par code."""
        pass

    @abstractmethod
    def exists_by_code(self, code: CodeChantier) -> bool:
        """Vérifie si un code existe."""
        pass

    @abstractmethod
    def get_last_code(self) -> Optional[str]:
        """Récupère le dernier code pour auto-génération."""
        pass

    @abstractmethod
    def list_all(
        self,
        statut: Optional[StatutChantier] = None,
        conducteur_id: Optional[int] = None,
    ) -> List[Chantier]:
        """Liste tous les chantiers (avec filtres optionnels)."""
        pass

    @abstractmethod
    def delete(self, chantier_id: int) -> bool:
        """Supprime un chantier."""
        pass
```

### 7.6 Events (Domain Events)

**Fichier** : `backend/modules/chantiers/domain/events/chantier_events.py`

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Tuple, Optional

@dataclass(frozen=True)
class ChantierCreatedEvent:
    """Event : Chantier créé."""
    chantier_id: int
    code: str
    nom: str
    statut: str
    conducteur_ids: Tuple[int, ...]
    chef_chantier_ids: Tuple[int, ...]
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class ChantierStatutChangedEvent:
    """Event : Statut chantier changé."""
    chantier_id: int
    code: str
    ancien_statut: str
    nouveau_statut: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class ConducteurAssigneEvent:
    """Event : Conducteur assigné."""
    chantier_id: int
    code: str
    conducteur_id: int
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class ChefChantierAssigneEvent:
    """Event : Chef de chantier assigné."""
    chantier_id: int
    code: str
    chef_id: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

---

## 8. Scénarios de test

### 8.1 Tests unitaires (Use Cases)

**Fichier** : `backend/tests/unit/modules/chantiers/application/use_cases/test_create_chantier.py`

```python
def test_create_chantier_success():
    """Test création chantier nominal."""
    # Given
    dto = CreateChantierDTO(
        nom="Rénovation Mairie",
        adresse="123 Avenue de la République",
        code="2026-01-TEST",
        couleur="#3B82F6",
    )

    # When
    result = create_uc.execute(dto)

    # Then
    assert result.code == "2026-01-TEST"
    assert result.statut == "ouvert"
    assert result.nom == "Rénovation Mairie"

def test_create_chantier_code_already_exists():
    """Test code déjà existant → erreur."""
    # Given
    dto = CreateChantierDTO(nom="Test", adresse="Test", code="A001")

    # When/Then
    with pytest.raises(CodeChantierAlreadyExistsError):
        create_uc.execute(dto)

def test_create_chantier_auto_generate_code():
    """Test auto-génération code."""
    # Given
    dto = CreateChantierDTO(nom="Test", adresse="Test")
    # Last code in DB: A005

    # When
    result = create_uc.execute(dto)

    # Then
    assert result.code == "A006"

def test_create_chantier_invalid_dates():
    """Test date_fin < date_debut → erreur."""
    # Given
    dto = CreateChantierDTO(
        nom="Test",
        adresse="Test",
        date_debut="2026-05-01",
        date_fin="2026-04-01",  # ← Incohérent
    )

    # When/Then
    with pytest.raises(InvalidDatesError):
        create_uc.execute(dto)
```

### 8.2 Tests statut

**Fichier** : `backend/tests/unit/modules/chantiers/application/use_cases/test_change_statut.py`

```python
def test_demarrer_chantier_success():
    """Test OUVERT → EN_COURS nominal."""
    # Given
    chantier = create_chantier(statut="ouvert")

    # When
    result = change_statut_uc.demarrer(chantier.id)

    # Then
    assert result.statut == "en_cours"

def test_receptionner_chantier_success():
    """Test EN_COURS → RECEPTIONNE nominal."""
    # Given
    chantier = create_chantier(statut="en_cours")

    # When
    result = change_statut_uc.receptionner(chantier.id)

    # Then
    assert result.statut == "receptionne"

def test_fermer_chantier_success():
    """Test * → FERME nominal."""
    # Given
    chantier = create_chantier(statut="receptionne")

    # When
    result = change_statut_uc.fermer(chantier.id)

    # Then
    assert result.statut == "ferme"

def test_transition_non_autorisee():
    """Test OUVERT → RECEPTIONNE (interdit) → erreur."""
    # Given
    chantier = create_chantier(statut="ouvert")
    dto = ChangeStatutDTO(nouveau_statut="receptionne")

    # When/Then
    with pytest.raises(TransitionNonAutoriseeError):
        change_statut_uc.execute(chantier.id, dto)

def test_chantier_ferme_aucune_transition():
    """Test FERME → EN_COURS (interdit) → erreur."""
    # Given
    chantier = create_chantier(statut="ferme")
    dto = ChangeStatutDTO(nouveau_statut="en_cours")

    # When/Then
    with pytest.raises(TransitionNonAutoriseeError):
        change_statut_uc.execute(chantier.id, dto)
```

### 8.3 Tests responsables

**Fichier** : `backend/tests/unit/modules/chantiers/application/use_cases/test_assign_responsable.py`

```python
def test_assigner_conducteur_success():
    """Test assignation conducteur nominal."""
    # Given
    chantier = create_chantier()
    dto = AssignResponsableDTO(user_id=3, role_type="conducteur")

    # When
    result = assign_uc.execute(chantier.id, dto)

    # Then
    assert 3 in result.conducteur_ids

def test_assigner_conducteur_deja_assigne():
    """Test assignation conducteur déjà assigné (idempotence)."""
    # Given
    chantier = create_chantier(conducteur_ids=[3])
    dto = AssignResponsableDTO(user_id=3, role_type="conducteur")

    # When
    result = assign_uc.execute(chantier.id, dto)

    # Then
    assert result.conducteur_ids.count(3) == 1  # Pas de doublon

def test_retirer_conducteur_success():
    """Test retrait conducteur nominal."""
    # Given
    chantier = create_chantier(conducteur_ids=[3, 5])

    # When
    result = assign_uc.retirer_conducteur(chantier.id, 3)

    # Then
    assert 3 not in result.conducteur_ids
    assert 5 in result.conducteur_ids
```

### 8.4 Tests d'intégration

**Fichier** : `backend/tests/integration/modules/chantiers/test_chantier_workflow.py`

```python
def test_workflow_complet_chantier(client, db_session):
    """
    Test workflow complet d'un chantier:
    1. Création (OUVERT)
    2. Assignation conducteur
    3. Démarrage (EN_COURS)
    4. Réception (RECEPTIONNE)
    5. Clôture (FERME)
    """
    # 1. Création
    response = client.post("/api/chantiers", json={
        "nom": "Test Workflow",
        "adresse": "123 Rue Test",
    })
    assert response.status_code == 201
    chantier_id = response.json()["id"]
    assert response.json()["statut"] == "ouvert"

    # 2. Assignation conducteur
    response = client.post(f"/api/chantiers/{chantier_id}/responsables", json={
        "user_id": 3,
        "role_type": "conducteur",
    })
    assert response.status_code == 200
    assert 3 in response.json()["conducteur_ids"]

    # 3. Démarrage
    response = client.post(f"/api/chantiers/{chantier_id}/demarrer")
    assert response.status_code == 200
    assert response.json()["statut"] == "en_cours"

    # 4. Réception
    response = client.post(f"/api/chantiers/{chantier_id}/receptionner")
    assert response.status_code == 200
    assert response.json()["statut"] == "receptionne"

    # 5. Clôture
    response = client.post(f"/api/chantiers/{chantier_id}/fermer")
    assert response.status_code == 200
    assert response.json()["statut"] == "ferme"

    # 6. Vérifier qu'on ne peut plus modifier
    response = client.patch(f"/api/chantiers/{chantier_id}", json={
        "nom": "Nouveau nom",
    })
    assert response.status_code == 400  # Chantier fermé
```

### 8.5 Couverture de tests attendue

| Module | Couverture cible | Actuel |
|--------|-----------------|--------|
| `domain/entities/chantier.py` | >= 95% | - |
| `domain/value_objects/statut_chantier.py` | 100% | - |
| `domain/value_objects/code_chantier.py` | 100% | - |
| `application/use_cases/create_chantier.py` | >= 90% | - |
| `application/use_cases/change_statut.py` | >= 90% | - |
| `application/use_cases/assign_responsable.py` | >= 85% | - |
| `infrastructure/persistence/*.py` | >= 80% | - |

**Commande** :

```bash
cd backend
pytest tests/unit/modules/chantiers -v --cov=modules/chantiers --cov-report=html
```

---

## 9. Points d'attention

### 9.1 Sécurité

| Point | Risque | Mitigation |
|-------|--------|------------|
| **Suppression chantier** | Perte de données | Soft delete par défaut, confirmation admin |
| **Transition FERME** | Irréversible | Confirmation explicite, log audit |
| **Modification chantier fermé** | Violation règles métier | Validation côté backend + frontend |
| **Assignation responsables** | Permissions incorrectes | Vérifier rôle user avant assignation |

### 9.2 Performance

| Point | Impact | Optimisation |
|-------|--------|--------------|
| **Liste chantiers** | N+1 queries | JOIN conducteurs + chefs lors du fetch |
| **Changement statut** | Cascade events | Async processing des events |
| **Suppression cascade** | Timeout | Batch delete + background job |

**Exemple JOIN** :

```python
# backend/modules/chantiers/infrastructure/persistence/sqlalchemy_chantier_repository.py

def list_all(self, statut=None, conducteur_id=None):
    query = (
        self.session.query(ChantierModel)
        .options(
            joinedload(ChantierModel.conducteurs),
            joinedload(ChantierModel.chefs_chantier),
        )
    )

    if statut:
        query = query.filter(ChantierModel.statut == statut)

    if conducteur_id:
        query = query.filter(
            ChantierModel.conducteur_ids.contains([conducteur_id])
        )

    return [self._to_entity(m) for m in query.all()]
```

### 9.3 Cohérence données

| Point | Problème | Solution |
|-------|----------|----------|
| **Code chantier unique** | Collision | Contrainte UNIQUE en DB + vérif use case |
| **Dates incohérentes** | date_fin < date_debut | Validation entité + use case |
| **Statut invalide** | Données corrompues | Enum PostgreSQL + validation |
| **Conducteur inexistant** | Référence cassée | Foreign key OU vérification use case |

### 9.4 Synchronisation modules

| Interaction | Problème potentiel | Solution |
|-------------|-------------------|----------|
| **Chantier → Planning** | Affectations sur chantier inactif | Écouter `ChantierStatutChangedEvent`, bloquer affectations |
| **Chantier → Pointages** | Pointages sur chantier fermé | Écouter event, bloquer pointages |
| **Chantier → Documents** | Documents orphelins | Cascade delete OU archivage |

**Event Handler Notifications** :

```python
# backend/modules/notifications/infrastructure/event_handlers.py

@event_handler('chantier.statut_changed')
def handle_chantier_statut_changed(event):
    """Notifie l'equipe du chantier lors d'un changement de statut."""
    # Recupere les conducteurs et chefs du chantier
    # Utilise StatutChantier.from_string(nouveau_statut).display_name pour le label
    # Cree une notification SYSTEM pour chaque destinataire (sauf l'auteur du changement)
```

### 9.5 RGPD et archivage

| Point | Obligation | Implémentation |
|-------|-----------|----------------|
| **Conservation données** | 10 ans (BTP) | Soft delete + archivage S3 |
| **Anonymisation** | Sur demande client | Script anonymisation coordonnées/contacts |
| **Export données** | Droit à la portabilité | Endpoint export JSON chantier complet |

### 9.6 UX et validation frontend

| Point | UX | Validation |
|-------|-----|-----------|
| **Transition statut** | Modal confirmation | Afficher transitions autorisées uniquement |
| **Suppression** | Modal + double confirmation | Afficher impact (pointages, docs, etc.) |
| **Dates** | Datepicker avec contraintes | date_fin >= date_debut |
| **Chantier fermé** | Icône cadenas + tooltip | Désactiver boutons édition |

**Exemple composant React** :

```tsx
// frontend/src/components/chantiers/ChantierStatutBadge.tsx

function ChantierStatutBadge({ statut }: { statut: string }) {
  const config = {
    ouvert: { color: "blue", icon: FolderOpenIcon },
    en_cours: { color: "green", icon: PlayIcon },
    receptionne: { color: "purple", icon: CheckCircleIcon },
    ferme: { color: "gray", icon: LockClosedIcon },
  };

  const { color, icon: Icon } = config[statut];

  return (
    <Badge color={color}>
      <Icon className="w-4 h-4 mr-1" />
      {statut.toUpperCase()}
    </Badge>
  );
}
```

### 9.7 Logs et audit

**Recommandations** :

```python
# backend/modules/chantiers/application/use_cases/change_statut.py

def execute(self, chantier_id, dto):
    logger.info(
        f"Changement statut chantier #{chantier_id}: "
        f"{chantier.statut} → {dto.nouveau_statut}",
        extra={
            "chantier_id": chantier_id,
            "ancien_statut": str(chantier.statut),
            "nouveau_statut": dto.nouveau_statut,
            "user_id": current_user.id,  # Context injection
        }
    )

    # ... use case logic ...
```

**Table audit** :

```sql
CREATE TABLE audit_chantiers (
    id SERIAL PRIMARY KEY,
    chantier_id INT REFERENCES chantiers(id),
    action VARCHAR(50),  -- create, update, change_statut, delete
    ancien_statut VARCHAR(20),
    nouveau_statut VARCHAR(20),
    user_id INT REFERENCES utilisateurs(id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    payload JSONB
);
```

---

## 10. Conclusion

### 10.1 Résumé

Le **Cycle de Vie d'un Chantier** est le workflow central de Hub Chantier. Il gère :

- ✅ Création avec code unique auto-généré
- ✅ Machine à états rigoureuse (4 statuts, transitions contrôlées)
- ✅ Assignation/retrait responsables (conducteurs, chefs)
- ✅ Modification contextuelle selon statut
- ✅ Suppression soft delete
- ✅ Synchronisation avec Planning, Pointages, Documents

### 10.2 Forces

- **Architecture** : Clean Architecture stricte, séparation domaine/application/infrastructure
- **Validation** : Règles métier dans entités + use cases
- **Traçabilité** : Domain events pour toutes les actions critiques
- **Sécurité** : Transitions contrôlées, soft delete, audit logs
- **Extensibilité** : Ajout facile de nouveaux statuts ou règles

### 10.3 Points d'amélioration futurs

| Amélioration | Priorité | Effort |
|--------------|----------|--------|
| Validation automatique prérequis réception (formulaires, docs) | Haute | 3j |
| Workflow approbation pour transition FERME | Moyenne | 2j |
| Export données chantier (RGPD) | Haute | 2j |
| ~~Notification sur changements statut~~ | ~~Moyenne~~ | ✅ Implémenté (handler `chantier.statut_changed`) |
| Dashboard KPI par statut | Basse | 3j |

### 10.4 Prochaines étapes

1. ✅ **Documentation complète** (ce fichier)
2. 🔄 **Tests unitaires** (>= 85% couverture)
3. 🔄 **Tests d'intégration** (workflow complet)
4. 📋 **Documenter autres workflows** (Validation FdH, GED, etc.)

---

**Auteur** : Claude Sonnet 4.5
**Date dernière mise à jour** : 31 janvier 2026
**Version** : 1.1 (audit executabilite : allows_modifications corrige, handlers chantier deplaces dans notifications)
**Statut** : ✅ Complet + Audite
