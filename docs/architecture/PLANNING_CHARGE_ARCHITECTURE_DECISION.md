# Planning Charge - Décision d'Architecture Requise

**Date**: 2026-01-28
**Status**: 🔴 **BLOQUANT** pour Clean Architecture compliance
**Violations**: **15+ imports cross-module critiques**

---

## 📊 Problème

Le module `planning_charge` viole massivement les principes de Clean Architecture en important directement les **Models SQLAlchemy** des modules `auth`, `chantiers`, et `planning`.

### Fichiers Problématiques

#### 1. `utilisateur_provider.py` (6 violations)
```python
# LIGNE 60 - COUNT par métier
from modules.auth.infrastructure.persistence import UserModel
results = session.query(UserModel.metier, func.count(UserModel.id))
    .filter(UserModel.is_active == True)
    .group_by(UserModel.metier).all()

# LIGNE 84 - Total utilisateurs actifs
from modules.auth.infrastructure.persistence import UserModel
return session.query(func.count(UserModel.id))
    .filter(UserModel.is_active == True).scalar()

# LIGNE 103-104 - Utilisateurs disponibles (avec affectations)
from modules.auth.infrastructure.persistence import UserModel
from modules.planning.infrastructure.persistence import AffectationModel
```

**Requêtes**: COUNT, GROUP BY, filtres complexes, jointures

#### 2. `chantier_provider.py` (4 violations)
```python
# LIGNES 39, 77, 105, 140 - Recherche chantiers actifs
from modules.chantiers.infrastructure.persistence import ChantierModel

query = session.query(ChantierModel).filter(
    ChantierModel.statut.in_(["ouvert", "en_cours"]),
    ChantierModel.deleted_at.is_(None),
    ChantierModel.nom.ilike(search_term)
)
```

**Requêtes**: Recherche ILIKE, filtres multiples (statut, deleted_at), ORDER BY

#### 3. `affectation_provider.py` (5+ violations estimées)
Import de `AffectationModel` depuis `planning` avec agrégations complexes.

---

## 🔍 Pourquoi EntityInfoService Ne Suffit Pas

### EntityInfoService actuel (shared/application/ports/)
```python
class EntityInfoService(ABC):
    def get_user_info(user_id: int) -> Optional[UserBasicInfo]
    def get_chantier_info(chantier_id: int) -> Optional[ChantierBasicInfo]
    def get_active_user_ids() -> List[int]
    def get_user_chantier_ids(user_id: int) -> List[int]
```

### Ce que planning_charge nécessite
```python
# ❌ Pas supporté par EntityInfoService
- COUNT(*) GROUP BY métier
- Recherche ILIKE avec filtres multiples
- Statistiques agrégées (capacité par métier)
- Utilisateurs disponibles (NOT IN subquery avec dates)
- Chantiers actifs avec heures estimées
- Filtres sur deleted_at, statut, etc.
```

**Conclusion**: EntityInfoService est trop simple pour les besoins de planning_charge.

---

## 🎯 Options de Résolution

### Option A: Fusionner planning_charge avec planning ✅ **RECOMMANDÉ**

**Avantages**:
- Élimine TOUTES les violations (15+)
- Planning et planning_charge sont étroitement couplés conceptuellement
- Simplifie l'architecture (1 module au lieu de 2)
- Les use cases de planning_charge dépendent déjà massivement de planning

**Inconvénients**:
- Refactoring moyen (2-3 jours)
- Réorganisation des fichiers
- Tests à adapter

**Effort**: 2-3 jours

### Option B: Créer des Ports Complexes 🟡 **COMPLEXE**

Créer des interfaces spécialisées dans `shared/application/ports/`:

```python
# shared/application/ports/user_stats.py
class UserStatsPort(ABC):
    @abstractmethod
    def get_capacite_par_type_metier(semaine: Semaine) -> Dict[str, float]:
        pass

    @abstractmethod
    def get_utilisateurs_disponibles(semaine: Semaine) -> int:
        pass

# shared/application/ports/chantier_search.py
class ChantierSearchPort(ABC):
    @abstractmethod
    def search_chantiers_actifs(query: str) -> List[ChantierSearchResult]:
        pass

    @abstractmethod
    def get_chantiers_with_heures(ids: List[int]) -> List[ChantierDetail]:
        pass
```

**Avantages**:
- Respecte Clean Architecture (Dependency Inversion)
- Modules restent séparés
- Interfaces clairement définies

**Inconvénients**:
- Complexité accrue (3-4 nouveaux Ports)
- Implémentations dans auth/chantiers/planning Infrastructure
- Maintenance plus difficile (3 modules à synchroniser)
- Risque de duplication de code

**Effort**: 5-8 jours

### Option C: Accepter les Violations 🔴 **NON RECOMMANDÉ**

Documenter et accepter que planning_charge viole Clean Architecture.

**Avantages**:
- Zéro effort immédiat

**Inconvénients**:
- ❌ Bloque certification Clean Architecture
- ❌ Score architect-reviewer restera < 60/100
- ❌ Dette technique permanente
- ❌ Difficile à tester en isolation
- ❌ Couplage fort entre modules

---

## 🏆 Recommandation Finale

### ✅ **Option A: Fusionner planning_charge avec planning**

**Justification**:
1. **Couplage conceptuel**: Planning de charge est une fonctionnalité du planning, pas un module indépendant
2. **Simplicité**: Solution la plus simple techniquement
3. **Maintenabilité**: 1 module au lieu de 2, moins de code à maintenir
4. **Performance**: Moins de niveaux d'abstraction
5. **Testabilité**: Tests plus simples (1 module)

### Structure Cible

```
modules/planning/
├── domain/
│   ├── entities/
│   │   ├── affectation.py
│   │   └── planning_charge.py  # Nouvelles entités
│   ├── value_objects/
│   │   ├── semaine.py
│   │   └── occupation.py
│   └── repositories/
│       ├── affectation_repository.py
│       └── planning_charge_repository.py
├── application/
│   └── use_cases/
│       ├── affectation/
│       │   ├── create_affectation.py
│       │   └── ...
│       └── planning_charge/  # Use cases déplacés ici
│           ├── get_planning_charge.py
│           ├── get_occupation_details.py
│           └── export_planning_charge.py
├── adapters/
│   └── controllers/
│       ├── affectation_controller.py
│       └── planning_charge_controller.py
└── infrastructure/
    ├── persistence/
    │   └── sqlalchemy_planning_charge_repository.py
    └── web/
        ├── affectation_routes.py
        └── planning_charge_routes.py
```

### Plan d'Action

1. **Préparation** (2h):
   - Créer branch `refactor/merge-planning-charge`
   - Backup du code actuel
   - Analyser dépendances exactes

2. **Migration** (1-2 jours):
   - Déplacer entities, value_objects → planning/domain/
   - Déplacer use_cases → planning/application/use_cases/planning_charge/
   - Déplacer repositories → planning/domain/repositories/
   - Déplacer providers → planning/infrastructure/ (renommer en repositories)
   - Déplacer routes → planning/infrastructure/web/

3. **Adaptation** (4-8h):
   - Mettre à jour tous les imports
   - Fusionner dependencies.py
   - Adapter les tests

4. **Validation** (4h):
   - Lancer tous les tests
   - Vérifier architect-reviewer (attendu: +15-20 points)
   - Vérifier coverage reste >= 80%

5. **Commit & PR** (1h):
   - Commit atomique avec message détaillé
   - PR avec description complète
   - Review par l'équipe

**Effort total**: 2-3 jours (16-24h)

---

## 📅 Prochaines Étapes

### Immédiat (avant merge P1)
1. ✅ Documenter ce problème (ce fichier)
2. ⏳ Obtenir validation de l'équipe sur Option A
3. ⏳ Créer ticket JIRA/GitHub Issue
4. ⏳ Planifier dans sprint

### Après validation
1. Créer branch `refactor/merge-planning-charge`
2. Exécuter Plan d'Action (2-3 jours)
3. PR + Review
4. Merge

### Alternative si délai contraint
- **Court terme**: Accepter temporairement les violations, documenter comme dette technique
- **Moyen terme** (dans 1-2 sprints): Exécuter fusion planning_charge

---

## 📊 Impact Attendu

### Avant (Actuel)
- ❌ architect-reviewer: **53/100** (FAIL)
- ❌ **32 violations** Clean Architecture
- ❌ planning_charge couplé à auth + chantiers + planning

### Après (Option A - Fusion)
- ✅ architect-reviewer: **75-80/100** (PASS)
- ✅ **17 violations** (-15 éliminées)
- ✅ 1 module cohérent au lieu de 2
- ✅ Testabilité améliorée
- ✅ Maintenabilité simplifiée

---

## 🔗 Références

- Rapport architect-reviewer: Phase 2.5 validation (2026-01-28)
- Clean Architecture (Uncle Bob): Dependency Rule
- Module auth: Architecture de référence exemplaire
- EntityInfoService: `shared/application/ports/entity_info_service.py`

---

## ✅ Décision

**À compléter par l'équipe**:

- [ ] Option A: Fusionner (recommandé)
- [ ] Option B: Créer Ports complexes
- [ ] Option C: Accepter violations (non recommandé)

**Décideur**: _______________________
**Date**: _______________________
**Justification**: _______________________

---

**Mis à jour**: 2026-01-28 par Claude (Session 011u3yRrSvnWiaaZPEQvnBg6)
