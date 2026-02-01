# Audit de Sécurité - Implémentation "Plusieurs Métiers par Utilisateur"

**Date:** 2026-01-31
**Agent:** security-auditor
**Périmètre:** Migration `metier` (string) → `metiers` (JSON array)
**Standards:** OWASP Top 10, RGPD, Clean Architecture

---

## 📊 Résumé Exécutif

| Statut Global | Findings Critiques | Findings Hauts | Findings Moyens | Findings Bas |
|--------------|-------------------|----------------|-----------------|--------------|
| **❌ FAIL** | 1 | 2 | 2 | 1 |

**⚠️ BLOCKER PRODUCTION DÉTECTÉ** - Correction immédiate requise avant déploiement.

---

## 🚨 CRITICAL - SEC-001: Incompatibilité Backend/Frontend

### Problème
Le backend utilise **TOUJOURS** le champ singulier `metier` (string) dans les routes API alors que:
- ✅ La migration BDD a converti `metier` → `metiers` (array)
- ✅ Le domaine `User.metiers` attend `Optional[List[str]]`
- ✅ Le frontend envoie `metiers` (array)
- ✅ Les DTOs définissent `metiers` (array)

### Impact
**PERTE DE DONNÉES TOTALE** - Les métiers sélectionnés par l'utilisateur ne sont **JAMAIS** sauvegardés.

### Localisation
```python
# ❌ backend/modules/auth/infrastructure/web/auth_routes.py
ligne 263:  metier=data.metier,              # ERREUR: devrait être metiers=data.metiers
ligne 385:  metier: Optional[str] = None     # ERREUR: devrait être metiers: Optional[List[str]]
ligne 588:  metier=request_body.metier,      # ERREUR
ligne 921:  metier=request.metier,           # ERREUR

# ❌ backend/modules/auth/adapters/controllers/auth_controller.py
ligne 76:   "metier": user_dto.metier,       # ERREUR: devrait être "metiers": user_dto.metiers
ligne 116:  metier: Optional[str] = None,    # ERREUR: devrait être metiers: Optional[List[str]]
```

### Scénario d'Exploitation
```bash
# Frontend envoie:
POST /auth/register
{
  "email": "test@example.com",
  "metiers": ["coffreur", "ferrailleur", "macon"]
}

# Backend cherche data.metier (n'existe pas!)
# → AttributeError OU metiers=None sauvegardé
# → Les 3 métiers sont PERDUS
```

### Correctif IMMÉDIAT (2h)
1. **Modifier `auth_routes.py`:**
```python
# RegisterRequest
class RegisterRequest(BaseModel):
    metiers: Optional[List[str]] = None  # ✅ Pluriel + List

# InviteUserModel
class InviteUserModel(BaseModel):
    metiers: Optional[List[str]] = None  # ✅ Pluriel + List

# UpdateUserRequest
class UpdateUserRequest(BaseModel):
    metiers: Optional[List[str]] = None  # ✅ Pluriel + List

# Routes
@router.post("/register")
def register(...):
    result = controller.register(
        metiers=data.metiers,  # ✅ Pluriel
        ...
    )

@router.post("/invite")
def invite_user(...):
    use_case.execute(
        metiers=request_body.metiers,  # ✅ Pluriel
        ...
    )

@users_router.put("/{user_id}")
def update_user(...):
    result = controller.update_user(
        metiers=request.metiers,  # ✅ Pluriel
        ...
    )
```

2. **Modifier `auth_controller.py`:**
```python
def _user_dto_to_dict(self, user_dto) -> Dict[str, Any]:
    return {
        ...
        "metiers": user_dto.metiers,  # ✅ Pluriel
        ...
    }

def register(self, ..., metiers: Optional[List[str]] = None, ...):
    dto = RegisterDTO(
        ...
        metiers=metiers,  # ✅ Pluriel
        ...
    )

def update_user(self, ..., metiers: Optional[List[str]] = None, ...):
    dto = UpdateUserDTO(
        ...
        metiers=metiers,  # ✅ Pluriel
        ...
    )
```

