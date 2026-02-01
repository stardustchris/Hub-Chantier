# Rapport de Validation Architecture - Plusieurs métiers par utilisateur

**Date:** 2026-01-31 14:30:00 UTC
**Agent:** architect-reviewer
**Fonctionnalité:** Migration `metier` (string) → `metiers` (JSON array)
**Statut:** **FAIL** (0 violation Clean Architecture, mais 4 violations de cohérence données critiques)

---

## Résumé Exécutif

**Statut Clean Architecture:** ✅ **PASS (10/10)**
**Statut Cohérence Données:** ❌ **FAIL (3/10)**
**Statut Global:** ⚠️ **WARN (7/10)** - Blocage commit

### Constat Principal

L'implémentation respecte **parfaitement** les règles de Clean Architecture (4 layers, pureté Domain, inversion de dépendance, communication inter-modules via EventBus). **CEPENDANT**, il existe une **incohérence critique** entre les schémas Pydantic de l'API et les DTOs/modèles de données.

**Problème:** Les routes FastAPI utilisent encore `metier` (singulier, string) alors que la base de données, les entités Domain, les DTOs et le frontend utilisent `metiers` (pluriel, array). Cela empêche l'API d'accepter les requêtes du frontend.

---

## Validation Clean Architecture ✅

### 1. Domain Layer Purity ✅ (10/10)

**Résultat:** PASS - Aucun import framework détecté

Fichiers vérifiés:
- `backend/modules/auth/domain/entities/user.py`
- `backend/modules/auth/domain/value_objects.py`
- `backend/modules/planning/domain/entities/*`

