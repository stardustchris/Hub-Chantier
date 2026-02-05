## 4. GESTION DES CHANTIERS

### 4.1 Vue d'ensemble

Le module Chantiers centralise toutes les informations d'un projet de construction avec un fil d'actualite temps reel, une gestion documentaire integree et un suivi des equipes affectees. Chaque chantier dispose d'onglets dedies pour une navigation fluide.

### 4.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| CHT-01 | Photo de couverture | Image representative du chantier | ✅ |
| CHT-02 | Couleur chantier | Palette 16 couleurs pour coherence visuelle globale | ✅ |
| CHT-03 | Statut chantier | Ouvert / En cours / Receptionne / Ferme | ✅ |
| CHT-04 | Coordonnees GPS | Latitude + Longitude pour geolocalisation | ✅ |
| CHT-05 | Multi-conducteurs | Affectation de plusieurs conducteurs de travaux | ✅ |
| CHT-06 | Multi-chefs de chantier | Affectation de plusieurs chefs | ✅ |
| CHT-07 | Contact chantier | Nom et telephone du contact sur place | ✅ |
| CHT-08 | Navigation GPS | Bouton direct vers Google Maps / Waze | ✅ |
| CHT-09 | Mini carte | Apercu cartographique avec marqueur de localisation | ✅ |
| CHT-10 | Fil d'actualite | Via module Dashboard avec ciblage chantier (FEED-03) | ✅ |
| CHT-11 | Publications photos/videos | Via module Dashboard (FEED-02) - max 5 photos | ✅ |
| CHT-12 | Commentaires | Via module Dashboard (FEED-05) | ✅ |
| CHT-13 | Signature dans publication | Option de signature electronique | 🔮 Future |
| CHT-14 | Navigation precedent/suivant | Parcourir les fiches chantiers | ✅ |
| CHT-15 | Stockage illimite | Aucune limite sur les documents et medias | ✅ |
| CHT-16 | Liste equipe affectee | Visualisation des collaborateurs assignes | ✅ |
| CHT-17 | Alertes signalements | Indicateur visuel si signalement actif | ⏳ Module signalements |
| CHT-18 | Heures estimees | Budget temps previsionnel du chantier | ✅ |
| CHT-19 | Code chantier | Identifiant unique (ex: A001, B023, 2026-01-MONTMELIAN) | ✅ |
| CHT-20 | Dates debut/fin previsionnelles | Planning macro du projet | ✅ |
| CHT-21 | Onglet Logistique | Reservations materiel, stats et planning dans la fiche | ✅ |
| CHT-TVA | Contexte TVA chantier | Type de travaux (renovation/energetique/neuf), anciennete batiment (> 2 ans), usage habitation — pour pre-remplissage automatique du taux TVA dans les devis | ✅ |

**Note**: CHT-10 a CHT-12 sont implementes via le module Dashboard avec ciblage par chantier. Les posts cibles sur un chantier specifique apparaissent dans le fil d'actualite de ce chantier.

### 4.3 Onglets de la fiche chantier

| N° | Onglet | Description | Acces |
|----|--------|-------------|-------|
| 1 | Resume | Informations generales + fil d'actualite temps reel | Tous |
| 2 | Documents | GED - Gestion documentaire avec droits d'acces | Selon droits |
| 3 | Formulaires | Templates a remplir (rapports, PV...) | Tous |
| 4 | Planning | Affectations equipe semaine par semaine | Chef+ |
| 5 | Taches | Liste des travaux hierarchiques avec avancement | Tous |
| 6 | Feuilles de taches | Declarations quotidiennes par compagnon | Conducteur+ |
| 7 | Feuilles d'heures | Saisie et validation du temps de travail | Tous |
| 8 | Logistique | Reservations materiel, stats et planning | Tous |
| 9 | Arrivees/Departs | Pointage et geolocalisation | Conducteur+ |

### 4.4 Codes chantier

