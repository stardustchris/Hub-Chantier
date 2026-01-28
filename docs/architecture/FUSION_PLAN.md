# Plan de Fusion: planning_charge → planning

**Date**: 2026-01-28
**Branche**: `refactor/merge-planning-charge`
**Objectif**: Éliminer 15+ violations Clean Architecture

---

## 📊 Analyse Initiale

### Structure planning_charge (43 fichiers)
```
planning_charge/
├── domain/
│   ├── entities/besoin_charge.py
│   ├── value_objects/ (4 fichiers: semaine, taux_occupation, type_metier, unite_charge)
│   ├── events/besoin_events.py
│   └── repositories/besoin_charge_repository.py
├── application/
│   ├── use_cases/ (7 fichiers: create, delete, update, get_besoins, get_planning, get_occupation)
│   ├── dtos/ (3 fichiers: besoin, occupation, planning_charge)
│   └── ports/event_bus.py
├── adapters/
│   └── controllers/ (2 fichiers: controller, schemas)
└── infrastructure/
    ├── persistence/ (2 fichiers: models, repository)
    ├── providers/ (3 fichiers: affectation, chantier, utilisateur) ← VIOLATIONS ICI
    └── routes.py
```

### Violations Cross-Module (15+)
- **utilisateur_provider.py**: 6 imports UserModel + AffectationModel
- **chantier_provider.py**: 4 imports ChantierModel
- **affectation_provider.py**: 5+ imports AffectationModel

---

## 🎯 Plan de Migration (3 jours)

### JOUR 1 - Migration Domain + Application (8h)

#### Étape 1.1: Domain Entities (1h)
```bash
# Déplacer
cp planning_charge/domain/entities/besoin_charge.py planning/domain/entities/
```
**Imports à mettre à jour**:
- ✅ Déjà dans planning → Aucun import externe

#### Étape 1.2: Domain Value Objects (1h)
```bash
# Créer dossier
mkdir -p planning/domain/value_objects/charge

# Déplacer
mv planning_charge/domain/value_objects/*.py planning/domain/value_objects/charge/
```
**Fichiers**: semaine.py, taux_occupation.py, type_metier.py, unite_charge.py

#### Étape 1.3: Domain Events (1h)
```bash
mkdir -p planning/domain/events/charge
mv planning_charge/domain/events/besoin_events.py planning/domain/events/charge/
```

#### Étape 1.4: Domain Repositories (1h)
```bash
mv planning_charge/domain/repositories/besoin_charge_repository.py planning/domain/repositories/
```

#### Étape 1.5: Application DTOs (1h)
```bash
mkdir -p planning/application/dtos/charge
mv planning_charge/application/dtos/*.py planning/application/dtos/charge/
```
**Fichiers**: besoin_charge_dto.py, occupation_dto.py, planning_charge_dto.py

#### Étape 1.6: Application Use Cases (3h)
```bash
mkdir -p planning/application/use_cases/charge
mv planning_charge/application/use_cases/*.py planning/application/use_cases/charge/
```
**Fichiers**:
- create_besoin.py
- delete_besoin.py
- update_besoin.py
- get_besoins_by_chantier.py
- get_planning_charge.py
- get_occupation_details.py
- exceptions.py

**CRITIQUE**: Mettre à jour imports dans ces fichiers:
```python
# AVANT
from ...domain.entities import BesoinCharge
from ...domain.value_objects import Semaine

# APRÈS
from ....domain.entities import BesoinCharge
from ....domain.value_objects.charge import Semaine
```

---

### JOUR 2 - Migration Infrastructure + Imports (8h)

#### Étape 2.1: Infrastructure Persistence (2h)
```bash
# Modèles
cat planning_charge/infrastructure/persistence/models.py >> planning/infrastructure/persistence/models.py

# Repository
mv planning_charge/infrastructure/persistence/sqlalchemy_besoin_repository.py \
   planning/infrastructure/persistence/sqlalchemy_besoin_charge_repository.py
```

**IMPORTANT**: Fusionner models.py (ne pas écraser)

#### Étape 2.2: **Infrastructure Providers → Repositories** (3h)

