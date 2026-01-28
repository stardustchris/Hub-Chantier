"""Configuration OpenAPI enrichie pour documentation API."""

from fastapi import FastAPI
from typing import Dict, Any


def configure_openapi(app: FastAPI) -> None:
    """
    Configure OpenAPI avec métadonnées enrichies.

    Args:
        app: Instance FastAPI
    """

    app.title = "Hub Chantier API"
    app.version = "1.0.0"
    app.description = """
# Hub Chantier API

API REST pour la gestion de chantiers BTP.

## Authentification

Hub Chantier supporte deux méthodes d'authentification :

### 1. API Key (Recommandé pour intégrations)

Créez une clé API depuis l'interface web (Paramètres > Clés API).

```bash
curl -H "Authorization: Bearer hbc_your_api_key_here" \\
     https://api.hub-chantier.fr/v1/chantiers
```

### 2. JWT (Frontend uniquement)

Obtenez un token via POST /v1/auth/login.

```bash
curl -X POST https://api.hub-chantier.fr/v1/auth/login \\
     -H "Content-Type: application/json" \\
     -d '{"email": "user@example.com", "password": "***"}'
```

## Rate Limiting

- **API Key** : 1000 requêtes/heure (configurable)
- **JWT** : 100 requêtes/minute

Les headers de réponse indiquent vos limites :

- `X-RateLimit-Limit` : Limite totale
- `X-RateLimit-Remaining` : Requêtes restantes
- `X-RateLimit-Reset` : Timestamp de reset

## Webhooks

Recevez des notifications temps réel sur les événements (chantiers créés, heures validées, etc.).

Voir la section **Webhooks** pour configurer.

## Pagination

Les listes sont paginées avec `limit` et `offset` :

```bash
GET /v1/chantiers?limit=20&offset=0
```

Response headers :

- `X-Total-Count` : Total d'items
- `X-Page-Limit` : Items par page
- `X-Page-Offset` : Offset actuel

## Erreurs

Toutes les erreurs retournent un JSON structuré :

```json
{
  "detail": "Description de l'erreur",
  "error_code": "VALIDATION_ERROR",
  "field": "email"
}
```

Codes HTTP standards :

- **400** : Requête invalide
- **401** : Non authentifié
- **403** : Non autorisé
- **404** : Ressource non trouvée
- **422** : Validation échouée
- **429** : Rate limit dépassé
- **500** : Erreur serveur

## Support

- **Email** : support@hub-chantier.fr
- **Documentation** : https://docs.hub-chantier.fr
- **Status** : https://status.hub-chantier.fr

## SDK Officiels

- **Python** : `pip install hub-chantier`
- **JavaScript** : `npm install @hub-chantier/sdk`

Voir guides SDK pour démarrer.
"""

    app.contact = {
        "name": "Hub Chantier Support",
        "email": "support@hub-chantier.fr",
        "url": "https://hub-chantier.fr"
    }

    app.license_info = {
        "name": "Proprietary",
        "url": "https://hub-chantier.fr/legal/terms"
    }

    # Serveurs
    app.servers = [
        {
            "url": "https://api.hub-chantier.fr",
            "description": "Production"
        },
        {
            "url": "https://sandbox.hub-chantier.fr",
            "description": "Sandbox (test)"
        },
        {
            "url": "http://localhost:8000",
            "description": "Développement local"
        }
    ]

    # Tags avec descriptions
    app.openapi_tags = [
        {
            "name": "Auth",
            "description": "Authentification et gestion des clés API"
        },
        {
            "name": "Chantiers",
            "description": "Gestion des chantiers de construction"
        },
        {
            "name": "Planning",
            "description": "Affectations et planning opérationnel"
        },
        {
            "name": "Feuilles Heures",
            "description": "Saisie et validation des heures travaillées"
        },
        {
            "name": "Documents",
            "description": "Gestion documentaire (GED)"
        },
        {
            "name": "Signalements",
            "description": "Remontée de problèmes et non-conformités"
        },
        {
            "name": "Webhooks",
            "description": "Notifications temps réel sur événements"
        }
    ]


def get_custom_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """
    Génère schéma OpenAPI personnalisé avec exemples enrichis.

    Args:
        app: Instance FastAPI

    Returns:
        Schéma OpenAPI complet
    """
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        servers=app.servers,
        tags=app.openapi_tags
    )

    # Ajouter exemples de sécurité
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "API Key",
            "description": "Clé API (format: `hbc_...`). Créez-en une depuis Paramètres > Clés API."
        },
        "JWTAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Token JWT obtenu via POST /v1/auth/login"
        }
    }

    # Ajouter exemples de réponses d'erreur globaux
    openapi_schema["components"]["responses"] = {
        "Unauthorized": {
            "description": "Non authentifié (API Key ou JWT invalide)",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string"}
                        }
                    },
                    "example": {"detail": "Invalid or expired API key"}
                }
            }
        },
        "Forbidden": {
            "description": "Non autorisé (permissions insuffisantes)",
            "content": {
                "application/json": {
                    "example": {"detail": "You don't have permission to access this resource"}
                }
            }
        },
        "NotFound": {
            "description": "Ressource non trouvée",
            "content": {
                "application/json": {
                    "example": {"detail": "Chantier with ID 999 not found"}
                }
            }
        },
        "RateLimitExceeded": {
            "description": "Rate limit dépassé",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Rate limit exceeded",
                        "limit": 1000,
                        "reset_at": "2026-01-29T15:00:00Z"
                    }
                }
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema
