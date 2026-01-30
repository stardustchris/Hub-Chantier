# Refactoring Pointages - Clean Architecture

> **Date** : 30 janvier 2026
> **Statut** : À PLANIFIER
> **Priorité** : MOYENNE (fonctionnalité opérationnelle)

---

## 📋 CONTEXTE

Suite à la correction du bug des noms fictifs dans les feuilles d'heures (commit 29892d8), une implémentation pragmatique a été mise en place pour afficher les vrais noms des utilisateurs et chantiers.

**Solution actuelle** : JOINs SQL dans le Repository avec enrichissement direct des entités Domain.

**Problème** : Cette approche viole les principes de la Clean Architecture.

---

## 🔍 ANALYSE ARCHITECTURALE

### Violations Identifiées

#### 1. Imports Cross-Module dans Repository (Infrastructure)

**Fichier** : `backend/modules/pointages/infrastructure/persistence/sqlalchemy_pointage_repository.py`

```python
# ❌ VIOLATION : Imports directs des Models d'autres modules
from modules.auth.infrastructure.persistence.user_model import UserModel
from modules.chantiers.infrastructure.persistence.chantier_model import ChantierModel
```

**Principe violé** : Les modules ne doivent PAS s'importer directement (CLEAN_ARCHITECTURE.md ligne 379).

#### 2. Enrichissement dans Repository

**Méthodes problématiques** :
- `_query_with_joins()` : Crée des JOINs cross-module
- `_to_entity_enriched()` : Enrichit l'entité avec des données de présentation

**Principe violé** : Le Repository doit gérer uniquement la persistence, pas la présentation.

#### 3. Entité Domain avec Données de Présentation

**Fichier** : `backend/modules/pointages/domain/entities/pointage.py`

```python
# ⚠️ COMPROMIS : Propriétés de présentation dans entité Domain
@property
def utilisateur_nom(self) -> Optional[str]:
    return self._utilisateur_nom
```

**Principe violé** : Une entité Domain doit représenter des concepts métier, pas des données d'affichage.

---

## ✅ SOLUTION RECOMMANDÉE : EntityInfoService Pattern

### Approche

1. **Supprimer JOINs du Repository** : Le repository ne charge QUE les données du domaine Pointages
2. **Enrichir dans Use Case** : Utiliser `EntityInfoService` pour charger les noms
3. **Ajouter champs dans DTOs** : Les DTOs portent les données enrichies, pas les entités

### Avantages

- ✅ Conforme Clean Architecture
- ✅ Séparation claire des responsabilités
- ✅ Aucun couplage entre modules
- ✅ Entités Domain pures
- ✅ Testabilité accrue

### Référence Existante

Le module `planning` utilise déjà ce pattern avec succès :

**Fichier** : `backend/modules/planning/application/use_cases/get_planning_use_case.py`

```python
# Exemple : Enrichissement avec EntityInfoService (lignes 169-211)
def _enrich_affectations(self, affectations: List[Affectation]) -> List[AffectationPlanningDTO]:
    user_cache = {}
    chantier_cache = {}

    for affectation in affectations:
        user_info = self._get_cached_user_info(affectation.utilisateur_id, user_cache)
        chantier_info = self._get_cached_chantier_info(affectation.chantier_id, chantier_cache)
        # ...
```

---

## 📝 PLAN DE REFACTORING

### Phase 1 : Nettoyer Infrastructure (Repository)

**Fichier** : `backend/modules/pointages/infrastructure/persistence/sqlalchemy_pointage_repository.py`

**Actions** :
1. ❌ Supprimer imports : `UserModel`, `ChantierModel`
2. ❌ Supprimer méthode : `_query_with_joins()`
3. ❌ Supprimer méthode : `_to_entity_enriched()`
4. ✅ Modifier TOUTES les méthodes de lecture pour utiliser `_to_entity()` classique
5. ✅ Revenir à une query SQL simple : `query = self.session.query(PointageModel)`