3. **Tester:**
```bash
# Test 1: Inscription
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234!",
    "nom": "Dupont",
    "prenom": "Jean",
    "metiers": ["coffreur", "ferrailleur"]
  }'

# Vérifier en BDD:
SELECT id, email, metiers FROM users WHERE email = 'test@example.com';
# Attendu: metiers = ["coffreur", "ferrailleur"]

# Test 2: Mise à jour
curl -X PUT http://localhost:8000/api/users/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"metiers": ["macon", "grutier", "couvreur"]}'
```

**Délai de remédiation:** 24-48h (CRITIQUE)

---

## 🔴 HIGH - SEC-002: Validation Serveur Absente

### Problème
Le frontend limite à **5 métiers** (`MAX_METIERS = 5`) mais le backend n'applique **AUCUNE validation**.

Un attaquant peut contourner la validation frontend:
```bash
# Burp Suite / curl
POST /auth/register
{
  "metiers": ["macon"] * 1000  # 1000 métiers!
}
# → Accepté par le backend
# → Surcharge mémoire JSON
# → DoS potentiel
```

### Impact
- Contournement validation client
- DoS mémoire (JSON trop volumineux)
- Données corrompues (valeurs invalides: `["<script>", "DROP TABLE"]`)

### Correctif (1h)
**Ajouter validation Pydantic stricte:**

```python
# backend/modules/auth/application/dtos/user_dto.py
from pydantic import validator, Field, constr

METIERS_AUTORISES = [
    'macon', 'coffreur', 'ferrailleur', 'grutier',
    'charpentier', 'couvreur', 'terrassier', 'administratif', 'autre'
]

@dataclass(frozen=True)
class RegisterDTO:
    metiers: Optional[List[constr(min_length=1, max_length=50)]] = Field(None, max_items=5)

    @validator('metiers')
    def validate_metiers(cls, v):
        if v is not None:
            if len(v) > 5:
                raise ValueError("Maximum 5 métiers autorisés")
            for metier in v:
                if metier not in METIERS_AUTORISES:
                    raise ValueError(f"Métier invalide: {metier}")
        return v

# Idem pour UpdateUserDTO
```

**Test d'injection:**
```bash
# Test 1: Trop de métiers
curl -X POST /api/auth/register \
  -d '{"metiers": ["macon","macon","macon","macon","macon","macon"]}'
# Attendu: HTTP 400 "Maximum 5 métiers autorisés"

# Test 2: Métier invalide
curl -X POST /api/auth/register \
  -d '{"metiers": ["<script>alert(1)</script>"]}'
# Attendu: HTTP 400 "Métier invalide"
```

**Délai de remédiation:** 1 semaine (HIGH)

---

## 🟠 MEDIUM - SEC-003: Pattern SQL+JSON à Risque

### Problème
La migration utilise `sa.text()` pour requêtes SQL brutes avec JSON:
```python
connection.execute(
    sa.text("""
        UPDATE users
        SET metiers = jsonb_build_array(metier)
        WHERE metier IS NOT NULL
    """)
)
```

**Risque:** Si des requêtes similaires sont ajoutées avec **input utilisateur non paramétré**, injection SQL possible.

### Impact
Pas d'exploitation immédiate (la migration est safe), mais **pattern dangereux** pour évolutions futures.

### Correctif (30min)
**Documentation préventive:**

Créer `docs/security/sql-json-queries.md`:
```markdown
# Sécurité des Requêtes SQL avec JSON/JSONB

## ❌ INTERDIT
```python
# Injection SQL possible!
metier_filter = request.args.get('metier')
query = f"SELECT * FROM users WHERE metiers @> '[{metier_filter}]'::jsonb"
```

## ✅ CORRECT
```python
# Utiliser bindparams
from sqlalchemy import text
metier_filter = request.args.get('metier')
query = text("SELECT * FROM users WHERE metiers @> :filter")
result = connection.execute(query, {"filter": json.dumps([metier_filter])})
```

## Code Review
Toute requête contenant `metiers`, `JSON`, `jsonb` doit être review par 2 personnes.
```

