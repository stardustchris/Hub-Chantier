# Clean Architecture - Guide Hub Chantier

## Introduction

Ce document décrit l'application de **Clean Architecture** (Robert C. Martin, "Uncle Bob") au projet Hub Chantier.

Clean Architecture vise à créer des systèmes :
- **Indépendants des frameworks** - Le framework est un outil, pas une contrainte
- **Testables** - La logique métier peut être testée sans UI, DB, serveur
- **Indépendants de l'UI** - L'UI peut changer sans impacter le reste
- **Indépendants de la base de données** - On peut changer de DB facilement
- **Indépendants des services externes** - Les règles métier ignorent le monde extérieur

## Les 4 Layers

```
┌───────────────────────────────────────────────────────────────────┐
│                        INFRASTRUCTURE                              │
│  Frameworks, Drivers, DB, Web, External APIs                      │
│                                                                    │
│    ┌───────────────────────────────────────────────────────────┐  │
│    │                       ADAPTERS                             │  │
│    │  Controllers, Gateways, Presenters                        │  │
│    │                                                            │  │
│    │    ┌───────────────────────────────────────────────────┐  │  │
│    │    │                  APPLICATION                       │  │  │
│    │    │  Use Cases, Application Services                  │  │  │
│    │    │                                                    │  │  │
│    │    │    ┌───────────────────────────────────────────┐  │  │  │
│    │    │    │               DOMAIN                       │  │  │  │
│    │    │    │  Entities, Value Objects, Domain Services │  │  │  │
│    │    │    │  Repository Interfaces, Domain Events     │  │  │  │
│    │    │    └───────────────────────────────────────────┘  │  │  │
│    │    └───────────────────────────────────────────────────┘  │  │
│    └───────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

### Layer 1 : Domain (Centre)

**Le coeur du système.** Contient la logique métier pure.

| Composant | Description | Exemple |
|-----------|-------------|---------|
| **Entities** | Objets avec identité unique | `User`, `Pointage`, `Chantier` |
| **Value Objects** | Objets immuables, égalité par valeur | `Email`, `Adresse`, `Coordonnees` |
| **Repository Interfaces** | Abstractions pour la persistence | `UserRepository` (interface) |
| **Domain Events** | Événements métier | `UserCreatedEvent`, `PointageValideEvent` |
| **Domain Services** | Logique métier transverse | `PasswordHashingService` |

**Règle absolue** : AUCUNE dépendance vers les couches externes.

```python
# ✅ CORRECT - Entité domain pure
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Pointage:
    id: Optional[int]
    employe_id: int
    chantier_id: int
    type: str  # ENTREE ou SORTIE
    timestamp: datetime

    def est_entree(self) -> bool:
        return self.type == "ENTREE"
```

### Layer 2 : Application

**Orchestration.** Contient les cas d'utilisation.

| Composant | Description | Exemple |
|-----------|-------------|---------|
| **Use Cases** | Logique applicative | `LoginUseCase`, `PointerEntreeUseCase` |
| **DTOs** | Objets de transfert | `UserDTO`, `PointageDTO` |
| **Ports** | Interfaces pour services externes | `TokenService`, `NotificationService` |

```python
# ✅ CORRECT - Use Case
from ...domain.repositories import UserRepository
from ...domain.entities import User
from ..dtos import LoginDTO, TokenDTO

class LoginUseCase:
    """Cas d'utilisation : Authentification utilisateur."""

    def __init__(self, user_repo: UserRepository, token_service: TokenService):
        self.user_repo = user_repo
        self.token_service = token_service

    def execute(self, dto: LoginDTO) -> TokenDTO:
        user = self.user_repo.find_by_email(dto.email)
        if not user or not user.verify_password(dto.password):
            raise InvalidCredentialsError()

        token = self.token_service.generate(user)
        return TokenDTO(access_token=token, token_type="bearer")
```

### Layer 3 : Adapters

**Conversion.** Adapte les données entre les couches.

| Composant | Description | Exemple |
|-----------|-------------|---------|
| **Controllers** | Gestion des requêtes entrantes | `AuthController` |
| **Presenters** | Formatage des réponses | `UserPresenter` |
| **Providers** | Implémentation des Ports | `JWTTokenService` |

```python
# ✅ CORRECT - Controller
from ..application.use_cases import LoginUseCase
from ..application.dtos import LoginDTO

class AuthController:
    def __init__(self, login_use_case: LoginUseCase):
        self.login_use_case = login_use_case

    def login(self, email: str, password: str) -> dict:
        dto = LoginDTO(email=email, password=password)
        result = self.login_use_case.execute(dto)
        return {"access_token": result.access_token, "token_type": result.token_type}
