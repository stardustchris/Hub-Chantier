# ADR 002: FastAPI pour le Backend

## Statut
**Accepté** - 21 janvier 2026

## Contexte

Le backend Hub Chantier nécessite :
- API REST pour le frontend React
- Authentification JWT
- Validation des données
- Documentation automatique
- Performance pour une utilisation terrain (mobile)

## Décision

Nous utilisons **FastAPI** comme framework backend.

### Version
- FastAPI 0.109+
- Python 3.11+

### Stack associée
- **ORM** : SQLAlchemy 2.0+
- **Validation** : Pydantic 2.5+
- **Auth** : python-jose (JWT)
- **Tests** : pytest + pytest-asyncio
- **Server** : Uvicorn

## Conséquences

### Positives
- **Performance** : Async natif, très rapide
- **Documentation** : OpenAPI/Swagger automatique
- **Validation** : Pydantic intégré, type hints
- **Écosystème** : Compatible avec l'existant Python
- **DX** : Reload automatique, messages d'erreur clairs

### Négatives
- **Maturité** : Plus jeune que Django/Flask
- **Async** : Peut complexifier certains patterns

### Intégration Clean Architecture

FastAPI reste dans la couche **Infrastructure** :
- Les routes sont dans `infrastructure/web/`
- Les modèles Pydantic pour la validation HTTP sont séparés des DTOs
- Les Use Cases ne connaissent pas FastAPI

```python
# infrastructure/web/auth_routes.py
from fastapi import APIRouter, Depends
from ..adapters.controllers import AuthController

router = APIRouter()

@router.post("/login")
def login(request: LoginRequest, controller: AuthController = Depends()):
    return controller.login(request.email, request.password)
```

## Alternatives considérées

1. **Django** - Rejeté car trop monolithique, impose son ORM
2. **Flask** - Rejeté car moins de features natives (validation, docs)
3. **Node.js/Express** - Rejeté car équipe Python existante

## Références

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic v2](https://docs.pydantic.dev/)
