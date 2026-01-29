# Prompt Phase 4-5-6-7 : Performance, Sécurité, Marketplace & Avancé

> **Objectif** : Implémenter les phases finales de l'API publique Hub Chantier avec performance optimale, sécurité renforcée, intégrations tierces et fonctionnalités avancées.

---

## CONTEXTE

**État actuel** (après Phases 1-3) :
- ✅ API REST complète (v1) avec authentification API Keys
- ✅ Système de Webhooks + Event Bus
- ✅ Documentation OpenAPI enrichie
- ✅ SDKs Python + JavaScript/TypeScript officiels
- ✅ Site documentation Swagger UI

**Ce qui reste à faire** :
- Phase 4 : Performance & Scalabilité
- Phase 5 : Sécurité & Conformité renforcée
- Phase 6 : Marketplace & Intégrations tierces
- Phase 7 : Fonctionnalités avancées (GraphQL, Batch, API v2)

---

## INSTRUCTIONS OBLIGATOIRES

### 1. Workflow agents (7 agents - `.claude/agents.md`)

**POUR CHAQUE FEATURE** :
```
1. [SPECS] Lire docs/SPECIFICATIONS.md pour contexte
2. [sql-pro] Concevoir schema DB (si nouvelles tables)
   → Task(subagent_type="sql-pro", prompt="...")
3. [python-pro] Implementer selon Clean Architecture
   → Task(subagent_type="python-pro", prompt="...")
4. [architect-reviewer] VALIDER conformite architecture
   → Task(subagent_type="architect-reviewer", prompt="...")
5. [test-automator] Generer tests unitaires (>85% couverture)
   → Task(subagent_type="test-automator", prompt="...")
6. [code-reviewer] VALIDER qualite code
   → Task(subagent_type="code-reviewer", prompt="...")
7. [security-auditor] VALIDER securite + RGPD
   → Task(subagent_type="security-auditor", prompt="...")
8. [SPECS] Mettre a jour SPECIFICATIONS.md (API-XX: ✅)
```

### 2. Règles critiques

- ❌ **0 breaking change** sur API v1 existante
- ✅ **Clean Architecture** stricte (Domain → Application → Adapters → Infrastructure)
- ✅ **Tests unitaires obligatoires** (>85% couverture)
- ✅ **Security audit PASS** avant commit (0 finding critique/haute)
- ✅ **Backward compatibility** totale

---

## PHASE 4 : PERFORMANCE & SCALABILITÉ

### Objectifs
- Pagination cursor-based pour gros volumes
- Field selection (sparse fieldsets)
- Cache Redis sur endpoints lourds
- ETags pour cache côté client
- Rate limiting avancé (par endpoint)
- Monitoring Prometheus/Grafana

---

### Feature 4.1 : Pagination Cursor-Based

**Contexte** : Remplacer pagination offset/limit (inefficace sur gros volumes) par cursors.

**Spécifications** :
```python
# Exemple endpoint paginé
GET /api/v1/chantiers?cursor=eyJpZCI6MTIzfQ==&limit=50

Response:
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTczfQ==",
    "prev_cursor": "eyJpZCI6NzN9",
    "has_more": true
  }
}
```

**Cursors encodés en Base64** contenant dernière valeur d'index (ex: `{"id": 123, "created_at": "2026-01-15T10:00:00Z"}`).

**Prompt sql-pro** :
```
Task(subagent_type="sql-pro", prompt="""
Analyse les index actuels sur les tables principales (chantiers, pointages, documents, signalements).

Pour la pagination cursor-based, vérifie que ces tables ont :
- Index sur (id, created_at) pour tri par date
- Index sur (id, updated_at) pour tri par mise à jour
- Index couvrants si colonnes supplémentaires utilisées dans WHERE

Si index manquants, génère les migrations Alembic.

Objectif : requêtes paginées < 50ms même sur 100k+ enregistrements.
""")
```

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente la pagination cursor-based pour l'API publique v1.

1. Crée shared/application/pagination/cursor_pagination.py :
   - Classe CursorPagination avec encode_cursor/decode_cursor (Base64)
   - Fonction paginate_query(query, cursor, limit, order_by)
   - DTOs CursorPaginatedResponse

2. Crée shared/adapters/cursor_utils.py :
   - Helper parse_cursor() avec validation
   - Helper build_pagination_links()

3. Modifie les endpoints API publique existants :
   - GET /api/v1/chantiers
   - GET /api/v1/pointages
   - GET /api/v1/documents
   - GET /api/v1/signalements

   Ajoute paramètre ?cursor=xxx&limit=50 (optionnel, backward compatible).

4. Ajoute tests unitaires tests/unit/shared/test_cursor_pagination.py :
   - encode/decode cursor
   - pagination avec cursors valides/invalides
   - limites (min=1, max=100)

**IMPORTANT** : Garde pagination offset/limit existante par défaut (backward compatibility).
Si ?cursor fourni, utiliser cursor-based, sinon offset/limit.

Architecture : Application layer (Use Cases inchangés), adaptateurs dans Adapters.
""")
```

**Prompt architect-reviewer** :
```
Task(subagent_type="architect-reviewer", prompt="""
Vérifie la conformité Clean Architecture de la pagination cursor-based :