**Fichiers impactés** :
- `find_by_id()`
- `find_by_utilisateur_and_date()`
- `find_by_utilisateur_and_semaine()`
- `find_by_chantier_and_date()`
- `find_by_chantier_and_semaine()`
- `find_by_utilisateur_chantier_date()`
- `find_by_affectation()`
- `find_pending_validation()`
- `search()`

### Phase 2 : Nettoyer Domain (Entité)

**Fichier** : `backend/modules/pointages/domain/entities/pointage.py`

**Actions** :
1. ❌ Supprimer propriétés :
   - `utilisateur_nom` (property + setter)
   - `chantier_nom` (property + setter)
   - `chantier_couleur` (property + setter)

2. ❌ Supprimer champs privés :
   - `_utilisateur_nom`
   - `_chantier_nom`
   - `_chantier_couleur`

**Résultat** : Entité Domain pure, sans données de présentation.

### Phase 3 : Enrichir dans Application (Use Cases)

**Use Cases à modifier** :

#### 3.1 GetVueSemaineUseCase

**Fichier** : `backend/modules/pointages/application/use_cases/get_vue_semaine.py`

**Actions** :
1. ✅ Injecter `EntityInfoService` dans `__init__()`
2. ✅ Implémenter `_enrich_pointages()` avec cache (pattern `GetPlanningUseCase`)
3. ✅ Enrichir dans `get_vue_compagnons()` :
   - Charger pointages depuis repository
   - Enrichir avec `EntityInfoService`
   - Construire DTOs enrichis

**Code pattern** :
```python
def __init__(
    self,
    pointage_repo: PointageRepository,
    entity_info_service: EntityInfoService,  # ✅ Injecter
):
    self.pointage_repo = pointage_repo
    self.entity_info_service = entity_info_service

def _enrich_pointages(self, pointages: List[Pointage]) -> List[dict]:
    """Enrichit les pointages avec noms users/chantiers."""
    user_cache = {}
    chantier_cache = {}

    enriched = []
    for p in pointages:
        # Charger user info avec cache
        if p.utilisateur_id not in user_cache:
            user_info = self.entity_info_service.get_user_info(p.utilisateur_id)
            user_cache[p.utilisateur_id] = user_info

        # Charger chantier info avec cache
        if p.chantier_id not in chantier_cache:
            chantier_info = self.entity_info_service.get_chantier_info(p.chantier_id)
            chantier_cache[p.chantier_id] = chantier_info

        enriched.append({
            "pointage": p,
            "utilisateur_nom": user_cache[p.utilisateur_id].get("nom"),
            "chantier_nom": chantier_cache[p.chantier_id].get("nom"),
            "chantier_couleur": chantier_cache[p.chantier_id].get("couleur"),
        })

    return enriched
```

#### 3.2 ListPointagesUseCase

**Fichier** : `backend/modules/pointages/application/use_cases/list_pointages.py`

**Note** : Ce use case a DÉJÀ `EntityInfoService` injecté (ligne 87) ! Il suffit de l'utiliser.

**Actions** :
1. ✅ Utiliser `self.entity_info_service` existant
2. ✅ Enrichir les pointages avant conversion en DTO

#### 3.3 GetFeuilleHeuresUseCase

**Fichier** : `backend/modules/pointages/application/use_cases/get_feuille_heures.py`

**Actions** :
1. ✅ Injecter `EntityInfoService`
2. ✅ Enrichir avant conversion en DTO

### Phase 4 : Mettre à Jour les DTOs

**Fichiers** :
- `backend/modules/pointages/application/dtos/feuille_heures_dtos.py`
- `backend/modules/pointages/application/dtos/pointage_dtos.py`

