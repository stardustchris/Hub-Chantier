# Fix - Incohérence calcul de marge chantier 8

**Date**: 2026-02-03
**Agent**: Python Pro
**Issue**: Marge différente selon endpoint (dashboard vs consolidation)

---

## Problème

Chantier 8 "Extension gymnase Ville-E" :
- **Dashboard individuel** : ~15% de marge (SANS coûts fixes)
- **Vue consolidée** : ~1% de marge (AVEC coûts fixes répartis)

**Cause** : Le paramètre `ca_total_annee` n'était pas passé au use case du dashboard.

---

## Solution appliquée

### Fichier modifié
`/backend/modules/financier/infrastructure/web/financier_routes.py`

**Ligne 1064** - Ancienne version :
```python
result = use_case.execute(chantier_id)
```

**Nouvelle version** :
```python
# Greg Construction : 4.3M€ de CA annuel (cf. specs projet)
from decimal import Decimal
CA_TOTAL_ENTREPRISE = Decimal("4300000")

result = use_case.execute(chantier_id, ca_total_annee=CA_TOTAL_ENTREPRISE)
```

---

## Impact

### Avant correction
```
Prix vente HT    : 390 000,00 €
Achats réalisés  : 300 089,43 €
Coût MO          :  31 704,00 €
Coûts fixes      :       0,00 €  ❌ NON répartis
─────────────────────────────────
Coût revient     : 331 793,43 €
Marge            :     14.92 %
```

### Après correction
```
Prix vente HT    : 390 000,00 €
Achats réalisés  : 300 089,43 €
Coût MO          :  31 704,00 €
Coûts fixes      :  54 418,60 €  ✅ Répartis au prorata
─────────────────────────────────
Coût revient     : 386 212,03 €
Marge            :      0.97 %
```

**Formule de répartition** :
```
Quote-part = (390 000 / 4 300 000) × 600 000 = 54 418,60 €
```

---

## Tests créés

`/backend/tests/integration/financier/test_marge_coherence.py`

1. **test_marge_dashboard_equals_consolidation** : Vérifie que les deux endpoints donnent la même marge
2. **test_dashboard_sans_ca_total_annee_exclut_couts_fixes** : Valide le comportement sans CA
3. **test_consolidation_calcule_ca_si_non_fourni** : Teste le calcul dynamique du CA
4. **test_marge_en_attente_sans_situation** : Statut "en_attente" sans situation
5. **test_marge_calculee_avec_situation** : Statut "calculee" avec situation

---

## Validation

```bash
# Backend
cd /Users/aptsdae/Hub-Chantier/backend
pytest tests/integration/financier/test_marge_coherence.py -v

# API manuelle
curl -X GET "http://localhost:8000/api/v1/finances/chantiers/8/dashboard-financier" \
  -H "Authorization: Bearer <token>"
# Vérifier : kpi.marge_estimee ≈ "0.97"
```

---

## Documentation complète

Voir `/Users/aptsdae/Hub-Chantier/ANALYSE_MARGE_CHANTIER_8.md` pour :
- Analyse détaillée des use cases
- Comparaison ligne par ligne des calculs
- Recommandations moyen/long terme
- Annexes avec requêtes SQL

---

**Résultat** : Marge désormais cohérente entre dashboard individuel et vue consolidée ✅
