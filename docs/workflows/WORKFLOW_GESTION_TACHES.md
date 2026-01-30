# Workflow Gestion des Taches - Hub Chantier

> Document cree le 30 janvier 2026
> Analyse complete du workflow de gestion des taches par chantier

---

## TABLE DES MATIERES

1. [Vue d'ensemble](#1-vue-densemble)
2. [Entites et objets metier](#2-entites-et-objets-metier)
3. [Statuts et progression](#3-statuts-et-progression)
4. [Taches hierarchiques](#4-taches-hierarchiques)
5. [Unites de mesure et quantites](#5-unites-de-mesure-et-quantites)
6. [Templates de taches](#6-templates-de-taches)
7. [Feuilles de taches et validation](#7-feuilles-de-taches-et-validation)
8. [Drag and drop - Reordonnancement](#8-drag-and-drop---reordonnancement)
9. [Export PDF](#9-export-pdf)
10. [Recherche et filtrage](#10-recherche-et-filtrage)
11. [Statistiques par chantier](#11-statistiques-par-chantier)
12. [Evenements domaine](#12-evenements-domaine)
13. [API REST - Endpoints](#13-api-rest---endpoints)
14. [Architecture technique](#14-architecture-technique)
15. [Frontend - Composants](#15-frontend---composants)
16. [Scenarios de test](#16-scenarios-de-test)
17. [Evolutions futures](#17-evolutions-futures)
18. [References CDC](#18-references-cdc)

---

## 1. VUE D'ENSEMBLE

### Objectif du module

Le module Taches permet de gerer les taches de production par chantier avec suivi d'avancement quantitatif et temporel. Il offre une structure hierarchique (tache/sous-tache), des templates metier pre-definis, des feuilles de taches pour le pointage detail par tache, et un systeme de validation N+1.

### Flux global simplifie

```
Chef de chantier cree des taches pour un chantier
    |
    +---> Manuellement (titre, description, echeance, unite, estimation)
    +---> Import template Gros Oeuvre (7 modeles pre-definis)
    |
    v
[A_FAIRE] Tache creee, sous-taches possibles
    |
    +---> Compagnons remplissent des feuilles de taches
    |     (heures + quantite + commentaire par jour)
    |         |
    |         v
    |     [EN_ATTENTE] Feuille soumise
    |         |
    |         +---> [VALIDEE] --> Heures/quantite ajoutees a la tache
    |         +---> [REJETEE] --> Compagnon peut modifier et resoumettre
    |
    v
[TERMINE] Tache marquee comme terminee
    |
    v
Export PDF du suivi de taches
```

### Complementarite avec les pointages

Les feuilles de taches sont **complementaires** aux feuilles d'heures (pointages) :
- **Feuilles d'heures** : Total d'heures par jour par utilisateur (macro)
- **Feuilles de taches** : Detail des heures et quantites **par tache** (micro)

Un compagnon peut pointer 8h dans sa feuille d'heures, et detailler : 4h coffrage voiles + 3h ferraillage + 1h nettoyage dans ses feuilles de taches.

### Fonctionnalites couvertes (CDC Section Taches)

| ID | Fonctionnalite | Description |
|----|----------------|-------------|
| TAC-01 | Liste taches | Vue par chantier avec filtres |
| TAC-02 | Taches hierarchiques | Parent / sous-taches |
| TAC-03 | Detail expandable | Chevron collapse/expand |
| TAC-04 | Bibliotheque templates | Modeles reutilisables |
| TAC-05 | Import template | Import depuis modele vers chantier |
| TAC-06 | Creation tache | Formulaire complet |
| TAC-07 | Creation multiple | Via modal |
| TAC-08 | Date echeance | Suivi deadline avec alerte retard |
| TAC-09 | Unite de mesure | 9 unites disponibles |
| TAC-10 | Quantite estimee | Objectif quantitatif |
| TAC-11 | Heures estimees | Budget temps |
| TAC-12 | Heures realisees | Suivi reel via feuilles |
| TAC-13 | Statut binaire | A_FAIRE / TERMINE |
| TAC-14 | Recherche | Recherche debounced dans titres/descriptions |
| TAC-15 | Drag & drop | Reordonnancement par glisser-deposer |
| TAC-16 | Export PDF | Export du suivi de taches |
| TAC-18 | Feuilles de taches | Saisie detail par tache/jour |
| TAC-19 | Validation N+1 | Workflow EN_ATTENTE → VALIDEE/REJETEE |
| TAC-20 | Code couleur progression | Gris/Vert/Jaune/Rouge |

---

## 2. ENTITES ET OBJETS METIER

### 2.1 Tache (entite principale)

**Fichier** : `backend/modules/taches/domain/entities/tache.py`

| Champ | Type | Defaut | Requis | Notes |
|-------|------|--------|--------|-------|
| id | Optional[int] | None | Non | Cle primaire |
| chantier_id | int | - | Oui | FK chantier |
| titre | str | - | Oui | Non vide apres strip |
| description | Optional[str] | None | Non | Detail de la tache |
| parent_id | Optional[int] | None | Non | FK taches.id (hierarchie TAC-02) |
| ordre | int | 0 | Non | Ordre d'affichage (TAC-15 drag&drop) |
| statut | StatutTache | A_FAIRE | Non | Binaire : A_FAIRE / TERMINE |
| date_echeance | Optional[date] | None | Non | Deadline (TAC-08) |
| unite_mesure | Optional[UniteMesure] | None | Non | 9 unites (TAC-09) |
| quantite_estimee | Optional[float] | None | Non | Objectif quantitatif (TAC-10) |
| quantite_realisee | float | 0.0 | Non | Reel (incremente via feuilles) |
| heures_estimees | Optional[float] | None | Non | Budget temps (TAC-11) |
| heures_realisees | float | 0.0 | Non | Reel (incremente via feuilles) |
| template_id | Optional[int] | None | Non | Source template si importe (TAC-05) |
| sous_taches | List[Tache] | [] | Non | Enfants (TAC-02) |
| created_at / updated_at | datetime | now() | Non | Horodatages |

**Validations** :
- `titre` non vide (apres strip)
- `heures_estimees` >= 0 (si fourni)
- `heures_realisees` >= 0
- `quantite_estimee` >= 0 (si fourni)
- `quantite_realisee` >= 0

**Methodes cles** :
- `terminer()` - Marquer A_FAIRE → TERMINE
- `rouvrir()` - Marquer TERMINE → A_FAIRE
- `ajouter_heures(heures)` - Incrementer heures_realisees
- `ajouter_quantite(quantite)` - Incrementer quantite_realisee
- `modifier_ordre(nouvel_ordre)` - Changer l'ordre d'affichage
- `ajouter_sous_tache(sous_tache)` - Ajouter un enfant

**Proprietes calculees** :
- `est_terminee` - statut == TERMINE
- `est_en_retard` - date_echeance passee et non terminee
- `progression_heures` - 0-100% (heures_realisees / heures_estimees)
- `progression_quantite` - 0-100% (quantite_realisee / quantite_estimee)
- `couleur_progression` - CouleurProgression calculee (TAC-20)
- `a_sous_taches` / `nombre_sous_taches` / `nombre_sous_taches_terminees`

### 2.2 FeuilleTache (TAC-18, TAC-19)

**Fichier** : `backend/modules/taches/domain/entities/feuille_tache.py`

| Champ | Type | Defaut | Requis | Notes |
|-------|------|--------|--------|-------|
| id | Optional[int] | None | Non | Cle primaire |
| tache_id | int | - | Oui | FK tache |
| utilisateur_id | int | - | Oui | FK user (compagnon) |
| chantier_id | int | - | Oui | FK chantier |
| date_travail | date | - | Oui | Jour de travail |
| heures_travaillees | float | 0.0 | Non | Heures sur cette tache ce jour |
| quantite_realisee | float | 0.0 | Non | Quantite realisee ce jour |
| commentaire | Optional[str] | None | Non | Note du compagnon |
| statut_validation | StatutValidation | EN_ATTENTE | Non | Workflow validation |
| validateur_id | Optional[int] | None | Non | Qui a valide/rejete |
| date_validation | Optional[datetime] | None | Non | Quand |
| motif_rejet | Optional[str] | None | Non | Motif si rejete (requis) |
| created_at / updated_at | datetime | now() | Non | Horodatages |

**Methodes cles** :
- `valider(validateur_id)` - EN_ATTENTE → VALIDEE, enregistre validateur et date
- `rejeter(validateur_id, motif)` - EN_ATTENTE → REJETEE, motif obligatoire
- `remettre_en_attente()` - Reset vers EN_ATTENTE
- `modifier(heures, quantite, commentaire)` - Met a jour si EN_ATTENTE ; si REJETEE, auto-revert vers EN_ATTENTE

**Regle importante** : On ne peut pas modifier une feuille deja VALIDEE (ValueError leve).

### 2.3 TemplateModele (TAC-04, TAC-05)

**Fichier** : `backend/modules/taches/domain/entities/template_modele.py`

| Champ | Type | Defaut | Requis | Notes |
|-------|------|--------|--------|-------|
| id | Optional[int] | None | Non | Cle primaire |
| nom | str | - | Oui | Unique, non vide |
| description | Optional[str] | None | Non | Description du modele |
| categorie | Optional[str] | None | Non | Ex: "Gros Oeuvre" |
| unite_mesure | Optional[UniteMesure] | None | Non | Unite par defaut |
| heures_estimees_defaut | Optional[float] | None | Non | Heures par defaut |
| sous_taches | List[SousTacheModele] | [] | Non | Sous-taches du modele |
| is_active | bool | True | Non | Template actif/inactif |
| created_at / updated_at | datetime | now() | Non | Horodatages |

**SousTacheModele** (nested) :
- `titre` (str, requis, non vide)
- `description` (Optional[str])
- `ordre` (int, defaut 0)
- `unite_mesure` (Optional[UniteMesure])
- `heures_estimees_defaut` (Optional[float])

---

## 3. STATUTS ET PROGRESSION

### StatutTache (binaire)

| Valeur | Display | Icone | Couleur |
|--------|---------|-------|---------|
| A_FAIRE | "A faire" | ☐ | #9E9E9E |
| TERMINE | "Termine" | ✅ | #4CAF50 |

Le statut est **binaire** par conception. Pas d'etats intermediaires (en cours, en revue, etc.).

### CouleurProgression (TAC-20)

Systeme de code couleur base sur le ratio heures_realisees / heures_estimees :

| Couleur | Hex | Condition | Label | Icone |
|---------|-----|-----------|-------|-------|
| GRIS | #9E9E9E | heures_realisees == 0 | "Non commence" | ⚪ |
| VERT | #4CAF50 | ratio <= 80% | "Dans les temps" | 🟢 |
| JAUNE | #FFC107 | 80% < ratio <= 100% | "Attention" | 🟡 |
| ROUGE | #F44336 | ratio > 100% | "Depassement" | 🔴 |

**Algorithme** :
```
si heures_realisees == 0 → GRIS
sinon si heures_estimees <= 0 → ROUGE (si heures > 0, sinon GRIS)
sinon:
    ratio = heures_realisees / heures_estimees
    si ratio <= 0.8 → VERT
    sinon si ratio <= 1.0 → JAUNE
    sinon → ROUGE
```

Les seuils (0%, 80%, 100%) sont documentes tels quels. Ils ne sont pas configurables actuellement.

---

## 4. TACHES HIERARCHIQUES

### Relation parent-enfant (TAC-02)

- Champ `parent_id` : FK self-referential vers `taches.id`
- `sous_taches: List[Tache]` : Liste des enfants charges en lazy
- **Cascade delete** : Supprimer un parent supprime ses enfants
- **Profondeur** : Pas de limite technique, mais 2-3 niveaux en pratique

### Rendu frontend

- Composant `TaskItem` se rend recursivement avec prop `level`
- **Indentation** : `paddingLeft = level * 24px`
- **Bordure gauche** sur les sous-taches pour repere visuel
- **Chevron** collapse/expand pour plier/deplier les sous-taches
- **Badge** : "2/5" indiquant sous-taches terminees / total

### Creation de sous-tache

- API : `POST /taches` avec `parent_id` renseigne
- Frontend : Action "Ajouter une sous-tache" dans le menu contextuel
- Le `chantier_id` est herite du parent

---

## 5. UNITES DE MESURE ET QUANTITES

### 9 unites disponibles (TAC-09)

| Valeur | Label | Symbole | Usage typique |
|--------|-------|---------|---------------|
| m2 | Metres carres | m² | Coffrage, decoffrage, pose predalles |
| m3 | Metres cubes | m³ | Coulage beton |
| ml | Metres lineaires | ml | Traitement reprise |
| kg | Kilogrammes | kg | Ferraillage |
| tonne | Tonnes | tonne | Materiaux lourds |
| litre | Litres | litre | Fluides |
| unite | Unites | unite | Reservations, pieces |
| heure | Heures | heure | Main d'oeuvre |
| jour | Jours | jour | Duree |

### Suivi quantitatif

- `quantite_estimee` : Objectif (ex: 150 m² de coffrage)
- `quantite_realisee` : Reel (incremente via feuilles de taches validees)
- `progression_quantite` : 0-100% calcule automatiquement

---

## 6. TEMPLATES DE TACHES

### Concept (TAC-04, TAC-05)

Les templates sont un **starter kit** : 7 modeles Gros Oeuvre pre-definis pour demarrer rapidement. Les utilisateurs peuvent aussi creer leurs propres templates.

### 7 modeles Gros Oeuvre pre-definis

| # | Template | Unite | Sous-taches |
|---|----------|-------|-------------|
| 1 | Coffrage voiles | m² | 4 sous-taches |
| 2 | Ferraillage plancher | kg | 4 sous-taches |
| 3 | Coulage beton | m³ | 5 sous-taches |
| 4 | Decoffrage | m² | 4 sous-taches |
| 5 | Pose predalles | m² | 4 sous-taches |
| 6 | Reservations | unite | 4 sous-taches |
| 7 | Traitement reprise | ml | 3 sous-taches |

### Import d'un template (TAC-05)

**Endpoint** : `POST /templates-taches/import`

**Corps** : `{ template_id: int, chantier_id: int }`

**Processus** :
1. Charger le template depuis la base
2. Determiner le prochain `ordre` selon les taches existantes du chantier
3. Creer la tache principale avec nom, description, unite, heures du template
4. Creer les sous-taches avec `parent_id` = tache principale
5. Emettre `TachesImportedFromTemplateEvent`
6. Retourner les DTOs des taches creees

---

## 7. FEUILLES DE TACHES ET VALIDATION

### Concept (TAC-18)

Une feuille de tache enregistre le travail d'un compagnon sur une tache precise pour un jour donne. C'est le pointage **detail par tache**.

### Workflow de validation (TAC-19)

```
Compagnon remplit feuille de tache
    |
    v
[EN_ATTENTE] Soumise pour validation
    |
    +---> Chef valide
    |     |
    |     v
    |   [VALIDEE]
    |     └──> heures_realisees += heures_travaillees (sur la tache)
    |     └──> quantite_realisee += quantite_realisee (sur la tache)
    |
    +---> Chef rejette (motif obligatoire)
          |
          v
        [REJETEE]
          └──> Compagnon modifie → auto-revert EN_ATTENTE
```

### Regles metier

- **Validation** : Ajoute heures et quantite a la tache parente. Emmet `FeuilleTacheValidatedEvent`.
- **Rejet** : Motif obligatoire (non vide). Emmet `FeuilleTacheRejectedEvent`. Pas d'impact sur la tache.
- **Modification apres rejet** : Modifie heures/quantite/commentaire → auto-revert vers EN_ATTENTE, efface validateur/date/motif.
- **Modification apres validation** : Interdit (ValueError).

### Endpoint validation

`POST /feuilles-taches/{feuille_id}/validate`

```json
{
  "valider": true,         // true = approuver, false = rejeter
  "motif_rejet": "..."     // requis si valider=false
}
```

---

## 8. DRAG AND DROP - REORDONNANCEMENT

### Mecanisme (TAC-15)

Chaque tache a un champ `ordre: int` (0-based) qui determine sa position d'affichage.

**Endpoint** : `POST /taches/reorder`

**Corps** : Liste de `{ tache_id: int, ordre: int }`

Le frontend envoie les positions finales apres glisser-deposer. Le backend met a jour le champ `ordre` et `updated_at` pour chaque tache.

### Frontend

Le composant `TaskItem` dispose d'un **drag handle** (icone 4 lignes). Le `TaskList` gere les callbacks de reordonnancement.

---

## 9. EXPORT PDF

### Mecanisme (TAC-16)

**Endpoint** : `GET /taches/chantier/{chantier_id}/export-pdf?include_completed=true`

**Reponse** :
- `Content-Type: application/pdf` (si WeasyPrint disponible)
- `Content-Type: text/html` (fallback si WeasyPrint absent)
- `Content-Disposition: attachment; filename="taches-{chantier_nom}.pdf"`

**Contenu** : Liste hierarchique des taches, statistiques, progression.

**Securite** :
- Validation du nom de chantier : max 200 caracteres, pattern `^[\w\s\-\.\'A-ÿ]+$`
- Piste d'audit RGPD : log user_id, IP, user-agent

---

## 10. RECHERCHE ET FILTRAGE

### Recherche (TAC-14)

**Parametres** : `GET /taches/chantier/{chantier_id}?query=...&statut=...&include_sous_taches=true`

- **Query** : Max 100 caracteres, pattern alphanumerique + accents + ponctuation
- **Frontend** : Debounced a 300ms
- **Backend** : Recherche LIKE dans titres et descriptions

### Filtres

- `statut` : "a_faire" | "termine"
- `include_sous_taches` : true (defaut) pour charger la hierarchie
- Pagination : `page` (defaut 1) et `size` (defaut 50)

---

## 11. STATISTIQUES PAR CHANTIER

### TacheStatsResponse (TAC-20)

**Endpoint** : `GET /taches/chantier/{chantier_id}/stats`

| Champ | Description |
|-------|-------------|
| total_taches | Nombre total de taches |
| taches_terminees | Taches completees |
| taches_en_cours | Taches en cours (a_faire, non terminees) |
| taches_en_retard | Taches en retard (est_en_retard=true) |
| heures_estimees_total | Somme heures estimees |
| heures_realisees_total | Somme heures realisees |
| progression_globale | 0-100% (realisees / estimees) |

### Code couleur global

La progression globale utilise les memes seuils que les taches individuelles :
- 0% → Gris
- 1-80% → Vert
- 81-100% → Jaune
- >100% → Rouge

---

## 12. EVENEMENTS DOMAINE

**Fichier** : `backend/modules/taches/domain/events/tache_events.py`

| Evenement | Champs | Declencheur |
|-----------|--------|-------------|
| **TacheCreatedEvent** | tache_id, chantier_id, titre, parent_id, template_id | Creation tache |
| **TacheUpdatedEvent** | tache_id, chantier_id, updated_fields | Modification |
| **TacheDeletedEvent** | tache_id, chantier_id, titre | Suppression |
| **TacheTermineeEvent** | tache_id, chantier_id, titre, heures_realisees, quantite_realisee | Completion |
| **SousTacheAddedEvent** | sous_tache_id, parent_id, chantier_id, titre | Ajout sous-tache |
| **FeuilleTacheCreatedEvent** | feuille_id, tache_id, utilisateur_id, chantier_id, heures, quantite, date | Saisie feuille |
| **FeuilleTacheValidatedEvent** | feuille_id, tache_id, utilisateur_id, validateur_id, heures | Validation |
| **FeuilleTacheRejectedEvent** | feuille_id, tache_id, utilisateur_id, validateur_id, motif | Rejet |
| **TachesImportedFromTemplateEvent** | template_id, chantier_id, taches_creees (List[int]) | Import template |

---

## 13. API REST - ENDPOINTS

### Taches (TAC-01 a TAC-16)

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/taches/chantier/{chantier_id}` | Lister taches (pagination, filtres, recherche) |
| GET | `/taches/chantier/{chantier_id}/stats` | Statistiques (TAC-20) |
| GET | `/taches/chantier/{chantier_id}/export-pdf` | Export PDF (TAC-16) |
| GET | `/taches/{tache_id}` | Detail tache |
| POST | `/taches` | Creer tache (TAC-06) |
| PUT | `/taches/{tache_id}` | Mettre a jour |
| DELETE | `/taches/{tache_id}` | Supprimer (cascade sous-taches) |
| POST | `/taches/{tache_id}/complete` | Terminer/rouvrir (TAC-13) |
| POST | `/taches/reorder` | Reordonnancer (TAC-15) |

### Templates (TAC-04, TAC-05)

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/templates-taches` | Lister templates |
| POST | `/templates-taches` | Creer template |
| POST | `/templates-taches/import` | Importer vers chantier |

### Feuilles de taches (TAC-18, TAC-19)

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/feuilles-taches/tache/{tache_id}` | Feuilles par tache |
| GET | `/feuilles-taches/chantier/{chantier_id}` | Feuilles par chantier |
| GET | `/feuilles-taches/en-attente` | Feuilles en attente de validation |
| POST | `/feuilles-taches` | Creer feuille |
| POST | `/feuilles-taches/{feuille_id}/validate` | Valider/rejeter |

**Total : 17 endpoints**

---

## 14. ARCHITECTURE TECHNIQUE

### Clean Architecture

```
taches/
├── domain/
│   ├── entities/
│   │   ├── tache.py                  # Entite principale (hierarchique)
│   │   ├── feuille_tache.py          # Pointage detail par tache
│   │   └── template_modele.py        # Templates + SousTacheModele
│   ├── value_objects/
│   │   ├── statut_tache.py           # A_FAIRE / TERMINE
│   │   ├── couleur_progression.py    # GRIS / VERT / JAUNE / ROUGE
│   │   └── unite_mesure.py           # 9 unites
│   ├── events/
│   │   └── tache_events.py           # 9 evenements
│   └── repositories/                 # Interfaces abstraites
├── application/
│   ├── dtos/                         # Request/Response DTOs
│   └── use_cases/
│       ├── tache_use_cases.py        # CRUD + completion
│       ├── reorder_taches.py         # Drag & drop
│       ├── import_template.py        # Import template
│       ├── export_pdf.py             # Export PDF
│       └── feuille_tache_use_cases.py # Feuilles + validation
└── infrastructure/
    └── persistence/
        ├── tache_model.py            # Table taches (self-ref FK)
        ├── feuille_tache_model.py    # Table feuilles_taches
        └── template_modele_model.py  # Tables templates + sous_taches_modeles
```

### Schema base de donnees

**Tables** : taches, feuilles_taches, templates_modeles, sous_taches_modeles

**Index notables** :
- `taches.chantier_id` (recherche par chantier)
- `taches.parent_id` (hierarchie)
- `feuilles_taches.tache_id`, `utilisateur_id`, `chantier_id`, `date_travail`
- `templates_modeles.categorie`, `nom` (UNIQUE)

---

## 15. FRONTEND - COMPOSANTS

### TaskList.tsx (composant principal)

**Props** : `chantierId: number, chantierNom: string`

**Fonctionnalites** :
- Liste paginee (50 taches/page)
- Recherche debounced (300ms) (TAC-14)
- Filtres par statut : "Toutes" | "A faire" | "Terminees"
- Dashboard statistiques (TAC-20) : total, terminees, en retard, progression
- Bouton import template (TAC-05)
- Bouton export PDF (TAC-16) avec etat de chargement
- Modal creation/edition tache
- Rendu recursif des TaskItem

### TaskItem.tsx (composant tache individuelle)

**Props** : `tache: Tache, level?: number, isDragging?: boolean, dragHandleProps?: object`

**Affichage** :
- Chevron collapse/expand pour sous-taches (TAC-03)
- Checkbox completion (TAC-13)
- Cercle couleur progression (TAC-20)
- Titre (barre si termine)
- Badge sous-taches (ex: "2/5")
- Info secondaire (responsive) : echeance, heures, quantite, barre de progression
- Menu contextuel : ajouter sous-tache, editer, supprimer
- Drag handle (TAC-15)
- Rendu recursif des enfants avec indentation (level * 24px)

### TaskModal.tsx (formulaire)

**Champs** :
1. Titre (requis, max 255, placeholder "Ex: Coffrage voiles R+1")
2. Description (textarea 3 lignes)
3. Date echeance (date picker)
4. Unite de mesure (dropdown 9 options + "Aucune")
5. Quantite estimee (number, desactive si pas d'unite)
6. Heures estimees (number, step 0.5, suffix "h")

**Titre dynamique** : "Nouvelle tache" / "Ajouter une sous-tache" / "Modifier la tache"

### TemplateImportModal.tsx (import template)

**Fonctionnalites** :
- Recherche templates (debounced, filtrage temps reel)
- Filtre par categorie (boutons)
- Selection simple (surbrillance)
- Apercu du template selectionne : description, badge categorie, nombre sous-taches, unite, heures
- Bouton import avec spinner

---

## 16. SCENARIOS DE TEST

| # | Scenario | Resultat attendu |
|---|----------|-----------------|
| 1 | Creer tache avec titre vide | Erreur validation |
| 2 | Creer tache avec heures estimees | OK, couleur GRIS (0 heures realisees) |
| 3 | Ajouter sous-tache | parent_id renseigne, chantier_id herite |
| 4 | Supprimer tache parent | Cascade : sous-taches supprimees |
| 5 | Terminer tache | statut = TERMINE, est_terminee = True |
| 6 | Rouvrir tache terminee | statut = A_FAIRE |
| 7 | Importer template Gros Oeuvre | Tache + sous-taches creees, template_id renseigne |
| 8 | Creer feuille de tache | statut EN_ATTENTE |
| 9 | Valider feuille | VALIDEE, heures/quantite ajoutees a la tache |
| 10 | Rejeter sans motif | Erreur validation |
| 11 | Modifier feuille rejetee | Auto-revert EN_ATTENTE |
| 12 | Modifier feuille validee | Erreur (ValueError) |
| 13 | Reordonnancer 3 taches | Ordres mis a jour |
| 14 | Export PDF | Fichier genere (PDF ou HTML fallback) |
| 15 | Progression > 100% | Couleur ROUGE |

---

## 17. EVOLUTIONS FUTURES

| Evolution | Description | Priorite |
|-----------|-------------|----------|
| Templates utilisateur | Interface complete de gestion des templates personnalises | Moyenne |
| Affectation de tache a un compagnon | Lier une tache a un utilisateur specifique | Moyenne |
| Notifications echeance | Alert J-1 avant deadline | Moyenne |
| Gantt interactif | Vue timeline des taches avec dependances | Basse |
| Import CSV | Import massif de taches depuis fichier | Basse |

---

## 18. REFERENCES CDC

| Section | Fonctionnalites | Status |
|---------|----------------|--------|
| TAC-01 a TAC-03 | Liste, hierarchie, detail expandable | Backend + Frontend OK |
| TAC-04, TAC-05 | Templates et import | Backend + Frontend OK |
| TAC-06 a TAC-08 | Creation, echeance | Backend + Frontend OK |
| TAC-09 a TAC-12 | Unites, quantites, heures | Backend + Frontend OK |
| TAC-13 | Statut binaire | Backend + Frontend OK |
| TAC-14 | Recherche | Backend + Frontend OK |
| TAC-15 | Drag & drop | Backend + Frontend OK |
| TAC-16 | Export PDF | Backend OK, Frontend OK |
| TAC-18, TAC-19 | Feuilles de taches + validation | Backend OK |
| TAC-20 | Code couleur progression | Backend + Frontend OK |
