# Workflow Feuilles d'Heures - Hub Chantier

> Document créé le 30 janvier 2026
> Analyse du workflow actuel et propositions de corrections

---

## 🔍 PROBLÈME IDENTIFIÉ

**Observation utilisateur** :
Dans la page Feuilles d'heures (screenshot fourni), on voit des personnes qui ne sont PAS des utilisateurs réels de la base de données :
- Julie ROUX
- Thomas LEROY
- Emma GARCIA
- Lucas MOREAU

**Utilisateurs réels dans seed_demo_data.py** :
- Super ADMIN
- Clémentine DELSALLE
- Robert BIANCHINI
- Nicolas DELSALLE
- Guillaume LOUYER
- Jérémy MONTMAYEUR
- Sébastien ACHKAR
- Carlos DE OLIVEIRA COVAS
- Abou DRAME
- Loic DUINAT
- Manuel FIGUEIREDO DE ALMEIDA
- Babaker HAROUN MOUSSA

**Diagnostic** :
Les personnes affichées dans les feuilles d'heures ne correspondent PAS aux utilisateurs réels du système.

---

## 📋 WORKFLOW ATTENDU (selon SPECIFICATIONS.md)

### Section 7 - FEUILLES D'HEURES

#### Fonctionnalités implémentées (FDH-01 à FDH-20)

| ID | Fonctionnalité | Description | Workflow |
|----|----------------|-------------|----------|
| **FDH-10** | **Création auto à l'affectation** | **Lignes pré-remplies depuis le planning** | ✅ **CRITIQUE** |

**Flux attendu** :

```
1. GESTION DES UTILISATEURS
   └─> Création d'un utilisateur (module users)
       ├─> Role : compagnon, chef_chantier, conducteur, admin
       ├─> Type : employe, interimaire, sous_traitant
       └─> Stockage en BD : users table

2. GESTION DES CHANTIERS
   └─> Création d'un chantier (module chantiers)
       ├─> Informations chantier
       └─> Stockage en BD : chantiers table

3. PLANNING OPÉRATIONNEL (FDH-10 déclencheur)
   └─> Affectation d'un utilisateur à un chantier
       ├─> Module : planning
       ├─> Création affectation (date_debut, date_fin, chantier_id, utilisateur_id)
       ├─> Stockage en BD : affectations table
       └─> ⚡ TRIGGER : Création automatique des pointages/feuilles d'heures

4. FEUILLES D'HEURES (FDH-01 à FDH-20)
   └─> Affichage vue Compagnons
       ├─> Source : utilisateurs RÉELS avec affectations actives
       ├─> Filtre : Uniquement utilisateurs avec role compagnon/chef_chantier
       ├─> Affichage : Feuilles d'heures par semaine
       └─> Saisie : Heures par jour/chantier

5. DASHBOARD (Section 2)
   └─> Affichage équipe/chantiers
       ├─> Source : utilisateurs RÉELS avec affectations
       └─> Posts ciblés par chantier/équipe

6. FICHE CHANTIER (Section 4, CHT-16)
   └─> Onglet Équipe
       ├─> Source : utilisateurs RÉELS affectés au chantier
       └─> Liste des collaborateurs assignés
```

---

## 🐛 ANOMALIES DÉTECTÉES

### 1. Source de données incorrecte dans Feuilles d'Heures

**Fichier** : `frontend/src/hooks/useFeuillesHeures.ts` (ligne 86-88)

```typescript
if (viewTab === 'compagnons') {
  const vueData = await pointagesService.getVueCompagnons(semaineDebut, utilisateurIds)
  setVueCompagnons(vueData)
}
```

**Problème potentiel** :
- `getVueCompagnons()` pourrait retourner des données mockées/hardcodées
- Les `utilisateurIds` pourraient pointer vers des IDs inexistants
- Le backend pourrait générer des données de test au lieu de données réelles

### 2. Filtrage des utilisateurs

**Fichier** : `frontend/src/hooks/useFeuillesHeures.ts` (ligne 76-81)

