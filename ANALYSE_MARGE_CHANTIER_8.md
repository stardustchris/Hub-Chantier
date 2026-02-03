# Rapport d'Analyse - Incohérence Marge Chantier 8 "Extension gymnase Ville-E"

**Date**: 2026-02-03
**Agent**: Python Pro
**Contexte**: Différence de marge entre dashboard individuel et vue consolidée

---

## 1. RÉSUMÉ EXÉCUTIF

**Problème identifié**: Le calcul de marge pour le chantier 8 diffère selon l'endpoint appelé :
- **Dashboard individuel** (`/chantiers/8/dashboard-financier`) : marge sans coûts fixes
- **Vue consolidée** (`/finances/consolidation`) : marge avec coûts fixes répartis

**Cause racine**: Le paramètre `ca_total_annee` n'est PAS passé lors de l'appel au dashboard individuel (ligne 1064 de `financier_routes.py`), alors qu'il est passé pour la vue consolidée (ligne 1165).

**Impact**: Les deux endpoints utilisent le même use case (`GetDashboardFinancierUseCase`) mais avec des paramètres différents, produisant des résultats incohérents.

---

## 2. DONNÉES DU CHANTIER 8

### Données financières (base de données)
```sql
-- Budget
montant_initial_ht    : 450 000,00 €
montant_avenants_ht   :  70 000,00 €
montant_revise_ht     : 520 000,00 €

-- Situation de travaux (dernière)
numero                : SIT-2026-GYMNASE
montant_cumule_ht     : 390 000,00 €  (prix de vente)

-- Achats réalisés (statut: valide, facture, paye)
total_realise         : 300 089,43 €

-- Coût main d'oeuvre (pointages validés)
cout_mo               :  31 704,00 €
```

### CA total entreprise
```
CA_TOTAL_ENTREPRISE (hardcodé) : 4 300 000,00 €
CA calculé (5 chantiers visibles): 1 462 500,00 €
```

---

## 3. CALCULS DE MARGE

### Formule BTP utilisée
```
Marge = (Prix Vente - Coût Revient) / Prix Vente × 100

Où :
  Prix Vente = situations de travaux facturées au client
  Coût Revient = achats réalisés + coût MO + coûts fixes répartis
```

### Cas 1: Dashboard individuel (SANS coûts fixes)

**Fichier**: `/backend/modules/financier/infrastructure/web/financier_routes.py`
**Ligne**: 1064

```python
result = use_case.execute(chantier_id)
# ⚠️ ca_total_annee non passé → reste None
```

**Calcul**:
```
Coût revient = 300 089,43 + 31 704,00 + 0
             = 331 793,43 €

Marge = (390 000,00 - 331 793,43) / 390 000,00 × 100
      = 14.92%
```

### Cas 2: Vue consolidée (AVEC coûts fixes répartis)

**Fichier**: `/backend/modules/financier/infrastructure/web/financier_routes.py`
**Ligne**: 1165

```python
CA_TOTAL_ENTREPRISE = Decimal("4300000")
result = use_case.execute(
    accessible_ids,
    statut_chantier=statut_chantier,
    ca_total_entreprise=CA_TOTAL_ENTREPRISE,  # ✅ Passé
)
```

**Calcul** (dans `consolidation_use_cases.py` lignes 211-216):
```
Quote-part coûts fixes = (390 000,00 / 4 300 000,00) × 600 000,00
                       = 54 418,60 €

Coût revient = 300 089,43 + 31 704,00 + 54 418,60
             = 386 212,03 €

Marge = (390 000,00 - 386 212,03) / 390 000,00 × 100
      = 0.97%
```

---

## 4. ANALYSE DES USE CASES

### `GetDashboardFinancierUseCase.execute()`

**Fichier**: `/backend/modules/financier/application/use_cases/dashboard_use_cases.py`
**Lignes**: 64-79, 124-140

```python
def execute(
    self, chantier_id: int, ca_total_annee: Optional[Decimal] = None
) -> DashboardFinancierDTO:
    """
    Args:
        ca_total_annee: CA total facturé sur l'année pour répartition des coûts fixes.
            Si None, les coûts fixes ne sont pas répartis.  # ⚠️ CLEF DU PROBLÈME
    """
```

**Logique de répartition** (lignes 127-133):
```python
if prix_vente_ht > Decimal("0"):
    # Répartition des coûts fixes au prorata du CA
    if ca_total_annee and ca_total_annee > Decimal("0"):  # ⚠️ Condition
        quote_part_couts_fixes = (
            prix_vente_ht / ca_total_annee
        ) * COUTS_FIXES_ANNUELS
        cout_revient += quote_part_couts_fixes  # ✅ Ajouté seulement si ca_total_annee fourni
```

### `GetVueConsolideeFinancesUseCase.execute()`

**Fichier**: `/backend/modules/financier/application/use_cases/consolidation_use_cases.py`
**Lignes**: 89-94, 149-161, 209-216

```python
def execute(
    self,
    user_accessible_chantier_ids: List[int],
    statut_chantier: Optional[str] = None,
    ca_total_entreprise: Optional[Decimal] = None,  # ✅ Reçu
) -> VueConsolideeDTO:
```