Checklist :
□ cursor_pagination.py dans shared/application (pas d'import framework)
□ cursor_utils.py dans shared/adapters (peut importer FastAPI)
□ Use Cases existants INCHANGÉS (pagination dans Adapters uniquement)
□ Aucun import direct SQLAlchemy dans Application layer
□ DTOs immutables (dataclass frozen=True)

Rapport : PASS ou liste des violations avec corrections.
""")
```

**Prompt test-automator** :
```
Task(subagent_type="test-automator", prompt="""
Génère tests unitaires pour cursor pagination :

tests/unit/shared/test_cursor_pagination.py :
- test_encode_decode_cursor() : aller-retour Base64
- test_paginate_query_first_page() : cursor=None, retourne next_cursor
- test_paginate_query_middle_page() : cursor valide, retourne prev+next
- test_paginate_query_last_page() : has_more=False
- test_invalid_cursor() : cursor malformé → 400 Bad Request
- test_limit_bounds() : limit=0 ou 101 → validation error

tests/integration/api/test_cursor_pagination_api.py :
- test_chantiers_cursor_pagination() : GET /api/v1/chantiers?cursor=xxx
- test_backward_compatibility() : GET /api/v1/chantiers?page=2&limit=20 (ancien)

Couverture cible : >90%
""")
```

**Prompt code-reviewer** :
```
Task(subagent_type="code-reviewer", prompt="""
Revue code pagination cursor-based :

Checklist :
□ Type hints sur toutes signatures
□ Docstrings Google style
□ Gestion erreurs cursor invalide (try/except + log)
□ Pas de secrets en clair dans cursors (juste IDs publics)
□ Validation Pydantic sur limite (1-100)
□ Pas de code dupliqué (DRY)

Rapport : APPROVED ou liste corrections.
""")
```

**Prompt security-auditor** :
```
Task(subagent_type="security-auditor", prompt="""
Audit sécurité pagination cursor-based :

Checklist :
□ Cursors ne contiennent AUCUNE donnée sensible (juste IDs/dates)
□ Validation Base64 decode avec try/except (pas de crash)
□ Rate limiting appliqué aux endpoints paginés
□ Aucun risque énumération IDs (cursors opaques)
□ Logs ne contiennent pas contenu cursors (RGPD)

Findings critiques/hautes → BLOCKER avant commit.
""")
```

---

### Feature 4.2 : Field Selection (Sparse Fieldsets)

**Contexte** : Permettre aux clients de demander uniquement les champs nécessaires.

**Exemple** :
```
GET /api/v1/chantiers?fields=id,nom,adresse
→ Retourne uniquement {id, nom, adresse}, pas les 20 champs complets
```

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente field selection (sparse fieldsets) pour API v1.

1. Crée shared/adapters/field_selector.py :
   - Fonction select_fields(obj: dict, fields: List[str]) -> dict
   - Validation champs demandés (whitelist par entité)
   - Gestion nested fields (ex: chantier.responsable.nom)

2. Crée middleware FastAPI FieldSelectionMiddleware :
   - Parse ?fields=id,nom,adresse
   - Applique filtrage sur response JSON avant envoi

3. Ajoute dans shared/domain/field_whitelist.py :
   - CHANTIER_FIELDS = ["id", "nom", "adresse", ...]
   - POINTAGE_FIELDS = [...]
   - Dictionnaire par entité

4. Tests unitaires tests/unit/shared/test_field_selector.py :
   - test_select_valid_fields() : fields=id,nom
   - test_select_all_fields() : fields=* (tous)
   - test_invalid_field() : field inexistant → 400
   - test_nested_fields() : chantier.responsable.nom

Architecture : Middleware dans Adapters, validation Domain.
""")
```

**Prompt security-auditor** :
```
Task(subagent_type="security-auditor", prompt="""
Audit field selection :

Checklist :
□ Whitelist stricte des champs exposables (pas de champs internes)
□ Pas d'accès à champs sensibles (password_hash, api_key_hash, etc.)
□ Validation avec regex sur noms champs (alphanumeric + underscore)
□ Pas de field injection SQL possible
□ Rate limiting sur fields=* (éviter abus)

Rapport findings.
""")
```

---

### Feature 4.3 : Cache Redis

**Contexte** : Mettre en cache les réponses endpoints lourds (ex: statistiques, listes chantiers).

**TTL** : 5 min pour listes, 1 min pour stats temps réel.

**Prompt sql-pro** :
```
Task(subagent_type="sql-pro", prompt="""
Pas de modifications DB requises pour Redis.

Vérifie que les requêtes à cacher sont optimisées :
- SELECT avec LIMIT (pas de full table scan)
- Index sur colonnes WHERE/ORDER BY
- EXPLAIN ANALYZE sur requêtes candidates

Liste les 5 requêtes les plus lentes (>200ms) à cibler pour cache.
""")
```

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente cache Redis pour API publique.

1. Ajoute dans backend/requirements.txt :
   - redis==5.0.1
   - aioredis==2.0.1 (si async)

2. Crée shared/infrastructure/cache/redis_cache.py :
   - Classe RedisCache avec get/set/delete
   - Méthode cache_key(endpoint, params) → "api:v1:chantiers:page=1:limit=20"
   - TTL configurable par type (CACHE_TTL_LISTS=300, CACHE_TTL_STATS=60)

3. Crée decorator @cached_response(ttl=300) :
   - Vérifie cache avant exécution
   - Si hit → retour immédiat
   - Si miss → exécute + stocke résultat

4. Applique sur endpoints :
   - GET /api/v1/chantiers (TTL=300s)
   - GET /api/v1/stats (TTL=60s)
   - GET /api/v1/planning (TTL=120s)

5. Ajoute invalidation cache sur mutations :
   - POST/PUT/DELETE chantier → redis.delete("api:v1:chantiers:*")
   - Pattern pub/sub Redis si nécessaire

6. Configuration dans backend/.env.production :
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=1
   REDIS_PASSWORD=...

7. Tests tests/unit/shared/test_redis_cache.py :
   - test_cache_hit()
   - test_cache_miss()
   - test_cache_invalidation()

Docker : Ajoute service redis dans docker-compose.prod.yml.
""")
```

**Prompt code-reviewer** :
```
Task(subagent_type="code-reviewer", prompt="""
Revue cache Redis :

Checklist :
□ Gestion erreurs connexion Redis (fallback sans cache)
□ Logs si Redis indisponible (warning, pas error)
□ TTL explicites (pas de valeurs hardcodées)
□ Keys Redis préfixées (api:v1:...) pour éviter collisions
□ Pas de données sensibles en cache (ou chiffrement)
□ Monitoring hits/misses (métriques Prometheus)

Rapport APPROVED ou corrections.
""")
```

**Prompt security-auditor** :
```
Task(subagent_type="security-auditor", prompt="""
Audit Redis cache :

Checklist :
□ Connexion Redis authentifiée (REDIS_PASSWORD requis en prod)
□ Redis sur réseau privé (pas exposé publiquement)
□ Aucune donnée sensible en cache sans chiffrement
□ TTL courts pour données RGPD (éviter rétention excessive)
□ Flush cache lors suppression utilisateur (droit à l'oubli)

Findings critiques → BLOCKER.
""")
```

