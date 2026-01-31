# Rapport GAP-T3 : Vérification JOINs avec table users

**Date**: 2026-01-31
**Contexte**: Vérifier que FeuilleHeuresRepository/PointageRepository joignent correctement la table `users` pour récupérer les noms des compagnons
**Endpoint testé**: `/api/pointages/vues/compagnons`

---

## 1. Résumé Exécutif

**Statut**: ✅ **CONFORME**

Le système effectue correctement l'enrichissement des données utilisateurs et chantiers via `EntityInfoService`. Les noms des compagnons sont récupérés et affichés dans la vue.

---

## 2. Architecture de la Solution

### 2.1 Flux de données

```
GET /api/pointages/vues/compagnons
    ↓
PointageController.get_vue_compagnons()
    ↓
GetVueSemaineUseCase.get_vue_compagnons()
    ↓
1. SQLAlchemyPointageRepository.search() → Récupère les pointages (IDs seulement)
2. _enrich_pointages() → Enrichit via EntityInfoService
    ↓
SQLAlchemyEntityInfoService.get_user_info(user_id)
    → SELECT FROM users WHERE id = ?
    → Retourne UserBasicInfo(nom="Prenom Nom")
    ↓
Pointage.utilisateur_nom = "Prenom Nom"
```

### 2.2 Pas de JOIN direct dans PointageRepository

Le `SQLAlchemyPointageRepository` **ne fait PAS de JOIN** avec la table `users`. Ceci est voulu dans l'architecture Clean Architecture pour respecter le découplage entre modules.

**Fichier**: `/Users/aptsdae/Hub-Chantier/backend/modules/pointages/infrastructure/persistence/sqlalchemy_pointage_repository.py`

- Requête SQL générée (ligne 150-165):
```sql
SELECT pointages.*
FROM pointages
WHERE pointages.date_pointage >= ? AND pointages.date_pointage <= ?
-- Pas de JOIN avec users ou chantiers
```

- Le modèle `PointageModel` stocke uniquement les IDs (lignes 28-29):
```python
utilisateur_id = Column(Integer, nullable=False, index=True)
chantier_id = Column(Integer, nullable=False, index=True)
# Pas de FK vers users/chantiers - découplage modules Clean Architecture
```

---

## 3. EntityInfoService : Le mécanisme d'enrichissement

### 3.1 Implémentation

**Fichier**: `/Users/aptsdae/Hub-Chantier/backend/shared/infrastructure/entity_info_impl.py`

```python
class SQLAlchemyEntityInfoService(EntityInfoService):
    def get_user_info(self, user_id: int) -> Optional[UserBasicInfo]:
        # Import lazy pour éviter imports circulaires
        from modules.auth.infrastructure.persistence import UserModel

        user = self._session.query(UserModel).filter(
            UserModel.id == user_id
        ).first()

        if user:
            nom = f"{user.prenom or ''} {user.nom or ''}".strip()
            return UserBasicInfo(
                id=user.id,
                nom=nom or f"User {user.id}",
                couleur=user.couleur,
                metier=user.metier,
                role=user.role,
                type_utilisateur=user.type_utilisateur,
            )
```

**Avantages**:
- Découplage complet entre modules
- Pas de dépendances circulaires
- Centralisation des imports inter-modules dans `shared/`

### 3.2 Utilisation dans GetVueSemaineUseCase

**Fichier**: `/Users/aptsdae/Hub-Chantier/backend/modules/pointages/application/use_cases/get_vue_semaine.py`

```python
def _enrich_pointages(self, pointages: List) -> None:
    """Enrichit les pointages avec les noms utilisateurs et chantiers."""
    if not self.entity_info_service or not pointages:
        return

    # Collecter les IDs uniques
    user_ids = {p.utilisateur_id for p in pointages}
    chantier_ids = {p.chantier_id for p in pointages}

    # Cache local pour éviter requêtes répétées
    user_cache = {}
    for uid in user_ids:
        info = self.entity_info_service.get_user_info(uid)
        if info:
            user_cache[uid] = info

    # Enrichir chaque pointage
    for p in pointages:
        user_info = user_cache.get(p.utilisateur_id)
        if user_info:
            p.utilisateur_nom = user_info.nom
```

**Points clés**:
- Cache local pour minimiser les requêtes SQL
- Requêtes séparées pour users et chantiers
- Enrichissement in-memory des entités Pointage

---

## 4. Test Réel

### 4.1 Commande de test

```bash
python3 -c "
from modules.pointages.application.use_cases import GetVueSemaineUseCase
use_case = GetVueSemaineUseCase(pointage_repo, entity_info_service)
result = use_case.get_vue_compagnons(semaine_debut)
"
```

### 4.2 Résultat

```
Nombre de compagnons: 12

Compagnon ID: 12
Nom: Babaker HAROUN MOUSSA
Total heures: 40:00
  Chantiers:
    - Chantier 24 (24): 40:00

Compagnon ID: 11
Nom: Manuel FIGUEIREDO DE ALMEIDA
Total heures: 40:00
  Chantiers:
    - Chantier 28 (28): 40:00
```

### 4.3 Requêtes SQL générées

**1. Récupération des pointages (sans JOIN)**:
```sql
SELECT pointages.*
FROM pointages
WHERE pointages.date_pointage >= '2026-01-26'
  AND pointages.date_pointage <= '2026-02-01'
```

**2. Enrichissement via EntityInfoService (1 requête par user_id unique)**:
```sql
SELECT users.* FROM users WHERE users.id = 7
SELECT users.* FROM users WHERE users.id = 8
SELECT users.* FROM users WHERE users.id = 9
...
```

