# Audit de Sécurité - Module Pointages Phase 2

**Date**: 2026-01-31
**Auditeur**: Security Auditor Agent
**Périmètre**: 4 nouvelles fonctionnalités (GAP-FDH-004, GAP-FDH-008, GAP-FDH-009)
**Statut**: **FAIL** - Blocage mise en production

---

## Score de Sécurité: 5.5/10 ❌

**Seuil de passage**: 9.0/10
**Statut**: **FAIL - Corrections critiques requises avant commit**

---

## Résumé Exécutif

L'audit de sécurité des 4 nouvelles fonctionnalités de la Phase 2 du module pointages révèle **9 vulnérabilités**, dont **1 CRITIQUE** et **2 HAUTES** qui bloquent la mise en production.

Les principales préoccupations concernent:
1. **Contrôles d'accès manquants** sur les nouveaux endpoints (validation par lot, récapitulatif mensuel)
2. **Fuite de données de paie sensibles** sans vérification d'autorisation
3. **Risque de déni de service total** via le verrouillage de périodes arbitraires

### Conformité

| Framework | Statut | Détails |
|-----------|--------|---------|
| **RGPD** | ❌ **FAIL** | 5 violations (Articles 5, 30, 32) |
| **OWASP Top 10** | ❌ **FAIL** | A01 Broken Access Control, A04 Insecure Design |

---

## Findings par Sévérité

| Sévérité | Nombre | IDs |
|----------|--------|-----|
| **CRITICAL** | 1 | SEC-PTG-P2-006 |
| **HIGH** | 2 | SEC-PTG-P2-001, SEC-PTG-P2-002 |
| **MEDIUM** | 4 | SEC-PTG-P2-003, SEC-PTG-P2-004, SEC-PTG-P2-005, SEC-PTG-P2-007 |
| **LOW** | 2 | SEC-PTG-P2-008, SEC-PTG-P2-009 |
| **TOTAL** | **9** | |

---

## Findings Critiques et Hautes

### 🔴 CRITICAL - SEC-PTG-P2-006: Verrouillage de périodes arbitraires

**Localisation**: `routes.py:694-723` (endpoint `/lock-period`)

**Problème**: La route `/lock-period` vérifie uniquement le rôle (admin/conducteur) mais n'empêche pas le verrouillage de périodes arbitraires. Un admin malveillant pourrait:
- Verrouiller 2020, 2025, 2030 (toutes les périodes passées et futures)
- Rendre le système totalement inutilisable (déni de service)
- Empêcher toute modification de pointage

**Impact**: Déni de service total du module pointages.

**Remédiation URGENTE**:
```python
# 1. Interdire le verrouillage de périodes futures
today = date.today()
if year > today.year or (year == today.year and month > today.month):
    raise HTTPException(
        status_code=400,
        detail="Impossible de verrouiller une période future"
    )

# 2. Interdire le verrouillage de périodes trop anciennes (> 12 mois)
period_date = date(year, month, 1)
if (today - period_date).days > 365:
    raise HTTPException(
        status_code=400,
        detail="Impossible de verrouiller une période de plus de 12 mois"
    )

# 3. Vérifier que la période n'est pas déjà verrouillée
if PeriodePaie.is_locked(date(year, month, 15)):
    raise HTTPException(
        status_code=409,
        detail="Cette période est déjà verrouillée"
    )
```

**Effort**: 2h
**Deadline**: **IMMÉDIATE** (48h)

---

### 🟠 HIGH - SEC-PTG-P2-001: Authorization Bypass sur /bulk-validate

**Localisation**: `routes.py:640-658` (endpoint `/bulk-validate`)

**Problème**: Aucun contrôle d'accès. Un **compagnon** pourrait théoriquement:
- Valider ses propres pointages (violation workflow hiérarchique)
- Valider les pointages d'autres utilisateurs
- Bypasser la validation N+1 requise

**Impact**: Compromission de l'intégrité des données de paie. Violation RGPD Article 32.

**Remédiation URGENTE**:
```python
@router.post("/bulk-validate")
def bulk_validate_pointages(
    request: BulkValidateRequest,
    validateur_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),  # AJOUTER
    controller: PointageController = Depends(get_controller),
):
    # AJOUTER CETTE VÉRIFICATION
    if not PointagePermissionService.can_validate(current_user_role):
        raise HTTPException(
            status_code=403,
            detail="Seuls les chefs de chantier, conducteurs et admins peuvent valider"
        )

    # ... reste du code
```