---

### Feature 4.4 : ETags & Conditional Requests

**Contexte** : Permettre cache côté client avec `If-None-Match`.

**Flow** :
1. Client GET /api/v1/chantiers/123 → Response avec `ETag: "abc123"`
2. Client GET /api/v1/chantiers/123 + `If-None-Match: "abc123"` → 304 Not Modified (si inchangé)

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente ETags pour API v1.

1. Crée shared/adapters/etag_utils.py :
   - generate_etag(data: dict) -> str : hash MD5 du JSON
   - Méthode compare_etag(etag1, etag2) -> bool

2. Crée middleware FastAPI ETagMiddleware :
   - Calcule ETag sur response body
   - Ajoute header ETag: "xxx"
   - Si request contient If-None-Match et match → 304 Not Modified

3. Applique sur endpoints GET :
   - GET /api/v1/chantiers/:id
   - GET /api/v1/documents/:id
   - GET /api/v1/signalements/:id

4. Supporte If-Match pour PUT/DELETE (conditional updates) :
   - PUT /api/v1/chantiers/123 + If-Match: "abc" → 412 Precondition Failed si changé

5. Tests tests/unit/shared/test_etag.py :
   - test_etag_generation()
   - test_304_not_modified()
   - test_412_precondition_failed()

Architecture : Middleware Adapters, aucun changement Use Cases.
""")
```

---

### Feature 4.5 : Rate Limiting Avancé

**Contexte** : Rate limiting par endpoint (ex: POST /chantiers limité à 100/jour, GET /stats à 1000/heure).

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Améliore rate limiting existant avec limites par endpoint.

1. Modifie shared/infrastructure/rate_limiting/rate_limiter.py :
   - Config RATE_LIMITS = {
       "POST:/api/v1/chantiers": "100/day",
       "GET:/api/v1/stats": "1000/hour",
       ...
     }
   - Fonction get_limit(method, path) -> tuple(limit, window)

2. Stockage Redis avec keys :
   - "ratelimit:api_key_abc123:POST:/api/v1/chantiers:2026-01-29"

3. Headers response :
   - X-RateLimit-Limit: 100
   - X-RateLimit-Remaining: 47
   - X-RateLimit-Reset: 1738195200 (timestamp)

4. Tests tests/unit/shared/test_advanced_rate_limiting.py :
   - test_endpoint_specific_limits()
   - test_headers_returned()
   - test_429_with_retry_after()

Architecture : Infrastructure layer.
""")
```

---

### Feature 4.6 : Monitoring Prometheus/Grafana

**Contexte** : Exposer métriques API pour monitoring.

**Métriques** :
- `api_requests_total{method, endpoint, status}`
- `api_request_duration_seconds{method, endpoint}`
- `api_cache_hits_total`
- `api_rate_limit_exceeded_total`

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente monitoring Prometheus pour API.

1. Ajoute dans requirements.txt :
   - prometheus-client==0.19.0
   - prometheus-fastapi-instrumentator==6.1.0

2. Crée shared/infrastructure/monitoring/prometheus_metrics.py :
   - Counters : requests_total, cache_hits, rate_limit_exceeded
   - Histograms : request_duration_seconds
   - Gauges : active_api_keys

3. Expose endpoint GET /metrics (non authentifié, IP whitelist) :
   - Format Prometheus text

4. Middleware MetricsMiddleware :
   - Incrémente compteurs sur chaque requête
   - Track latence

5. Docker : Ajoute services prometheus + grafana dans docker-compose.prod.yml :
   - Prometheus scrape /metrics toutes les 15s
   - Grafana dashboards pré-configurés (API overview, cache stats, rate limiting)

6. Dashboards JSON dans docs/monitoring/ :
   - api_overview_dashboard.json
   - cache_performance_dashboard.json

Tests : Vérifie endpoint /metrics retourne format Prometheus valide.
""")
```

**Prompt security-auditor** :
```
Task(subagent_type="security-auditor", prompt="""
Audit monitoring Prometheus :

Checklist :
□ Endpoint /metrics protégé (IP whitelist ou basic auth)
□ Aucune métrique contenant données sensibles (IDs OK, noms/emails NON)
□ Prometheus accessible uniquement réseau privé
□ Grafana avec authentification forte (HTTPS + strong password)
□ Logs métriques sans PII

Rapport findings.
""")
```

---

## PHASE 5 : SÉCURITÉ & CONFORMITÉ

### Objectifs
- OAuth2 complet (authorization code flow)
- Audit trail exhaustif
- IP whitelisting
- Détection anomalies
- Rotation secrets automatique

---

### Feature 5.1 : OAuth2 Authorization Code Flow

**Contexte** : Ajouter OAuth2 en complément des API Keys (pour apps tierces).

**Flow** :
1. Client redirige vers `/oauth/authorize?client_id=xxx&redirect_uri=xxx`
2. Utilisateur Hub Chantier login + consent
3. Redirect vers `redirect_uri?code=xxx`
4. Client échange code contre token : POST `/oauth/token`
5. Token JWT valide 1h, refresh token valide 30j

**Prompt sql-pro** :
```
Task(subagent_type="sql-pro", prompt="""
Crée schema OAuth2.

Tables :
1. oauth_clients :
   - id (PK)
   - client_id (unique, varchar 64)
   - client_secret_hash (varchar 255)
   - redirect_uris (json array)
   - scopes (json array : ["chantiers:read", "pointages:write", ...])
   - created_at, updated_at

2. oauth_authorization_codes :
   - id (PK)
   - code (unique, varchar 64)
   - client_id (FK oauth_clients)
   - user_id (FK users)
   - scopes (json)
   - redirect_uri (varchar 500)
   - expires_at (timestamp, +10 min)
   - used (boolean default false)
   - created_at

3. oauth_tokens :
   - id (PK)
   - access_token_hash (varchar 255)
   - refresh_token_hash (varchar 255)
   - client_id (FK oauth_clients)
   - user_id (FK users)
   - scopes (json)
   - access_token_expires_at (timestamp, +1h)
   - refresh_token_expires_at (timestamp, +30d)
   - created_at

Index :
- oauth_clients(client_id)
- oauth_authorization_codes(code)
- oauth_tokens(access_token_hash)

Migration Alembic avec révision.
""")
```

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente OAuth2 Authorization Code Flow.