```typescript
const ROLES_CHANTIER = ['chef_chantier', 'compagnon']
const utilisateurIds = filterUtilisateurs.length > 0
  ? filterUtilisateurs
  : allActive.filter((u) => ROLES_CHANTIER.includes(u.role)).map((u) => Number(u.id))
```

**Analyse** :
- ✅ Bon : Filtre par roles chantier
- ❌ Risque : Si `allActive` est vide ou contient des données incorrectes

### 3. Vérification backend requise

**À vérifier** :
- `/api/pointages/vue-compagnons` endpoint
- Repository `FeuilleHeuresRepository`
- Join avec table `users`

---

## ✅ SOLUTION PROPOSÉE

### Option A : Vérification et correction simple (RECOMMANDÉ)

**Si le backend retourne déjà les bons utilisateurs :**

1. **Vérifier les données en base**
   ```bash
   # Vérifier les utilisateurs
   SELECT id, prenom, nom, role, is_active FROM users WHERE role IN ('compagnon', 'chef_chantier');

   # Vérifier les affectations actives
   SELECT a.id, a.utilisateur_id, u.prenom, u.nom, a.chantier_id, a.date_debut, a.date_fin
   FROM affectations a
   JOIN users u ON a.utilisateur_id = u.id
   WHERE a.date_fin >= CURRENT_DATE OR a.date_fin IS NULL;

   # Vérifier les pointages
   SELECT p.id, p.utilisateur_id, u.prenom, u.nom, p.chantier_id, p.date_pointage
   FROM pointages p
   JOIN users u ON p.utilisateur_id = u.id
   ORDER BY p.date_pointage DESC
   LIMIT 20;
   ```

2. **Corriger le seed si nécessaire**
   - S'assurer que `seed_demo_data.py` crée bien les affectations
   - S'assurer que les pointages sont créés pour les VRAIS utilisateurs

3. **Vérifier l'endpoint backend**
   ```python
   # modules/pointages/infrastructure/web/endpoints.py
   # L'endpoint doit bien joindre avec la table users
   ```

### Option B : Refactoring complet (si problème structurel)

**Si les données sont fondamentalement incorrectes :**

1. **Backend** : S'assurer que le repository joint correctement
   ```python
   # Dans FeuilleHeuresRepository ou PointageRepository
   query = (
       session.query(PointageModel, UserModel)
       .join(UserModel, PointageModel.utilisateur_id == UserModel.id)
       .filter(UserModel.is_active == True)
       .filter(UserModel.role.in_(['compagnon', 'chef_chantier']))
   )
   ```

2. **Frontend** : Afficher un debug temporaire
   ```typescript
   console.log('Utilisateurs chargés:', utilisateurs)
   console.log('Vue compagnons:', vueCompagnons)
   ```

3. **Seed** : Ajouter des affectations et pointages pour TOUS les compagnons

---

## 🔄 WORKFLOW CORRIGÉ COMPLET

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. CREATION UTILISATEUR (Module users)                         │
│    - Admin crée un compagnon : "Sébastien ACHKAR"             │
│    - Stocké en BD avec ID=7                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. CREATION CHANTIER (Module chantiers)                        │
│    - Admin crée : "Villa Moderne Duplex"                       │
│    - Stocké en BD avec ID=1                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. AFFECTATION (Module planning) ⚡ FDH-10                     │
│    - Admin affecte Sébastien ACHKAR au chantier Villa Duplex  │
│    - Affectation : user_id=7, chantier_id=1                   │
│    - Dates : 26/01/2026 → 31/01/2026                          │
│    - ✅ Création auto feuille heures pour la semaine          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. FEUILLES D'HEURES (Module pointages)                        │
│    - Page Feuilles d'heures → Onglet Compagnons               │
│    - Affiche : "Sébastien ACHKAR" (PAS "Julie ROUX")          │
│    - Chantier : "Villa Moderne Duplex"                         │
│    - Semaine : 26-31 janvier 2026                             │
│    - Cellules : Lundi 26, Mardi 27, ..., Vendredi 30         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. SAISIE HEURES                                               │
│    - Chef/Admin clique cellule Lundi 26                       │
│    - Saisit : 08:00 heures normales                           │
│    - Sauvegarde → pointages table                             │
│    - Affichage immédiat dans la grille                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. DASHBOARD & FICHE CHANTIER                                 │
│    - Dashboard : Affiche Sébastien dans équipe chantier       │
│    - Fiche chantier → Onglet Équipe : Liste Sébastien         │
│    - Fiche chantier → Onglet Feuilles heures : Ses heures     │
│    - COHÉRENCE TOTALE : Même source de données (users table)  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 ACTIONS IMMÉDIATES RECOMMANDÉES