```

### Layer 4 : Infrastructure

**Détails techniques.** Frameworks, DB, APIs externes.

| Composant | Description | Exemple |
|-----------|-------------|---------|
| **Persistence** | Implémentation des repositories | `SQLAlchemyUserRepository` |
| **Web** | Routes, middleware | `auth_routes.py` |
| **External** | APIs tierces | `SMSNotificationService` |

```python
# ✅ CORRECT - Repository Implementation
from sqlalchemy.orm import Session
from ...domain.repositories import UserRepository
from ...domain.entities import User
from .models import UserModel

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_email(self, email: str) -> Optional[User]:
        model = self.session.query(UserModel).filter_by(email=email).first()
        return self._to_entity(model) if model else None

    def save(self, user: User) -> User:
        model = self._to_model(user)
        self.session.add(model)
        self.session.commit()
        return self._to_entity(model)
```

## La Règle de Dépendance

> **Les dépendances du code source ne doivent pointer que vers l'intérieur.**

```
Infrastructure  →  Adapters  →  Application  →  Domain
     │                │              │             │
     ▼                ▼              ▼             ▼
  Dépend de       Dépend de      Dépend de     AUCUNE
  Adapters +      Application +  Domain        dépendance
  Application +   Domain                       externe
  Domain
```

### Ce qui est INTERDIT

```python
# ❌ Domain qui dépend de l'infrastructure
# modules/auth/domain/entities/user.py
from sqlalchemy import Column, Integer, String  # INTERDIT !

# ❌ Application qui dépend de l'infrastructure
# modules/auth/application/use_cases/login.py
from infrastructure.persistence import SQLAlchemyUserRepository  # INTERDIT !

# ❌ Domain qui dépend d'un framework
# modules/auth/domain/entities/user.py
from pydantic import BaseModel  # INTERDIT !
from fastapi import HTTPException  # INTERDIT !
```

### Ce qui est CORRECT

```python
# ✅ Domain PURE
# modules/auth/domain/entities/user.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    email: str
    created_at: datetime

# ✅ Application dépend d'interfaces (pas d'implémentations)
# modules/auth/application/use_cases/login.py
from ...domain.repositories import UserRepository  # Interface abstraite

class LoginUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo  # Injection de dépendance
```

## Inversion de Dépendance

Le Domain définit des **interfaces** (abstractions), l'Infrastructure les **implémente**.

```python
# 1. Domain définit l'interface
# modules/auth/domain/repositories/user_repository.py
from abc import ABC, abstractmethod
from ..entities import User

class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: int) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass

# 2. Infrastructure implémente
# modules/auth/infrastructure/persistence/sqlalchemy_user_repository.py
from ...domain.repositories import UserRepository
from ...domain.entities import User

class SQLAlchemyUserRepository(UserRepository):
    def find_by_id(self, id: int) -> Optional[User]:
        # Implémentation avec SQLAlchemy
        pass

    def save(self, user: User) -> User:
        # Implémentation avec SQLAlchemy
        pass
```

## Communication Inter-Modules

**JAMAIS d'import direct entre modules.** Utiliser les **Domain Events**.

```python
# ❌ INTERDIT - Couplage direct
from modules.employes.application.use_cases import GetEmployeUseCase

# ✅ CORRECT - Via EventBus
# 1. Publier un event
from shared.infrastructure.event_bus import EventBus
from modules.employes.domain.events import EmployeCreeEvent

EventBus.publish(EmployeCreeEvent(employe_id=123, nom="Dupont"))

# 2. S'abonner
def on_employe_cree(event: EmployeCreeEvent):
    # Réagir à l'événement
    pass

EventBus.subscribe(EmployeCreeEvent, on_employe_cree)
```

## Testing

### Tests Unitaires (Obligatoires)

Testent les Use Cases avec des mocks.

```python
# tests/unit/auth/test_login.py
from unittest.mock import Mock
from modules.auth.application.use_cases import LoginUseCase
from modules.auth.domain.repositories import UserRepository
from modules.auth.domain.entities import User

def test_login_success():
    # Arrange
    mock_repo = Mock(spec=UserRepository)
    mock_repo.find_by_email.return_value = User(
        id=1, email="test@test.com", password_hash="..."
    )

    mock_token_service = Mock()
    mock_token_service.generate.return_value = "jwt-token"

    use_case = LoginUseCase(mock_repo, mock_token_service)

    # Act
    result = use_case.execute(LoginDTO(email="test@test.com", password="pass"))

    # Assert
    assert result.access_token == "jwt-token"
    mock_repo.find_by_email.assert_called_once_with("test@test.com")
```

### Tests d'Intégration

Testent l'ensemble avec vraie DB (SQLite en mémoire).

```python
# tests/integration/auth/test_auth_routes.py
from fastapi.testclient import TestClient

def test_login_endpoint(client: TestClient, test_user):
    response = client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()
```

## Avantages

1. **Testabilité** - Le domain peut être testé sans DB ni framework
2. **Maintenabilité** - Changements isolés dans leur layer
3. **Flexibilité** - Facile de changer de framework ou de DB
4. **Compréhension** - Structure claire et prévisible
5. **Indépendance** - L'équipe peut travailler en parallèle sur différentes couches

## Références

- Robert C. Martin, "Clean Architecture" (2017)
- [The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Clean Architecture avec Python](https://www.cosmicpython.com/)
