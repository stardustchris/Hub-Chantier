# Contexte pour Claude (et autres assistants IA)

> **Ce fichier est ton guide de référence pour travailler sur Hub Chantier.**
> Lis-le attentivement avant toute intervention.

## Projet

**Hub Chantier** - Application de gestion de chantiers BTP
- **Client** : Greg Construction
- **Taille** : 20 employés, 4,3M€ CA
- **Initié le** : 21 janvier 2026
- **Initié par** : Claude (Projects)

## Architecture : Clean Architecture (Uncle Bob)

### Les 4 Layers (de l'intérieur vers l'extérieur)

```
1. DOMAIN (centre)     → Règles métier pures, AUCUNE dépendance technique
2. APPLICATION         → Use cases, orchestration, DTOs
3. ADAPTERS            → Controllers, Presenters, Providers
4. INFRASTRUCTURE      → Frameworks, DB, APIs externes
```

### Règle de dépendance (NON NÉGOCIABLE)

```
Infrastructure → Adapters → Application → Domain
     ↓              ↓            ↓           ↓
  dépend de     dépend de    dépend de    AUCUNE
                                         dépendance
```

**Les dépendances pointent TOUJOURS vers l'intérieur.**

## Structure d'un module

```
modules/auth/
├── domain/                    # Layer 1 - PURE (aucun framework)
│   ├── entities/              # Objets métier avec identité
│   │   └── user.py
│   ├── value_objects/         # Objets immuables sans identité
│   │   ├── email.py
│   │   └── password_hash.py
│   ├── repositories/          # INTERFACES (abstractions)
│   │   └── user_repository.py
│   ├── events/                # Événements domaine
│   │   └── user_created_event.py
│   └── services/              # Services domaine
│       └── password_service.py
├── application/               # Layer 2 - Logique applicative
│   ├── use_cases/             # Cas d'utilisation
│   │   ├── login.py
│   │   └── register.py
│   ├── dtos/                  # Data Transfer Objects
│   │   └── user_dto.py
│   └── ports/                 # Interfaces pour l'extérieur
│       └── token_service.py
├── adapters/                  # Layer 3 - Adaptation
│   ├── controllers/           # Gestion des requêtes
│   │   └── auth_controller.py
│   ├── presenters/            # Formatage des réponses
│   │   └── user_presenter.py
│   └── providers/             # Implémentation des ports
│       └── jwt_token_service.py
└── infrastructure/            # Layer 4 - Technique
    ├── persistence/           # Implémentation repositories
    │   └── sqlalchemy_user_repository.py
    └── web/                   # Routes FastAPI
        └── auth_routes.py
```

## Règles STRICTES (à ne JAMAIS violer)

### Règle 1 : Domain Layer PURE

```python
# ❌ INTERDIT dans domain/
from fastapi import ...
from sqlalchemy import ...
from pydantic import ...
import requests

# ✅ AUTORISÉ dans domain/
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from abc import ABC, abstractmethod
from ..value_objects import Email
from ..entities import User
```

### Règle 2 : Use Cases dépendent d'INTERFACES

```python
# ❌ INTERDIT
from infrastructure.persistence.sqlalchemy_user_repository import SQLAlchemyUserRepository

# ✅ CORRECT
from ...domain.repositories import UserRepository  # Interface abstraite

class LoginUseCase:
    def __init__(self, user_repo: UserRepository):  # Injection de dépendance
        self.user_repo = user_repo
```

### Règle 3 : Communication inter-modules via EVENTS

```python
# ❌ INTERDIT - Import direct entre modules
from modules.employes.application.use_cases import GetEmployeUseCase

# ✅ CORRECT - Via EventBus
from shared.infrastructure.event_bus import EventBus
from modules.employes.domain.events import EmployeCreeEvent

# Publier
EventBus.publish(EmployeCreeEvent(employe_id=123, nom="Dupont"))

# S'abonner
EventBus.subscribe(EmployeCreeEvent, handle_employe_cree)
```

### Règle 4 : Tests unitaires OBLIGATOIRES

Chaque use case DOIT avoir ses tests unitaires avec mocks des dépendances.

```python
# tests/unit/auth/test_login.py
def test_login_success():
    # Arrange - Mock du repository
    mock_repo = Mock(spec=UserRepository)
    mock_repo.find_by_email.return_value = User(...)

    use_case = LoginUseCase(user_repo=mock_repo)

    # Act
    result = use_case.execute(LoginDTO(email="test@test.com", password="pass"))

    # Assert
    assert result.success is True
```

