# Rapport d'Audit de Sécurité - Module Pointages

**Date:** 2026-01-31
**Auditeur:** security-auditor
**Scope:** Validation corrections sécurité SEC-PTG-001 et SEC-PTG-002
**Score de Sécurité:** 7.5/10

---

## Résumé Exécutif

Audit de sécurité du module `pointages` suite aux corrections des findings SEC-PTG-001 (validation regex heures) et SEC-PTG-002 (contrôles permissions).

**Résultats:**
- ✅ **SEC-PTG-001 RÉSOLU** - Validation stricte des formats d'heures implémentée
- ✅ **SEC-PTG-002 RÉSOLU** - Contrôles de permissions intégrés dans POST/PUT
- ⚠️ **4 nouveaux findings détectés** (3 MEDIUM, 1 LOW, 1 INFO)
- 📊 **Score 7.5/10** - Bon niveau de sécurité, améliorations nécessaires

**Verdict:** APPROVED WITH CONDITIONS - Déploiement autorisé APRÈS correction de SEC-PTG-003 et SEC-PTG-004 (permissions critiques manquantes).

---

## 1. Validation des Corrections Précédentes

### ✅ SEC-PTG-001: Validation regex heures - RÉSOLU

**Location:** `backend/modules/pointages/infrastructure/web/routes.py:34-91`

**Implémentation vérifiée:**
```python
def validate_time_format(time_str: str) -> str:
    """Valide le format HH:MM strictement."""
    pattern = r"^(\d{1,2}):(\d{2})$"
    match = re.match(pattern, time_str)

    if not match:
        raise ValueError("Format d'heure invalide. Format attendu: HH:MM")

    hours = int(match.group(1))
    minutes = int(match.group(2))

    # Validation des plages
    if hours < 0 or hours > 23:
        raise ValueError("Heures invalides (doit être entre 00 et 23)")

    if minutes < 0 or minutes > 59:
        raise ValueError("Minutes invalides (doit être entre 00 et 59)")

    return f"{hours:02d}:{minutes:02d}"
```

**Tests de couverture:**
- ✅ Formats valides: `08:30`, `23:59`, `00:00`
- ✅ Formats invalides rejetés: `24:00`, `12:60`, `-1:30`, `99:99`
- ✅ Normalisation avec padding zéros
- ✅ Messages d'erreur explicites

**Status:** RÉSOLU ✅

---

### ✅ SEC-PTG-002: Contrôles permissions routes - RÉSOLU

**Service de permissions:** `backend/modules/pointages/domain/services/permission_service.py`

**Intégration vérifiée:**

1. **POST /pointages (ligne 216):**
```python
if not PointagePermissionService.can_create_for_user(
    current_user_id=current_user_id,
    target_user_id=request.utilisateur_id,
    user_role=current_user_role,
):
    raise HTTPException(
        status_code=403,
        detail="Vous n'avez pas la permission de créer un pointage pour cet utilisateur"
    )
```

2. **PUT /pointages/{pointage_id} (ligne 501):**
```python
if not PointagePermissionService.can_modify(
    current_user_id=current_user_id,
    pointage_owner_id=pointage.get("utilisateur_id"),
    user_role=current_user_role,
):
    raise HTTPException(
        status_code=403,
        detail="Vous n'avez pas la permission de modifier ce pointage"
    )
```

**Matrice de permissions implémentée:**
| Rôle | Créer pour soi | Créer pour autres | Modifier propres | Modifier autres |
|------|---------------|-------------------|------------------|-----------------|
| Compagnon | ✅ | ❌ | ✅ | ❌ |
| Chef de chantier | ✅ | ✅ | ✅ | ✅ |
| Conducteur | ✅ | ✅ | ✅ | ✅ |
| Admin | ✅ | ✅ | ✅ | ✅ |

**Status:** RÉSOLU ✅

---

## 2. Nouveaux Findings

### 🔴 SEC-PTG-003: Permissions validation/rejet manquantes (MEDIUM)