**Optimisation**: Grâce au cache local, on fait **1 requête par utilisateur unique**, pas 1 requête par pointage.

---

## 5. Endpoint API

**Route**: `GET /api/pointages/vues/compagnons`

**Fichier**: `/Users/aptsdae/Hub-Chantier/backend/modules/pointages/infrastructure/web/routes.py` (lignes 227-238)

```python
@router.get("/vues/compagnons")
def get_vue_compagnons(
    semaine_debut: date = Query(..., description="Date du lundi de la semaine"),
    utilisateur_ids: Optional[str] = Query(None, description="IDs utilisateurs"),
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Vue par compagnons pour une semaine (FDH-01 onglet Compagnons)."""
    utilisateur_ids_list = None
    if utilisateur_ids:
        utilisateur_ids_list = [int(x) for x in utilisateur_ids.split(",")]
    return controller.get_vue_compagnons(semaine_debut, utilisateur_ids_list)
```

**Injection de dépendances** (lignes 96-110):
```python
def get_controller(db: Session = Depends(get_db)) -> PointageController:
    pointage_repo = SQLAlchemyPointageRepository(db)
    entity_info_service = SQLAlchemyEntityInfoService(db)  # ← Injecté ici

    return PointageController(
        pointage_repo=pointage_repo,
        entity_info_service=entity_info_service,  # ← Passé au controller
    )
```

---

## 6. Structure des DTOs retournés

**Fichier**: `/Users/aptsdae/Hub-Chantier/backend/modules/pointages/adapters/controllers/pointage_controller.py` (lignes 322-365)

```json
[
  {
    "utilisateur_id": 12,
    "utilisateur_nom": "Babaker HAROUN MOUSSA",  // ← Enrichi
    "total_heures": "40:00",
    "total_heures_decimal": 40.0,
    "chantiers": [
      {
        "chantier_id": 24,
        "chantier_nom": "Chantier 24",  // ← Enrichi (échec dans ce cas)
        "chantier_couleur": "#808080",
        "total_heures": "40:00",
        "pointages_par_jour": { ... }
      }
    ],
    "totaux_par_jour": { ... }
  }
]
```

---

## 7. Points d'Attention

### 7.1 Erreur dans get_chantier_info()

Le test a révélé une erreur lors de la récupération des chantiers:

```
Erreur recuperation chantier 24:
When initializing mapper Mapper[ChantierModel(chantiers)],
expression 'DossierModel' failed to locate a name
```

**Impact**: Les noms de chantiers ne sont pas récupérés (fallback sur "Chantier {id}"), mais les **noms d'utilisateurs fonctionnent correctement**.

**À corriger**: Le modèle `ChantierModel` a une référence à `DossierModel` qui pose problème. Ceci est hors scope de GAP-T3 mais devrait être corrigé.

### 7.2 Performance

**Nombre de requêtes SQL**:
- 1 requête pour les pointages
- N requêtes pour les users (N = nombre d'utilisateurs uniques)
- N requêtes pour les chantiers (N = nombre de chantiers uniques)

Pour une semaine avec 12 compagnons et 8 chantiers:
- Total: ~21 requêtes

**Alternative possible** (non implémentée): JOIN direct dans le repository, mais cela violerait le découplage entre modules.

---

## 8. Conformité aux Spécifications

### 8.1 FDH-01: Vue par Compagnons

> "Afficher la liste des compagnons avec leurs noms et heures travaillées par chantier"

**Status**: ✅ Conforme
- Noms des compagnons affichés
- Heures par chantier calculées
- Structure de données correcte

### 8.2 Clean Architecture

**Status**: ✅ Conforme
- Pas de FK directes entre modules
- EntityInfoService centralise les imports inter-modules
- Découplage respecté

---

## 9. Recommandations

### 9.1 Court terme

1. **Corriger l'erreur DossierModel** dans ChantierModel pour afficher les noms de chantiers
2. **Ajouter un test d'intégration** pour valider l'endpoint complet

### 9.2 Moyen terme

1. **Monitorer les performances** si le nombre de compagnons/chantiers augmente (>100)
2. **Envisager un cache Redis** pour UserBasicInfo/ChantierBasicInfo si nécessaire
3. **Ajouter des métriques** sur le nombre de requêtes SQL par endpoint

---

## 10. Conclusion

**GAP-T3**: ✅ **RÉSOLU**

Le système effectue correctement la récupération des noms d'utilisateurs via `EntityInfoService`. La méthode utilisée (requêtes séparées + cache) est conforme à l'architecture Clean Architecture et au découplage entre modules.

**Prochaine étape**: Corriger l'erreur `DossierModel` dans le module chantiers (hors scope GAP-T3).

---

## Annexe: Fichiers Analysés

1. `/Users/aptsdae/Hub-Chantier/backend/modules/pointages/infrastructure/persistence/sqlalchemy_pointage_repository.py`
2. `/Users/aptsdae/Hub-Chantier/backend/modules/pointages/application/use_cases/get_vue_semaine.py`
3. `/Users/aptsdae/Hub-Chantier/backend/shared/infrastructure/entity_info_impl.py`
4. `/Users/aptsdae/Hub-Chantier/backend/modules/pointages/infrastructure/web/routes.py`
5. `/Users/aptsdae/Hub-Chantier/backend/modules/pointages/adapters/controllers/pointage_controller.py`
6. `/Users/aptsdae/Hub-Chantier/backend/modules/pointages/domain/entities/pointage.py`
7. `/Users/aptsdae/Hub-Chantier/backend/modules/pointages/infrastructure/persistence/models.py`
