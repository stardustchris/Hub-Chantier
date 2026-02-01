# 📊 Résumé des Données Mock - Dashboard Financier Phase 3

## ✅ Données créées avec succès !

### 🎯 Vue d'ensemble

**Chantier** : 2025-11-TRIALP (Reconstruction hall de tri Ville-R)
**Budget total** : 1 200 000 € HT
**Période** : Novembre 2025 → Avril 2026 (6 mois)
**État actuel** : 58.7% consommé (704 000 € sur 1.2M €)

---

## 📈 Évolution Financière Mensuelle

```
Mois        Situation     Montant      Cumulé        % Budget   État
─────────────────────────────────────────────────────────────────────
11/2025     SIT-2025-11    89 000 €     89 000 €       7.4%     ✅ Validée
12/2025     SIT-2025-12   180 000 €    269 000 €      22.4%     ✅ Validée
01/2026     SIT-2026-01   240 000 €    509 000 €      42.4%     ✅ Validée
02/2026     SIT-2026-02   195 000 €    704 000 €      58.7%     📝 Brouillon
03/2026     (prévisionnel)    -            -            -       🔮 À venir
04/2026     (prévisionnel)    -            -            -       🔮 À venir
```

**📊 Progression mensuelle** :
- Nov : +7.4% → Terrassement
- Déc : +15% → Fondations
- Jan : +20% → Dalles + Voiles
- Fév : +16.3% → Suite voiles (en cours)

---

## 🛒 Achats Détaillés (16 achats sur 6 mois)

### Novembre 2025 (2 achats - 89k€)
- ✅ Terrassement phase 1 (300 m³ × 280€)
- ✅ Évacuation terres (200 m³ × 25€)

### Décembre 2025 (3 achats - 99k€)
- ✅ Terrassement phase 2 (250 m³ × 280€)
- ✅ Béton C30/37 semelles (180 m³ × 450€)
- ✅ Ferraillage fondations (8 T × 1200€)

### Janvier 2026 (4 achats - 354k€)
- ✅ Béton fondations finale (120 m³ × 450€)
- ✅ Béton C25/30 dalle RDC (400 m³ × 180€)
- 🔄 Ferraillage dalles (12 T × 1100€) - **Commandé**
- ⏳ Béton C30/37 voiles (200 m³ × 320€) - **Validé**

### Février 2026 (4 achats - 266k€)
- ✅ Béton dalle étages (450 m³ × 180€)
- 🔄 Béton voiles étages (280 m³ × 320€) - **Commandé**
- ⏳ Ferraillage voiles (15 T × 1150€) - **Validé**
- ❓ Béton poteaux (150 m³ × 520€) - **Demande**

### Mars 2026 (2 achats prévisionnels - 146k€)
- ❓ Béton poutres (130 m³ × 520€) - **Demande**
- ❓ Planchers préfab étage 1 (400 m² × 195€) - **Demande**

### Avril 2026 (1 achat prévisionnel - 107k€)
- ❓ Planchers préfab étage 2 (550 m² × 195€) - **Demande**

**Total achats** : 971 500 € HT

---

## 📊 Ce que tu verras dans le Dashboard

### 1️⃣ KPI Cards (en haut)
- **Budget révisé** : 1 200 000 € HT
- **Engagé** : ~125 000 € (achats validés/commandés)
- **Réalisé** : 0 € (pas encore facturé côté fournisseur)
- **Reste à dépenser** : ~1 075 000 €
- **Marge estimée** : ~89.4%

### 2️⃣ Graphique "Évolution financière" 📈
**Courbes sur 6 mois (Nov 2025 → Avr 2026)** :
- 🔵 **Ligne Engagé** : Monte progressivement de 0 → 971k€
- 🟠 **Ligne Prévu** : Progression linéaire vers 1.2M€
- 🟢 **Ligne Réalisé** : Reste à 0€ (pas de livraisons facturées)

