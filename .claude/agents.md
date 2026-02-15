# Regles d'utilisation des sous-agents

> Ce fichier definit quand Claude doit utiliser des sous-agents specialises.
> L'utilisateur n'a pas a s'en occuper - c'est automatique.

---

## REGLES CRITIQUES (rappel — voir aussi CLAUDE.md)

### Sous-agents background INTERDITS
- **JAMAIS** de `run_in_background: true` — les agents background plantent systematiquement (confirme x3)
- Validations = Grep/Read directs dans le contexte principal
- Agents foreground synchrones OK si necessaire

### Source des agents d'implementation
Les agents d'implementation doivent etre choisis depuis le catalogue officiel :
**https://github.com/VoltAgent/awesome-claude-code-subagents/tree/main** (127+ agents, 10 categories)
Toujours privilegier un agent du catalogue plutot qu'un agent generique.

---

## Agents disponibles (16 agents)

### Agents d'implementation (6)

| Agent | Prompt | Role | Outils |
|-------|--------|------|--------|
| sql-pro | `agents/sql-pro.md` | Expert SQL/PostgreSQL, schema, migrations | Read, Glob, Grep, Bash |
| postgres-pro | `agents/postgres-pro.md` | Expert PostgreSQL avance (replication, PITR, tuning) | Read, Write, Edit, Bash, Glob, Grep |
| python-pro | `agents/python-pro.md` | Expert FastAPI/SQLAlchemy | Read, Write, Edit, Bash |
| typescript-pro | `agents/typescript-pro.md` | Expert React/TypeScript | Read, Write, Edit, Bash |
| react-specialist | `agents/react-specialist.md` | Expert React 18+ (hooks, SSR, performance) | Read, Write, Edit, Bash, Glob, Grep |
| api-designer | `agents/api-designer.md` | Expert REST/GraphQL API design, OpenAPI | Read, Write, Edit, Bash, Glob, Grep |

### Agents de validation (5)

| Agent | Prompt | Role | Outils |
|-------|--------|------|--------|
| architect-reviewer | `agents/architect-reviewer.md` | Validation Clean Architecture | Read, Glob, Grep |
| test-automator | `agents/test-automator.md` | Generation de tests pytest/vitest | Read, Write, Edit, Bash |
| code-reviewer | `agents/code-reviewer.md` | Qualite et conventions du code | Read, Glob, Grep |
| security-auditor | `agents/security-auditor.md` | Audit securite et vulnerabilites | Read, Glob, Grep |
| compliance-auditor | `agents/compliance-auditor.md` | Conformite RGPD, SOC2, ISO 27001 | Read, Glob, Grep |

### Agents specialises (5)

| Agent | Prompt | Role | Outils |
|-------|--------|------|--------|
| performance-engineer | `agents/performance-engineer.md` | Optimisation performance, profiling, load testing | Read, Write, Edit, Bash, Glob, Grep |
| accessibility-tester | `agents/accessibility-tester.md` | Conformite WCAG, accessibilite PWA | Read, Glob, Grep, Bash |
| business-analyst | `agents/business-analyst.md` | Analyse specs metier BTP, requirements | Read, Write, Edit, Glob, Grep, WebFetch, WebSearch |
| documentation-engineer | `agents/documentation-engineer.md` | Documentation technique, API docs | Read, Write, Edit, Glob, Grep, WebFetch, WebSearch |
| devops-engineer | `agents/devops-engineer.md` | CI/CD, Docker, deploiement, monitoring | Read, Write, Edit, Bash, Glob, Grep |

---

## Declencheurs automatiques

### Quand implementer une fonctionnalite du CDC

```
Utilisateur demande: "Implemente CHT-03" ou "Cree le module chantiers"

1. [SPECS] Lire docs/SPECIFICATIONS.md pour les details de la fonctionnalite
2. [sql-pro] Concevoir le schema DB et migrations (si nouvelles tables/colonnes)
3. [python-pro] Implementer selon Clean Architecture
4. [architect-reviewer] Verifier la conformite architecture
5. [test-automator] Generer les tests unitaires
6. [code-reviewer] Verifier qualite du code
7. [security-auditor] Audit securite et conformite RGPD
8. [SPECS] Mettre a jour SPECIFICATIONS.md:
   - Modifier le contenu si l'implementation differe de la spec initiale
   - Passer le statut a ✅
9. [DOCS] Mettre a jour .claude/history.md (resume session)
```