**Délai de remédiation:** 1 mois (MEDIUM - préventif)

---

## 🟠 MEDIUM - SEC-004: Risque XSS (Frontend)

### Problème
Les badges métiers sont affichés avec:
```tsx
// frontend/src/components/users/MetierMultiSelect.tsx
<span style={{ backgroundColor: metierInfo.color + '20' }}>
  {metierInfo.label}  {/* Potentiel XSS si metierInfo.label corrompu */}
</span>
```

**Actuellement:** Risque faible car `METIERS` est une constante statique.
**Après SEC-002:** Risque moyen si validation backend est contournée.

### Impact
XSS possible si un attaquant injecte un métier malveillant:
```json
{"metiers": ["<img src=x onerror=alert(document.cookie)>"]}
```

### Correctif (30min)
1. **Vérifier échappement React** (déjà OK car `{expression}` est auto-escaped)
2. **Ajouter CSP Header:**
```python
# backend/shared/infrastructure/middleware.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    ...,
    expose_headers=["Content-Security-Policy"],
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline';"
    )
    return response
```

3. **Test XSS:**
```bash
# Après contournement hypothétique de la validation
curl -X POST /api/auth/register \
  -d '{"metiers": ["<img src=x onerror=alert(1)>"]}'
# Vérifier que:
# 1. Backend rejette (validation SEC-002)
# 2. Si accepté, frontend échappe correctement
```

**Délai de remédiation:** 1 mois (MEDIUM)

---

## 🟡 MEDIUM - SEC-005: Perte de Données (Migration Downgrade)

### Problème
Le downgrade `metiers[] → metier` ne garde que le **premier métier**:
```sql
-- Si user.metiers = ["coffreur", "ferrailleur", "macon"]
UPDATE users SET metier = metiers->>0  -- Garde uniquement "coffreur"
-- "ferrailleur" et "macon" sont PERDUS
```

**Documenté** (ligne 73 migration) mais **non loggué**.

### Impact
Perte de données silencieuse lors d'un rollback. Acceptable si downgrade exceptionnel.

### Correctif (30min)
**Ajouter logging:**
```python
def downgrade():
    connection = op.get_bind()

    # Compter les utilisateurs affectés
    affected = connection.execute(
        sa.text("SELECT COUNT(*) FROM users WHERE jsonb_array_length(metiers) > 1")
    ).scalar()

    if affected > 0:
        print(f"⚠️  WARNING: {affected} utilisateurs perdront des métiers lors du downgrade!")
        # Logger les IDs pour audit
        users = connection.execute(
            sa.text("SELECT id, email, metiers FROM users WHERE jsonb_array_length(metiers) > 1")
        ).fetchall()
        for user in users:
            print(f"  - User {user.id} ({user.email}): {user.metiers} → {user.metiers[0]}")

    # Downgrade...
```

**Délai de remédiation:** 3 mois (LOW)

---

## ✅ LOW - SEC-006: RGPD Conformité

### Conclusion
Les **métiers ne sont PAS des données sensibles** au sens du RGPD (Article 9).

| Critère | Statut | Justification |
|---------|--------|---------------|
| Chiffrement requis | ❌ NON | Données professionnelles standard |
| Consentement explicite | ❌ NON | Traitement légitime (contrat de travail) |
| Export RGPD (Art. 20) | ✅ OUI | Inclus dans `UserDTO` |
| Droit à l'oubli (Art. 17) | ✅ OUI | Suppression cascade OK |

**Aucune action requise.**

---

## 📋 Statut de Conformité

### OWASP Top 10 2021
| Catégorie | Statut | Findings |
|-----------|--------|----------|
| A01 - Broken Access Control | ✅ PASS | - |
| A03 - Injection | ❌ FAIL | SEC-002, SEC-003, SEC-004 |
| A04 - Insecure Design | ❌ FAIL | SEC-001 |
| A05 - Security Misconfiguration | ✅ PASS | - |
| A07 - Identification Failures | ✅ PASS | - |