**Actions** :
1. ✅ Ajouter champs enrichis dans les DTOs :
   ```python
   @dataclass
   class PointageJourDTO:
       # ... champs existants ...
       utilisateur_nom: str  # ✅ Ajouté
       chantier_nom: str     # ✅ Ajouté
       chantier_couleur: str # ✅ Ajouté
   ```

2. ✅ Mettre à jour `from_entity()` pour accepter paramètres optionnels :
   ```python
   @classmethod
   def from_entity(
       cls,
       pointage: Pointage,
       utilisateur_nom: str = None,
       chantier_nom: str = None,
       chantier_couleur: str = None,
   ) -> "PointageDTO":
       return cls(
           id=pointage.id,
           # ... autres champs ...
           utilisateur_nom=utilisateur_nom or f"Utilisateur {pointage.utilisateur_id}",
           chantier_nom=chantier_nom or f"Chantier {pointage.chantier_id}",
           chantier_couleur=chantier_couleur or "#808080",
       )
   ```

### Phase 5 : Tests

**Actions** :
1. ✅ Adapter tests unitaires du Repository (supprimer tests de JOINs)
2. ✅ Mocker `EntityInfoService` dans tests Use Case
3. ✅ Vérifier que TOUS les tests passent
4. ✅ Ajouter tests d'intégration pour vérifier enrichissement

---

## 🎯 CRITÈRES D'ACCEPTATION

### Tests

- [ ] Tous les tests unitaires passent
- [ ] Tous les tests d'intégration passent
- [ ] Couverture ≥ 85%

### Fonctionnalités

- [ ] Les feuilles d'heures affichent les VRAIS noms (pas de régression)
- [ ] Vue Compagnons : noms utilisateurs corrects
- [ ] Vue Chantiers : noms chantiers corrects
- [ ] Dashboard : cohérence avec feuilles d'heures
- [ ] Fiches chantier : cohérence avec feuilles d'heures

### Architecture

- [ ] Aucun import cross-module dans Repository
- [ ] Repository ne contient QUE de la persistence
- [ ] Entités Domain pures (sans données de présentation)
- [ ] Enrichissement dans Use Case avec `EntityInfoService`
- [ ] DTOs portent les données enrichies

### Performance

- [ ] Pas de régression de performance (max +10% temps de réponse)
- [ ] Cache dans Use Case évite le problème N+1
- [ ] Requêtes SQL optimisées

---

## 📊 ESTIMATION

| Phase | Complexité | Temps Estimé | Dépendances |
|-------|------------|--------------|-------------|
| Phase 1 : Repository | Facile | 1h | Aucune |
| Phase 2 : Entité | Facile | 0.5h | Phase 1 |
| Phase 3 : Use Cases | Moyenne | 3h | Phase 1, 2 |
| Phase 4 : DTOs | Facile | 1h | Phase 3 |
| Phase 5 : Tests | Moyenne | 2h | Phase 1-4 |
| **TOTAL** | **Moyenne** | **7.5h** | - |

---

## 🚀 PROCHAINES ÉTAPES

1. **Créer un ticket GitHub** : Issue détaillée avec ce plan de refactoring
2. **Prioriser** : À discuter avec l'équipe (Priorité MOYENNE car fonctionnalité opérationnelle)
3. **Planifier** : Intégrer dans un sprint futur
4. **Implémenter** : Suivre le plan phase par phase
5. **Valider** : Tests + Review code + Validation utilisateur

---

## 📚 RÉFÉRENCES

- **CLEAN_ARCHITECTURE.md** : Principes de Clean Architecture du projet
- **GetPlanningUseCase** : Pattern de référence pour EntityInfoService
- **EntityInfoService** : Interface `shared/application/ports/entity_info_service.py`
- **Commit 29892d8** : Solution actuelle (à refactorer)
- **WORKFLOW_FEUILLES_HEURES.md** : Workflow complet et diagnostic du problème

---

**Auteur** : Claude Sonnet 4.5
**Date de création** : 30 janvier 2026
**Dernière mise à jour** : 30 janvier 2026
