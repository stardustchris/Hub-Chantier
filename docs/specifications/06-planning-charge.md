## 6. PLANNING DE CHARGE

### 6.1 Vue d'ensemble

Le Planning de Charge est un tableau de bord strategique permettant de visualiser la charge de travail par chantier et par semaine, avec gestion des besoins par type/metier et indicateurs de taux d'occupation. Il permet d'anticiper les recrutements et d'optimiser l'affectation des ressources.

### 6.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| PDC-01 | Vue tabulaire | Chantiers en lignes, semaines en colonnes | ✅ |
| PDC-02 | Compteur chantiers | Badge indiquant le nombre total (ex: 107 Chantiers) | ✅ |
| PDC-03 | Barre de recherche | Filtrage dynamique par nom de chantier | ✅ |
| PDC-04 | Toggle mode Avance | Affichage des options avancees | ✅ |
| PDC-05 | Toggle Hrs / J/H | Basculer entre Heures et Jours/Homme | ✅ |
| PDC-06 | Navigation temporelle | < Aujourd'hui > pour defiler les semaines | ✅ |
| PDC-07 | Colonnes semaines | Format SXX - YYYY (ex: S30 - 2025) | ✅ |
| PDC-08 | Colonne Charge | Budget total d'heures prevu par chantier | ✅ |
| PDC-09 | Double colonne par semaine | Planifie (affecte) + Besoin (a couvrir) | ✅ |
| PDC-10 | Cellules Besoin colorees | Violet pour les besoins non couverts | ✅ |
| PDC-11 | Footer repliable | Indicateurs agreges en bas du tableau | ✅ |
| PDC-12 | Taux d'occupation | Pourcentage par semaine avec code couleur | ✅ |
| PDC-13 | Alerte surcharge | ⚠️ si taux >= 100% | ✅ |
| PDC-14 | A recruter | Nombre de personnes a embaucher par semaine | ✅ |
| PDC-15 | A placer | Personnes disponibles a affecter | ✅ |
| PDC-16 | Modal Planification besoins | Saisie detaillee par type/metier | ✅ |
| PDC-17 | Modal Details occupation | Taux par type avec code couleur | ✅ |

### 6.3 Modal - Planification des besoins

Cette modal s'ouvre en cliquant sur une cellule Besoin. Elle permet de saisir les besoins en main d'oeuvre par type/metier pour un chantier et une semaine donnes.

| Element | Description |
|---------|-------------|
| Dropdown chantier | Selection du chantier concerne |
| Selecteur semaine | Calendrier pour choisir la semaine |
| Zone note | Commentaire optionnel sur les besoins |
| Tableau par type | Badge colore \| Planifie (lecture) \| Besoin (saisie) \| Unite |
| Bouton Ajouter | + Ajouter une ligne de type |
| Bouton Supprimer | 🗑️ pour retirer une ligne |

### 6.4 Codes couleur - Taux d'occupation

| Seuil | Couleur | Signification |
|-------|---------|---------------|
| < 70% | 🟢 Vert | Sous-charge, capacite disponible |
| 70% - 90% | 🔵 Bleu clair | Charge normale, equilibree |
| 90% - 100% | 🟡 Jaune/Orange | Charge haute, vigilance requise |
| >= 100% | 🔴 Rouge + ⚠️ | Surcharge, alerte critique |
| > 100% | 🔴 Rouge fonce | Depassement critique, action urgente |

---