1. Crée module oauth2/ :
   - domain/entities/oauth_client.py
   - domain/entities/authorization_code.py
   - domain/entities/oauth_token.py
   - domain/repositories/ (interfaces)
   - application/use_cases/authorize_client.py
   - application/use_cases/exchange_code_for_token.py
   - application/use_cases/refresh_access_token.py
   - adapters/controllers/oauth_controller.py
   - infrastructure/persistence/ (SQLAlchemy models)
   - infrastructure/web/oauth_routes.py

2. Endpoints :
   - GET /oauth/authorize (UI consent page)
   - POST /oauth/authorize (user approves)
   - POST /oauth/token (code exchange + refresh)
   - POST /oauth/revoke (revoke token)

3. Scopes :
   - chantiers:read, chantiers:write
   - pointages:read, pointages:write
   - documents:read, documents:write
   - signalements:read, signalements:write

4. Tokens JWT avec claims :
   {
     "sub": user_id,
     "client_id": "client_xxx",
     "scopes": ["chantiers:read"],
     "exp": 1738195200
   }

5. Middleware OAuth2Middleware :
   - Parse header Authorization: Bearer <token>
   - Valide JWT + scopes
   - Injecte user + client dans request.state

6. Tests tests/unit/oauth2/ :
   - test_authorize_flow()
   - test_exchange_code()
   - test_refresh_token()
   - test_expired_code()
   - test_invalid_scope()

Architecture : Module séparé oauth2/, Clean Architecture complète.
""")
```

**Prompt architect-reviewer** :
```
Task(subagent_type="architect-reviewer", prompt="""
Vérifie module oauth2/ :

Checklist :
□ Domain entities sans dépendances frameworks
□ Use Cases dépendent d'interfaces (pas SQLAlchemy)
□ Repositories dans domain/repositories/ (interfaces)
□ Implémentations dans infrastructure/persistence/
□ Routes dans infrastructure/web/
□ Aucun import entre modules (oauth2 indépendant)

Rapport PASS ou violations.
""")
```

**Prompt security-auditor** :
```
Task(subagent_type="security-auditor", prompt="""
Audit OAuth2 implementation :

Checklist CRITIQUE :
□ Authorization codes usage unique (flag used=true après échange)
□ Authorization codes TTL 10 min max
□ Codes aléatoires cryptographiques (secrets.token_urlsafe(32))
□ Client secret hashé (bcrypt, jamais en clair)
□ Tokens hashés en DB (SHA-256 min)
□ Refresh tokens rotation (nouveau refresh à chaque usage)
□ Redirect URI validation stricte (whitelist exact match)
□ PKCE supporté (Proof Key for Code Exchange, optionnel mais recommandé)
□ Scopes validation (pas de scope escalation)
□ Rate limiting sur /oauth/token (10 req/min par client)
□ Logs tentatives échecs (audit trail)

Findings critiques/hautes → BLOCKER.
""")
```

---

### Feature 5.2 : Audit Trail Exhaustif

**Contexte** : Logger TOUTES les actions API (qui, quoi, quand, IP, user-agent).

**Prompt sql-pro** :
```
Task(subagent_type="sql-pro", prompt="""
Crée table audit_logs :
- id (PK bigint auto_increment)
- timestamp (timestamp NOT NULL, index)
- user_id (int, FK users, nullable si public)
- api_key_id (int, FK api_keys, nullable)
- oauth_client_id (int, FK oauth_clients, nullable)
- action (varchar 100 : "create_chantier", "update_pointage", ...)
- resource_type (varchar 50 : "chantier", "pointage", ...)
- resource_id (int, nullable)
- http_method (varchar 10 : GET, POST, ...)
- endpoint (varchar 200 : /api/v1/chantiers)
- status_code (int : 200, 404, ...)
- ip_address (inet ou varchar 45)
- user_agent (text)
- request_body_hash (varchar 64 : SHA-256 du body, pas le body complet)
- changes (jsonb : {"before": {...}, "after": {...}})

Index :
- (timestamp DESC)
- (user_id, timestamp DESC)
- (resource_type, resource_id)

Partitionnement par mois (table audit_logs_2026_01, audit_logs_2026_02, ...).

Migration Alembic.
""")
```

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente audit trail.

1. Crée shared/infrastructure/audit/audit_logger.py :
   - Classe AuditLogger avec méthode log(event: AuditEvent)
   - AuditEvent dataclass avec tous champs

2. Middleware AuditMiddleware :
   - Intercepte TOUTES requêtes API
   - Extrait user_id, api_key_id, IP, user-agent
   - Log avant/après (changes pour PUT/DELETE)
   - Stocke en DB via AuditLogger

3. Endpoint admin GET /api/v1/admin/audit-logs :
   - Pagination cursor-based
   - Filtres : user_id, resource_type, date range
   - Réservé rôle admin

4. Rétention : job APScheduler supprime logs > 1 an.

5. Tests tests/unit/shared/test_audit_logger.py :
   - test_log_create_action()
   - test_log_with_changes()
   - test_ip_anonymization() (RGPD : IP tronquée après 30j)

Architecture : shared/infrastructure/audit/.
""")
```

**Prompt security-auditor** :
```
Task(subagent_type="security-auditor", prompt="""
Audit trail security :

Checklist :
□ Logs immuables (append-only, aucun UPDATE/DELETE sauf purge auto)
□ Request body hashé (pas stocké en clair si sensible)
□ Aucun password/token en logs
□ IP anonymisées après 30j (RGPD : 192.168.1.0)
□ Accès logs réservé admin + audit trail sur accès logs (meta-audit)
□ Rotation logs anciens (>1 an) vers archive cold storage

Findings critiques → BLOCKER.
""")
```

---

### Feature 5.3 : IP Whitelisting

**Contexte** : Permettre restriction API keys à IPs spécifiques.

**Prompt sql-pro** :
```
Task(subagent_type="sql-pro", prompt="""
Modifie table api_keys :
- Ajoute colonne ip_whitelist (json array : ["192.168.1.100", "10.0.0.0/24"])

Migration Alembic (colonne nullable, défaut null = pas de restriction).
""")
```

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente IP whitelisting.

1. Modifie shared/domain/entities/api_key.py :
   - Ajoute ip_whitelist: Optional[List[str]]
   - Méthode is_ip_allowed(ip: str) -> bool (supporte CIDR)

2. Modifie APIKeyMiddleware :
   - Extrait IP client (X-Forwarded-For ou request.client.host)
   - Appelle api_key.is_ip_allowed(ip)
   - Si refusé → 403 Forbidden + log audit

3. Endpoint POST /api/v1/admin/api-keys (admin) :
   - Paramètre ip_whitelist: ["1.2.3.4", "10.0.0.0/16"]

4. Tests tests/unit/shared/test_ip_whitelist.py :
   - test_ip_allowed()
   - test_ip_denied()
   - test_cidr_range()

Architecture : Logique Domain (entity), validation Adapters.
""")
```

