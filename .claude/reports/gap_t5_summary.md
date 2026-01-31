# GAP-T5 : Résumé du diagnostic FDH-10 (Création auto pointages)

**Date**: 2026-01-31
**Analyste**: Claude Sonnet 4.5
**Statut**: ⚠️ **PARTIELLEMENT FONCTIONNEL**

---

## Résumé exécutif

Le mécanisme FDH-10 de création automatique de pointages depuis les affectations **fonctionne**, mais avec un **bug critique** : les heures prévues sont toujours fixées à **08:00** au lieu de reprendre la valeur réelle de l'affectation.

### Impact métier
- ✅ **Faible** si Greg Construction utilise uniquement des journées standard de 8h
- ❌ **Élevé** si l'entreprise utilise des demi-journées (4h), heures variables, etc.

### Urgence
- **Non bloquant** pour le lancement
- **Correction recommandée** avant mise en production si usage d'heures variables

---

## Ce qui fonctionne ✅

1. **Câblage du système**
   - ✅ `setup_planning_integration()` est bien appelé dans `main.py` (ligne 140)
   - ✅ `setup_planning_integration()` est bien appelé dans `seed_demo_data.py` (ligne 1366)
   - ✅ L'événement `affectation.created` est bien écouté

2. **Handler d'événements**
   - ✅ `handle_affectation_created` reçoit bien les événements
   - ✅ Extraction correcte de `affectation_id`, `utilisateur_id`, `chantier_id`, `date`, `created_by`
   - ✅ Fallback à "08:00" si `heures_prevues` manquant (ligne 77)

3. **Use case de création**
   - ✅ Filtrage des chantiers système (CONGES, MALADIE, RTT, FORMATION)
   - ✅ Vérification de doublons par `affectation_id`
   - ✅ Vérification de doublons par triplet `utilisateur_id/chantier_id/date`
   - ✅ Création du pointage avec `heures_normales = heures_prevues`
   - ✅ Création automatique de la feuille d'heures

4. **Tests unitaires**
   - ✅ 11/11 tests du module `pointages/test_event_handlers.py` passent
   - ✅ 4/4 tests d'événements du module `planning/test_create_affectation_use_case.py` passent

---

## Problèmes identifiés ❌

### 🔴 ISSUE-001 : Événement incomplet
**Fichier**: `backend/modules/planning/domain/events/affectation_created.py`
**Ligne**: 48-61

**Problème**: L'événement `AffectationCreatedEvent` ne transmet **PAS** le champ `heures_prevues`.

**Code actuel**:
```python
data={
    'affectation_id': affectation_id,
    'user_id': user_id,
    'chantier_id': chantier_id,
    'date': date_affectation.isoformat(),
    'heure_debut': heure_debut.isoformat() if heure_debut else None,
    'heure_fin': heure_fin.isoformat() if heure_fin else None,
    'note': note
    # ❌ 'heures_prevues' manquant
}
```

### 🔴 ISSUE-002 : Use case ne passe pas heures_prevues
**Fichier**: `backend/modules/planning/application/use_cases/create_affectation.py`
**Ligne**: 203-209

**Problème**: Le use case `CreateAffectationUseCase` ne passe **PAS** `heures_prevues` lors de la création de l'événement.

**Code actuel**:
```python
event = AffectationCreatedEvent(
    affectation_id=affectations[0].id,
    utilisateur_id=affectations[0].utilisateur_id,
    chantier_id=affectations[0].chantier_id,
    date=affectations[0].date,
    created_by=created_by,
    # ❌ heures_prevues=affectations[0].heures_prevues manquant
)
```

### ⚠️ ISSUE-003 : Fallback masque le problème
**Fichier**: `backend/modules/pointages/infrastructure/event_handlers.py`
**Ligne**: 77

**Problème**: Le handler utilise un fallback à `"08:00"` si `heures_prevues` n'est pas trouvé, ce qui masque le bug.

**Code actuel**:
```python
heures_prevues = _extract_event_field(event, 'heures_prevues') or "08:00"
```

**Note**: Ce fallback est une bonne pratique pour la robustesse, mais il empêche de détecter que `heures_prevues` manque dans l'événement.

---

## Scénario de bug

### Cas d'usage : Demi-journée
```python
# 1. L'utilisateur crée une affectation de 4h
affectation = Affectation(
    utilisateur_id=5,
    chantier_id=10,
    date=date(2026, 2, 1),
    heures_prevues=4.0,  # ✅ Demi-journée
    created_by=1
)
# affectation.heures_prevues == 4.0 ✅

# 2. L'événement est publié SANS heures_prevues
event = AffectationCreatedEvent(
    affectation_id=affectation.id,
    utilisateur_id=5,
    chantier_id=10,
    date=date(2026, 2, 1),
    created_by=1
    # ❌ heures_prevues manquant
)

# 3. Le handler utilise le fallback
heures_prevues = event.data.get('heures_prevues', None) or "08:00"
# heures_prevues == "08:00" ❌ (au lieu de "04:00")

# 4. Le pointage est créé avec 08:00
pointage = Pointage(
    heures_normales=Duree.from_string("08:00")  # ❌ 8h au lieu de 4h
)
```

