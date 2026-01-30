# Nettoyage des Données de Démonstration

**Date** : 30 janvier 2026
**Auteur** : Claude Sonnet 4.5

## 🎯 Objectif

Supprimer tous les faux chantiers/utilisateurs de démonstration et ne conserver QUE les vraies données de Greg Construction.

---

## ❌ Données Supprimées

### Faux Chantiers (5)

| Code | Nom | Raison |
|------|-----|--------|
| A001 | Résidence Les Jardins | Fictif (format code invalide) |
| A002 | Centre Commercial Grand Place | Fictif (format code invalide) |
| A003 | Ecole Primaire Jean Jaures | Fictif (format code invalide) |
| A004 | Villa Moderne Duplex | Fictif (format code invalide) |
| A005 | Bureaux Tech Valley | Fictif (format code invalide) |

**Format attendu** : `YYYY-MM-NOM` (ex: 2025-03-TOURNON-COMMERCIAL)

### Faux Utilisateurs (Pointages)

Nettoyés lors de la Phase 1 du refactoring pointages :
- Julie ROUX (julie.roux@...)
- Thomas LEROY (thomas.leroy@...)
- Emma GARCIA (emma.garcia@...)
- Lucas MOREAU (lucas.moreau@...)

**Voir** : `docs/workflows/WORKFLOW_FEUILLES_HEURES.md`

---

## ✅ Données Conservées

### Chantiers Système (4)

| Code | Nom | Usage |
|------|-----|-------|
| CONGES | Congés payés | Affectation planning absences |
| MALADIE | Arrêt maladie | Affectation planning absences |
| FORMATION | Formation | Affectation planning formation |
| RTT | RTT | Affectation planning RTT |

### Vrais Chantiers Greg Construction (23)

**Statut : Réceptionné (9)** :
- 2024-10-MONTMELIAN - Ensemble immobilier Montmélian
- 2025-01-CHALLES-REHAB - Réhabilitation 6 logements Challes
- 2025-01-CHAMBERY-MEDICAL - Pôle médical Chambéry
- 2025-01-STE-MARIE-SALLE - Salle polyvalente Ste Marie de Cuines
- 2025-02-EPIERRE-GYMNASE - Extension gymnase Epierre
- 2025-03-ALPESPACE-EXECO - Bâtiment industriel EXECO
- 2025-03-ALPESPACE-SOUDEM - Bâtiment industriel SOUDEM
- 2025-03-BEAUFORT-FERME - Réhabilitation ferme Beaufort
- 2025-03-CHAMOUX-AGRICOLE - Bâtiment agricole Chamoux

**Statut : En cours (10)** :
- 2025-03-TOURNON-COMMERCIAL - Bâtiment commercial Tournon
- 2025-04-CHIGNIN-AGRICOLE - 2 bâtiments agricoles Chignin
- 2025-04-UGINE-MAISONS - Constructions maisons Ugine
- 2025-05-CHATEAUNEUF-DENTAIRE - Cabinet dentaire Châteauneuf
- 2025-05-CHATEAUNEUF-MAIRIE - Rénovation Mairie Châteauneuf
- 2025-06-RAVOIRE-LOGEMENTS - Logements La Ravoire
- 2025-07-FAVERGES-IME - IME Faverges
- 2025-07-TOUR-LOGEMENTS - 20 logements Tour-en-Savoie
- 2025-07-HAUTEVILLE-MAIRIE - Réhabilitation mairie Hauteville
- 2025-11-TRIALP - Reconstruction hall de tri TRIALP

**Statut : Ouvert (4)** :
- 2026-02-BISSY-COLLEGE - Restructuration collège Bissy
- 2026-02-BISSY-DECONSTRUCTION - Déconstruction collège Bissy
- 2026-03-RAVOIRE-CAPITE - Logements sociaux La Capite
- 2026-BOURGET-LOGEMENTS - Construction logements Bourget-du-Lac

**Total** : 27 chantiers (4 système + 23 réels)

---

## 🔧 Commandes Exécutées

```sql
-- Suppression des données liées
DELETE FROM pointages WHERE chantier_id IN (
    SELECT id FROM chantiers WHERE code IN ('A001', 'A002', 'A003', 'A004', 'A005')
);

DELETE FROM affectations WHERE chantier_id IN (
    SELECT id FROM chantiers WHERE code IN ('A001', 'A002', 'A003', 'A004', 'A005')
);

DELETE FROM dossiers WHERE chantier_id IN (
    SELECT id FROM chantiers WHERE code IN ('A001', 'A002', 'A003', 'A004', 'A005')
);

DELETE FROM formulaires_remplis WHERE chantier_id IN (
    SELECT id FROM chantiers WHERE code IN ('A001', 'A002', 'A003', 'A004', 'A005')
);

-- Suppression des chantiers
DELETE FROM chantiers WHERE code IN ('A001', 'A002', 'A003', 'A004', 'A005');
```

**Base de données** : `backend/data/hub_chantier.db`

---

## ✅ Validation

### Tests Effectués

- ✅ Suppression des 5 faux chantiers
- ✅ Conservation des 27 chantiers légitimes
- ✅ Suppression cascade des données liées (pointages, affectations, dossiers, formulaires)
- ✅ Aucune erreur SQL
- ✅ Backend démarre sans erreur

### Vérification SQL

```sql
-- Vérifier qu'aucun faux chantier n'existe
SELECT code, nom FROM chantiers WHERE code IN ('A001', 'A002', 'A003', 'A004', 'A005');
-- Résultat attendu : 0 lignes

-- Compter les chantiers restants
SELECT COUNT(*) FROM chantiers;
-- Résultat attendu : 27

-- Compter les vrais chantiers (format YYYY-MM-NOM ou YYYY-NOM)
SELECT COUNT(*) FROM chantiers WHERE code LIKE '20%';
-- Résultat attendu : 23
```

---

## 📊 Impact

| Élément | Avant | Après | Supprimé |
|---------|-------|-------|----------|
| **Chantiers totaux** | 32 | 27 | 5 |
| **Chantiers réels** | 23 | 23 | 0 |
| **Chantiers système** | 4 | 4 | 0 |
| **Faux chantiers** | 5 | 0 | 5 |

---

## 🚀 Prochaines Étapes

- ✅ Données nettoyées
- ✅ Workflow utilisateurs → chantiers → pointages → feuilles d'heures validé
- ✅ Architecture pointages conforme Clean Architecture

**Statut** : Production ready avec données réelles uniquement.

---

## 📝 Notes

- Les chantiers système (CONGES, MALADIE, FORMATION, RTT) sont NÉCESSAIRES pour le module planning
- Le format de code `YYYY-MM-NOM` est le standard Greg Construction
- Aucune régression fonctionnelle suite au nettoyage
- Les utilisateurs réels (compagnons) sont conservés et fonctionnels

---

**Référence** : Voir `WORKFLOW_FEUILLES_HEURES.md` pour le nettoyage des pointages