---

### Feature 5.4 : Détection Anomalies

**Contexte** : Détecter comportements suspects (trop de 404, rate spikes, etc.).

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente détection anomalies.

1. Crée shared/infrastructure/security/anomaly_detector.py :
   - Classe AnomalyDetector
   - Méthode check_anomalies(api_key_id, window="1h") -> List[Anomaly]

   Règles :
   - > 50% requêtes 4xx en 1h → "high_error_rate"
   - > 100 req/min soudainement (vs moyenne) → "traffic_spike"
   - Accès ressources inexistantes répétés → "scanning_behavior"
   - Changement user-agent fréquent → "suspicious_client"

2. Job APScheduler toutes les 5 min :
   - Analyse logs récents
   - Si anomalie → log + notification admin (email/Slack)

3. Endpoint GET /api/v1/admin/anomalies :
   - Liste anomalies détectées 7 derniers jours

4. Tests tests/unit/shared/test_anomaly_detector.py :
   - test_detect_high_error_rate()
   - test_detect_traffic_spike()

Architecture : shared/infrastructure/security/.
""")
```

---

### Feature 5.5 : Rotation Secrets Automatique

**Contexte** : Rotation API key secrets tous les 90j (optionnel, activable par client).

**Prompt sql-pro** :
```
Task(subagent_type="sql-pro", prompt="""
Modifie table api_keys :
- Ajoute colonne auto_rotate (boolean default false)
- Ajoute colonne last_rotated_at (timestamp)
- Ajoute colonne rotation_interval_days (int default 90)

Migration Alembic.
""")
```

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente rotation automatique secrets.

1. Crée application/use_cases/rotate_api_key.py :
   - Use Case RotateAPIKeyUseCase
   - Génère nouveau secret
   - Invalide ancien (grace period 7j : les 2 acceptés)
   - Notifie client par email/webhook

2. Job APScheduler quotidien :
   - Cherche API keys avec auto_rotate=true et last_rotated_at > 90j
   - Appelle RotateAPIKeyUseCase

3. Endpoint POST /api/v1/admin/api-keys/:id/rotate (manuel) :
   - Force rotation immédiate

4. Tests tests/unit/auth/test_rotate_api_key.py :
   - test_rotate_success()
   - test_grace_period()
   - test_notification_sent()

Architecture : Use Case Application layer.
""")
```

---

## PHASE 6 : MARKETPLACE & INTÉGRATIONS

### Objectifs
- Connecteurs ERP : Sage 100, Silae, QuickBooks
- Connecteurs collaboration : Slack, Google Calendar, Dropbox
- Architecture générique pour futurs connecteurs

---

### Feature 6.1 : Architecture Connecteurs

**Contexte** : Système générique plug-and-play pour intégrations tierces.

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Crée architecture connecteurs.

1. Crée module integrations/ :
   - domain/entities/connector.py
   - domain/entities/connector_config.py
   - domain/repositories/connector_repository.py (interface)
   - application/ports/connector_service.py (interface abstraite)
   - application/use_cases/sync_connector.py
   - adapters/controllers/connectors_controller.py
   - infrastructure/connectors/ (implémentations)

2. Entité Connector :
   - id
   - type (enum : SAGE_100, SILAE, QUICKBOOKS, SLACK, CALENDAR, DROPBOX)
   - enabled (bool)
   - config (json : credentials, API keys, options)
   - last_sync_at (timestamp)
   - sync_status (enum : SUCCESS, ERROR, IN_PROGRESS)

3. Interface ConnectorService (application/ports/) :
   ```python
   class ConnectorService(ABC):
       @abstractmethod
       def authenticate(self, config: dict) -> bool:
           pass

       @abstractmethod
       def sync_data(self) -> SyncResult:
           pass

       @abstractmethod
       def send_event(self, event: DomainEvent):
           pass
   ```

4. Table DB connectors :
   - id, user_id (FK users), type (varchar 50), enabled (bool)
   - config (jsonb chiffré), last_sync_at, sync_status, error_message

5. Tests tests/unit/integrations/ :
   - test_connector_lifecycle()

Architecture : Module integrations/ indépendant, Clean Architecture complète.
""")
```

**Prompt sql-pro** :
```
Task(subagent_type="sql-pro", prompt="""
Crée schéma connecteurs.

Tables :
1. connectors :
   - id (PK)
   - user_id (FK users)
   - type (varchar 50 : sage_100, silae, ...)
   - enabled (boolean default true)
   - config (jsonb) -- chiffré avec pgcrypto
   - last_sync_at (timestamp)
   - sync_status (varchar 20 : success, error, in_progress)
   - error_message (text nullable)
   - created_at, updated_at

2. connector_sync_logs :
   - id (PK)
   - connector_id (FK connectors)
   - started_at (timestamp)
   - completed_at (timestamp nullable)
   - status (varchar 20)
   - records_synced (int)
   - error_details (jsonb nullable)

Index :
- connectors(user_id, type)
- connector_sync_logs(connector_id, started_at DESC)

Migration Alembic avec chiffrement pgcrypto (config).
""")
```

**Prompt security-auditor** :
```
Task(subagent_type="security-auditor", prompt="""
Audit architecture connecteurs :

Checklist CRITIQUE :
□ Config connecteurs chiffrée en DB (pgcrypto AES-256)
□ Credentials API tierces JAMAIS en logs
□ Tokens OAuth stockés chiffrés + rotation
□ Rate limiting appels API tierces (respecter limites éditeurs)
□ Timeout connecteurs (max 30s)
□ Retry logic avec backoff exponentiel
□ Isolation erreurs (failure connector X n'affecte pas Y)
□ Audit trail accès config connecteurs (admin only)

Findings critiques → BLOCKER.
""")
```