**Imports autorisés trouvés:**
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from abc import ABC, abstractmethod
```

**Imports interdits:** Aucun (fastapi, sqlalchemy, pydantic)

### 2. Application Layer Purity ✅ (10/10)

**Résultat:** PASS - Application ne dépend que de Domain

Fichiers vérifiés:
- `backend/modules/auth/application/dtos/user_dto.py`
- `backend/modules/auth/application/use_cases/*`
- `backend/modules/planning/application/*`

### 3. Dependency Rule ✅ (10/10)

**Résultat:** PASS - Dépendances pointent vers l'intérieur

```
Infrastructure → Adapters → Application → Domain
```

Aucune violation détectée. Les dépendances respectent strictement la règle de Clean Architecture.

### 4. Inter-Module Communication ✅ (10/10)

**Résultat:** PASS - Communication via EventBus

Fichiers vérifiés:
- `backend/modules/planning/infrastructure/event_handlers.py`
- `backend/modules/pointages/infrastructure/event_handlers.py`
- `backend/modules/notifications/infrastructure/event_handlers.py`

**Pattern correct utilisé:**
```python
from shared.infrastructure.event_bus import event_handler

@event_handler('chantier.statut_changed')
def handle_chantier_statut_changed_for_planning(event: 'DomainEvent') -> None:
    # ...
```

**Pas d'import direct inter-modules détecté** (par ex. `from modules.employes import ...`)

### 5. Database Migration ✅ (10/10)

**Résultat:** PASS - Migration Alembic bien structurée

**Fichier:** `backend/migrations/versions/20260131_0001_convert_metier_to_metiers_array.py`

**Stratégie:**
1. Ajouter colonne `metiers` (JSON)
2. Migrer données existantes: `metiers = [metier]` si `metier` existe
3. Supprimer ancienne colonne `metier`

**Support multi-SGBD:** PostgreSQL (`jsonb_build_array`) et SQLite (`json_array`)

---

## Violations de Cohérence Données ❌

### Violation 1: Schémas Pydantic Routes (CRITICAL)

**Fichier:** `backend/modules/auth/infrastructure/web/auth_routes.py`
**Lignes:** 64, 75, 263, 385, 588, 910, 921, 1178

**Problème:**
```python
# ❌ INCORRECT - Routes utilisent 'metier' (singulier)
class RegisterRequest(BaseModel):
    metier: Optional[str] = None  # Ligne 64 - devrait être metiers: Optional[List[str]]

class UpdateUserRequest(BaseModel):
    metier: Optional[str] = None  # Ligne 75 - devrait être metiers: Optional[List[str]]

class InviteUserModel(BaseModel):
    metier: Optional[str] = None  # Ligne 385 - devrait être metiers: Optional[List[str]]
```

**Impact:** Le frontend envoie `metiers: ["macon", "coffreur"]` mais Pydantic attend `metier: "macon"` → **Erreur de validation 422**

**Correction requise:**
```python
# ✅ CORRECT
class RegisterRequest(BaseModel):
    metiers: Optional[List[str]] = None

class UpdateUserRequest(BaseModel):
    metiers: Optional[List[str]] = None

class InviteUserModel(BaseModel):
    metiers: Optional[List[str]] = None
```

---

### Violation 2: Controller Parameters (CRITICAL)

**Fichier:** `backend/modules/auth/adapters/controllers/auth_controller.py`
**Lignes:** 150, 243

**Problème:**
```python
# ❌ INCORRECT
dto = RegisterDTO(
    email=email,
    password=password,
    nom=nom,
    prenom=prenom,
    metier=metier,  # Ligne 150 - devrait être metiers=metiers
    ...
)

dto = UpdateUserDTO(
    nom=nom,
    prenom=prenom,
    metier=metier,  # Ligne 243 - devrait être metiers=metiers
    ...
)
```

**Impact:** Le controller passe `metier` au DTO qui attend `metiers` → **AttributeError**

**Correction requise:**
```python
# ✅ CORRECT
dto = RegisterDTO(..., metiers=metiers, ...)
dto = UpdateUserDTO(..., metiers=metiers, ...)
```

---

### Violation 3: Password Reset Route (CRITICAL)

**Fichier:** `backend/modules/auth/infrastructure/web/password_routes.py`
**Ligne:** 275

**Problème:** Même incohérence lors de l'acceptation d'invitation

---

### Violation 4: InviteUser Use Case (CRITICAL)

**Fichier:** `backend/modules/auth/application/use_cases/invite_user.py`
**Ligne:** 88

**Problème:** Signature du use case accepte `metier: str` au lieu de `metiers: Optional[List[str]]`

**Correction requise:**
```python
# ✅ CORRECT
def execute(
    self,
    email: str,
    nom: str,
    prenom: str,
    role: Role,
    type_utilisateur: TypeUtilisateur,
    code_utilisateur: Optional[str] = None,
    metiers: Optional[List[str]] = None,  # Pluriel
    inviter_name: str = "L'équipe Hub Chantier",
) -> None:
```

---

## Analyse du Flux de Données

### Frontend → Backend ❌ INCONSISTENT

**Frontend (TypeScript):**
```typescript
// ✅ CORRECT
interface User {
  metiers?: Metier[]  // Array de métiers
}

// Frontend envoie:
POST /api/auth/register
{
  "email": "jean@greg.fr",
  "nom": "Dupont",
  "metiers": ["macon", "coffreur"]  // ✅ Array
}
```

**Backend (Pydantic):**
```python
# ❌ INCORRECT
class RegisterRequest(BaseModel):
    metier: Optional[str] = None  # ❌ Attend string

# Résultat: Pydantic valide FAIL avec 422 Unprocessable Entity
```

---

### Backend → Database ✅ CORRECT

```python
# Domain Entity (✅)
@dataclass
class User:
    metiers: Optional[List[str]] = None

# SQLAlchemy Model (✅)
class UserModel(Base):
    metiers = Column(JSON, nullable=True)

# Repository Mapping (✅)
model.metiers = user.metiers  # Ligne 117
```

---

### Database → Backend ✅ CORRECT

```python
# DTO Mapping (✅)
@dataclass(frozen=True)
class UserDTO:
    metiers: Optional[List[str]]

    @classmethod
    def from_entity(cls, user: User) -> "UserDTO":
        return cls(..., metiers=user.metiers, ...)
```

---

### Backend → Frontend ❌ INCONSISTENT

```python
# ❌ INCORRECT dans _transform_user_response (ligne 1178)
return UserResponse(
    ...
    metier=user_dict.get("metier"),  # ❌ Devrait être metiers
    ...
)
```

**Impact:** Frontend reçoit `metier: "macon"` au lieu de `metiers: ["macon"]`

---

## Validation Frontend ✅

**Fichiers vérifiés:**
- `frontend/src/types/index.ts` (ligne 15)
- `frontend/src/components/users/MetierMultiSelect.tsx`
- `frontend/src/components/users/CreateUserModal.tsx`
- `frontend/src/components/users/EditUserModal.tsx`

**Résultat:** Types TypeScript correctement définis avec `metiers: Metier[]`

---

## Scores Détaillés

| Critère | Score | Statut |
|---------|-------|--------|
| Clean Architecture | 10/10 | ✅ PASS |
| Modularity | 10/10 | ✅ PASS |
| Maintainability | 5/10 | ⚠️ WARN |
| Data Consistency | 3/10 | ❌ FAIL |
| **Overall** | **7/10** | **⚠️ WARN** |

---

## Recommandations

### Corrections URGENTES (Bloquantes pour commit)

1. **Modifier `backend/modules/auth/infrastructure/web/auth_routes.py`:**
   - RegisterRequest.metier → metiers: Optional[List[str]]
   - UpdateUserRequest.metier → metiers: Optional[List[str]]
   - InviteUserModel.metier → metiers: Optional[List[str]]
   - \_transform\_user\_response: metier= → metiers=

2. **Modifier `backend/modules/auth/adapters/controllers/auth_controller.py`:**
   - Ligne 150: metier=metier → metiers=metiers
   - Ligne 243: metier=metier → metiers=metiers

3. **Modifier `backend/modules/auth/infrastructure/web/password_routes.py`:**
   - Ligne 275: metier=request_data.metier → metiers=request_data.metiers

4. **Modifier `backend/modules/auth/application/use_cases/invite_user.py`:**
   - Signature execute(): metier: str → metiers: Optional[List[str]]

### Tests de Non-Régression

Après corrections, tester:
```bash
# 1. Tests unitaires
pytest backend/tests/unit/auth -v

# 2. Test manuel
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@greg.fr",
    "password": "SecurePass123!",
    "nom": "Test",
    "prenom": "User",
    "metiers": ["macon", "coffreur"]
  }'

# Résultat attendu: 201 Created (actuellement: 422 Unprocessable Entity)
```

---

## Conclusion

**Clean Architecture: ✅ EXEMPLAIRE**

L'implémentation respecte **parfaitement** les règles de Clean Architecture:
- Domain layer 100% pure (0 import framework)
- Application layer dépend uniquement de Domain
- Communication inter-modules via EventBus (pas d'import direct)
- Migration base de données bien structurée

**Cohérence Données: ❌ CRITIQUE**

Cependant, **l'API ne peut pas fonctionner** en raison des incohérences entre:
- Frontend qui envoie `metiers: []` (array)
- Routes Pydantic qui attendent `metier: ""` (string)

**Décision: FAIL - Commit bloqué**

Les corrections sont **simples et rapides** (renommage de paramètres), mais **essentielles** pour que l'API accepte les requêtes du frontend.

---

## Prochaines Étapes

1. ✅ Appliquer les 4 corrections listées ci-dessus
2. ✅ Exécuter `pytest backend/tests/unit/auth -v`
3. ✅ Tester manuellement création utilisateur avec plusieurs métiers
4. ✅ RE-VALIDER avec architect-reviewer
5. ✅ Commit après PASS de toutes les validations

**Estimation temps corrections:** 15-20 minutes
**Complexité:** Faible (renommage de paramètres)
**Risque:** Faible (tests unitaires couvrent le comportement)