Le code chantier est l'identifiant unique obligatoire de chaque chantier. Deux formats sont supportes :

| Format | Pattern | Exemples | Usage |
|--------|---------|----------|-------|
| **Legacy** | `[A-Z]\d{3}` | A001, B023, Z999 | Chantiers anciens, absences (CONGES, MALADIE) |
| **Standard** | `\d{4}-[A-Z0-9_-]+` | 2026-01-MONTMELIAN, 2024-10-TOURNON-COMMERCIAL | Chantiers depuis 2024 |

**Regles** :
- Code unique par chantier (contrainte DB)
- Auto-generation si non fourni (A001, A002, ..., A999, B001, ...)
- Codes speciaux pour absences : CONGES, MALADIE, FORMATION, RTT, ABSENT
- Format annee-numero-nom recommande pour nouveaux chantiers

### 4.5 Statuts de chantier

| Statut | Icone | Description | Actions possibles |
|--------|-------|-------------|-------------------|
| Ouvert | 🔵 | Chantier cree, en preparation | Planification, affectation equipe |
| En cours | 🟢 | Travaux en cours d'execution | Toutes actions operationnelles |
| Receptionne | 🟡 | Travaux termines, en attente cloture | SAV, levee reserves |
| Ferme | 🔴 | Chantier cloture definitivement | Consultation uniquement |

**Transitions autorisees** :
- Ouvert → En cours, Ferme
- En cours → Receptionne, Ferme
- Receptionne → En cours (reouverture exceptionnelle), Ferme
- Ferme → (aucune transition, etat terminal)

### 4.6 Note technique - Améliorations qualité (31/01/2026)

**Session d'amélioration** : Type coverage, Test coverage, Architecture

**Résultats** :
- **Type coverage** : 85% → 95% (+10%) - 41 type hints ajoutés
- **Test coverage use cases + controller** : 88% → 99% (+11%) - 28 tests générés
- **Clean Architecture** : 6/10 → 10/10 (+4) - 4 violations HIGH résolues
- **Tests** : 120 → 148 (+28 tests, 100% pass)

**Type hints ajoutés** (41 issues):
- Events (4) : ChantierCreatedEvent, ChantierDeletedEvent, ChantierStatutChangedEvent, ChantierUpdatedEvent
- Exceptions (8) : CodeChantierAlreadyExistsError, InvalidDatesError, TransitionNonAutoriseeError, etc.
- Routes FastAPI (24) : Return types pour documentation OpenAPI
- Controller + Repository : Types méthodes __init__ et privées

**Tests controller** (28 tests):
- CRUD operations : create, list, get_by_id, get_by_code, update, delete
- Status management : change_statut, demarrer, receptionner, fermer
- Responsable assignment : conducteur, chef_chantier
- Error handling : ChantierNotFoundError, validation errors
- Fichier : `backend/tests/unit/modules/chantiers/adapters/controllers/test_chantier_controller.py`

**Architecture** (Service Registry pattern):
- Fichier créé : `backend/shared/infrastructure/service_registry.py` (114 lignes)
- Violations corrigées : Suppression imports directs cross-module (auth, formulaires, signalements, pointages)
- Pattern : Service Locator pour isolation stricte des modules
- Impact : Code plus propre (-16 lignes), couplage réduit, réutilisable

**Validation agents** :
- architect-reviewer : PASS (10/10 Clean Architecture, 0 violation)
- code-reviewer : PASS (10/10 qualité)
- security-auditor : PASS (0 critical/high)
- test-automator : 148/148 tests passed in 0.30s

**Commits** :
- `f58aebb` - Type hints (95% coverage)
- `7677c36` - Controller tests (99% coverage)
- `c1865ae` - Architecture fixes (Service Registry)

**Coverage détaillée module chantiers** :
- Use cases : 100%
- Controller : 99%
- Domain services : 100%
- Infrastructure routes : 41% (non testé)
- Infrastructure repository : 28% (non testé)

---