---

### Feature 6.2 : Connecteur Sage 100

**Contexte** : Synchronisation bidirectionnelle chantiers, clients, factures avec Sage 100.

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente connecteur Sage 100.

1. Crée infrastructure/connectors/sage100_connector.py :
   - Classe Sage100Connector implements ConnectorService
   - Méthodes :
     - authenticate(config) : test connexion API Sage
     - sync_chantiers() : import chantiers depuis Sage → Hub Chantier
     - sync_clients() : import clients/prospects
     - export_factures() : export feuilles heures → factures Sage

2. Config required :
   - api_url (ex: https://sage100.monentreprise.fr/api)
   - api_key (secret)
   - company_id (identifiant dossier Sage)

3. Mapping :
   - Sage "Affaires" → Hub Chantier "Chantiers"
   - Sage "Tiers" → Hub Chantier "Clients"
   - Hub Chantier "FeuilleHeures" → Sage "Factures"

4. Sync job APScheduler quotidien (minuit) :
   - Appelle sync_chantiers() pour tous connecteurs Sage actifs

5. Tests tests/unit/integrations/test_sage100_connector.py :
   - test_authenticate_success()
   - test_sync_chantiers() (mock API Sage)
   - test_export_factures()

Architecture : Infrastructure layer, implémente port ConnectorService.
""")
```

---

### Feature 6.3 : Connecteur Silae (Paie)

**Contexte** : Export feuilles heures vers Silae pour génération bulletins paie.

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente connecteur Silae.

1. Crée infrastructure/connectors/silae_connector.py :
   - Classe SilaeConnector implements ConnectorService
   - Méthodes :
     - export_heures(month, year) : envoie feuilles heures validées du mois
     - format_payload() : format XML Silae (spec éditeur)

2. Config :
   - api_url, api_key, company_code

3. Mapping :
   - Hub Chantier Pointages → Silae Heures Travaillées
   - Type pointage (normal, nuit, weekend) → Codes Silae

4. Job mensuel (1er du mois) :
   - Export mois précédent vers tous connecteurs Silae actifs

5. Tests tests/unit/integrations/test_silae_connector.py :
   - test_format_xml()
   - test_export_heures() (mock API Silae)

Architecture : Infrastructure layer.
""")
```

---

### Feature 6.4 : Connecteur QuickBooks

**Contexte** : Synchronisation factures, dépenses.

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente connecteur QuickBooks.

1. Crée infrastructure/connectors/quickbooks_connector.py :
   - OAuth2 QuickBooks (authorization code flow)
   - Sync invoices : Hub Chantier Factures → QuickBooks Invoices
   - Sync expenses : QuickBooks Expenses → Hub Chantier Dépenses

2. Config :
   - client_id, client_secret, realm_id
   - access_token, refresh_token (stockés chiffrés)

3. Endpoint callback OAuth :
   - GET /api/v1/integrations/quickbooks/callback?code=xxx
   - Échange code → tokens
   - Stocke dans connectors.config

4. Tests tests/unit/integrations/test_quickbooks_connector.py :
   - test_oauth_flow() (mock)
   - test_sync_invoices()

Architecture : Infrastructure layer + OAuth callback route.
""")
```

---

### Feature 6.5 : Connecteur Slack

**Contexte** : Notifications automatiques dans canal Slack (nouveau chantier, signalement urgent, etc.).

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente connecteur Slack.

1. Crée infrastructure/connectors/slack_connector.py :
   - Classe SlackConnector implements ConnectorService
   - Méthode send_message(channel, text, attachments)
   - Méthode send_event(event: DomainEvent) : traduit event → message Slack

2. Config :
   - webhook_url (Incoming Webhook Slack)
   - ou bot_token (si bot Slack)

3. Souscription Event Bus :
   - ChantierCreeEvent → message Slack "Nouveau chantier X créé"
   - SignalementUrgentEvent → "@channel Signalement urgent sur chantier Y"
   - PointageValideeEvent → message stats hebdo

4. Tests tests/unit/integrations/test_slack_connector.py :
   - test_send_message() (mock requests)
   - test_event_to_slack_format()

Architecture : Infrastructure layer, écoute Event Bus.
""")
```

---

### Feature 6.6 : Connecteur Google Calendar

**Contexte** : Synchronisation affectations planning → événements Calendar.

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente connecteur Google Calendar.

1. Crée infrastructure/connectors/google_calendar_connector.py :
   - OAuth2 Google Calendar API
   - Sync affectations : AffectationCreeEvent → create event Calendar
   - Sync bidirectionnel : changements Calendar → update Hub Chantier

2. Config :
   - client_id, client_secret (Google Cloud Console)
   - calendar_id (ID calendrier cible)
   - access_token, refresh_token

3. Endpoint callback OAuth :
   - GET /api/v1/integrations/google-calendar/callback

4. Webhook Google Calendar :
   - Recevoir notifications changements → sync vers Hub Chantier

5. Tests tests/unit/integrations/test_google_calendar_connector.py :
   - test_create_event()
   - test_sync_from_calendar()

Architecture : Infrastructure layer.
""")
```

---

### Feature 6.7 : Connecteur Dropbox

**Contexte** : Sauvegarde automatique documents Hub Chantier → Dropbox.

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente connecteur Dropbox.

1. Crée infrastructure/connectors/dropbox_connector.py :
   - OAuth2 Dropbox
   - Upload documents : DocumentCreeEvent → upload Dropbox
   - Arborescence Dropbox : /Hub-Chantier/{chantier_nom}/{categorie}/
   - Sync bidirectionnel optionnel (import Dropbox → Hub Chantier)

2. Config :
   - app_key, app_secret
   - access_token, refresh_token
   - root_folder (ex: /Hub-Chantier)

3. Endpoint callback OAuth :
   - GET /api/v1/integrations/dropbox/callback

4. Tests tests/unit/integrations/test_dropbox_connector.py :
   - test_upload_document()
   - test_folder_structure()

Architecture : Infrastructure layer.
""")
```