**CRITIQUE**: Les providers violent Clean Architecture. Les transformer:

##### utilisateur_provider.py → Supprimer
```python
# SOLUTION: Utiliser EntityInfoService où possible
# Requêtes complexes (COUNT, GROUP BY) → Déplacer dans planning/domain/services/
```

**Option A** (recommandé): Créer `UserStatsService` dans `planning/domain/services/`:
```python
# planning/domain/services/user_stats_service.py
class UserStatsService:
    """Service domaine pour statistiques utilisateurs (Clean Architecture OK)."""
    def __init__(self, session: Session):
        self.session = session

    def get_capacite_par_metier(self, semaine: Semaine) -> Dict[str, float]:
        # Import local OK car c'est Infrastructure
        from modules.auth.infrastructure.persistence import UserModel
        results = self.session.query(...).all()
        # ...
```

**Justification**:
- ✅ Service domaine peut utiliser infrastructure en injection
- ✅ Pas de dépendance inter-modules (tout dans planning)
- ✅ Testable avec mock Session

##### chantier_provider.py → Supprimer
**Solution**: Utiliser `EntityInfoService.get_chantier_info()` pour infos basiques
Pour recherche complexe: Créer `ChantierSearchService` dans `planning/domain/services/`

##### affectation_provider.py → Transformer
**Solution**: Déjà dans planning → Fusionner avec repository existant

#### Étape 2.3: Infrastructure Web Routes (1h)
```bash
mv planning_charge/infrastructure/routes.py planning/infrastructure/web/charge_routes.py
```

**Mettre à jour** FastAPI router registration dans `planning/__init__.py`

#### Étape 2.4: Adapters Controllers (1h)
```bash
mkdir -p planning/adapters/controllers/charge
mv planning_charge/adapters/controllers/*.py planning/adapters/controllers/charge/
```