### RGPD
| Article | Statut | Détails |
|---------|--------|---------|
| Art. 6 - Licéité | ✅ PASS | Données professionnelles légitimes |
| Art. 9 - Données sensibles | ✅ PASS | Métiers NON sensibles |
| Art. 15 - Droit d'accès | ✅ PASS | Inclus dans UserDTO |
| Art. 17 - Droit à l'oubli | ✅ PASS | Suppression cascade |
| Art. 20 - Portabilité | ✅ PASS | Export JSON disponible |
| Art. 32 - Sécurité | ⚠️  PARTIAL | Validation à ajouter (SEC-002) |

### Clean Architecture
| Critère | Statut | Détails |
|---------|--------|---------|
| Indépendance domaine | ✅ PASS | `User.metiers` bien défini |
| Validation DTOs | ❌ FAIL | SEC-002 |
| Cohérence API | ❌ FAIL | SEC-001 |

---

## 🎯 Plan d'Action Priorisé

| Priorité | Finding | Action | Effort | Délai |
|----------|---------|--------|--------|-------|
| **IMMEDIATE** | SEC-001 | Corriger `metier` → `metiers` routes/controller | 2h | 24-48h |
| **HIGH** | SEC-002 | Validation Pydantic stricte | 1h | 1 semaine |
| **MEDIUM** | SEC-004 | CSP header + vérification XSS | 30min | 1 mois |
| **MEDIUM** | SEC-003 | Documentation SQL+JSON | 30min | 1 mois |
| **LOW** | SEC-005 | Logging downgrade migration | 30min | 3 mois |

**Effort total:** ~4h (corrections) + 2h (tests)

---

## 🧪 Plan de Tests

### SEC-001-T1: Sauvegarde métiers via API
```bash
# Test inscription
POST /auth/register
{
  "email": "test@example.com",
  "password": "Test1234!",
  "nom": "Dupont",
  "prenom": "Jean",
  "metiers": ["coffreur", "ferrailleur"]
}

# Vérification
GET /users/{id}
# Attendu: metiers = ["coffreur", "ferrailleur"]

# Vérification BDD
SELECT metiers FROM users WHERE email = 'test@example.com';
# Attendu: ["coffreur", "ferrailleur"]
```

### SEC-002-T1: Validation >5 métiers
```bash
POST /auth/register
{
  "metiers": ["macon", "coffreur", "ferrailleur", "grutier", "charpentier", "couvreur"]
}
# Attendu: HTTP 400 "Maximum 5 métiers autorisés"
```

### SEC-002-T2: Validation métier invalide
```bash
POST /auth/register
{
  "metiers": ["<script>alert(1)</script>"]
}
# Attendu: HTTP 400 "Métier invalide"
```

### SEC-004-T1: XSS échappement
```tsx
// DevTools: Inspecter badge métier
// Vérifier: textContent utilisé, pas innerHTML
// Tenter: Payload XSS après contournement validation
// Attendu: React échappe automatiquement
```

---

## 📝 Conclusion

### Statut Global: ❌ FAIL

**BLOCKER PRODUCTION:**
- **SEC-001 (CRITICAL):** Incompatibilité backend/frontend provoque **perte totale des métiers**

### Avant Production (MUST FIX)
1. ✅ Corriger SEC-001 (metier → metiers)
2. ✅ Implémenter SEC-002 (validation Pydantic)
3. ✅ Exécuter plan de tests complet
4. ✅ Re-auditer après corrections

### Après Production (Améliorations)
- SEC-003: Documentation SQL+JSON
- SEC-004: CSP header
- SEC-005: Logging downgrade

### Prochaines Étapes
1. **Immédiatement:** Corriger SEC-001 (blocker)
2. **Cette semaine:** Implémenter SEC-002 (high)
3. **Tests:** Exécuter SEC-001-T1, SEC-001-T2, SEC-002-T1, SEC-002-T2
4. **Re-audit:** Vérifier status PASS avant déploiement

---

**Objectif:** **PASS** (0 finding CRITICAL/HIGH) avant mise en production.

**Statut actuel:** **FAIL** - Corrections requises.