**Sévérité:** MEDIUM
**CVSS v3.1:** 6.5 (AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
**Catégorie:** OWASP A01:2021 - Broken Access Control

**Description:**
Les endpoints `/validate` et `/reject` ne vérifient PAS les permissions avant d'autoriser l'action. Un compagnon pourrait potentiellement valider ses propres heures ou celles d'autres utilisateurs.

**Endpoints affectés:**
- `POST /pointages/{pointage_id}/validate` (ligne 566)
- `POST /pointages/{pointage_id}/reject` (ligne 599)

**Impact:**
Un utilisateur non autorisé (compagnon) pourrait valider/rejeter des pointages alors que seuls les chefs/conducteurs/admins devraient avoir ce droit selon la matrice de permissions.

**Preuve:**
```python
# backend/modules/pointages/infrastructure/web/routes.py:566-597
@router.post("/{pointage_id}/validate")
async def validate_pointage(
    pointage_id: int,
    validateur_id: int = Depends(get_current_user_id),
    # ❌ MANQUE: current_user_role: str = Depends(get_current_user_role)
    event_bus = Depends(get_event_bus),
    controller: PointageController = Depends(get_controller),
):
    # ❌ MANQUE: Vérification PointagePermissionService.can_validate()
    try:
        result = controller.validate_pointage(pointage_id, validateur_id)
        # ...
```

**Remédiation (Effort: 30 min):**
```python
@router.post("/{pointage_id}/validate")
async def validate_pointage(
    pointage_id: int,
    validateur_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),  # ✅ Ajouter
    event_bus = Depends(get_event_bus),
    controller: PointageController = Depends(get_controller),
):
    # ✅ Ajouter vérification permissions
    if not PointagePermissionService.can_validate(current_user_role):
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas la permission de valider des pointages"
        )

    try:
        result = controller.validate_pointage(pointage_id, validateur_id)
        # ...
```

**Priorité:** HIGH (P1)

---

### 🔴 SEC-PTG-004: Permissions export manquantes (MEDIUM)

**Sévérité:** MEDIUM
**CVSS v3.1:** 6.5 (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
**Catégorie:** OWASP A01:2021 - Broken Access Control

**Description:**
L'endpoint `POST /export` ne vérifie PAS les permissions. Selon la matrice, seuls les conducteurs et admins peuvent exporter (pas les chefs de chantier ni les compagnons).

**Endpoint affecté:**
- `POST /pointages/export` (ligne 356)

**Impact:**
Un chef de chantier ou un compagnon pourrait exporter des données de paie alors que cette action est restreinte aux conducteurs/admins uniquement.

**Preuve:**
```python
# backend/modules/pointages/infrastructure/web/routes.py:356-386
@router.post("/export")
def export_feuilles_heures(
    request: ExportRequest,
    current_user_id: int = Depends(get_current_user_id),
    # ❌ MANQUE: current_user_role: str = Depends(get_current_user_role)
    controller: PointageController = Depends(get_controller),
):
    # ❌ MANQUE: Vérification PointagePermissionService.can_export()
    result = controller.export_feuilles_heures(...)
    # ...
```

**Remédiation (Effort: 15 min):**
```python
@router.post("/export")
def export_feuilles_heures(
    request: ExportRequest,
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),  # ✅ Ajouter
    controller: PointageController = Depends(get_controller),
):
    # ✅ Ajouter vérification permissions
    if not PointagePermissionService.can_export(current_user_role):
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas la permission d'exporter les feuilles d'heures"
        )

    result = controller.export_feuilles_heures(...)
    # ...
```

**Priorité:** HIGH (P1)

---

### 🟡 SEC-PTG-005: Sanitization XSS commentaires (LOW)

**Sévérité:** LOW
**CVSS v3.1:** 4.4 (AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:N)
**Catégorie:** OWASP A03:2021 - Injection

**Description:**
Le champ `commentaire` (texte libre) n'est pas sanitizé contre les attaques XSS. Bien que Pydantic valide le type, il n'y a pas de nettoyage HTML/JS.

**Champs affectés:**
- `CreatePointageRequest.commentaire`
- `UpdatePointageRequest.commentaire`
- `RejectPointageRequest.motif`

**Impact:**
Un attaquant pourrait injecter du JavaScript dans les commentaires qui serait exécuté si affiché dans le frontend sans échappement.

**Remédiation (Effort: 1h):**
```python
from pydantic import validator
import bleach

class CreatePointageRequest(BaseModel):
    commentaire: Optional[str] = None

    @validator('commentaire')
    def sanitize_commentaire(cls, v):
        if v:
            return bleach.clean(v, tags=[], strip=True)
        return v
```

**Note:** Le frontend devrait également échapper les données lors de l'affichage (défense en profondeur).

**Priorité:** MEDIUM (P2)

---

### ℹ️ SEC-PTG-006: Logging audit manquant (INFO)

**Sévérité:** INFO
**Catégorie:** Logging & Monitoring

**Description:**
Aucun logging d'audit pour les actions sensibles (validation, rejet, export de paie). Les événements de sécurité ne sont pas tracés.

**Opérations affectées:**
- Validation de pointage (ligne 566)
- Rejet de pointage (ligne 599)
- Export feuilles heures (ligne 356)

**Impact:**
En cas d'incident de sécurité ou de fraude, impossible de retracer qui a effectué quelle action sensible et quand.

**Remédiation (Effort: 2h):**
```python
import logging
security_logger = logging.getLogger('security.audit')

# Dans validate_pointage:
security_logger.info(
    f"VALIDATION_POINTAGE: user={validateur_id} pointage={pointage_id} action=VALIDATE"
)

# Dans reject_pointage:
security_logger.warning(
    f"REJECTION_POINTAGE: user={validateur_id} pointage={pointage_id} motif={request.motif}"
)

# Dans export:
security_logger.info(
    f"EXPORT_PAIE: user={current_user_id} format={request.format_export} "
    f"periode={request.date_debut} to {request.date_fin}"
)
```

**Conformité:**
- RGPD Art. 32 - Traçabilité des accès aux données de paie
- ISO 27001 A.12.4.1 - Event logging

**Priorité:** MEDIUM (P2)

---

## 3. Points Forts de Sécurité

### ✅ Protection SQL Injection
**Détails:** Utilisation correcte de SQLAlchemy ORM avec requêtes paramétrées. Aucune concaténation de chaînes SQL détectée.
**Fichier:** `backend/modules/pointages/infrastructure/persistence/sqlalchemy_pointage_repository.py`
**Exemple:**
```python
model = self.session.query(PointageModel).filter(
    PointageModel.utilisateur_id == utilisateur_id,  # ✅ Paramétré
    PointageModel.date_pointage == date_pointage,    # ✅ Paramétré
).first()
```

### ✅ Protection CSRF
**Détails:** Middleware CSRF actif au niveau application avec validation token sur POST/PUT/DELETE.
**Fichier:** `backend/shared/infrastructure/web/csrf_middleware.py`
**Configuration:** Exemptions appropriées pour `/auth/login`, rotation token après requêtes mutables.

### ✅ Rate Limiting
**Détails:** Middleware de rate limiting avec backoff exponentiel déployé.
**Fichier:** `backend/shared/infrastructure/web/rate_limit_middleware.py`
**Stratégie:** Backoff 30s → 60s → 120s → 240s → 300s max après violations.

### ✅ Cookie Security
**Détails:** Configuration cookies sécurisée en production.
**Fichier:** `backend/shared/infrastructure/config.py`
**Paramètres:**
- `SameSite=strict` (protection CSRF)
- `Secure=true` (HTTPS uniquement)
- `HttpOnly=true` (protection XSS)

### ✅ Clean Architecture
**Détails:** Séparation stricte Domain → Application → Infrastructure.
**Bénéfice:** Isolation des données sensibles (heures de paie), testabilité accrue.

---

## 4. Conformité OWASP & RGPD

### OWASP Top 10 2021

| Vulnérabilité | Status | Détails |
|---------------|--------|---------|
| A01 - Broken Access Control | ⚠️ PARTIAL | Gaps: SEC-PTG-003, SEC-PTG-004 (permissions validation/export manquantes) |
| A02 - Cryptographic Failures | ✅ PASS | Aucune donnée sensible nécessitant chiffrement dans ce module |
| A03 - Injection | ⚠️ PARTIAL | SQL injection PASS, XSS MEDIUM (SEC-PTG-005) |
| A04 - Insecure Design | ✅ PASS | Clean Architecture respectée, séparation domaine/infra |
| A05 - Security Misconfiguration | ✅ PASS | CSRF actif, rate limiting actif, cookies sécurisés |
| A06 - Vulnerable Components | N/A | Pas d'analyse de dépendances dans ce scope |
| A07 - Authentication Failures | ✅ PASS | Authentification gérée par module auth (hors scope) |
| A08 - Software Data Integrity | ✅ PASS | Event bus pour intégrité événements |
| A09 - Logging & Monitoring | ⚠️ MEDIUM | SEC-PTG-006 (logging audit manquant) |
| A10 - SSRF | N/A | Pas de requêtes HTTP sortantes dans ce module |

### RGPD

| Article | Status | Détails |
|---------|--------|---------|
| Art. 5 - Minimisation | ✅ PASS | Collecte uniquement heures/commentaires nécessaires |
| Art. 25 - Privacy by Design | ✅ PASS | Clean Architecture, données découplées |
| Art. 32 - Sécurité | ⚠️ PARTIAL | Chiffrement N/A, mais logging audit manquant (SEC-PTG-006) |
| Art. 33 - Notification de fuite | ⚠️ MEDIUM | Pas de mécanisme de détection de fuite de données de paie |

**Données sensibles identifiées:**
- **CONFIDENTIEL:** Heures de travail (lié à la paie)
- **HAUTE CONFIDENTIALITÉ:** Variables de paie (montants)
- **BAS:** Commentaires (texte libre, potentiel XSS)

---

## 5. Recommandations

### Actions Immédiates (P1)

| # | Action | Finding | Effort | Impact |
|---|--------|---------|--------|--------|
| 1 | Intégrer `PointagePermissionService.can_validate()` dans `POST /validate` | SEC-PTG-003 | 30 min | Empêche compagnons de valider leurs propres heures |
| 2 | Intégrer `PointagePermissionService.can_reject()` dans `POST /reject` | SEC-PTG-003 | 30 min | Empêche accès non autorisé au workflow de validation |
| 3 | Intégrer `PointagePermissionService.can_export()` dans `POST /export` | SEC-PTG-004 | 15 min | Restreint export paie aux conducteurs/admins uniquement |

**Total effort P1:** 1h15

### Actions Court Terme (P2)

| # | Action | Finding | Effort | Impact |
|---|--------|---------|--------|--------|
| 4 | Ajouter sanitization `bleach` pour commentaire/motif | SEC-PTG-005 | 1h | Prévient injection XSS dans commentaires |
| 5 | Implémenter logging d'audit sécurité pour validation/rejet/export | SEC-PTG-006 | 2h | Conformité RGPD Art. 32, traçabilité incidents |

**Total effort P2:** 3h

### Actions Long Terme (P3)

| # | Action | Effort | Impact |
|---|--------|--------|--------|
| 6 | Ajouter tests de sécurité automatisés pour les permissions | 4h | Détection régression permissions |
| 7 | Implémenter détection d'anomalies export paie (volume inhabituel) | 1 jour | Alerte en cas d'exfiltration massive de données |

---

## 6. Tests Recommandés

### Tests Unitaires

```python
# backend/tests/unit/pointages/test_validation_heures.py
def test_validate_time_format_rejects_invalid():
    with pytest.raises(ValueError):
        validate_time_format("24:00")
    with pytest.raises(ValueError):
        validate_time_format("12:60")
    with pytest.raises(ValueError):
        validate_time_format("-1:30")

# backend/tests/unit/pointages/test_permission_service.py
def test_can_validate_compagnon_false():
    assert PointagePermissionService.can_validate("compagnon") == False

def test_can_validate_chef_true():
    assert PointagePermissionService.can_validate("chef_chantier") == True
```

### Tests d'Intégration

```python
# backend/tests/integration/pointages/test_routes_security.py
def test_validate_compagnon_returns_403(client):
    response = client.post(
        "/api/pointages/1/validate",
        headers={"Authorization": f"Bearer {compagnon_token}"}
    )
    assert response.status_code == 403

def test_export_chef_returns_403(client):
    response = client.post(
        "/api/pointages/export",
        headers={"Authorization": f"Bearer {chef_token}"}
    )
    assert response.status_code == 403
```

### Tests de Sécurité

```python
# backend/tests/security/test_pointages_xss.py
def test_commentaire_xss_sanitized(client):
    xss_payload = "<script>alert('XSS')</script>"
    response = client.post(
        "/api/pointages",
        json={"commentaire": xss_payload, ...}
    )
    pointage = response.json()
    assert "<script>" not in pointage["commentaire"]
```

---

## 7. Score de Sécurité

### Score Global: 7.5/10

| Dimension | Score | Détails |
|-----------|-------|---------|
| **Input Validation** | 8.0/10 | ✅ Validation stricte heures, ⚠️ Sanitization XSS manquante |
| **Authentication** | 10.0/10 | ✅ Géré par module auth (bcrypt, JWT) |
| **Authorization** | 6.0/10 | ⚠️ Permissions POST/PUT OK, validation/export manquantes |
| **Cryptography** | 9.0/10 | ✅ Pas de données nécessitant chiffrement dans ce module |
| **Error Handling** | 8.0/10 | ✅ HTTPException appropriées, pas de stack traces exposées |
| **Logging** | 6.0/10 | ⚠️ Logging audit manquant pour actions sensibles |
| **Configuration** | 9.0/10 | ✅ CSRF, rate limiting, cookies sécurisés |

**Justification:**
Score 7.5/10 reflète un bon niveau de sécurité avec corrections SEC-PTG-001 et SEC-PTG-002 résolues. Principales faiblesses: permissions validation/export manquantes (SEC-PTG-003, SEC-PTG-004) et logging audit absent (SEC-PTG-006).

**Objectif:** 9.0/10
**Gap:** 1.5 points - Corriger findings MEDIUM restants

---

## 8. Conclusion

### Résumé
Audit de sécurité du module `pointages` suite aux corrections SEC-PTG-001 et SEC-PTG-002. Les deux findings précédents sont **RÉSOLUS avec succès**. Détection de 4 nouveaux findings (3 MEDIUM, 1 LOW, 1 INFO) principalement liés aux contrôles de permissions manquants sur les endpoints sensibles (validation, rejet, export).

### Points Critiques
Aucun finding CRITICAL ou HIGH détecté. Les findings MEDIUM (SEC-PTG-003, SEC-PTG-004, SEC-PTG-006) peuvent être corrigés rapidement (effort total ~4h).

### Prochaines Étapes

1. ✅ **Corriger SEC-PTG-003 et SEC-PTG-004** (permissions validation/export) - **Effort 1h15**
2. ✅ **Ajouter sanitization XSS** (SEC-PTG-005) - **Effort 1h**
3. ✅ **Implémenter logging audit** (SEC-PTG-006) - **Effort 2h**
4. ✅ **Créer tests de sécurité automatisés** - **Effort 4h**
5. ✅ **Re-audit après corrections** pour valider score 9/10

### Statut d'Approbation

**APPROVED WITH CONDITIONS**

Le module peut être déployé **APRÈS correction de SEC-PTG-003 et SEC-PTG-004** (permissions critiques manquantes sur validation/rejet/export). Ces corrections sont obligatoires pour respecter la matrice de permissions métier et éviter des accès non autorisés aux données de paie.

---

**Fin du rapport**
