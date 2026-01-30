# Workflow : Formulaires Chantier Dynamiques

**Complexité** : ⭐⭐⭐⭐ (Élevée)
**Module** : `backend/modules/formulaires`
**Date** : 30 janvier 2026
**Statut** : ✅ Documenté

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Acteurs et permissions](#2-acteurs-et-permissions)
3. [Entités métier](#3-entités-métier)
4. [Machine à états](#4-machine-à-états)
5. [Workflows détaillés](#5-workflows-détaillés)
6. [Types de champs](#6-types-de-champs)
7. [Fonctionnalités terrain](#7-fonctionnalités-terrain)
8. [Interactions avec autres modules](#8-interactions-avec-autres-modules)
9. [Architecture technique](#9-architecture-technique)
10. [Scénarios de test](#10-scénarios-de-test)
11. [Points d'attention](#11-points-dattention)

---

## 1. Vue d'ensemble

### 1.1 Définition

Les **Formulaires Dynamiques** permettent de créer des formulaires personnalisés pour le terrain : PPSPS, comptes-rendus de réunion, rapports d'incident, PV de réception, etc. Un administrateur crée un **template** (modèle), puis les équipes terrain **remplissent** des instances de ce template sur tablette/mobile.

```
┌─────────────────────────────────────────────────────────────┐
│  TEMPLATE (modèle défini par l'admin)                        │
│  "Rapport d'incident sécurité"                              │
│                                                              │
│  Champs :                                                    │
│  ├── 📝 Titre (texte, obligatoire)                          │
│  ├── 📅 Date incident (auto-date)                           │
│  ├── 📍 Localisation (auto-GPS)                             │
│  ├── 📋 Description (texte long, obligatoire)               │
│  ├── ⚠️  Gravité (select : mineur/moyen/grave/critique)     │
│  ├── 📷 Photos (photo multiple)                             │
│  └── ✍️  Signature responsable (signature)                  │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │ Le chef de chantier remplit
                       │ une instance sur le terrain
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  FORMULAIRE REMPLI (instance liée à un chantier)            │
│  Chantier : "Villa Duplex"                                  │
│  Rempli par : Nicolas DELSALLE le 27/01/2026                │
│                                                              │
│  Titre       : "Chute de matériau depuis R+1"              │
│  Date        : 27/01/2026 14:30 (auto)                     │
│  Localisation: 45.5036, 6.0565 (auto GPS)                  │
│  Description : "Un parpaing est tombé du 1er étage..."     │
│  Gravité     : "grave"                                      │
│  Photos      : [photo1.jpg, photo2.jpg]                     │
│  Signature   : [signature manuscrite de Nicolas]            │
│                                                              │
│  Statut : SOUMIS → en attente de validation                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Objectifs métier

| Objectif | Description |
|----------|-------------|
| **Dématérialisation** | Remplacer les formulaires papier par des formulaires numériques |
| **Conformité** | Garantir que les formulaires réglementaires sont remplis (PPSPS, sécurité) |
| **Traçabilité** | Horodatage, géolocalisation, signature manuscrite sur chaque formulaire |
| **Flexibilité** | L'admin crée les templates, pas besoin de développeur |
| **Terrain** | Saisie optimisée pour tablette/mobile en conditions de chantier |

### 1.3 Références CDC

| CDC ID | Fonctionnalité | Implémenté |
|--------|----------------|------------|
| FOR-01 | Création templates avec champs dynamiques | ✅ |
| FOR-02 | Remplissage formulaires | ✅ |
| FOR-03 | Auto-remplissage (date, heure, GPS, intervenant) | ✅ |
| FOR-04 | Photos horodatées et géolocalisées | ✅ |
| FOR-05 | Signature électronique manuscrite | ✅ |
| FOR-07 | Soumission avec horodatage | ✅ |
| FOR-08 | Versioning et historique | ✅ |
| FOR-09 | Export PDF | ✅ |
| FOR-10 | Association au chantier | ✅ |
| FOR-11 | Création formulaire depuis template | ✅ |

---

## 2. Acteurs et permissions

| Rôle | Templates | Formulaires |
|------|-----------|-------------|
| **Admin** | Créer, modifier, supprimer | Tout (tous chantiers) |
| **Conducteur** | Consulter | Créer, remplir, soumettre, valider, rejeter (ses chantiers) |
| **Chef de chantier** | Consulter | Créer, remplir, soumettre (ses chantiers) |
| **Compagnon** | Consulter | Créer, remplir, soumettre (ses formulaires) |

---

## 3. Entités métier

### 3.1 Template (modèle de formulaire)

**Fichier** : `backend/modules/formulaires/domain/entities/template_formulaire.py`

| Champ | Type | Description |
|-------|------|-------------|
| `id` | int | Identifiant unique |
| `nom` | str | Nom du template (unique) |
| `description` | str | Description du formulaire |
| `categorie` | CategorieFormulaire | Catégorie (8 valeurs) |
| `champs` | List[ChampTemplate] | Définition des champs |
| `is_active` | bool | Template utilisable ? |
| `version` | int | Numéro de version (FOR-08) |
| `created_by` | int | Créateur |

**8 catégories disponibles** :

| Catégorie | Usage | Exemples |
|-----------|-------|----------|
| INTERVENTION | Rapports d'intervention terrain | Fiche intervention, suivi SAV |
| RECEPTION | PV de réception, réserves | PV réception, levée réserves |
| SECURITE | Formulaires sécurité | PPSPS, visite sécurité, audit |
| INCIDENT | Rapports d'incident | Accident, presqu'accident, non-conformité |
| APPROVISIONNEMENT | Commandes et livraisons | Bon de commande, bon de livraison |
| ADMINISTRATIF | Formulaires administratifs | Demande congé, CERFA |
| GROS_OEUVRE | Suivi travaux | Rapport journalier, fiche bétonnage |
| AUTRE | Divers | Tout le reste |

### 3.2 Formulaire rempli (instance)

**Fichier** : `backend/modules/formulaires/domain/entities/formulaire_rempli.py`

| Champ | Type | Description |
|-------|------|-------------|
| `id` | int | Identifiant |
| `template_id` | int | Template source |
| `chantier_id` | int | Chantier concerné (FOR-10) |
| `user_id` | int | Rédacteur |
| `statut` | StatutFormulaire | État du workflow |
| `champs` | List[ChampRempli] | Valeurs saisies |
| `photos` | List[PhotoFormulaire] | Photos jointes (FOR-04) |
| `signature_url` | str | Signature manuscrite base64 (FOR-05) |
| `signature_nom` | str | Nom du signataire |
| `signature_timestamp` | datetime | Horodatage signature |
| `localisation_latitude` | float | GPS latitude (FOR-03) |
| `localisation_longitude` | float | GPS longitude (FOR-03) |
| `soumis_at` | datetime | Date de soumission (FOR-07) |
| `valide_by` | int | Validateur |
| `valide_at` | datetime | Date validation |
| `version` | int | Version (FOR-08) |
| `parent_id` | int | Version précédente (chaîne d'historique) |

---

## 4. Machine à états

```
┌─────────────┐
│  BROUILLON  │ (Initial - en cours de saisie)
└──────┬──────┘
       │
       │ soumettre() — horodatage automatique (FOR-07)
       │
       ▼
┌─────────────┐
│   SOUMIS    │ (En attente de validation)
└──────┬──────┘
       │
       ├──────────────────────┐
       │                      │
       ▼                      ▼
┌─────────────┐        ┌─────────────┐
│   VALIDÉ    │        │  (rejeté →  │
│             │        │  BROUILLON) │
└──────┬──────┘        └─────────────┘
       │
       │ archiver()
       ▼
┌─────────────┐
│  ARCHIVÉ    │ (Conservation longue durée)
└─────────────┘
```

**Règles** :
- Seul un formulaire en BROUILLON est modifiable
- La soumission ajoute automatiquement un horodatage (`soumis_at`)
- Le rejet retourne le formulaire en BROUILLON (pas de statut REJETÉ dédié)
- L'archivage est une étape finale de conservation

---

## 5. Workflows détaillés

### 5.1 Création d'un template (Admin)

```http
POST /api/templates-formulaires
Content-Type: application/json

{
  "nom": "Rapport incident sécurité",
  "description": "À remplir pour tout incident/presqu'accident",
  "categorie": "incident",
  "champs": [
    {"nom": "titre", "label": "Titre", "type_champ": "texte", "obligatoire": true, "ordre": 1},
    {"nom": "date_incident", "label": "Date", "type_champ": "auto_date", "ordre": 2},
    {"nom": "localisation", "label": "Localisation", "type_champ": "auto_localisation", "ordre": 3},
    {"nom": "description", "label": "Description", "type_champ": "texte_long", "obligatoire": true, "ordre": 4},
    {"nom": "gravite", "label": "Gravité", "type_champ": "select", "options": ["mineur", "moyen", "grave", "critique"], "ordre": 5},
    {"nom": "photos", "label": "Photos", "type_champ": "photo_multiple", "ordre": 6},
    {"nom": "signature", "label": "Signature responsable", "type_champ": "signature", "ordre": 7}
  ]
}
```

### 5.2 Remplissage terrain (Chef/Compagnon)

**Étape 1** : Création du formulaire

```http
POST /api/formulaires
Content-Type: application/json

{
  "template_id": 5,
  "chantier_id": 28,
  "localisation_latitude": 45.5036,
  "localisation_longitude": 6.0565
}
```

→ Statut initial : BROUILLON. Les champs `auto_date`, `auto_heure`, `auto_localisation`, `auto_intervenant` sont pré-remplis.

**Étape 2** : Saisie des champs

```http
PUT /api/formulaires/42
Content-Type: application/json

{
  "champs": [
    {"nom": "titre", "valeur": "Chute de matériau depuis R+1", "type_champ": "texte"},
    {"nom": "description", "valeur": "Un parpaing est tombé du 1er étage...", "type_champ": "texte_long"},
    {"nom": "gravite", "valeur": "grave", "type_champ": "select"}
  ]
}
```

**Étape 3** : Ajout de photos (FOR-04)

```http
POST /api/formulaires/42/photos
Content-Type: application/json

{
  "url": "https://storage/photos/incident_001.jpg",
  "nom_fichier": "incident_zone_R+1.jpg",
  "champ_nom": "photos",
  "latitude": 45.5036,
  "longitude": 6.0565
}
```

Chaque photo est **horodatée** et optionnellement **géolocalisée**.

**Étape 4** : Signature (FOR-05)

```http
POST /api/formulaires/42/signature
Content-Type: application/json

{
  "signature_url": "data:image/png;base64,iVBORw0KGgo...",
  "signature_nom": "Nicolas DELSALLE"
}
```

**Étape 5** : Soumission (FOR-07)

```http
POST /api/formulaires/42/submit
```

→ Statut passe à SOUMIS, `soumis_at` est renseigné automatiquement.

### 5.3 Validation

```http
POST /api/formulaires/42/validate
```

→ Statut passe à VALIDÉ, `valide_by` et `valide_at` renseignés.

### 5.4 Rejet

```http
POST /api/formulaires/42/reject
```

→ Statut retourne à BROUILLON (le rédacteur peut corriger et re-soumettre).

### 5.5 Export PDF (FOR-09)

```http
GET /api/formulaires/42/export
```

→ Réponse : `{ "filename": "formulaire_20260130.pdf", "content_base64": "..." }`

Le PDF contient toutes les données du formulaire, les photos et la signature.

---

## 6. Types de champs

### 6.1 Les 21 types disponibles

| Catégorie | Type | Rendu | Usage |
|-----------|------|-------|-------|
| **Texte** | `texte` | Input texte | Champs courts (titre, nom) |
| | `texte_long` | Textarea | Descriptions, commentaires |
| | `nombre` | Input numérique | Quantités, mesures |
| **Date/Heure** | `date` | Datepicker | Date manuelle |
| | `heure` | Timepicker | Heure manuelle |
| | `date_heure` | DateTimepicker | Date + heure |
| **Sélection** | `checkbox` | Case à cocher | Oui/Non |
| | `radio` | Boutons radio | Choix unique |
| | `select` | Dropdown | Choix unique (liste) |
| | `multi_select` | Dropdown multi | Choix multiples |
| **Auto-rempli** | `auto_date` | Auto | Date du jour (FOR-03) |
| | `auto_heure` | Auto | Heure actuelle (FOR-03) |
| | `auto_localisation` | Auto GPS | Coordonnées GPS (FOR-03) |
| | `auto_intervenant` | Auto | Nom de l'utilisateur (FOR-03) |
| **Média** | `photo` | Capture photo | Photo unique (FOR-04) |
| | `photo_multiple` | Capture multi | Plusieurs photos (FOR-04) |
| | `signature` | Pad signature | Signature manuscrite (FOR-05) |
| **Décoratif** | `titre_section` | Titre H2 | Séparation visuelle |
| | `separateur` | Ligne HR | Séparation visuelle |

### 6.2 Validation des champs

| Propriété | Applicable à | Description |
|-----------|-------------|-------------|
| `obligatoire` | Tous sauf décoratifs | Le champ doit être rempli |
| `validation_regex` | Texte | Pattern regex à respecter |
| `min_value` / `max_value` | Nombre | Bornes numériques |
| `options` | Select, Radio, Multi-select | Liste de choix (obligatoire) |
| `valeur_defaut` | Tous | Valeur pré-remplie |
| `placeholder` | Texte, Nombre | Texte indicatif |

---

## 7. Fonctionnalités terrain

### 7.1 Auto-remplissage (FOR-03)

Quand un formulaire est créé sur le terrain, certains champs sont **automatiquement remplis** :

| Champ auto | Source | Exemple |
|-----------|--------|---------|
| `auto_date` | Horloge du device | 27/01/2026 |
| `auto_heure` | Horloge du device | 14:30 |
| `auto_localisation` | GPS du device | 45.5036, 6.0565 |
| `auto_intervenant` | Session utilisateur | Nicolas DELSALLE |

### 7.2 Photos horodatées (FOR-04)

Chaque photo est enrichie de métadonnées :

```
┌─────────────────────────────────────┐
│  📷 incident_zone_R+1.jpg          │
│                                     │
│  Prise le : 27/01/2026 14:35      │
│  GPS : 45.5036, 6.0565            │
│  Champ : "photos"                  │
│  Formulaire : #42                  │
└─────────────────────────────────────┘
```

### 7.3 Signature manuscrite (FOR-05)

Même mécanisme que pour les feuilles d'heures : signature manuscrite tracée au doigt ou stylet sur tablette, stockée en base64 PNG, avec horodatage et nom du signataire.

### 7.4 Versioning (FOR-08)

Chaque modification significative peut créer une nouvelle version. L'historique est consultable :

```http
GET /api/formulaires/42/history
```

→ Retourne la chaîne des versions : v3 → v2 → v1 (via `parent_id`).

---

## 8. Interactions avec autres modules

| Module | Interaction |
|--------|-------------|
| **Chantiers** | Formulaire lié à un chantier (FOR-10) |
| **GED** | Export PDF stocké en GED |
| **Signalements** | Un formulaire d'incident peut déclencher un signalement |
| **Auth** | `user_id` pour traçabilité, `valide_by` pour validation |

**Note** : L'association de templates obligatoires par type de chantier n'est pas encore implémentée. Les templates sont actuellement sélectionnés manuellement. C'est une évolution possible.

---

## 9. Architecture technique

```
backend/modules/formulaires/
├── domain/
│   ├── entities/          template_formulaire.py, formulaire_rempli.py
│   ├── value_objects/     categorie_formulaire.py, statut_formulaire.py, type_champ.py
│   ├── repositories/      template_repo.py, formulaire_rempli_repo.py
│   └── events/            formulaire_events.py (7 events)
├── application/
│   ├── dtos/              template_dto.py, formulaire_dto.py
│   └── use_cases/         13 use cases (CRUD templates + CRUD formulaires + submit + validate + reject + export PDF + history)
├── adapters/
│   └── controllers/       formulaire_controller.py
└── infrastructure/
    ├── persistence/       template_model.py, formulaire_model.py, sqlalchemy_*_repository.py
    └── web/               formulaire_routes.py, dependencies.py
```

**API Endpoints résumés** :

| Méthode | Endpoint | Action |
|---------|----------|--------|
| POST | `/templates-formulaires` | Créer template |
| GET | `/templates-formulaires` | Lister templates |
| PUT | `/templates-formulaires/{id}` | Modifier template |
| DELETE | `/templates-formulaires/{id}` | Supprimer template |
| POST | `/formulaires` | Créer formulaire (FOR-11) |
| GET | `/formulaires/chantier/{id}` | Lister par chantier (FOR-10) |
| PUT | `/formulaires/{id}` | Saisir les champs (FOR-02) |
| POST | `/formulaires/{id}/photos` | Ajouter photo (FOR-04) |
| POST | `/formulaires/{id}/signature` | Signer (FOR-05) |
| POST | `/formulaires/{id}/submit` | Soumettre (FOR-07) |
| POST | `/formulaires/{id}/validate` | Valider |
| POST | `/formulaires/{id}/reject` | Rejeter |
| GET | `/formulaires/{id}/history` | Historique versions (FOR-08) |
| GET | `/formulaires/{id}/export` | Export PDF (FOR-09) |

---

## 10. Scénarios de test

```python
def test_workflow_complet_formulaire(client):
    """Cycle complet : création → saisie → soumission → validation."""
    # 1. Créer formulaire
    response = client.post("/api/formulaires", json={
        "template_id": 5, "chantier_id": 28})
    assert response.status_code == 201
    form_id = response.json()["id"]
    assert response.json()["statut"] == "brouillon"

    # 2. Remplir les champs
    response = client.put(f"/api/formulaires/{form_id}", json={
        "champs": [{"nom": "titre", "valeur": "Test", "type_champ": "texte"}]})
    assert response.status_code == 200

    # 3. Soumettre
    response = client.post(f"/api/formulaires/{form_id}/submit")
    assert response.status_code == 200
    assert response.json()["statut"] == "soumis"
    assert response.json()["soumis_at"] is not None

    # 4. Valider
    response = client.post(f"/api/formulaires/{form_id}/validate")
    assert response.status_code == 200
    assert response.json()["statut"] == "valide"

def test_modification_formulaire_soumis_interdit(client):
    """Un formulaire soumis ne peut pas être modifié."""
    form_id = create_and_submit_form(client)
    response = client.put(f"/api/formulaires/{form_id}", json={
        "champs": [{"nom": "titre", "valeur": "Modifié", "type_champ": "texte"}]})
    assert response.status_code == 400

def test_rejet_retour_brouillon(client):
    """Le rejet remet le formulaire en brouillon."""
    form_id = create_and_submit_form(client)
    response = client.post(f"/api/formulaires/{form_id}/reject")
    assert response.status_code == 200
    assert response.json()["statut"] == "brouillon"
```

---

## 11. Points d'attention

### 11.1 Évolutions futures

| Amélioration | Priorité | Description |
|-------------|----------|-------------|
| Templates obligatoires par chantier | Haute | PPSPS obligatoire pour tout chantier |
| Mode offline | Haute | Saisie sans réseau, sync différée |
| Workflow approbation multi-niveaux | Moyenne | Chef valide → conducteur contre-valide |
| Notifications | Moyenne | Push quand un formulaire est soumis |
| OCR photos | Basse | Reconnaissance texte sur photos |

### 11.2 UX terrain

| Contrainte | Solution |
|-----------|---------|
| Gros doigts + gants | Champs larges, boutons XL |
| Soleil | Contraste élevé |
| Rapidité | Auto-remplissage GPS/date/intervenant |
| Photos | Capture directe depuis l'appareil photo |

---

**Auteur** : Claude Opus 4.5
**Date dernière mise à jour** : 30 janvier 2026
**Version** : 1.0
**Statut** : ✅ Complet
