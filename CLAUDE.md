# Hub Chantier - Contexte pour Claude

> Ce fichier est lu par Claude au debut de chaque session.
> Il permet de reprendre le travail la ou on s'est arrete.

## Projet

- **Client** : Greg Construction (20 employes, 4,3M EUR CA)
- **Type** : Application SaaS de gestion de chantiers BTP
- **Initie le** : 21 janvier 2026

## Documentation

| Fichier | Description |
|---------|-------------|
| `docs/SPECIFICATIONS.md` | Cahier des charges fonctionnel (177 fonctionnalites) |
| `docs/CDC Greg Constructions v2.1.docx` | CDC original client |
| `CONTRIBUTING.md` | Conventions, workflow, checklist |
| `docs/architecture/CLEAN_ARCHITECTURE.md` | Architecture detaillee |
| `docs/architecture/ADR/` | Decisions d'architecture |
| `.claude/agents.md` | Regles d'utilisation des sous-agents |
| `.claude/history.md` | Historique des sessions de travail |

## Architecture (resume)

Clean Architecture 4 layers : `Domain → Application → Adapters → Infrastructure`

**Regle d'or** : Les dependances pointent TOUJOURS vers l'interieur.

### Regles critiques

1. **Domain layer = PURE** - Aucune dependance technique (pas de FastAPI, SQLAlchemy, Pydantic)
2. **Use cases dependent d'interfaces** - Jamais d'implementations directes
3. **Communication inter-modules via EventBus** - Pas d'import direct entre modules
4. **Module `auth` = reference** - Toujours s'en inspirer

> Details complets : `CONTRIBUTING.md`

## Etat des modules

| Module | CDC Section | Fonctionnalites | Status |
|--------|-------------|-----------------|--------|
| auth (utilisateurs) | 3 | USR-01 a USR-13 | **COMPLET** |
| dashboard | 2 | FEED-01 a FEED-20 | **COMPLET** |
| chantiers | 4 | CHT-01 a CHT-20 | **COMPLET** |
| planning | 5 | PLN-01 a PLN-28 | **COMPLET** |
| planning_charge | 6 | PDC-01 a PDC-17 | Structure only |
| feuilles_heures | 7 | FDH-01 a FDH-20 | **COMPLET** |
| formulaires | 8 | FOR-01 a FOR-11 | **COMPLET** |
| documents | 9 | GED-01 a GED-15 | Structure only |
| memos | 10 | MEM-01 a MEM-13 | Structure only |
| logistique | 11 | LOG-01 a LOG-18 | Structure only |
| interventions | 12 | INT-01 a INT-17 | Structure only |
| taches | 13 | TAC-01 a TAC-20 | **COMPLET** |

> Details des modules : voir `.claude/history.md`

## Prochaines taches prioritaires

1. [x] **Module dashboard** (CDC Section 2) - Backend complet + Frontend
2. [x] **Module chantiers** (CDC Section 4) - CRUD chantiers avec statuts et GPS + Frontend
3. [x] **Frontend React** - Dashboard, Chantiers, Utilisateurs
4. [x] **Module planning** (CDC Section 5) - Backend complet (API REST + Domain Events + 220 tests)
5. [x] **Module feuilles_heures** (CDC Section 7) - Backend complet (API REST + 17/20 fonctionnalites)
6. [x] **Frontend Planning** - Interface React pour le planning operationnel
7. [x] **Frontend Feuilles d'heures** - Interface React pour la saisie des heures
8. [x] **Module taches** (CDC Section 13) - Backend complet (API REST + 20/20 fonctionnalites)
9. [x] **Frontend Taches** - Interface React pour la gestion des taches (onglet dans fiche chantier)
10. [x] **Module formulaires** (CDC Section 8) - Backend complet (API REST + 11/11 fonctionnalites)
11. [ ] **Frontend formulaires** - Interface React pour les formulaires terrain

## Workflow de developpement

**Regles d'utilisation des sous-agents** : `.claude/agents.md`

### REGLE CRITIQUE - Verification environnement (DEBUT DE SESSION)

**AU DEBUT de chaque session de developpement, OBLIGATOIREMENT :**