**Effort**: 1h
**Deadline**: **IMMÉDIATE** (48h)

---

### 🟠 HIGH - SEC-PTG-P2-002: Fuite de données de paie sur /recap

**Localisation**: `routes.py:660-685` (endpoint `/recap/{utilisateur_id}/{year}/{month}`)

**Problème**: Aucun contrôle d'accès. Un **compagnon** peut consulter:
- Les heures d'un autre compagnon
- Les heures supplémentaires, primes, paniers (données sensibles)
- Les absences (données médicales potentielles)

**Exemple d'exploitation**:
```bash
# Compagnon user_id=7 accède aux données du compagnon user_id=8
GET /pointages/recap/8/2026/1
→ 200 OK avec TOUTES les données de paie du compagnon 8
```

**Impact**: Violation RGPD Article 5.1.b (limitation de la finalité) et Article 32 (confidentialité). Les données de paie sont classifiées **HAUTE CONFIDENTIALITÉ**.

**Remédiation URGENTE**:
```python
@router.get("/recap/{utilisateur_id}/{year}/{month}")
def get_monthly_recap(
    utilisateur_id: int,
    year: int,
    month: int,
    export_pdf: bool = Query(False),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),  # AJOUTER
    controller: PointageController = Depends(get_controller),
):
    # AJOUTER CETTE VÉRIFICATION
    # Un compagnon ne peut consulter que son propre récapitulatif
    if current_user_role == 'compagnon' and current_user_id != utilisateur_id:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez consulter que votre propre récapitulatif"
        )

    # Les managers peuvent consulter tous les récapitulatifs (OK)

    # ... reste du code
```

**Effort**: 30min
**Deadline**: **IMMÉDIATE** (48h)

---

## Findings Medium

### 🟡 SEC-PTG-P2-003: Race Condition dans bulk_validate

**Problème**: La validation par lot itère sans transaction atomique. Deux validateurs simultanés peuvent valider les mêmes pointages, causant:
- Double validation
- Événements dupliqués vers le système de paie
- États incohérents

**Remédiation**: Implémenter verrouillage optimiste avec `SELECT FOR UPDATE`.

**Effort**: 4h
**Deadline**: 1 semaine

---

### 🟡 SEC-PTG-P2-004: Test échoué pour période verrouillée

**Problème**: Le test `test_bulk_validate_periode_locked` échoue. Le pointage est validé malgré `PeriodePaie.is_locked() == True`.

**Evidence**:
```
FAILED test_bulk_validate_periode_locked
assert result.success_count == 0  # attendu
assert result.success_count == 1  # réel (❌ BUG)
```

**Remédiation**: Corriger la logique de verrouillage ou le test mock.

**Effort**: 2h
**Deadline**: 1 semaine

---

### 🟡 SEC-PTG-P2-005: Limite excessive dans generate_monthly_recap

**Problème**: `limit=10000` pour récupérer les pointages d'un mois. Risque de:
- Déni de service (DoS)
- Exposition massive de données
- Violation principe de minimisation RGPD

**Remédiation**: Réduire à `limit=50` (max raisonnable pour un mois).

**Effort**: 30min
**Deadline**: 1 mois

---

### 🟡 SEC-PTG-P2-007: Scheduler sans validation EventBus

**Problème**: Le scheduler utilise `get_event_bus()` sans vérifier qu'il est initialisé. En cas d'échec, le verrouillage automatique échoue silencieusement.

**Remédiation**: Ajouter validation + healthcheck + alertes admins.

**Effort**: 3h
**Deadline**: 1 semaine

---

## Findings Low

### 🟢 SEC-PTG-P2-008: Logs insuffisants pour audit trail

**Problème**: La validation par lot ne log pas assez de détails (qui, quand, combien, IP, user-agent).

**Effort**: 1h

---

### 🟢 SEC-PTG-P2-009: Pas de limite max pour bulk_validate

**Problème**: Un attaquant peut envoyer 100000 IDs dans une seule requête (DoS).

**Remédiation**: Ajouter `max_items=100` dans le DTO.

**Effort**: 15min

---

## Plan d'Action

### ⚡ IMMÉDIATE (48h) - BLOCAGE COMMIT