### Quand ajouter une nouvelle fonctionnalite (hors CDC initial)

```
Utilisateur demande: "Ajoute la fonctionnalite X"

1. [SPECS] Ajouter la fonctionnalite dans SPECIFICATIONS.md:
   - Generer un nouvel ID (ex: CHT-21 si c'est pour chantiers)
   - Documenter la spec complete (description, regles metier, criteres)
   - Status initial: ⏳
2. [sql-pro] Concevoir le schema DB et migrations (si nouvelles tables/colonnes)
3. [python-pro] Implementer selon Clean Architecture
4. [architect-reviewer] Verifier la conformite architecture
5. [test-automator] Generer les tests unitaires
6. [code-reviewer] Verifier qualite du code
7. [security-auditor] Audit securite et conformite RGPD
8. [SPECS] Passer le statut a ✅
9. [DOCS] Mettre a jour .claude/history.md (resume session)
```

### Quand creer un nouveau module

```
Utilisateur demande: "Cree le module X"

1. [SPECS] Lire la section correspondante dans SPECIFICATIONS.md
2. [sql-pro] Concevoir le schema DB du module (tables, relations, index)
3. [python-pro] Creer la structure:
   - domain/entities/
   - domain/value_objects/
   - domain/repositories/ (interfaces)
   - domain/events/
   - application/use_cases/
   - application/dtos/
   - adapters/controllers/
   - infrastructure/persistence/
   - infrastructure/web/
4. [architect-reviewer] Valider la structure
5. [test-automator] Generer les tests de base
6. [security-auditor] Valider securite du module (si donnees sensibles)
7. [DOCS] Mettre a jour .claude/project-status.md (etat module)
```

### Quand modifier du code existant

```
Utilisateur demande: "Modifie X" ou "Corrige Y"

1. [sql-pro] Si modifications DB: migrations, index (optionnel)
2. [python-pro/typescript-pro] Effectuer les modifications
3. [architect-reviewer] Verifier que Clean Architecture est respectee
4. [test-automator] Mettre a jour les tests si necessaire
5. [code-reviewer] Verifier qualite du code
6. [security-auditor] Si donnees sensibles: audit securite (optionnel)
```

---

## Quand utiliser les nouveaux agents

### postgres-pro (complementaire a sql-pro)
```
Utilisateur demande: "Optimise les requetes" ou "Configure la replication"

→ Utiliser postgres-pro pour:
  - Replication streaming/logique
  - PITR (Point-In-Time Recovery)
  - Tuning avance (vacuum, checkpoints)
  - Extensions (pg_stat_statements, PostGIS)
  - Partitionnement de tables
```

### react-specialist (complementaire a typescript-pro)
```
Utilisateur demande: "Optimise le frontend" ou "Ajoute du SSR"

→ Utiliser react-specialist pour:
  - React 18+ features (Suspense, Transitions)
  - Performance (memo, useMemo, code splitting)
  - State management (Zustand, React Query)
  - Server-side rendering
  - Testing React (Testing Library)
```

### api-designer
```
Utilisateur demande: "Conçois l'API" ou "Documente les endpoints"

→ Utiliser api-designer pour:
  - Design REST/GraphQL
  - OpenAPI 3.1 specifications
  - Pagination, filtrage, versioning
  - Webhooks design
  - SDK generation
```

### compliance-auditor (complementaire a security-auditor)
```
Utilisateur demande: "Verifie la conformite RGPD" ou "Prepare l'audit"

→ Utiliser compliance-auditor pour:
  - RGPD (donnees personnelles employes)
  - Audit trail et logs
  - Politiques de retention
  - Documentation conformite
  - Evidence collection
```

### performance-engineer
```
Utilisateur demande: "L'app est lente" ou "Fais des tests de charge"

→ Utiliser performance-engineer pour:
  - Profiling application
  - Load testing (Locust, k6)
  - Bottleneck identification
  - Caching strategies
  - Monitoring setup
```