```bash
# 1. Installer les dependances backend
cd backend && pip install -r requirements.txt

# 2. Verifier que TOUS les tests passent
python -m pytest tests/unit -v --tb=short

# 3. Installer les dependances frontend
cd ../frontend && npm install

# 4. Verifier le build frontend
npm run build
```

**NE PAS commencer le developpement si ces verifications echouent.**

> Cette regle existe car ne pas verifier l'environnement en debut de session
> rend impossible la validation du code et peut mener a pousser du code casse.

### REGLE CRITIQUE - Couverture de tests >= 85%

**AVANT tout commit, verifier la couverture du code modifie :**

```bash
cd backend && python -m pytest tests/unit --cov=modules --cov-report=term-missing
```

**Seuil minimum : 85% sur le code modifie/ajoute.**

- Si couverture < 85% : ajouter des tests avant de committer
- Verifier particulierement les use cases et les entites domain

### REGLE CRITIQUE - Tests obligatoires par couche

**Chaque module COMPLET doit avoir :**

| Couche | Tests requis | Emplacement |
|--------|--------------|-------------|
| Domain | Entites, Value Objects | `tests/unit/{module}/test_entities.py`, `test_value_objects.py` |
| Application | Use Cases (tous) | `tests/unit/{module}/test_use_cases.py` |
| Infrastructure | Repository | `tests/unit/{module}/test_repository.py` |
| **API** | **Integration tests** | `tests/integration/test_{module}_api.py` |

**VERIFICATION OBLIGATOIRE avant de marquer un module COMPLET :**

```bash
# Verifier qu'un test d'integration existe pour chaque module backend complet
ls backend/tests/integration/test_*_api.py
```

**Si un fichier manque → Le module N'EST PAS complet.**

> Cette regle existe car les tests d'integration API sont essentiels pour detecter
> les regressions sur les endpoints FastAPI et les problemes d'integration DB.

### REGLE CRITIQUE - Pre-commit

**AVANT tout `git commit` contenant `*.py`, `*.ts`, `*.tsx`, `*.sql` :**

```
1. Lancer architect-reviewer → Corriger violations
2. Lancer test-automator → Noter les gaps
3. Lancer code-reviewer → Corriger issues critiques
4. Verifier tests integration: ls tests/integration/test_*_api.py
5. SEULEMENT APRES → git commit
```

> Details : `.claude/pre-commit-checklist.md`

### Quand une fonctionnalite est demandee

(ex: "Implemente CHT-03"):
1. Lire `docs/SPECIFICATIONS.md` pour les details
2. `python-pro` implemente selon Clean Architecture
3. `architect-reviewer` verifie la conformite
4. `test-automator` genere les tests pytest
5. `code-reviewer` verifie qualite et securite
6. Mettre a jour SPECIFICATIONS.md:
   - Modifier le contenu si l'implementation differe de la spec initiale
   - Ajouter la feature si nouvelle (hors CDC)
   - Passer le statut a ✅
7. Mettre a jour `.claude/history.md` avec le resume de la session

> **SPECIFICATIONS.md = source de verite vivante** - elle reflète toujours l'implementation reelle


### Apres validation complete

Quand tous les agents ont valide et les tests passent :
1. Committer et pousser sur la branche de travail
2. **Proposer automatiquement** de merger sur main (PR ou merge direct)
3. Ne pas attendre que l'utilisateur le demande

---
## Commandes utiles

```bash
# Dev
./scripts/start-dev.sh

# Tests
pytest backend/tests/unit -v
pytest --cov=backend --cov-report=html

# Verification architecture
./scripts/check-architecture.sh

# Nouveau module
./scripts/generate-module.sh nom_module
```

## En cas de doute

1. Consulter `modules/auth/` comme module de reference
2. Lire `docs/SPECIFICATIONS.md` pour les specs fonctionnelles
3. Lire `CONTRIBUTING.md` pour les conventions
4. Lire `.claude/agents.md` pour le workflow agents
5. Lancer `./scripts/check-architecture.sh`

## Blocages / Questions en suspens

(Aucun pour l'instant)