**Phase 1** : Calcul du CA total (lignes 149-161):
```python
if ca_total_entreprise is not None and ca_total_entreprise > Decimal("0"):
    ca_total_annee = ca_total_entreprise  # ✅ Utilisé directement
else:
    ca_total_annee = Decimal("0")
    for chantier_id in filtered_ids:
        if self._situation_repository:
            derniere_sit = self._situation_repository.find_derniere_situation(chantier_id)
            if derniere_sit:
                ca_total_annee += Decimal(str(derniere_sit.montant_cumule_ht))
```

**Phase 2** : Répartition par chantier (lignes 209-216):
```python
if prix_vente_ht > Decimal("0"):
    # Répartition des coûts fixes au prorata du CA
    if ca_total_annee > Decimal("0"):  # ✅ Toujours True car calculé
        quote_part_couts_fixes = (prix_vente_ht / ca_total_annee) * COUTS_FIXES_ANNUELS
        cout_revient += quote_part_couts_fixes
```

---

## 5. COMPARAISON DES APPELS

| Aspect | Dashboard individuel | Vue consolidée |
|--------|---------------------|----------------|
| **Endpoint** | `GET /chantiers/{id}/dashboard-financier` | `GET /finances/consolidation` |
| **Route (fichier)** | `financier_routes.py` ligne 1051 | `financier_routes.py` ligne 1149 |
| **Use case** | `GetDashboardFinancierUseCase` | `GetVueConsolideeFinancesUseCase` |
| **Paramètre `ca_total_annee`** | ❌ **NON PASSÉ** (ligne 1064) | ✅ **PASSÉ** = 4.3M€ (ligne 1165) |
| **Coûts fixes répartis** | ❌ Non (0 €) | ✅ Oui (54 418,60 €) |
| **Marge calculée** | **14.92%** | **0.97%** |
| **Différence** | - | **-13.95 points** |

---

## 6. RACINE DU PROBLÈME

### Code source problématique

**Fichier**: `/backend/modules/financier/infrastructure/web/financier_routes.py`

```python
# Ligne 1051-1067 : Dashboard individuel
@router.get("/chantiers/{chantier_id}/dashboard-financier")
async def get_dashboard_financier(
    chantier_id: int,
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_dashboard_financier_use_case),
):
    """Tableau de bord financier d'un chantier."""
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    try:
        result = use_case.execute(chantier_id)  # ❌ PROBLÈME : ca_total_annee manquant
        return result.to_dict()
    except BudgetNotFoundError:
        raise HTTPException(...)
```

```python
# Lignes 1149-1167 : Vue consolidée
@router.get("/finances/consolidation")
async def get_consolidation_finances(
    ...
):
    """Vue consolidée des finances multi-chantiers."""
    ...
    # Greg Construction : 4.3M€ de CA annuel (cf. specs projet)
    from decimal import Decimal
    CA_TOTAL_ENTREPRISE = Decimal("4300000")  # ✅ Défini

    result = use_case.execute(
        accessible_ids,
        statut_chantier=statut_chantier,
        ca_total_entreprise=CA_TOTAL_ENTREPRISE,  # ✅ Passé
    )
    return result.to_dict()
```

### Pourquoi c'est un problème

1. **Incohérence métier** : Un même chantier a deux marges différentes selon où on le consulte
2. **Confusion utilisateur** : Les marges affichées ne sont pas comparables
3. **Mauvaise décision** : Une marge de 14.92% peut sembler correcte, alors que la vraie marge BTP (avec charges) est proche de 0%
4. **Non-conformité Clean Architecture** : Le use case accepte un paramètre optionnel mais la route ne le fournit pas systématiquement

---

## 7. SOLUTION PROPOSÉE

### Option A : Passer `ca_total_annee` au dashboard individuel (RECOMMANDÉ)

**Avantages** :
- Unifie les calculs de marge
- Conforme à la formule BTP standard
- Cohérence entre tous les affichages

**Modification** :

```python
# Fichier: /backend/modules/financier/infrastructure/web/financier_routes.py
# Ligne 1064

@router.get("/chantiers/{chantier_id}/dashboard-financier")
async def get_dashboard_financier(
    chantier_id: int,
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_dashboard_financier_use_case),
):
    """Tableau de bord financier d'un chantier."""
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    try:
        # Greg Construction : 4.3M€ de CA annuel (cf. specs projet)
        from decimal import Decimal
        CA_TOTAL_ENTREPRISE = Decimal("4300000")

        result = use_case.execute(chantier_id, ca_total_annee=CA_TOTAL_ENTREPRISE)  # ✅ FIX
        return result.to_dict()
    except BudgetNotFoundError:
        raise HTTPException(...)
```

**Impact** :
- Chantier 8 : marge passe de 14.92% à **0.97%**
- Tous les chantiers voient leur marge recalculée avec coûts fixes

### Option B : Calculer le CA dynamiquement

**Avantages** :
- CA exact basé sur les vraies situations
- Pas de valeur hardcodée

