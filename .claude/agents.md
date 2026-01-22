# Regles d'utilisation des sous-agents

> Ce fichier definit quand Claude doit utiliser des sous-agents specialises.
> L'utilisateur n'a pas a s'en occuper - c'est automatique.
> Source: https://github.com/VoltAgent/awesome-claude-code-subagents

---

## Agents disponibles

| Agent | Prompt | Role | Outils |
|-------|--------|------|--------|
| architect-reviewer | `agents/architect-reviewer.md` | Validation Clean Architecture | Read, Glob, Grep |
| code-reviewer | `agents/code-reviewer.md` | Qualite et securite du code | Read, Glob, Grep |
| test-automator | `agents/test-automator.md` | Generation de tests pytest | Read, Write, Edit, Bash |
| python-pro | `agents/python-pro.md` | Expert FastAPI/SQLAlchemy | Read, Write, Edit, Bash |
| typescript-pro | `agents/typescript-pro.md` | Expert React/TypeScript | Read, Write, Edit, Bash |

---

## Declencheurs automatiques

### Quand implementer une fonctionnalite du CDC

```
Utilisateur demande: "Implemente CHT-03" ou "Cree le module chantiers"

1. [SPECS] Lire docs/SPECIFICATIONS.md pour les details de la fonctionnalite
2. [python-pro] Implementer selon Clean Architecture
3. [architect-reviewer] Verifier la conformite architecture
4. [test-automator] Generer les tests unitaires
5. [code-reviewer] Verifier qualite et securite
6. [SPECS] Mettre a jour SPECIFICATIONS.md:
   - Modifier le contenu si l'implementation differe de la spec initiale
   - Passer le statut a ✅
7. [CLAUDE.md] Mettre a jour l'etat du projet
```

### Quand ajouter une nouvelle fonctionnalite (hors CDC initial)

```
Utilisateur demande: "Ajoute la fonctionnalite X"

1. [SPECS] Ajouter la fonctionnalite dans SPECIFICATIONS.md:
   - Generer un nouvel ID (ex: CHT-21 si c'est pour chantiers)
   - Documenter la spec complete (description, regles metier, criteres)
   - Status initial: ⏳
2. [python-pro] Implementer selon Clean Architecture
3. [architect-reviewer] Verifier la conformite architecture
4. [test-automator] Generer les tests unitaires
5. [code-reviewer] Verifier qualite et securite
6. [SPECS] Passer le statut a ✅
7. [CLAUDE.md] Mettre a jour l'etat du projet
```

### Quand creer un nouveau module

```
Utilisateur demande: "Cree le module X"

1. [SPECS] Lire la section correspondante dans SPECIFICATIONS.md
2. [python-pro] Creer la structure:
   - domain/entities/
   - domain/value_objects/
   - domain/repositories/ (interfaces)
   - domain/events/
   - application/use_cases/
   - application/dtos/
   - adapters/controllers/
   - infrastructure/persistence/
   - infrastructure/web/
3. [architect-reviewer] Valider la structure
4. [test-automator] Generer les tests de base
5. [CLAUDE.md] Mettre a jour l'etat des modules
```

### Quand modifier du code existant

```
Utilisateur demande: "Modifie X" ou "Corrige Y"

1. [python-pro/typescript-pro] Effectuer les modifications
2. [architect-reviewer] Verifier que Clean Architecture est respectee
3. [code-reviewer] Verifier qualite et securite
4. [test-automator] Mettre a jour les tests si necessaire
```

---

## Workflow detaille

```
┌─────────────────────────────────────────────────────────────────┐
│  0. LECTURE SPECS                                               │
│     - Lire docs/SPECIFICATIONS.md (ID fonctionnalite)           │
│     - Comprendre les regles metier et contraintes               │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. IMPLEMENTATION (python-pro ou typescript-pro)               │
│     - Domain: Entities, Value Objects, Repository interfaces    │
│     - Application: Use Cases, DTOs                              │
│     - Adapters: Controllers, Providers                          │
│     - Infrastructure: Persistence, Web routes                   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. ARCHITECTURE REVIEW (architect-reviewer)                    │
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
│  3. TESTS (test-automator)                                      │
│     - Generer tests/unit/{module}/test_{use_case}.py            │
│     - Mocks pour toutes les dependances                         │
│     - Cas nominaux + cas d'erreur                               │
│     - Objectif: > 80% couverture                                │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. CODE REVIEW (code-reviewer)                                 │
│     Checklist:                                                  │
│     □ Securite (injections, auth, validation)                   │
│     □ Type hints sur toutes les signatures                      │
│     □ Docstrings Google style                                   │
│     □ Conventions de nommage respectees                         │
│     → Si echec: CORRIGER avant de continuer                     │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. MISE A JOUR DOCUMENTATION                                   │
│     - SPECIFICATIONS.md:                                        │
│       • Modifier le contenu si implementation differe           │
│       • Ajouter la feature si nouvelle (hors CDC)               │
│       • Passer le statut a ✅                                   │
│     - CLAUDE.md: Mettre a jour etat du module                   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. COMMIT & PUSH                                               │
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
→ 8 tests crees

[code-reviewer]
→ Type hints... OK
→ Docstrings... OK
→ Enum bien utilise... OK
→ Status: approved

[SPECS] Mise a jour SPECIFICATIONS.md
→ CHT-03: ⏳ → ✅

[CLAUDE.md] Mise a jour
→ Module chantiers: "Structure only" → "CHT-03 implemente"

Reponse a l'utilisateur:
"CHT-03 (Statut chantier) implemente:
- backend/modules/chantiers/domain/value_objects/statut_chantier.py
- tests/unit/chantiers/test_statut_chantier.py (8 tests)

Statuts disponibles: Ouvert 🔵, En cours 🟢, Receptionne 🟡, Ferme 🔴"
```
