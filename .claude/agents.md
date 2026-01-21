# Regles d'utilisation des sous-agents

> Ce fichier definit quand Claude doit utiliser des sous-agents specialises.
> L'utilisateur n'a pas a s'en occuper - c'est automatique.
> Source: https://github.com/VoltAgent/awesome-claude-code-subagents

## Agents disponibles

| Agent | Fichier | Role |
|-------|---------|------|
| architect-reviewer | `agents/architect-reviewer.md` | Validation Clean Architecture |
| code-reviewer | `agents/code-reviewer.md` | Qualite et securite du code |
| test-automator | `agents/test-automator.md` | Generation de tests |
| python-pro | `agents/python-pro.md` | Expert FastAPI/SQLAlchemy |
| typescript-pro | `agents/typescript-pro.md` | Expert React/TypeScript |

## Quand utiliser chaque agent

### architect-reviewer
**Declencheur** : Creation/modification de code dans un module
**Actions** :
1. Verifier la regle de dependance (Domain <- Application <- Adapters <- Infrastructure)
2. Scanner les imports interdits dans domain/
3. Verifier la communication inter-modules (Events uniquement)
4. Evaluer le couplage et la modularite

**Sortie attendue** : Status PASS/WARN/FAIL avec violations et score

### code-reviewer
**Declencheur** : Avant commit ou sur demande de review
**Actions** :
1. Verifier la securite (injections, auth, crypto)
2. Analyser la performance (Big O, requetes DB)
3. Valider la qualite (docstrings, type hints, nommage)
4. Verifier les principes SOLID et DRY

**Sortie attendue** : Status approved/changes_requested avec findings detailles

### test-automator
**Declencheur** : Apres creation d'un use case ou entity
**Actions** :
1. Generer les tests unitaires avec mocks
2. Creer les fixtures necessaires
3. Couvrir les cas nominaux et d'erreur
4. Viser > 80% de couverture

**Sortie attendue** : Fichiers test_*.py avec tests complets

### python-pro
**Declencheur** : Developpement backend (FastAPI, SQLAlchemy)
**Actions** :
1. Ecrire du code Python idiomatique
2. Appliquer les patterns Clean Architecture
3. Utiliser les features modernes (dataclass, type hints)
4. Respecter les conventions Hub Chantier

**Sortie attendue** : Code Python conforme aux standards

### typescript-pro
**Declencheur** : Developpement frontend (React, TypeScript)
**Actions** :
1. Ecrire du code TypeScript strict
2. Creer des composants type-safe
3. Maintenir la coherence des types avec l'API
4. Optimiser le bundle

**Sortie attendue** : Code TypeScript/React conforme aux standards

## Workflow automatique

```
┌─────────────────────────────────────────────────────────────┐
│                    TACHE DE DEV                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  1. IMPLEMENTATION (python-pro ou typescript-pro)           │
│     - Ecrire le code selon les patterns                     │
│     - Respecter Clean Architecture                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. ARCHITECTURE REVIEW (architect-reviewer)                │
│     - Verifier les imports                                  │
│     - Valider la structure                                  │
│     - CORRIGER si violations                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  3. TESTS (test-automator)                                  │
│     - Generer les tests unitaires                           │
│     - Creer les mocks                                       │
│     - Verifier la couverture                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  4. CODE REVIEW (code-reviewer)                             │
│     - Verifier qualite et securite                          │
│     - CORRIGER si problemes                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  5. COMMIT & PUSH                                           │
└─────────────────────────────────────────────────────────────┘
```

## Regles d'execution

### Sequencement
1. **Un agent a la fois** - Jamais plusieurs en parallele
2. **Toujours finir** - Ne pas lancer un agent si le precedent n'a pas termine
3. **Correction immediate** - Corriger les problemes trouves avant de continuer

### Communication
1. **Transparent** - L'utilisateur voit le resultat final, pas les etapes intermediaires
2. **Signaler les problemes majeurs** - Informer si un probleme critique est detecte
3. **Pas de bruit** - Ne pas detailler chaque verification si tout va bien

### Quand NE PAS utiliser d'agent
- Questions simples ou informations
- Modifications mineures (< 20 lignes)
- Documentation seule
- Configuration/scripts basiques
- Commandes git simples

## Exemple d'utilisation interne

```
Utilisateur: "Cree le use case PointerEntree dans le module pointages"

[python-pro]
→ Cree domain/entities/pointage.py
→ Cree domain/repositories/pointage_repository.py
→ Cree application/use_cases/pointer_entree.py
→ Cree application/dtos/pointage_dto.py

[architect-reviewer]
→ Scan des imports... OK
→ Regle de dependance... OK
→ Communication inter-modules... OK
→ Status: PASS

[test-automator]
→ Genere tests/unit/pointages/test_pointer_entree.py
→ 6 tests crees
→ Couverture estimee: 85%

[code-reviewer]
→ Securite... OK
→ Type hints... OK
→ Docstrings... OK
→ Status: approved

Reponse a l'utilisateur:
"Use case PointerEntree cree avec tests. Structure:
- backend/modules/pointages/domain/entities/pointage.py
- backend/modules/pointages/application/use_cases/pointer_entree.py
- backend/tests/unit/pointages/test_pointer_entree.py (6 tests)"
```