---

## PHASE 7 : FONCTIONNALITÉS AVANCÉES

### Objectifs
- GraphQL API (alternative REST)
- Opérations batch (bulk create/update/delete)
- Versioning API (v2)

---

### Feature 7.1 : GraphQL API

**Contexte** : Offrir alternative GraphQL pour clients préférant requêtes flexibles.

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente GraphQL API.

1. Ajoute dans requirements.txt :
   - strawberry-graphql[fastapi]==0.215.0

2. Crée shared/infrastructure/graphql/ :
   - schema.py : schéma GraphQL (types, queries, mutations)
   - resolvers.py : resolvers mappés sur Use Cases
   - context.py : injection dépendances (repos, services)

3. Types GraphQL :
   ```graphql
   type Chantier {
     id: ID!
     nom: String!
     adresse: String
     statut: StatutChantier!
     responsable: User
   }

   type Query {
     chantiers(limit: Int = 20): [Chantier!]!
     chantier(id: ID!): Chantier
   }

   type Mutation {
     createChantier(input: CreateChantierInput!): Chantier!
   }
   ```

4. Endpoint POST /graphql :
   - Authentification API Key ou OAuth2
   - Rate limiting GraphQL queries (complexité max)

5. GraphQL Playground : GET /graphql (UI exploratoire)

6. Tests tests/unit/graphql/ :
   - test_query_chantiers()
   - test_mutation_create_chantier()
   - test_authentication_required()

Architecture : shared/infrastructure/graphql/, resolvers appellent Use Cases.
""")
```

**Prompt security-auditor** :
```
Task(subagent_type="security-auditor", prompt="""
Audit GraphQL :

Checklist :
□ Query depth limit (max 5 niveaux imbrication)
□ Query complexity limit (éviter queries coûteuses)
□ Rate limiting GraphQL spécifique
□ Pas d'introspection en production (schema caché)
□ Validation input strict (Pydantic sur mutations)
□ Pas de leak informations via error messages

Findings critiques → BLOCKER.
""")
```

---

### Feature 7.2 : Opérations Batch

**Contexte** : Permettre créations/updates/suppressions en masse.

**Exemple** :
```json
POST /api/v1/batch
{
  "operations": [
    {"method": "POST", "path": "/chantiers", "body": {...}},
    {"method": "PUT", "path": "/chantiers/123", "body": {...}},
    {"method": "DELETE", "path": "/chantiers/456"}
  ]
}

Response:
{
  "results": [
    {"status": 201, "body": {...}},
    {"status": 200, "body": {...}},
    {"status": 204, "body": null}
  ]
}
```

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente batch operations.

1. Crée shared/adapters/batch_processor.py :
   - Classe BatchProcessor
   - Méthode process(operations: List[BatchOp]) -> List[BatchResult]
   - Limite 100 opérations par batch
   - Exécution transactionnelle (rollback si une échoue) OU atomique (best-effort)

2. Endpoint POST /api/v1/batch :
   - Parse operations
   - Appelle BatchProcessor
   - Retourne résultats avec statuts individuels

3. Options :
   - atomic: true (rollback si échec) vs false (continue)
   - parallel: true (exécution parallèle si indépendant) vs false (séquentiel)

4. Tests tests/unit/shared/test_batch_processor.py :
   - test_batch_success()
   - test_partial_failure_atomic()
   - test_parallel_execution()

Architecture : Adapters layer.
""")
```

**Prompt security-auditor** :
```
Task(subagent_type="security-auditor", prompt="""
Audit batch operations :

Checklist :
□ Limite 100 ops par batch (éviter DoS)
□ Rate limiting sur /batch (10 req/min max)
□ Validation chaque operation (méthode, path, body)
□ Timeout global batch (max 60s)
□ Audit trail chaque op individuelle
□ Pas de bypass permissions (check authorization par op)

Findings critiques → BLOCKER.
""")
```

---

### Feature 7.3 : API v2 (Versioning)

**Contexte** : Préparer évolutions futures sans casser v1.

**Prompt python-pro** :
```
Task(subagent_type="python-pro", prompt="""
Implémente versioning API v2.

1. Crée infrastructure/web/api_v2_routes.py :
   - Routes préfixées /api/v2/
   - DTOs v2 (changements : snake_case → camelCase, champs renommés)

2. Exemple changement v2 :
   - v1 : GET /api/v1/chantiers → {nom, adresse}
   - v2 : GET /api/v2/chantiers → {name, location} (renommage)

3. Middleware APIVersionMiddleware :
   - Détecte version via URL (/api/v1/ ou /api/v2/)
   - Injecte version dans request.state

4. Use Cases partagés :
   - Même Use Cases pour v1 et v2
   - Adaptateurs différents (DTOs v1 vs v2)

5. Deprecation v1 :
   - Header X-API-Deprecation: "v1 deprecated, migrate to v2"
   - Sunset header : Sunset: Sat, 31 Dec 2026 23:59:59 GMT

6. Tests tests/integration/api/test_v2_endpoints.py :
   - test_v2_chantiers()
   - test_backward_compatibility_v1()

Architecture : Routes séparées, Use Cases partagés, DTOs distincts.
""")
```

---

## VALIDATION FINALE (TOUTES PHASES)

### Checklist Globale

**Après implémentation de TOUTES les features** :

```
Task(subagent_type="architect-reviewer", prompt="""
Audit global architecture API publique (Phases 4-7) :

Checklist :
□ Aucun module ne viole Clean Architecture
□ Tous nouveaux modules suivent structure domain/application/adapters/infrastructure
□ Aucun import inter-modules direct (sauf EntityInfoService/Event Bus)
□ Repositories implémentés dans infrastructure, interfaces dans domain
□ Use Cases testables sans DB (mocks)

Rapport PASS ou liste violations avec fichiers concernés.
""")
```

```
Task(subagent_type="test-automator", prompt="""
Audit couverture tests API publique (Phases 4-7) :

Génère tests manquants pour atteindre >85% couverture sur :
- shared/application/pagination/
- shared/infrastructure/cache/
- modules/oauth2/
- modules/integrations/
- shared/infrastructure/graphql/

Rapport : couverture actuelle + tests générés.
""")
```

```
Task(subagent_type="code-reviewer", prompt="""
Revue qualité code API publique (Phases 4-7) :

Checklist :
□ Type hints sur 100% signatures
□ Docstrings Google style sur classes/méthodes publiques
□ Pas de code mort ou commenté
□ Conventions nommage respectées (snake_case, classes PascalCase)
□ Logs structurés (JSON) avec niveaux appropriés (INFO, WARNING, ERROR)
□ Pas de secrets hardcodés (vérif grep -r "password\|secret\|key")

Rapport APPROVED ou corrections requises.
""")
```

```
Task(subagent_type="security-auditor", prompt="""
Audit sécurité COMPLET API publique (Phases 1-7) :

Checklist CRITIQUE :
□ Authentification sur TOUS endpoints (API Key, OAuth2, JWT)
□ Rate limiting sur TOUS endpoints (y compris /graphql, /batch)
□ Validation input stricte (Pydantic) sur mutations
□ Aucune injection SQL possible (SQLAlchemy ORM uniquement)
□ Aucun secret en clair en DB (hashing bcrypt, chiffrement AES-256)
□ HTTPS obligatoire en production (redirect HTTP → HTTPS)
□ CORS configuré strictement (whitelist domaines autorisés)
□ Headers sécurité (HSTS, CSP, X-Content-Type-Options)
□ Audit trail exhaustif (toutes actions API loggées)
□ Conformité RGPD (droit accès, rectification, suppression, portabilité)
□ Monitoring alertes sécurité (Prometheus + alertmanager)

Générer rapport complet (format : RAPPORT-SECURITE-API-PUBLIQUE.md).

Findings critiques/hautes → BLOCKER avant déploiement production.
""")
```

---

## TESTS D'INTÉGRATION GLOBAUX

**Après validation agents** :

```bash
# Backend : tests unitaires + intégration
cd backend
pytest tests/unit -v --cov=modules --cov=shared --cov-report=term --cov-report=html
pytest tests/integration/api -v