| ID | Action | Effort | Responsable |
|----|--------|--------|-------------|
| SEC-PTG-P2-006 | Ajouter validations métier pour /lock-period | 2h | Dev Backend |
| SEC-PTG-P2-001 | Ajouter contrôle can_validate() sur /bulk-validate | 1h | Dev Backend |
| SEC-PTG-P2-002 | Ajouter règle d'accès compagnon sur /recap | 30min | Dev Backend |

**Total effort CRITICAL**: 3h30

---

### 🔴 HIGH (1 semaine)

| ID | Action | Effort |
|----|--------|--------|
| SEC-PTG-P2-003 | Implémenter SELECT FOR UPDATE | 4h |
| SEC-PTG-P2-004 | Corriger test période verrouillée | 2h |
| SEC-PTG-P2-007 | Valider EventBus dans scheduler | 3h |

**Total effort HIGH**: 9h

---

### 🟡 MEDIUM (1 mois)

| ID | Action | Effort |
|----|--------|--------|
| SEC-PTG-P2-005 | Réduire limite à 50 pointages | 30min |
| SEC-PTG-P2-008 | Ajouter logs structurés | 1h |
| SEC-PTG-P2-009 | Limiter bulk_validate à 100 IDs | 15min |

**Total effort MEDIUM**: 1h45

---

## Recommandations Architecturales

1. **Créer un décorateur `@require_manager_role`** pour éviter la duplication de code de contrôle d'accès
2. **Implémenter rate limiting** sur `/bulk-validate` (max 10 requêtes/minute/user)
3. **Ajouter contrainte DB CHECK** pour empêcher modifications sur périodes verrouillées
4. **Créer un audit trail dédié** pour toutes les opérations sensibles (validation, verrouillage)
5. **Système d'alertes** pour les échecs du scheduler (email/Slack vers admins)

---

## Tests de Sécurité Manquants

Créer `tests/unit/pointages/test_security_fixes_phase2.py` avec:

- [ ] Test d'authorization pour /bulk-validate (compagnon ne peut pas valider)
- [ ] Test d'authorization pour /recap (compagnon ne peut consulter que son récapitulatif)
- [ ] Test de limite maximale pour bulk_validate (>100 IDs)
- [ ] Test de verrouillage de période future/passée
- [ ] Test de race condition pour bulk_validate (2 validateurs simultanés)
- [ ] Test de scheduler avec EventBus null/non-initialisé

**Couverture cible**: >= 90% des findings identifiés

---

## Points Positifs

- Validation de période verrouillée présente dans bulk_validate (même si test échoue)
- Scheduler utilise APScheduler correctement (bonne pratique)
- Événements correctement publiés pour traçabilité
- DTOs avec typage fort (dataclasses)
- Séparation des responsabilités (Use Case, Controller, Routes) respectée
- Scheduler gère les cas limites (mois courant + précédent)
- Erreurs catchées et loggées dans scheduler

---

## Violations RGPD Détectées

| Article | Violation | Finding |
|---------|-----------|---------|
| Article 5.1.b | Limitation de la finalité | SEC-PTG-P2-002 |
| Article 5.1.c | Minimisation des données | SEC-PTG-P2-005 |
| Article 30 | Registre des traitements | SEC-PTG-P2-008 |
| Article 32 | Intégrité des données | SEC-PTG-P2-001, SEC-PTG-P2-004 |
| Article 32 | Confidentialité | SEC-PTG-P2-002 |
| Article 32 | Disponibilité | SEC-PTG-P2-006 |

---

## Conclusion

**Le module pointages Phase 2 NE PEUT PAS être mis en production dans son état actuel.**

Les 3 findings CRITICAL/HIGH (SEC-PTG-P2-001, SEC-PTG-P2-002, SEC-PTG-P2-006) représentent des risques sérieux:
- Bypass d'autorisation
- Fuite de données de paie sensibles
- Déni de service total

**TOUTES les corrections IMMEDIATE doivent être appliquées AVANT le commit.**

Une fois corrigé:
1. Faire re-auditer par security-auditor
2. Exécuter les tests de sécurité (couverture >= 90%)
3. Mettre à jour SPECIFICATIONS.md
4. Documenter les contrôles d'accès dans .claude/security-guidelines.md

**Score actuel**: 5.5/10 ❌
**Score cible**: 9.0/10 ✅
**Statut**: **FAIL - Blocage mise en production**

---

**Rapport détaillé**: `.claude/reports/security_audit_pointages_phase2.json`
**Audité par**: Security Auditor Agent
**Date**: 2026-01-31