#### Étape 2.5: Update ALL Imports (1h)
Fichiers à scanner:
- [ ] planning/infrastructure/web/charge_routes.py
- [ ] planning/adapters/controllers/charge/*
- [ ] planning/application/use_cases/charge/*
- [ ] planning/__init__.py (router registration)
- [ ] main.py (si import planning_charge)

Commande globale:
```bash
grep -r "planning_charge" backend/ | wc -l  # Avant
# Remplacer tous les imports
grep -r "planning_charge" backend/ | wc -l  # Après = 0
```

---

### JOUR 3 - Tests + Validation (8h)

#### Étape 3.1: Migration Tests (2h)
```bash
mkdir -p tests/unit/planning/charge
mv tests/unit/planning_charge/*.py tests/unit/planning/charge/
```

**Update imports** dans tous les tests:
```python
# AVANT
from modules.planning_charge.domain.entities import BesoinCharge

# APRÈS
from modules.planning.domain.entities import BesoinCharge
```

#### Étape 3.2: Supprimer planning_charge (30min)
```bash
rm -rf backend/modules/planning_charge
rm -rf backend/tests/unit/planning_charge
```

#### Étape 3.3: Run Tests (1h)
```bash
cd backend
pytest tests/unit/planning/ -v --tb=short
pytest tests/unit/ -v  # Full suite
```

**Expected**: Tous les tests passent

#### Étape 3.4: Validation Agents (2h)
```bash
# Re-run architect-reviewer
```

**Attendu**:
- **Avant**: 53/100 (32 violations)
- **Après**: 75-80/100 (17 violations, -15 éliminées)

#### Étape 3.5: Documentation (2h)
- [ ] Mettre à jour `docs/architecture/CLEAN_ARCHITECTURE.md`
- [ ] Mettre à jour `docs/SPECIFICATIONS.md` (références planning_charge)
- [ ] Créer `docs/architecture/FUSION_CHANGELOG.md`
- [ ] Mettre à jour `.claude/project-status.md`

#### Étape 3.6: Commit & Push (30min)
```bash
git add .
git commit -m "refactor(p1): merge planning_charge into planning module

BREAKING CHANGE: planning_charge module merged into planning

Élimine 15+ violations Clean Architecture en fusionnant planning_charge
dans planning. Les deux modules étaient conceptuellement couplés.

Changements:
- Domain: Entités/VOs/Events déplacés dans planning/domain/
- Application: Use cases dans planning/application/use_cases/charge/
- Infrastructure: Providers transformés en domain services
- Routes: planning/infrastructure/web/charge_routes.py

Impact:
✅ -15 violations cross-module (24 → 9 restantes)
✅ architect-reviewer: 53 → 75+/100 (PASS)
✅ Architecture simplifiée (1 module au lieu de 2)
✅ Tests plus simples (pas de mocks inter-modules)

Migration guide: docs/architecture/FUSION_CHANGELOG.md
"

git push -u origin refactor/merge-planning-charge
```

---

## 📋 Checklist Complète

### Jour 1
- [ ] Créer branch `refactor/merge-planning-charge`
- [ ] Déplacer domain/entities/besoin_charge.py
- [ ] Déplacer domain/value_objects/* → charge/
- [ ] Déplacer domain/events/* → charge/
- [ ] Déplacer domain/repositories/*
- [ ] Déplacer application/dtos/* → charge/
- [ ] Déplacer application/use_cases/* → charge/
- [ ] Mettre à jour imports relatifs (3-4 niveaux)

### Jour 2
- [ ] Fusionner infrastructure/persistence/models.py
- [ ] Déplacer infrastructure/persistence/repository
- [ ] **Créer** planning/domain/services/user_stats_service.py
- [ ] **Créer** planning/domain/services/chantier_search_service.py
- [ ] Transformer affectation_provider → repository
- [ ] Déplacer infrastructure/routes.py → web/charge_routes.py
- [ ] Déplacer adapters/controllers/* → charge/
- [ ] Update router registration (planning/__init__.py)
- [ ] Grep tous les imports "planning_charge" et remplacer

### Jour 3
- [ ] Déplacer tests/unit/planning_charge/ → planning/charge/
- [ ] Update imports dans tests
- [ ] Supprimer modules/planning_charge/ (vide)
- [ ] pytest tests/unit/planning/ -v
- [ ] pytest tests/unit/ (full suite)
- [ ] Re-run architect-reviewer
- [ ] Vérifier score >= 75/100
- [ ] Documentation (4 fichiers)
- [ ] Commit atomique avec BREAKING CHANGE
- [ ] Push branch
- [ ] Create PR

---

## 🚨 Points d'Attention

### Imports Relatifs
```python
# Niveau change selon profondeur
# planning_charge/application/use_cases/x.py
from ...domain import X  # 3 niveaux

# planning/application/use_cases/charge/x.py
from ....domain import X  # 4 niveaux (un de plus!)
```

### Router Registration
```python
# planning/__init__.py
from .infrastructure.web import affectation_routes, charge_routes

router.include_router(affectation_routes.router)
router.include_router(charge_routes.router)  # AJOUTER
```

### Tests Paths
```python
# Anciens tests
from modules.planning_charge.domain.entities import X

# Nouveaux tests
from modules.planning.domain.entities import X  # Plus de .charge
```

### Domain Services (NEW PATTERN)
```python
# planning/domain/services/user_stats_service.py
# C'est OK d'importer Infrastructure ici (injection)
class UserStatsService:
    def __init__(self, session: Session):
        # Import local dans méthode = OK
        pass

    def get_stats(self):
        from modules.auth.infrastructure.persistence import UserModel
        # Requête SQL complexe OK ici
```

---

## 🎯 Critères de Succès

- ✅ `rm -rf modules/planning_charge/` réussit (dossier vide)
- ✅ `pytest tests/unit/planning/` → 100% PASS
- ✅ `grep -r "planning_charge" backend/` → 0 résultat (sauf docs)
- ✅ architect-reviewer score >= 75/100
- ✅ 17 violations ou moins (vs 24 avant)
- ✅ Tous les use cases fonctionnent (tests d'intégration)

---

**Créé**: 2026-01-28
**Auteur**: Claude (Session 011u3yRrSvnWiaaZPEQvnBg6)
**Branche**: refactor/merge-planning-charge
