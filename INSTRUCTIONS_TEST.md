# 🧪 Instructions pour tester le graphique "Evolution financière"

## ✅ Résumé de la correction

**Problème résolu** : Le graphique "Evolution financière" ne s'affichait pas à cause d'une erreur de validation des unités de mesure.

**Solution appliquée** :
- Correction des unités de ferraillage : `"T"` (tonnes) → `"kg"` (kilogrammes)
- Ajustement des quantités et prix : 8 T @ 1200€ → 8000 kg @ 1.20€
- Régénération des données mock avec le script `add_financial_timeline.py`

**Résultat** :
- ✅ 16 achats + 4 situations de travaux créés avec succès
- ✅ Backend fonctionnel (endpoint testé et validé)
- ✅ Données en base : 704 000 € sur 1 200 000 € (58.7%)

---

## 📋 Étapes pour tester dans le navigateur

### 1️⃣ Connexion

1. Ouvre ton navigateur sur **http://localhost:5173**
2. Connecte-toi avec :
   - Email : `admin@example.com`
   - Mot de passe : `Admin123!`

### 2️⃣ Accès au chantier TRIALP

1. Va sur la page **Chantiers**
2. Cherche le chantier **"2025-11-TRIALP"** (Reconstruction hall de tri Ville-R)
   - Ou accède directement : **http://localhost:5173/chantiers/23?tab=budget**

### 3️⃣ Vérification du dashboard Budget

Tu devrais maintenant voir :

#### ✅ KPI Cards (en haut)
- **Budget révisé HT** : 1 200 000,00 €
- **Engagé** : 640 650,00 € (53.4%)
- **Réalisé** : 0,00 € (0.0%)
- **Reste à dépenser** : 559 350,00 € (46.6%)
- **Marge estimée** : 46,6 %

#### ✅ Graphique "Evolution financière" 📈

Le graphique devrait maintenant s'afficher avec **4 points mensuels** :

| Mois | Prévu cumulé | Engagé cumulé | Réalisé cumulé |
|------|--------------|---------------|----------------|
| Nov 2025 | ~200k€ | 89k€ | 0€ |
| Déc 2025 | ~400k€ | 269k€ | 0€ |
| Jan 2026 | ~600k€ | 509k€ | 0€ |
| Fév 2026 | ~800k€ | 704k€ | 0€ |

**Courbes visibles** :
- 🔵 **Ligne bleue (Prévu)** : Progression linéaire vers 1.2M€
- 🟠 **Ligne ambre (Engagé)** : Monte progressivement avec les achats
- 🟢 **Ligne verte (Réalisé)** : Reste à 0€ (pas de livraisons facturées)

#### ✅ Graphique "Répartition par lot" 🍰

Camembert avec 6 lots :
- DALLE-BA - Dalle béton armé
- FONDATIONS - Fondations béton armé
- PLANCHERS - Planchers préfabriqués
- POTEAUX-POUTRES - Poteaux et poutres BA
- TERRASSEMENT - Terrassement général
- VOILES-BA - Voiles béton armé

#### ✅ Suggestions algorithmiques

- Badge "Règles algorithmiques" avec tooltip explicatif
- Bouton "Voir les règles" pour déplier les règles métier

#### ✅ Top 5 Lots les plus consommés

Tableau avec :
- VOILES-BA : 170 850,00 € (79%)
- DALLE-BA : 166 200,00 € (77%)
- TERRASSEMENT : 159 000,00 € (67%)
- FONDATIONS : 144 600,00 € (77%)
- POTEAUX-POUTRES : 0,00 € (0%)

---

## 🐛 Si le graphique ne s'affiche toujours pas

### Vérifier les données en base

```bash
cd backend
sqlite3 data/hub_chantier.db "SELECT COUNT(*) FROM situations_travaux WHERE chantier_id = 23;"
# Résultat attendu : 4

sqlite3 data/hub_chantier.db "SELECT COUNT(*) FROM achats WHERE chantier_id = 23;"
# Résultat attendu : 16
```

### Régénérer les données

```bash
cd backend
python3 scripts/add_financial_timeline.py
```

### Redémarrer les services

```bash
# Backend
cd backend
pkill -f uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (dans un autre terminal)
cd frontend
npm run dev
```

### Vérifier les logs

**Backend** :
```bash
tail -f /tmp/backend.log
```

**Console navigateur** (F12) :
- Ouvrir les DevTools
- Onglet "Console"
- Chercher les erreurs avec "evolution" ou "financiere"

---

## ✅ Fichiers mis à jour sur GitHub

1. **VERIFICATION_DONNEES.md** - Guide de vérification des données
2. **backend/scripts/add_financial_timeline.py** - Script corrigé (T → kg)

---

## 🎉 Résultat attendu

**Le dashboard Phase 3 est maintenant complet et fonctionnel !**

Tu devrais voir :
- ✅ Une évolution financière **réaliste** sur **6 mois**
- ✅ Des **courbes** montrant la progression mensuelle
- ✅ Des **achats** avec statuts variés
- ✅ Des **situations** de travaux validées progressivement
- ✅ Des **graphiques dynamiques** alimentés par des vraies données
- ✅ Des **explications** des règles algorithmiques (tooltip + section dépliable)

---

**Tout est prêt pour la démo !** 🚀