### accessibility-tester
```
Utilisateur demande: "Verifie l'accessibilite" ou "PWA mobile"

→ Utiliser accessibility-tester pour:
  - WCAG 2.1 compliance
  - Screen reader compatibility
  - Keyboard navigation
  - Color contrast
  - Mobile accessibility
```

### business-analyst
```
Utilisateur demande: "Analyse les specs" ou "Comprends le metier BTP"

→ Utiliser business-analyst pour:
  - Analyse des requirements
  - Process mapping
  - Gap analysis
  - ROI calculation
  - Stakeholder management
```

### documentation-engineer
```
Utilisateur demande: "Documente l'API" ou "Cree le guide utilisateur"

→ Utiliser documentation-engineer pour:
  - API documentation (Swagger)
  - Architecture docs
  - User guides
  - Code examples
  - Search optimization
```

### devops-engineer
```
Utilisateur demande: "Configure le CI/CD" ou "Deploie en production"

→ Utiliser devops-engineer pour:
  - Docker/Docker Compose
  - CI/CD pipelines (GitHub Actions)
  - Monitoring (Prometheus, Grafana)
  - Infrastructure as Code
  - Deployment strategies
```

---

## Workflow detaille (16 agents)

```
┌─────────────────────────────────────────────────────────────────┐
│  0. LECTURE SPECS                                               │
│     - Lire docs/SPECIFICATIONS.md (ID fonctionnalite)           │
│     - Comprendre les regles metier et contraintes               │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. DATABASE (sql-pro) - si nouvelles tables/colonnes           │
│     - Concevoir le schema (tables, relations, contraintes)      │
│     - Creer les migrations Alembic                              │
│     - Definir les index pour requetes frequentes                │
│     - Objectif: requetes < 100ms                                │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. IMPLEMENTATION (python-pro ou typescript-pro)               │
│     - Domain: Entities, Value Objects, Repository interfaces    │
│     - Application: Use Cases, DTOs                              │
│     - Adapters: Controllers, Providers                          │
│     - Infrastructure: Persistence, Web routes                   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. ARCHITECTURE REVIEW (architect-reviewer)                    │
│     Checklist:                                                  │
│     □ Domain n'importe pas de frameworks                        │
│     □ Use cases dependent d'interfaces (pas d'implementations)  │
│     □ Pas d'import direct entre modules (sauf events)           │
│     □ Regle de dependance respectee                             │
│     → Si echec: CORRIGER avant de continuer                     │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. TESTS (test-automator)                                      │
│     - Generer tests/unit/{module}/test_{use_case}.py            │
│     - Mocks pour toutes les dependances                         │
│     - Cas nominaux + cas d'erreur                               │
│     - Objectif: > 85% couverture                                │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. CODE REVIEW (code-reviewer)                                 │
│     Checklist:                                                  │
│     □ Type hints sur toutes les signatures                      │
│     □ Docstrings Google style                                   │
│     □ Conventions de nommage respectees                         │
│     □ Pas de code mort ou commente                              │
│     → Si echec: CORRIGER avant de continuer                     │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. SECURITY AUDIT (security-auditor)                           │
│     Checklist:                                                  │
│     □ Aucune injection SQL/XSS possible                         │
│     □ Validation des entrees (Pydantic)                         │
│     □ Donnees sensibles chiffrees                               │
│     □ Conformite RGPD (si donnees personnelles)                 │
│     □ Audit trail sur actions sensibles                         │
│     → Si finding CRITIQUE/HAUTE: CORRIGER avant commit          │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. MISE A JOUR DOCUMENTATION                                   │
│     - SPECIFICATIONS.md:                                        │
│       • Modifier le contenu si implementation differe           │
│       • Ajouter la feature si nouvelle (hors CDC)               │
│       • Passer le statut a ✅                                   │
│     - .claude/history.md: Resume de la session                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  8. COMMIT & PUSH                                               │
│     Format: feat(module): description                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Regles d'execution

### Sequencement
1. **Un agent a la fois** - Jamais plusieurs en parallele
2. **Toujours finir** - Ne pas lancer un agent si le precedent n'a pas termine
3. **Correction immediate** - Corriger les problemes trouves avant de continuer
4. **Specs d'abord** - Toujours lire SPECIFICATIONS.md avant d'implementer

### Communication avec l'utilisateur
1. **Transparent** - Montrer le resultat final, pas chaque etape intermediaire
2. **Signaler les problemes majeurs** - Informer si un probleme critique est detecte
3. **Resume concis** - Liste des fichiers crees/modifies + tests generes

### Regle obligatoire AVANT tout commit

**Lancer les agents SI** le commit contient :
- `*.py` (code Python)
- `*.ts` / `*.tsx` (code TypeScript/React)
- `*.sql` (migrations, schemas)

**NE PAS lancer les agents pour** :
- `*.md` (documentation : CLAUDE.md, history.md, README, etc.)
- `.claude/*` (configuration Claude)
- `*.json` / `*.yaml` / `*.toml` (configuration)
- `scripts/*` (scripts utilitaires simples)

### Quand NE PAS utiliser les agents
- Questions simples ou informations
- Lecture/exploration du code sans modification
- Commandes git simples (status, log, etc.)

### Apres validation complete

Quand tous les agents ont valide et les tests passent :
1. Committer et pousser sur la branche de travail
2. **Proposer automatiquement** de merger sur main (PR ou merge direct)
3. Ne pas attendre que l'utilisateur le demande

---

## Correspondance Modules ↔ CDC

| Module | Section CDC | IDs Fonctionnalites |
|--------|-------------|---------------------|
| auth | Section 2 | USR-01 à USR-14 |
| chantiers | Section 3 | CHT-01 à CHT-20 |
| planning | Section 4 | PLN-01 à PLN-28 |
| planning_charge | Section 5 | PDC-01 à PDC-17 |
| feuilles_heures | Section 6 | FDH-01 à FDH-20 |
| formulaires | Section 7 | FOR-01 à FOR-11 |
| documents | Section 8 | GED-01 à GED-15 |
| memos | Section 9 | MEM-01 à MEM-13 |
| logistique | Section 10 | LOG-01 à LOG-18 |
| interventions | Section 11 | INT-01 à INT-17 |
| taches | Section 12 | TAC-01 à TAC-20 |

---

## Exemple complet

```
Utilisateur: "Implemente CHT-03 (Statut chantier)"

[SPECS] Lecture docs/SPECIFICATIONS.md Section 3
→ CHT-03: Statut chantier - Ouvert / En cours / Receptionne / Ferme
→ Statuts avec icones et actions possibles

[sql-pro]
→ Pas de nouvelle table, statut = colonne enum existante
→ Verifie index sur chantiers.statut... OK
→ Status: SKIP (pas de migration necessaire)

[python-pro]
→ Cree modules/chantiers/domain/value_objects/statut_chantier.py
→ Cree modules/chantiers/domain/entities/chantier.py (si n'existe pas)
→ Ajoute methode changer_statut() avec regles metier

[architect-reviewer]
→ Scan des imports... OK
→ Value Object immutable... OK
→ Pas de framework dans domain... OK
→ Status: PASS

[test-automator]
→ Genere tests/unit/chantiers/test_statut_chantier.py
→ Tests: creation, transitions valides, transitions invalides
→ 8 tests crees, couverture 92%

[code-reviewer]
→ Type hints... OK
→ Docstrings... OK
→ Enum bien utilise... OK
→ Status: APPROVED

[security-auditor]
→ Pas de donnees sensibles dans statut... OK
→ Validation Pydantic sur changement statut... OK
→ Status: PASS (aucun finding)

[SPECS] Mise a jour SPECIFICATIONS.md
→ CHT-03: ⏳ → ✅

[DOCS] Mise a jour .claude/history.md
→ Resume: CHT-03 implemente avec tests

Reponse a l'utilisateur:
"CHT-03 (Statut chantier) implemente:
- backend/modules/chantiers/domain/value_objects/statut_chantier.py
- tests/unit/chantiers/test_statut_chantier.py (8 tests)

Statuts disponibles: Ouvert 🔵, En cours 🟢, Receptionne 🟡, Ferme 🔴"
```
