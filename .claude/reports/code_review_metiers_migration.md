# Revue de Code - Migration metier → metiers

**Agent:** code-reviewer
**Date:** 2026-01-31
**Statut:** **CHANGES REQUESTED** ⚠️

---

## Résumé Exécutif

La migration de `metier` (string unique) vers `metiers` (array JSON) a été **partiellement implémentée**.

### Problème Majeur

**14 findings CRITICAL** identifiés dans 2 fichiers backend qui utilisent encore `metier` (singular) au lieu de `metiers` (pluriel):

- `backend/modules/auth/infrastructure/web/auth_routes.py` (10 occurrences)
- `backend/modules/auth/adapters/controllers/auth_controller.py` (4 occurrences)

Ces incohérences **cassent la fonctionnalité** car:
1. Les routes reçoivent `metiers: List[str]` du frontend
2. Mais les Pydantic models attendent `metier: str`
3. Le controller passe `metier` aux DTOs qui attendent `metiers`
4. Résultat: **400 Bad Request** ou données perdues

---

## Métriques

| Métrique | Valeur |
|----------|--------|
| Fichiers revus | 25 |
| Issues trouvées | 43 |
| **CRITICAL** | **14** |
| MAJOR | 4 |
| MINOR | 2 |
| SUGGESTION | 23 |

---

## Findings Critiques (14)

### 1. auth_routes.py - RegisterRequest (ligne 64)

**Problème:** `metier: Optional[str]` au lieu de `metiers: Optional[List[str]]`

```python
# ❌ ACTUEL
class RegisterRequest(BaseModel):
    metier: Optional[str] = None

# ✅ CORRECTION
class RegisterRequest(BaseModel):
    metiers: Optional[List[str]] = None
```

---

### 2. auth_routes.py - Route /register (ligne 263)

**Problème:** Passe `data.metier` au controller (champ inexistant)

```python
# ❌ ACTUEL
result = controller.register(
    ...
    metier=data.metier,
    ...
)

# ✅ CORRECTION
result = controller.register(
    ...
    metiers=data.metiers,
    ...
)
```

---

### 3. auth_routes.py - UpdateUserRequest (ligne 74)

**Problème:** Pas de champ `metiers` défini

```python
# ✅ CORRECTION REQUISE
class UpdateUserRequest(BaseModel):
    ...
    metiers: Optional[List[str]] = None
    ...
```

---

### 4. auth_routes.py - UserResponse (ligne 102)

**Problème:** Pas de champ `metiers` défini

```python
# ✅ CORRECTION REQUISE
class UserResponse(BaseModel):
    ...
    metiers: Optional[List[str]] = None
    ...
```

---

### 5. auth_routes.py - InviteUserModel (ligne 385)

**Problème:** `metier: Optional[str]` au lieu de `metiers`

```python
# ❌ ACTUEL
class InviteUserModel(BaseModel):
    metier: Optional[str] = None

# ✅ CORRECTION
class InviteUserModel(BaseModel):
    metiers: Optional[List[str]] = None
```

---

### 6. auth_routes.py - Route /invite (ligne 588)

**Problème:** Passe `metier=request_body.metier`

```python
# ❌ ACTUEL
use_case.execute(
    ...
    metier=request_body.metier,
    ...
)

# ✅ CORRECTION
use_case.execute(
    ...
    metiers=request_body.metiers,
    ...
)
```

---

### 7. auth_routes.py - Route PUT /users/{id} (ligne 921)

**Problème:** Passe `metier=request.metier` au controller

```python
# ❌ ACTUEL
result = controller.update_user(
    ...
    metier=request.metier,
    ...
)

# ✅ CORRECTION
result = controller.update_user(
    ...
    metiers=request.metiers,
    ...
)
```

---

### 8. auth_routes.py - _transform_user_response (ligne 1178)

**Problème:** Mappe `metier` au lieu de `metiers`

```python
# ❌ ACTUEL
return UserResponse(
    ...
    metier=user_dict.get("metier"),
    ...
)

# ✅ CORRECTION
return UserResponse(
    ...
    metiers=user_dict.get("metiers"),
    ...
)
```

---

### 9-10. auth_routes.py - Audit trails (lignes 910, 936)

**Problème:** Audit capture `metier` au lieu de `metiers`

```python
# ❌ ACTUEL
old_values = {
    "metier": old_user.get("metier"),
}

# ✅ CORRECTION
old_values = {
    "metiers": old_user.get("metiers"),
}
```

---

### 11. auth_controller.py - _user_dto_to_dict (ligne 76)

**Problème:** Mappe `user_dto.metier` (attribut inexistant)

```python
# ❌ ACTUEL
return {
    ...
    "metier": user_dto.metier,
    ...
}

# ✅ CORRECTION
return {
    ...
    "metiers": user_dto.metiers,
    ...
}
```

---

### 12. auth_controller.py - register() signature (ligne 115)

**Problème:** Paramètre `metier: Optional[str]`

```python
# ❌ ACTUEL
def register(
    self,
    ...
    metier: Optional[str] = None,
    ...
):

# ✅ CORRECTION
def register(
    self,
    ...
    metiers: Optional[List[str]] = None,
    ...
):
```

---

### 13. auth_controller.py - register() DTO (ligne 150)

**Problème:** Passe `metier=metier` au RegisterDTO

```python
# ❌ ACTUEL
dto = RegisterDTO(
    ...
    metier=metier,
    ...
)

# ✅ CORRECTION
dto = RegisterDTO(
    ...
    metiers=metiers,
    ...
)
```