## Conventions de nommage

### Classes

| Type | Convention | Exemple |
|------|------------|---------|
| Entity | Substantif singulier | `class User`, `class Pointage` |
| Value Object | Substantif descriptif | `class Email`, `class Adresse` |
| Use Case | Verbe + Substantif + UseCase | `class LoginUseCase`, `class PointerEntreeUseCase` |
| Repository (interface) | Entity + Repository | `class UserRepository`, `class PointageRepository` |
| Repository (impl) | Techno + Entity + Repository | `class SQLAlchemyUserRepository` |
| Event | Action passée + Event | `class UserCreatedEvent`, `class EmployePointeEvent` |
| DTO | Entity + DTO | `class UserDTO`, `class PointageDTO` |
| Controller | Module + Controller | `class AuthController` |

### Fichiers

| Classe | Fichier |
|--------|---------|
| `LoginUseCase` | `login.py` |
| `PointerEntreeUseCase` | `pointer_entree.py` |
| `User` | `user.py` |
| `UserCreatedEvent` | `user_created_event.py` |

### Tests

| Fichier source | Fichier test |
|----------------|--------------|
| `login.py` | `test_login.py` |
| `user.py` | `test_user.py` |

## Imports

### Dans un même module (relatifs)

```python
# Dans modules/auth/application/use_cases/login.py
from ...domain.entities import User
from ...domain.repositories import UserRepository
from ..dtos import LoginDTO
```

### Entre modules (absolus, via events uniquement !)

```python
# Dans modules/pointages/application/use_cases/pointer_entree.py
from shared.infrastructure.event_bus import EventBus
from modules.employes.domain.events import EmployePointeEvent  # Event seulement !
```

## Workflow de développement

### Pour ajouter une fonctionnalité

1. **Identifier le module** concerné
2. **Commencer par le domaine** (entities, value objects, règles métier)
3. **Créer le use case** (logique applicative)
4. **Écrire les tests unitaires** (use case avec mocks)
5. **Créer l'adapter** (controller si nécessaire)
6. **Implémenter l'infrastructure** (repository, routes)
7. **Tests d'intégration**
8. **Commit** : `feat(module): description`

### Pour créer un nouveau module

```bash
./scripts/generate-module.sh nom_module
```

Puis suivre le pattern de `modules/auth/`.

## Checklist avant commit

- [ ] Règle de dépendance respectée (layers)
- [ ] Aucun import interdit dans `domain/`
- [ ] Use cases utilisent des interfaces (pas d'implémentations directes)
- [ ] Communication inter-modules via Events uniquement
- [ ] Tests unitaires écrits (minimum : use cases)
- [ ] Docstrings Google style présentes
- [ ] Type hints présents partout
- [ ] Pas d'import circulaire
- [ ] Conventions de nommage respectées
- [ ] `./scripts/check-architecture.sh` passe

## Modules existants

| Module | Status | Responsabilité |
|--------|--------|----------------|
| **auth** | Complet | Authentification, JWT, rôles |
| **employes** | Complet | CRUD employés, corps de métier |
| **pointages** | Complet | Entrée/sortie chantier |
| **chantiers** | Complet | Gestion des chantiers |
| **planning** | Partiel | Planning des équipes |
| **documents** | TODO | Documents de chantier |
| **formulaires** | TODO | Formulaires terrain |

## Rôles utilisateurs

| Rôle | Permissions |
|------|-------------|
| `admin` | Tout |
| `chef_chantier` | Gestion de son chantier, validation pointages |
| `employe` | Pointer, consulter son planning |

## En cas de doute

1. **Consulte le module `auth`** - C'est le module de référence
2. **Lis les ADRs** dans `docs/architecture/ADR/`
3. **Lance** `./scripts/check-architecture.sh`
4. **Pose la question** à l'utilisateur
5. **NE DÉVIE JAMAIS** de Clean Architecture

## Commandes utiles

```bash
# Dev
./scripts/start-dev.sh

# Tests
pytest backend/tests/unit -v
pytest backend/tests/integration -v
pytest --cov=backend --cov-report=html

# Architecture
./scripts/check-architecture.sh

# Nouveau module
./scripts/generate-module.sh nom_module
```

---

**Rappel** : Tu continues le travail initié par Claude (Projects).
Maintiens la qualité et la cohérence du code existant.