**Résultat**: L'utilisateur voit 8h dans son pointage au lieu de 4h. Il devra **manuellement corriger** le pointage.

---

## Solution recommandée

### Correctif A : Modifier `AffectationCreatedEvent`
**Fichier**: `backend/modules/planning/domain/events/affectation_created.py`

**Changements**:
1. Ajouter `heures_prevues: Optional[float] = None` dans `__init__`
2. Inclure `'heures_prevues': heures_prevues` dans `data`

```python
def __init__(
    self,
    affectation_id: int,
    user_id: int,
    chantier_id: int,
    date_affectation: date,
    heures_prevues: Optional[float] = None,  # ✅ AJOUTER
    heure_debut: Optional[time] = None,
    heure_fin: Optional[time] = None,
    note: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    super().__init__(
        event_type='affectation.created',
        aggregate_id=str(affectation_id),
        data={
            'affectation_id': affectation_id,
            'user_id': user_id,
            'chantier_id': chantier_id,
            'date': date_affectation.isoformat(),
            'heures_prevues': heures_prevues,  # ✅ AJOUTER
            'heure_debut': heure_debut.isoformat() if heure_debut else None,
            'heure_fin': heure_fin.isoformat() if heure_fin else None,
            'note': note
        },
        metadata=metadata or {}
    )
```

### Correctif B : Modifier `CreateAffectationUseCase`
**Fichier**: `backend/modules/planning/application/use_cases/create_affectation.py`
**Ligne**: 203-209

**Changements**: Passer `heures_prevues` lors de la création de l'événement

```python
event = AffectationCreatedEvent(
    affectation_id=affectations[0].id,
    utilisateur_id=affectations[0].utilisateur_id,
    chantier_id=affectations[0].chantier_id,
    date=affectations[0].date,
    heures_prevues=affectations[0].heures_prevues,  # ✅ AJOUTER
    created_by=created_by,
)
```

### Correctif C : Mettre à jour les tests
**Fichier**: `backend/tests/unit/planning/test_affectation_events.py`

**Changements**: Ajouter des tests vérifiant que `heures_prevues` est bien dans le `data` de l'événement

```python
def test_should_include_heures_prevues_in_event(self):
    """Test: heures_prevues est inclus dans l'événement."""
    event = AffectationCreatedEvent(
        affectation_id=1,
        user_id=5,
        chantier_id=10,
        date_affectation=date(2026, 1, 30),
        heures_prevues=4.0,  # ✅ Demi-journée
    )

    assert event.data['heures_prevues'] == 4.0
```

---

## Fichiers analysés (10)

1. ✅ `backend/scripts/seed_demo_data.py`
2. ✅ `backend/main.py`
3. ✅ `backend/modules/pointages/infrastructure/event_handlers.py`
4. ✅ `backend/modules/pointages/application/use_cases/bulk_create_from_planning.py`
5. ❌ `backend/modules/planning/domain/events/affectation_created.py` (à corriger)
6. ❌ `backend/modules/planning/application/use_cases/create_affectation.py` (à corriger)
7. ✅ `backend/modules/planning/domain/entities/affectation.py`
8. ✅ `backend/tests/unit/pointages/test_event_handlers.py`
9. ✅ `backend/tests/unit/planning/test_affectation_events.py`
10. ✅ `backend/tests/unit/planning/test_create_affectation_use_case.py`

---

## Temps estimé de correction

- **Correctif A + B + C**: 30 minutes
- **Tests unitaires**: 15 minutes
- **Test intégration**: 15 minutes
- **Total**: ~1 heure

---

## Recommandation finale

**Verdict**: ⚠️ FDH-10 fonctionne **partiellement**.

### Pour lancement immédiat
Si Greg Construction utilise **uniquement** des journées standard de 8h → **OK, pas de correctif urgent**

### Pour usage production
Si l'entreprise utilise des **heures variables** (demi-journées, etc.) → **Correction obligatoire avant MEP**

### Priorisation
- **P0** : Appliquer correctif A + B + C
- **P1** : Ajouter tests d'intégration
- **P2** : Documenter le comportement attendu

---

**Rapport généré le**: 2026-01-31
**Fichiers de rapport**:
- `/Users/aptsdae/Hub-Chantier/.claude/reports/gap_t5_analysis.md` (détaillé)
- `/Users/aptsdae/Hub-Chantier/.claude/reports/gap_t5_analysis.json` (structured)
- `/Users/aptsdae/Hub-Chantier/.claude/reports/gap_t5_summary.md` (exécutif)
