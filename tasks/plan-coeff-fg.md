# Plan : Coefficient FG sur déboursé sec — Alignement devis + dashboard

## Constat

| Composant | Méthode actuelle | Problème |
|-----------|-----------------|----------|
| **Devis** | `coefficient_frais_generaux = 12%` sur déboursé sec | Fonctionne, mais le 12% par défaut est arbitraire |
| **Dashboard** | `(CA_chantier / 4.3M) × 600k` prorata CA hardcodé | Faux : répartition injuste, valeurs en dur |
| **P&L** | Même logique que dashboard | Même problème |

## Cible

Un **coefficient unique configurable au niveau entreprise**, appliqué sur le déboursé sec.
Utilisé par : devis (défaut), dashboard, P&L.

Formule dashboard/P&L :
```
FG_chantier = (cout_mo_charge + cout_achats + cout_materiel) × COEFF_FG / 100
```

Valeur par défaut Greg : **19%** (= 600k / ~3.16M de déboursés annuels estimés).

---

## Étapes d'implémentation

### 1. Backend — `calcul_financier.py`
- Remplacer `COUTS_FIXES_ANNUELS = 600000` par `COEFF_FRAIS_GENERAUX = Decimal("19")`
- Refactorer `calculer_quote_part_frais_generaux()` :
  ```python
  def calculer_quote_part_frais_generaux(
      debourse_sec: Decimal,
      coeff_frais_generaux: Decimal = COEFF_FRAIS_GENERAUX,
  ) -> Decimal:
      return arrondir_montant(debourse_sec * coeff_frais_generaux / Decimal("100"))
  ```
- `COUTS_FIXES_ANNUELS` → supprimé (plus utilisé)

### 2. Backend — `dashboard_use_cases.py`
- Supprimer le bloc `ca_total_annee` auto-calculé (plus besoin)
- Calculer `debourse_sec = cout_achats + cout_mo + cout_materiel`
- Appeler `calculer_quote_part_frais_generaux(debourse_sec)`
- Supprimer le paramètre `ca_total_annee` de `execute()`

### 3. Backend — `pnl_use_cases.py`
- Même changement : remplacer prorata CA par coefficient sur déboursé sec
- La ligne "Frais généraux (quote-part)" dans le P&L utilise le nouveau calcul

### 4. Backend — `financier_routes.py` (route dashboard)
- Supprimer le `CA_TOTAL_ENTREPRISE = Decimal("4300000")` hardcodé
- L'appel `use_case.execute(chantier_id)` sans `ca_total_annee`

### 5. Backend — Devis `devis.py` entité
- Changer le défaut : `coefficient_frais_generaux = COEFF_FRAIS_GENERAUX` (19%)
  au lieu de `Decimal("12")` hardcodé
- Import depuis `shared.domain.calcul_financier`

### 6. Nettoyage
- Supprimer `COUTS_FIXES_ANNUELS` de calcul_financier.py
- Supprimer tout code lié à `ca_total_annee` dans dashboard/P&L
- Vérifier les tests qui référencent ces valeurs

---

## Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `backend/shared/domain/calcul_financier.py` | Nouvelle constante + refactor fonction |
| `backend/modules/financier/application/use_cases/dashboard_use_cases.py` | Simplifier : coeff sur déboursé sec |
| `backend/modules/financier/application/use_cases/pnl_use_cases.py` | Idem |
| `backend/modules/financier/infrastructure/web/financier_routes.py` | Supprimer CA hardcodé |
| `backend/modules/devis/domain/entities/devis.py` | Default = COEFF_FRAIS_GENERAUX |
| Tests impactés | Adapter les mocks/assertions |

## Fichiers NON modifiés

- `calcul_totaux_use_cases.py` (devis) : utilise déjà `devis.coefficient_frais_generaux` ✅
- `RentabiliteSidebar.tsx` : utilise déjà le coefficient ✅
- Frontend dashboard/P&L : consomme l'API existante, aucun champ ne change ✅
- `MargesAdjustModal.tsx` : permet déjà d'ajuster le coeff par devis ✅

## Impact utilisateur

- Dashboard : la marge va baisser (les FG sont maintenant calculés correctement)
- Devis : le coefficient par défaut passe de 12% à 19% (nouveaux devis)
- Devis existants : inchangés (le coeff est stocké par devis)
