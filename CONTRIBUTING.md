# Guide de contribution - Hub Chantier

## Architecture Clean Architecture

Ce projet suit **strictement** les principes de Clean Architecture (Uncle Bob).

```
Infrastructure → Adapters → Application → Domain
     ↓              ↓            ↓           ↓
  depend de     depend de    depend de    AUCUNE
                                         dependance
```

**Regle d'or** : Les dependances pointent TOUJOURS vers l'interieur.

## Structure d'un module

```
modules/{module}/
├── domain/                    # Layer 1 - PURE (aucun framework)
│   ├── entities/              # Objets metier avec identite
│   ├── value_objects/         # Objets immuables sans identite
│   ├── repositories/          # INTERFACES (abstractions)
│   ├── events/                # Evenements domaine
│   └── services/              # Services domaine
├── application/               # Layer 2 - Logique applicative
│   ├── use_cases/             # Cas d'utilisation
│   ├── dtos/                  # Data Transfer Objects
│   └── ports/                 # Interfaces pour l'exterieur
├── adapters/                  # Layer 3 - Adaptation
│   ├── controllers/           # Gestion des requetes
│   ├── presenters/            # Formatage des reponses
│   └── providers/             # Implementation des ports
└── infrastructure/            # Layer 4 - Technique
    ├── persistence/           # Implementation repositories
    └── web/                   # Routes FastAPI
```

**Reference** : Le module `auth` est le module de reference a suivre.

## Regles strictes

### Regle 1 : Domain Layer PURE

```python
# INTERDIT dans domain/
from fastapi import ...
from sqlalchemy import ...
from pydantic import ...
import requests

# AUTORISE dans domain/
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from abc import ABC, abstractmethod
```

### Regle 2 : Use Cases dependent d'INTERFACES

```python
# INTERDIT
from infrastructure.persistence.sqlalchemy_user_repository import SQLAlchemyUserRepository

# CORRECT
from ...domain.repositories import UserRepository  # Interface abstraite

class LoginUseCase:
    def __init__(self, user_repo: UserRepository):  # Injection de dependance
        self.user_repo = user_repo
```

### Regle 3 : Communication inter-modules via EVENTS

```python
# INTERDIT - Import direct entre modules
from modules.employes.application.use_cases import GetEmployeUseCase

# CORRECT - Via EventBus
from shared.infrastructure.event_bus import EventBus
EventBus.publish(EmployeCreeEvent(employe_id=123, nom="Dupont"))
EventBus.subscribe(EmployeCreeEvent, handle_employe_cree)
```

### Regle 4 : Tests unitaires OBLIGATOIRES

Chaque use case DOIT avoir ses tests unitaires avec mocks des dependances.

```python
def test_login_success():
    mock_repo = Mock(spec=UserRepository)
    mock_repo.find_by_email.return_value = User(...)
    use_case = LoginUseCase(user_repo=mock_repo)
    result = use_case.execute(LoginDTO(email="test@test.com", password="pass"))
    assert result.success is True
```

## Conventions de nommage

### Classes

| Type | Convention | Exemple |
|------|------------|---------|
| Entity | Substantif singulier | `class User`, `class Pointage` |
| Value Object | Substantif descriptif | `class Email`, `class Adresse` |
| Use Case | Verbe + Substantif + UseCase | `class LoginUseCase` |
| Repository (interface) | Entity + Repository | `class UserRepository` |
| Repository (impl) | Techno + Entity + Repository | `class SQLAlchemyUserRepository` |
| Event | Action passee + Event | `class UserCreatedEvent` |
| DTO | Entity + DTO | `class UserDTO` |
| Controller | Module + Controller | `class AuthController` |

### Fichiers

| Classe | Fichier |
|--------|---------|
| `LoginUseCase` | `login.py` |
| `User` | `user.py` |
| `UserCreatedEvent` | `user_created_event.py` |

### Tests

| Fichier source | Fichier test |
|----------------|--------------|
| `login.py` | `test_login.py` |

## Imports

### Dans un meme module (relatifs)

```python
from ...domain.entities import User
from ...domain.repositories import UserRepository
from ..dtos import LoginDTO
```

### Entre modules (absolus, via events uniquement)

```python
from shared.infrastructure.event_bus import EventBus
from modules.employes.domain.events import EmployePointeEvent
```

## Workflow de developpement

### Pour ajouter une fonctionnalite

1. **Identifier le module** concerne
2. **Commencer par le domaine** (entities, value objects, regles metier)
3. **Creer le use case** (logique applicative)
4. **Ecrire les tests unitaires** (use case avec mocks)
5. **Creer l'adapter** (controller si necessaire)
6. **Implementer l'infrastructure** (repository, routes)
7. **Tests d'integration**
8. **Commit** : `feat(module): description`

### Pour creer un nouveau module

```bash
./scripts/generate-module.sh nom_module
```

## Commits

Format conventionnel : `type(scope): description`

```bash
feat(auth): add JWT refresh token support
fix(pointages): correct timezone handling
docs(readme): update installation steps
test(employes): add unit tests for CreateEmployeUseCase
refactor(chantiers): extract address validation to value object
```

## Style de code

- Docstrings Google style
- Type hints partout
- 1 classe = 1 fichier
- Tests unitaires obligatoires pour les use cases

## Checklist avant commit

- [ ] Regle de dependance respectee (layers)
- [ ] Aucun import interdit dans `domain/`
- [ ] Use cases utilisent des interfaces (pas d'implementations directes)
- [ ] Communication inter-modules via Events uniquement
- [ ] Tests unitaires ecrits (minimum : use cases)
- [ ] Docstrings Google style presentes
- [ ] Type hints presents partout
- [ ] Pas d'import circulaire
- [ ] Conventions de nommage respectees
- [ ] `./scripts/check-architecture.sh` passe

## En cas de doute

1. Consulter le module `auth/` comme reference
2. Lire les ADRs dans `docs/architecture/ADR/`
3. Lancer `./scripts/check-architecture.sh`