**Inconvénient** :
- Nécessite un repository `SituationRepository` dans le dashboard use case
- Plus complexe

```python
# Nécessiterait modification du use case pour calculer CA total
# Similaire à consolidation_use_cases.py lignes 154-160
```

### Option C : Documentation explicite de la différence

**Avantages** :
- Pas de code à modifier
- Transparence sur les deux méthodes

**Inconvénient** :
- Ne résout pas l'incohérence
- Confusion persistante pour les utilisateurs

---

## 8. RECOMMANDATIONS

### Immédiat
1. ✅ **Implémenter l'Option A** : Passer `CA_TOTAL_ENTREPRISE` au dashboard individuel
2. ✅ **Tester** : Vérifier que la marge du chantier 8 devient cohérente (~0.97%)
3. ✅ **Valider** : S'assurer que tous les chantiers calculent la marge avec coûts fixes

### Moyen terme
4. 📋 **Extraire la constante** : Créer une config centralisée pour `CA_TOTAL_ENTREPRISE`
   ```python
   # backend/shared/domain/constants.py
   CA_ANNUEL_ENTREPRISE = Decimal("4300000")  # Greg Construction 2026
   ```

5. 📋 **Ajouter tests** : Garantir cohérence marge dashboard vs consolidation
   ```python
   # test_marge_coherence.py
   def test_marge_dashboard_equals_consolidation_for_same_chantier():
       """La marge d'un chantier doit être identique dashboard vs consolidation."""
   ```

### Long terme
6. 🔄 **Calcul dynamique du CA** : Récupérer le CA réel depuis les situations au lieu de hardcoder
7. 📊 **Indicateur de confiance** : Afficher si la marge inclut ou non les coûts fixes
8. 🔍 **Audit** : Vérifier si d'autres use cases ont des paramètres optionnels non fournis

---

## 9. FICHIERS CONCERNÉS

### À modifier
- `/backend/modules/financier/infrastructure/web/financier_routes.py` (ligne 1064)

### Référence (lecture seule)
- `/backend/modules/financier/application/use_cases/dashboard_use_cases.py`
- `/backend/modules/financier/application/use_cases/consolidation_use_cases.py`

### Tests à créer/modifier
- `/backend/tests/unit/financier/test_dashboard_use_cases.py`
- `/backend/tests/integration/financier/test_marge_coherence.py` (nouveau)

---

## 10. VALIDATION

### Tests manuels après correction

```bash
# 1. Appeler le dashboard individuel
curl -X GET "http://localhost:8000/api/v1/finances/chantiers/8/dashboard-financier" \
  -H "Authorization: Bearer <token>"

# Vérifier : kpi.marge_estimee ≈ 0.97%

# 2. Appeler la vue consolidée
curl -X GET "http://localhost:8000/api/v1/finances/consolidation" \
  -H "Authorization: Bearer <token>"

# Vérifier : chantiers[id=8].marge_estimee_pct ≈ 0.97%

# 3. Comparer : les deux valeurs doivent être IDENTIQUES
```

### Tests unitaires

```python
def test_dashboard_avec_ca_total_annee():
    """GetDashboardFinancierUseCase avec ca_total_annee doit répartir les coûts fixes."""
    # Arrange
    ca_total = Decimal("4300000")

    # Act
    result = use_case.execute(chantier_id=8, ca_total_annee=ca_total)

    # Assert
    assert result.kpi.marge_estimee == "0.97"  # Avec coûts fixes
    assert result.kpi.marge_statut == "calculee"
```

---

## 11. ANNEXES

### A. Constantes utilisées

```python
# dashboard_use_cases.py ligne 40
COUTS_FIXES_ANNUELS = Decimal("600000")

# consolidation_use_cases.py ligne 25
COUTS_FIXES_ANNUELS = Decimal("600000")

# financier_routes.py lignes 1160 et 1213
CA_TOTAL_ENTREPRISE = Decimal("4300000")
```

### B. Formule de répartition des coûts fixes

```
Quote-part chantier = (CA chantier / CA total entreprise) × Coûts fixes annuels

Pour le chantier 8 :
Quote-part = (390 000 / 4 300 000) × 600 000
           = 0.0906976744 × 600 000
           = 54 418,60 €
```

### C. Vérification données

```sql
-- Dernière situation chantier 8
SELECT montant_cumule_ht FROM situations_travaux
WHERE chantier_id = 8
ORDER BY id DESC LIMIT 1;
-- Résultat : 390 000,00 €

-- Achats réalisés chantier 8
SELECT SUM(prix_unitaire_ht * quantite) FROM achats
WHERE chantier_id = 8
AND statut IN ('valide', 'facture', 'paye');
-- Résultat : 300 089,43 €

-- Coût MO chantier 8
SELECT SUM((heures_normales_minutes + heures_supplementaires_minutes) / 60.0 * u.taux_horaire)
FROM pointages p
JOIN users u ON p.utilisateur_id = u.id
WHERE p.chantier_id = 8 AND p.statut = 'valide';
-- Résultat : 31 704,00 €
```

---

**Fin du rapport**

*Généré par Python Pro Agent - 2026-02-03*