**Points de données** :
- Nov 25 : 89k€
- Déc 25 : 269k€
- Jan 26 : 509k€
- Fév 26 : 704k€
- Mar 26 : Prévisionnel
- Avr 26 : Prévisionnel

### 3️⃣ Graphique "Répartition par lot" 🍰
Camembert montrant la distribution budgétaire :
- DALLE-BA : 216 000 € (18%)
- VOILES-BA : 217 600 € (18.1%)
- TERRASSEMENT : 238 000 € (19.8%)
- FONDATIONS : 189 000 € (15.8%)
- POTEAUX-POUTRES : 145 600 € (12.1%)
- PLANCHERS : 185 250 € (15.4%)

### 4️⃣ Top 5 Lots Consommés
| Lot | Engagé | % | Écart |
|-----|--------|---|-------|
| FONDATIONS | 52 200 € | 28% | 136 800 € |
| DALLE-BA | 25 650 € | 12% | 190 350 € |
| TERRASSEMENT | 17 500 € | 7% | 220 500 € |
| VOILES-BA | 0 € | 0% | 217 600 € |
| POTEAUX-POUTRES | 0 € | 0% | 145 600 € |

### 5️⃣ Indicateurs Prédictifs
- **Burn rate** : ~176 000 €/mois (basé sur historique)
- **Mois restants** : ~6.8 mois
- **Date épuisement** : ~Août 2026
- **Avancement financier** : 58.7%

### 6️⃣ Suggestions Algorithmiques
✅ **Règle déclenchée** :
- "CREATE SITUATION → Créer une situation de travaux"
  _(Le budget dépasse 100 000 EUR)_

Avec tooltip et section dépliable "Voir les règles" affichant :
- Budget > 100k€ → Créer situation
- Dépassement > 10% → Alerte burn rate
- Marge < 15% → Optimiser coûts

---

## 🎬 Pour Visualiser

### Étape 1 : Accéder à l'application
```
URL : http://localhost:5173
```

### Étape 2 : Se connecter
```
Email : admin@example.com
Mot de passe : Admin123!
```

### Étape 3 : Naviguer vers le chantier
```
Menu : Chantiers → 2025-11-TRIALP → Onglet "Budget"
```

### Étape 4 : Explorer les données
- **Scroll en haut** → Voir les 5 KPI cards avec jauges
- **Graphique Evolution** → Courbes sur 6 mois avec 4 points de données réels
- **Graphique Répartition** → Camembert des 6 lots budgétaires
- **Suggestions** → Badge "Règles algorithmiques" avec tooltip + section dépliable
- **Scroll en bas** → Tableau des lots avec montants engagés/réalisés/écarts

---

## 🔧 Régénérer les Données

Si besoin de recréer la timeline :

```bash
cd backend
python3 scripts/add_financial_timeline.py
```

Le script :
1. Supprime les achats/situations existants pour TRIALP
2. Crée 16 achats échelonnés sur 6 mois
3. Crée 4 situations de travaux (3 validées + 1 brouillon)
4. Affiche un résumé détaillé

---

## 📦 Fichiers Importants

| Fichier | Description |
|---------|-------------|
| `backend/scripts/add_financial_timeline.py` | Script de génération de la timeline |
| `backend/data/hub_chantier.db` | Base SQLite (1.4 MB) |
| `EVOLUTION_FINANCIERE.md` | Documentation détaillée de l'évolution |
| `frontend/src/components/financier/SuggestionsPanel.tsx` | Composant avec tooltip + règles |

---

## ✅ Résultat Final

**Tu as maintenant** :
- ✅ Une évolution financière **réaliste** sur **6 mois**
- ✅ Des **courbes** montrant la progression mensuelle
- ✅ Des **achats** avec statuts variés (livré → commandé → validé → demande)
- ✅ Des **situations** de travaux validées progressivement
- ✅ Des **graphiques dynamiques** alimentés par des vraies données
- ✅ Des **explications** des règles algorithmiques (tooltip + section dépliable)

**Le dashboard Phase 3 est complet et prêt pour la démo** ! 🚀