# Vérifier couverture >85%
coverage report --fail-under=85

# Tests performance (locust)
locust -f tests/performance/api_load_test.py --headless -u 100 -r 10 -t 5m

# Tests sécurité (bandit)
bandit -r modules/ shared/ -f json -o security-report.json
```

---

## DOCUMENTATION FINALE

**Mise à jour obligatoire** :

1. **SPECIFICATIONS.md** :
   - Ajouter section "API Publique" avec IDs API-01 à API-50
   - Marquer toutes features ✅

2. **docs/api/** :
   - openapi_v1.yaml (enrichi)
   - openapi_v2.yaml (nouveau)
   - GUIDE-MIGRATION-V1-V2.md
   - WEBHOOKS-GUIDE.md
   - SDK-PYTHON-GUIDE.md
   - SDK-JS-GUIDE.md
   - INTEGRATIONS-MARKETPLACE.md

3. **.claude/project-status.md** :
   - Ajouter section "API Publique" dans modules
   - Stats : 50 features API, 100% complet

4. **.claude/history.md** :
   - Résumé session Phases 4-7

---

## COMMIT & DÉPLOIEMENT

**Après validation complète** :

```bash
# Commit atomiques par phase
git add backend/modules/oauth2/ backend/tests/unit/oauth2/
git commit -m "feat(api): Phase 5 - OAuth2 Authorization Code Flow

- Entities OAuth clients, authorization codes, tokens
- Use cases authorize, exchange, refresh
- Tests unitaires 90% couverture
- Security audit PASS (0 findings critiques)

API-15: ✅"

# Push branche
git push origin feature/api-publique-phases-4-7

# Créer PR (après tous commits)
gh pr create --title "API Publique Phases 4-7 : Performance, Sécurité, Marketplace, Avancé" \
  --body "$(cat <<EOF
## Résumé

Implémentation complète Phases 4-7 API publique Hub Chantier.

### Phase 4 : Performance & Scalabilité
- ✅ Pagination cursor-based (API-20)
- ✅ Field selection (API-21)
- ✅ Cache Redis (API-22)
- ✅ ETags (API-23)
- ✅ Rate limiting avancé (API-24)
- ✅ Monitoring Prometheus/Grafana (API-25)

### Phase 5 : Sécurité & Conformité
- ✅ OAuth2 complet (API-30)
- ✅ Audit trail exhaustif (API-31)
- ✅ IP whitelisting (API-32)
- ✅ Détection anomalies (API-33)
- ✅ Rotation secrets (API-34)

### Phase 6 : Marketplace
- ✅ Architecture connecteurs (API-40)
- ✅ Sage 100 (API-41)
- ✅ Silae (API-42)
- ✅ QuickBooks (API-43)
- ✅ Slack (API-44)
- ✅ Google Calendar (API-45)
- ✅ Dropbox (API-46)

### Phase 7 : Avancé
- ✅ GraphQL API (API-50)
- ✅ Batch operations (API-51)
- ✅ API v2 versioning (API-52)

## Validation

- ✅ architect-reviewer : PASS
- ✅ test-automator : 87% couverture (2145 tests)
- ✅ code-reviewer : APPROVED
- ✅ security-auditor : PASS (0 critiques, 0 hautes)

## Tests

\`\`\`
Backend : 2145/2145 tests pass
Frontend : 2253/2259 tests pass
Performance : 100 users, latence p95 < 200ms
\`\`\`

## Breaking Changes

**AUCUN** - Backward compatibility 100% préservée.

## Déploiement

- Docker images : hub-chantier-api:v1.5.0
- Migrations Alembic : 15 nouvelles révisions
- Variables env : 12 nouvelles (voir .env.production.example)

🤖 Généré par Claude Code
EOF
)"
```

---

## SUCCÈS

**Critères de validation** :

✅ **Toutes features implémentées** (API-01 à API-52)
✅ **7 agents validation PASS** (architect, tests, code, security)
✅ **Tests >85% couverture**
✅ **0 breaking changes**
✅ **Security audit PASS** (0 findings critiques/hautes)
✅ **Documentation complète**
✅ **Déploiement Docker ready**

---

**FIN DU PROMPT PHASES 4-5-6-7**

🎯 **Action** : Exécuter ce prompt avec supervision agents complète.
