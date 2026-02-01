# Résolution Finding HIGH: Rate Limiting sur /login

**Date**: 2026-02-01
**Statut**: ✅ **RÉSOLU** (Fausse alerte)
**Severity**: HIGH → **N/A**

## Finding Original

```json
{
  "severity": "HIGH",
  "message": "Endpoint de login sans rate limiting",
  "file": "backend/modules/auth/infrastructure/web/dependencies.py",
  "suggestion": "Implémenter rate limiting (slowapi ou similar)",
  "category": "security"
}
```

## Analyse

Le finding pointe vers `dependencies.py`, mais ce fichier ne contient QUE des dépendances FastAPI (use cases, repositories, etc.). L'endpoint `/login` réel se trouve dans `auth_routes.py`.

## Vérification de l'implémentation

### 1. Rate Limiting slowapi (Couche 1)

**Fichier**: `backend/modules/auth/infrastructure/web/auth_routes.py`
**Ligne**: 180-181

```python
@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")  # Protection brute force: 10 tentatives/minute par IP
def login(
    request: Request,  # Requis par slowapi
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    controller: AuthController = Depends(get_auth_controller),
):
```

✅ **Limite**: 10 requêtes par minute par IP
✅ **Outil**: slowapi (industry standard)
✅ **Configuration**: `backend/main.py` lignes 71-72

```python
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### 2. RateLimitMiddleware avec Backoff Exponentiel (Couche 2)

**Fichier**: `backend/shared/infrastructure/web/rate_limit_middleware.py`
**Ligne**: 136-144

```python
def _is_sensitive_endpoint(self, path: str) -> bool:
    sensitive_prefixes = [
        "/api/auth/login",    # ← Login protégé
        "/api/auth/register",
        "/api/auth/refresh",
        "/api/upload",
        "/api/documents/upload",
    ]
    return any(path.startswith(prefix) for prefix in sensitive_prefixes)
```

✅ **Backoff**: 30s → 60s → 120s → 240s → 300s max après échecs répétés
✅ **Reset**: Automatique après 1h sans violation
✅ **Headers**: Retry-After sur réponses 429
✅ **Configuration**: `backend/main.py` ligne 90

```python
app.add_middleware(RateLimitMiddleware)
```

## Protection Complète

L'endpoint `/api/auth/login` bénéficie de **deux couches de protection** complémentaires :

| Couche | Mécanisme | Limite | Réponse |
|--------|-----------|--------|---------|
| 1 | slowapi | 10 req/min par IP | 429 immédiat |
| 2 | RateLimitMiddleware | Backoff exponentiel | 429 avec Retry-After |

### Scénario d'attaque par brute force

1. **0-10 tentatives** (1 minute) : Autorisées
2. **11e tentative** : 429 "Too Many Requests" (slowapi)
3. **Après 1 min** : Nouvelles tentatives autorisées
4. **Échecs répétés** : Backoff progressif (30s, 60s, 120s, 240s, 300s max)
5. **Après 1h sans violation** : Reset complet

## Conclusion

**Le finding est une FAUSSE ALERTE**. L'endpoint `/login` est correctement protégé par:

1. ✅ Rate limiting par IP (10/min)
2. ✅ Backoff exponentiel progressif
3. ✅ Headers standards (Retry-After)
4. ✅ Protection X-Forwarded-For spoofing
5. ✅ Configuration middleware globale

**Recommandation**: Mettre à jour le scanner security-auditor pour vérifier les endpoints dans `auth_routes.py` et non uniquement `dependencies.py`.

---

**Validé par**: Claude Sonnet 4.5
**Date de résolution**: 2026-02-01 01:15 UTC