### Phase 1 : Diagnostic (15 min)

1. ✅ Vérifier données en base
   ```bash
   cd backend
   python3 -m scripts.check_pointages_data  # À créer
   ```

2. ✅ Ajouter logs frontend
   ```typescript
   console.log('DEBUG - Utilisateurs:', utilisateurs)
   console.log('DEBUG - IDs filtres:', utilisateurIds)
   console.log('DEBUG - Vue compagnons:', vueCompagnons)
   ```

3. ✅ Tester endpoint API directement
   ```bash
   curl http://localhost:8000/api/pointages/vue-compagnons?semaine_debut=2026-01-27&utilisateur_ids=7,8,9
   ```

### Phase 2 : Correction (30 min)

**Si données incorrectes en base :**
1. Corriger `seed_demo_data.py` pour créer affectations + pointages
2. Re-seed la base : `python -m scripts.seed_demo_data`

**Si problème dans le code :**
1. Corriger le repository backend (join users)
2. Corriger le DTO pour inclure user.prenom, user.nom
3. Tester l'endpoint

### Phase 3 : Validation (15 min)

1. Vérifier que les vrais noms apparaissent (Sébastien ACHKAR, etc.)
2. Tester filtres par utilisateur
3. Tester vue Chantiers
4. Tester cohérence Dashboard ↔ Feuilles heures ↔ Fiche chantier

---

## 📝 CHECKLIST DE VALIDATION

- [ ] Les utilisateurs affichés correspondent aux utilisateurs réels en BD
- [ ] Les affectations créent automatiquement des feuilles d'heures (FDH-10)
- [ ] La vue Compagnons affiche les compagnons avec affectations actives
- [ ] La vue Chantiers affiche les chantiers avec affectations actives
- [ ] Le Dashboard affiche les mêmes utilisateurs
- [ ] La fiche chantier (onglet Équipe) affiche les mêmes utilisateurs
- [ ] La fiche chantier (onglet Feuilles heures) affiche les heures des mêmes utilisateurs
- [ ] Les filtres par utilisateur fonctionnent correctement
- [ ] Les totaux par ligne et par groupe sont corrects
- [ ] L'export fonctionne avec les données réelles

---

## 🔗 RÉFÉRENCES

- **CDC Section 7** : Feuilles d'heures (FDH-01 à FDH-20)
- **CDC Section 5** : Planning Opérationnel (affectations)
- **CDC Section 3** : Gestion des Utilisateurs
- **CDC Section 4 CHT-16** : Liste équipe affectée dans fiche chantier
- **CDC Section 2** : Dashboard avec équipes

---

## 📧 QUESTIONS À L'UTILISATEUR

1. **Origine des noms fictifs** : Savez-vous d'où viennent "Julie ROUX", "Thomas LEROY", etc. ?
   - Données de test hardcodées ?
   - Mock dans le frontend ?
   - Données d'un ancien seed ?

2. **Comportement attendu** : Voulez-vous voir :
   - Les VRAIS compagnons (Sébastien ACHKAR, Carlos DE OLIVEIRA COVAS, etc.) ?
   - Ou voulez-vous changer les noms dans le seed ?

3. **Affectations existantes** : Les compagnons sont-ils déjà affectés à des chantiers dans votre BD actuelle ?

---

**Prochaine étape** : Attendre confirmation utilisateur sur l'origine du problème et le comportement attendu.