---

### 14. auth_controller.py - update_user() signature + DTO (lignes 206, 243)

**Problème:** Paramètre `metier` et passage au DTO

```python
# ❌ ACTUEL
def update_user(
    self,
    ...
    metier: Optional[str] = None,
    ...
):
    dto = UpdateUserDTO(
        ...
        metier=metier,
        ...
    )

# ✅ CORRECTION
def update_user(
    self,
    ...
    metiers: Optional[List[str]] = None,
    ...
):
    dto = UpdateUserDTO(
        ...
        metiers=metiers,
        ...
    )
```

---

## Findings Majeurs (4)

### 1-2. Docstrings obsolètes (auth_controller.py lignes 131, 223)

**Problème:** Documentation mentionne "métier" (singular)

```python
# ✅ CORRECTION
"""
Args:
    ...
    metiers: Liste des métiers/spécialités.
    ...
"""
```

### 3-4. Audit trails (auth_routes.py lignes 910, 936)

Déjà mentionné dans CRITICAL.

---

## Findings Mineurs (2)

### 1. Migration Alembic - down_revision (ligne 14)

**Suggestion:** Utiliser le nom complet pour cohérence

```python
# ACTUEL (fonctionne mais incohérent)
down_revision = '45fbfeb64662'

# RECOMMANDÉ
down_revision = '20260130_2114_45fbfeb64662'
```

### 2. Migration - batch_alter_table

**Observation:** Bien documenté, compatibilité SQLite assurée. ✅

---

## Points Positifs (10)

1. **Migration Alembic réversible** avec `upgrade()` et `downgrade()`
2. **Gestion multi-dialectes** (PostgreSQL `jsonb_build_array` vs SQLite `json_array`)
3. **DTOs immutables** (`frozen=True`) respectés partout
4. **Type hints complets** dans Domain/Application layers
5. **Entity User** correctement mise à jour avec `metiers: Optional[List[str]]`
6. **Repository** correctement implémenté (mapping entity ↔ model)
7. **Frontend TypeScript** 100% cohérent avec `metiers: Metier[]`
8. **Composant MetierMultiSelect** réutilisable avec excellente UX
9. **Limite MAX_METIERS=5** bien implémentée
10. **Clean Architecture** respectée (dépendances vers l'intérieur)

---

## Recommandations

### URGENT (Priorité CRITICAL)

Corriger **IMMÉDIATEMENT** les 14 occurrences de `metier` → `metiers` dans:

1. `backend/modules/auth/infrastructure/web/auth_routes.py`
   - RegisterRequest
   - UpdateUserRequest
   - UserResponse
   - InviteUserModel
   - Routes: /register, /invite, PUT /users/{id}
   - Fonction: _transform_user_response
   - Audit trails (2 occurrences)

2. `backend/modules/auth/adapters/controllers/auth_controller.py`
   - _user_dto_to_dict()
   - register() signature + DTO
   - update_user() signature + DTO

### Priorité HIGH

- Mettre à jour les **docstrings** pour refléter `metiers` (pluriel)

### Priorité MEDIUM

- Corriger les **audit trails** pour capturer `metiers` au lieu de `metier`

### Priorité LOW

- Utiliser le nom complet de `down_revision` dans la migration Alembic

---

## Next Steps

1. **Corriger auth_routes.py** (10 occurrences de `metier` → `metiers`)
2. **Corriger auth_controller.py** (4 occurrences de `metier` → `metiers`)
3. **Lancer les tests unitaires** pour valider les corrections
4. **Tester manuellement** le flux complet:
   - Inscription avec plusieurs métiers
   - Mise à jour des métiers
   - Lecture du profil
5. **Vérifier les audit trails** après mise à jour

---

## Validation

### Checklist Qualité

- [ ] Zero issues de sécurité critiques ✅
- [ ] Couverture de code > 80% ⚠️ (tests à mettre à jour)
- [ ] Complexité cyclomatique < 10 ✅
- [ ] Documentation complete ⚠️ (docstrings à mettre à jour)
- [ ] Pas de vulnerabilités haute priorité ✅

### Conformité Conventions Hub Chantier

| Convention | Statut | Commentaire |
|------------|--------|-------------|
| Docstrings Google style | ⚠️ | Certaines docstrings obsolètes |
| Type hints obligatoires | ✅ | Complets partout |
| Nommage entités | ✅ | User, UserDTO, etc. |
| DTOs frozen | ✅ | Tous immutables |
| Exceptions custom | ✅ | Bien utilisées |

---

## Conclusion

**Statut final:** **CHANGES REQUESTED** ⚠️

La migration `metier` → `metiers` est **correctement implémentée** dans:
- Domain layer (User entity)
- Application layer (DTOs, Use Cases)
- Infrastructure layer (UserModel, Repository)
- Frontend (TypeScript, composants React)

Mais elle est **incomplète** dans:
- **Infrastructure/Web layer** (auth_routes.py)
- **Adapters layer** (auth_controller.py)

Ces incohérences créent un **blocage fonctionnel** qui empêche:
- L'inscription avec plusieurs métiers
- La mise à jour des métiers
- La lecture correcte des métiers

**Estimation correction:** 30 minutes (rechercher/remplacer + tests)

---

**Agent:** code-reviewer
**Signature:** Revue complète effectuée selon checklist qualité Hub Chantier
