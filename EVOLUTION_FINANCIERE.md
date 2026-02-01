# Évolution Financière - Chantier TRIALP

## 📊 Vue d'ensemble

Le chantier **2025-11-TRIALP** (Reconstruction hall de tri Ville-R) dispose maintenant d'une évolution financière complète sur **6 mois** (novembre 2025 à avril 2026).

**Budget total** : 1 200 000 € HT

---

## 📈 Situations de travaux mensuelles

| Période | Situation | Montant période | Cumulé | % Budget | Statut |
|---------|-----------|-----------------|--------|----------|--------|
| Nov 2025 | SIT-2025-11 | 89 000 € | 89 000 € | 7.4% | ✅ Validée |
| Déc 2025 | SIT-2025-12 | 180 000 € | 269 000 € | 22.4% | ✅ Validée |
| Jan 2026 | SIT-2026-01 | 240 000 € | 509 000 € | 42.4% | ✅ Validée |
| Fév 2026 | SIT-2026-02 | 195 000 € | 704 000 € | 58.7% | 📝 Brouillon |
| Mar 2026 | - | - | - | - | 🔮 Prévisionnel |
| Avr 2026 | - | - | - | - | 🔮 Prévisionnel |

**État actuel** : 58.7% du budget consommé (704k€ sur 1.2M€)

---

## 🛒 Achats mensuels

| Mois | Nb achats | Montant total | Statuts |
|------|-----------|---------------|---------|
| Déc 2025 | 3 achats | 98 600 € | Livré |
| Jan 2026 | 6 achats | 354 200 € | Livré, Commandé, Validé |
| Fév 2026 | 4 achats | 265 850 € | Livré, Commandé, Validé, Demande |
| Mar 2026 | 2 achats | 145 600 € | Demande (prévisionnel) |
| Avr 2026 | 1 achat | 107 250 € | Demande (prévisionnel) |

**Total achats** : 16 achats sur 6 mois = **971 500 € HT**

---

## 🏗️ Chronologie des travaux

### Mois 1 - Novembre 2025 : Démarrage
- ✅ Terrassement phase 1 (300 m³)
- ✅ Évacuation terres (200 m³)
- **89k€** facturé

### Mois 2 - Décembre 2025 : Fondations
- ✅ Terrassement phase 2 (250 m³)
- ✅ Béton fondations (180 m³)
- ✅ Ferraillage fondations (8 T)
- **180k€** facturé

### Mois 3 - Janvier 2026 : Dalles et voiles
- ✅ Béton fondations finale (120 m³)
- ✅ Béton dalles RDC (400 m³)
- 🔄 Ferraillage dalles (12 T) - en commande
- ⏳ Béton voiles (200 m³) - validé
- **240k€** facturé

### Mois 4 - Février 2026 : Suite voiles (en cours)
- ✅ Béton dalle étages (450 m³)
- 🔄 Béton voiles étages (280 m³) - en commande
- ⏳ Ferraillage voiles (15 T) - validé
- ❓ Béton poteaux (150 m³) - en demande
- **195k€** en cours

### Mois 5 - Mars 2026 : Poteaux et planchers (prévisionnel)
- ❓ Béton poutres (130 m³)
- ❓ Planchers préfab étage 1 (400 m²)
- Non facturé

### Mois 6 - Avril 2026 : Suite planchers (prévisionnel)
- ❓ Planchers préfab étage 2 (550 m²)
- Non facturé

---

## 📊 Graphiques disponibles dans l'application

Le dashboard affiche maintenant :

1. **Évolution financière** : Courbe mensuelle (Nov 2025 → Avr 2026)
   - Ligne bleue : Engagé (achats)
   - Ligne orange : Prévu (budget)
   - Ligne verte : Réalisé (facturé)

2. **Répartition par lot** : Camembert montrant la distribution budgétaire

3. **Comparaison par lot** : Barres comparatives Prévu vs Engagé vs Réalisé

4. **Indicateurs prédictifs** :
   - Burn rate mensuel
   - Date d'épuisement estimée
   - Avancement financier

5. **Top 5 lots consommés** : Table avec % d'engagement

---

## 🎯 Pour visualiser

1. Connectez-vous sur http://localhost:5173
   - Email : `admin@example.com`
   - Mot de passe : `Admin123!`

2. Accédez à : **Chantiers → 2025-11-TRIALP → Onglet Budget**

3. Scrollez pour voir :
   - Les KPI cards (Budget, Engagé, Réalisé, Marge)
   - Le graphique "Évolution financière" avec **4 mois de données réelles**
   - Les suggestions algorithmiques avec explications

---

## ✅ Script de génération

Le script `backend/scripts/add_financial_timeline.py` crée automatiquement :
- 16 achats échelonnés sur 6 mois
- 4 situations de travaux (3 validées + 1 brouillon)
- Statuts progressifs : livre → commande → valide → demande

**Exécution** :
```bash
cd backend
python3 scripts/add_financial_timeline.py
```

---

**Résultat** : Une vraie évolution financière avec courbes, tendances et prédictions ! 📈
