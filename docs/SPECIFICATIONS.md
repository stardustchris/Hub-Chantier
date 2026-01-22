# GREG CONSTRUCTIONS - Cahier des Charges Fonctionnel

> **Application SaaS de Gestion de Chantiers**
> Version 2.1 - Janvier 2026
> Document confidentiel

---

## Table des matières

1. [Introduction](#1-introduction)
2. [Gestion des Utilisateurs](#2-gestion-des-utilisateurs)
3. [Gestion des Chantiers](#3-gestion-des-chantiers)
4. [Planning Opérationnel](#4-planning-opérationnel)
5. [Planning de Charge](#5-planning-de-charge)
6. [Feuilles d'Heures](#6-feuilles-dheures)
7. [Formulaires Chantier](#7-formulaires-chantier)
8. [Gestion Documentaire (GED)](#8-gestion-documentaire-ged)
9. [Mémos](#9-mémos)
10. [Logistique - Gestion du Matériel](#10-logistique---gestion-du-matériel)
11. [Gestion des Interventions](#11-gestion-des-interventions)
12. [Gestion des Tâches](#12-gestion-des-tâches)
13. [Intégrations](#13-intégrations)
14. [Sécurité et Conformité](#14-sécurité-et-conformité)
15. [Tableau de Bord & Feed d'Actualités](#15-tableau-de-bord--feed-dactualités)
16. [Glossaire](#16-glossaire)

---

## 1. Introduction

### 1.1 Contexte du projet

Greg Constructions est une entreprise spécialisée dans le gros œuvre et la construction de bâtiments. Ce cahier des charges définit les spécifications fonctionnelles d'une application SaaS permettant de gérer l'ensemble des opérations de chantier, depuis la planification des équipes jusqu'au suivi documentaire.

### 1.2 Objectifs

L'application vise à :
- Centraliser la gestion des chantiers et des équipes
- Optimiser la planification des ressources humaines et matérielles
- Faciliter la communication terrain/bureau en temps réel
- Automatiser la gestion des heures et la préparation de la paie
- Assurer la traçabilité documentaire et le suivi qualité

### 1.3 Périmètre fonctionnel

| Module | Description | Status |
|--------|-------------|--------|
| Utilisateurs | Gestion des comptes, rôles et permissions | ⏳ TODO |
| Chantiers | Création et suivi des projets de construction | ⏳ TODO |
| Planning Opérationnel | Affectation des équipes aux chantiers | ⏳ TODO |
| Planning de Charge | Vision capacitaire et besoins par métier | ⏳ TODO |
| Feuilles d'heures | Saisie et validation du temps de travail | ⏳ TODO |
| Tâches | Gestion des travaux et avancement | ⏳ TODO |
| Formulaires | Templates personnalisables (rapports, PV...) | ⏳ TODO |
| Documents | GED avec gestion des droits d'accès | ⏳ TODO |
| Mémos | Communication d'urgence et suivi problèmes | ⏳ TODO |
| Interventions | Gestion SAV et maintenance ponctuelle | ⏳ TODO |
| Logistique | Réservation engins et gros matériel | ⏳ TODO |

### 1.4 Références

Ce cahier des charges s'inspire des meilleures pratiques de l'application Alobees, solution de référence dans le secteur du BTP, tout en étant adapté aux besoins spécifiques du gros œuvre et de la construction.

---

## 2. Gestion des Utilisateurs

### 2.1 Vue d'ensemble

Le module Utilisateurs permet de gérer l'ensemble des collaborateurs (employés et sous-traitants) avec un système de rôles et permissions granulaires. Chaque utilisateur dispose d'une fiche complète avec photo, couleur d'identification et informations de contact.

### 2.2 Fonctionnalités

| ID | Fonctionnalité | Description | Status |
|----|----------------|-------------|--------|
| USR-01 | Ajout illimité | Nombre d'utilisateurs non plafonné | ⏳ |
| USR-02 | Invitation SMS | Envoi automatique du lien d'installation de l'app | ⏳ |
| USR-03 | Photo de profil | Upload d'une photo personnelle | ⏳ |
| USR-04 | Couleur utilisateur | Palette 16 couleurs pour identification visuelle | ⏳ |
| USR-05 | Statut Activé/Désactivé | Toggle pour activer/désactiver l'accès | ⏳ |
| USR-06 | Type utilisateur | Employé ou Sous-traitant | ⏳ |
| USR-07 | Rôle | Administrateur / Conducteur / Chef de Chantier / Compagnon | ⏳ |
| USR-08 | Code utilisateur | Matricule optionnel pour export paie | ⏳ |
| USR-09 | Numéro mobile | Format international avec sélecteur pays | ⏳ |
| USR-10 | Navigation précédent/suivant | Parcourir les fiches utilisateurs | ⏳ |
| USR-11 | Révocation instantanée | Désactivation sans suppression des données historiques | ⏳ |
| USR-12 | Métier/Spécialité | Classification par corps de métier | ⏳ |
| USR-13 | Email professionnel | Adresse email optionnelle | ⏳ |
| USR-14 | Coordonnées d'urgence | Contact en cas d'accident | ⏳ |

### 2.3 Matrice des rôles et permissions

| Rôle | Web | Mobile | Périmètre | Droits principaux |
|------|-----|--------|-----------|-------------------|
| Administrateur | ✅ | ✅ | Global | Tous droits, configuration système |
| Conducteur | ✅ | ✅ | Ses chantiers | Planification, validation, export |
| Chef de Chantier | ❌ | ✅ | Ses chantiers assignés | Saisie, consultation, publication |
| Compagnon | ❌ | ✅ | Planning perso | Consultation, saisie heures |

### 2.4 Palette de couleurs utilisateurs

16 couleurs disponibles pour l'identification visuelle des utilisateurs.

| Couleur | Code | Couleur | Code |
|---------|------|---------|------|
| Rouge | `#E74C3C` | Bleu foncé | `#2C3E50` |
| Orange | `#E67E22` | Bleu clair | `#3498DB` |
| Jaune | `#F1C40F` | Cyan | `#1ABC9C` |
| Vert clair | `#2ECC71` | Violet | `#9B59B6` |
| Vert foncé | `#27AE60` | Rose | `#E91E63` |
| Marron | `#795548` | Gris | `#607D8B` |
| Corail | `#FF7043` | Indigo | `#3F51B5` |
| Magenta | `#EC407A` | Lime | `#CDDC39` |

---

## 3. Gestion des Chantiers

### 3.1 Vue d'ensemble

Le module Chantiers centralise toutes les informations d'un projet de construction avec un fil d'actualité temps réel, une gestion documentaire intégrée et un suivi des équipes affectées. Chaque chantier dispose d'onglets dédiés pour une navigation fluide.

### 3.2 Fonctionnalités

| ID | Fonctionnalité | Description | Status |
|----|----------------|-------------|--------|
| CHT-01 | Photo de couverture | Image représentative du chantier | ⏳ |
| CHT-02 | Couleur chantier | Palette 16 couleurs pour cohérence visuelle globale | ⏳ |
| CHT-03 | Statut chantier | Ouvert / En cours / Réceptionné / Fermé | ⏳ |
| CHT-04 | Coordonnées GPS | Latitude + Longitude pour géolocalisation | ⏳ |
| CHT-05 | Multi-conducteurs | Affectation de plusieurs conducteurs de travaux | ⏳ |
| CHT-06 | Multi-chefs de chantier | Affectation de plusieurs chefs | ⏳ |
| CHT-07 | Contact chantier | Nom et téléphone du contact sur place | ⏳ |
| CHT-08 | Navigation GPS | Bouton direct vers Google Maps / Waze | ⏳ |
| CHT-09 | Mini carte | Aperçu cartographique avec marqueur de localisation | ⏳ |
| CHT-10 | Fil d'actualité | Timeline des publications et événements | ⏳ |
| CHT-11 | Publications photos/vidéos | Jusqu'à 10 photos simultanées par publication | ⏳ |
| CHT-12 | Commentaires | Système de discussion sur chaque publication | ⏳ |
| CHT-13 | Signature dans publication | Option de signature électronique | ⏳ |
| CHT-14 | Navigation précédent/suivant | Parcourir les fiches chantiers | ⏳ |
| CHT-15 | Stockage illimité | Aucune limite sur les documents et médias | ⏳ |
| CHT-16 | Liste équipe affectée | Visualisation des collaborateurs assignés | ⏳ |
| CHT-17 | Alertes mémo | Indicateur visuel si mémo actif | ⏳ |
| CHT-18 | Heures estimées | Budget temps prévisionnel du chantier | ⏳ |
| CHT-19 | Code chantier | Identifiant unique (ex: A001, B023) | ⏳ |
| CHT-20 | Dates début/fin prévisionnelles | Planning macro du projet | ⏳ |

### 3.3 Onglets de la fiche chantier

| N° | Onglet | Description | Accès |
|----|--------|-------------|-------|
| 1 | Résumé | Informations générales + fil d'actualité temps réel | Tous |
| 2 | Documents | GED - Gestion documentaire avec droits d'accès | Selon droits |
| 3 | Formulaires | Templates à remplir (rapports, PV...) | Tous |
| 4 | Planning | Affectations équipe semaine par semaine | Chef+ |
| 5 | Tâches | Liste des travaux hiérarchiques avec avancement | Tous |
| 6 | Feuilles de tâches | Déclarations quotidiennes par compagnon | Conducteur+ |
| 7 | Feuilles d'heures | Saisie et validation du temps de travail | Tous |
| 8 | Arrivées/Départs | Pointage et géolocalisation | Conducteur+ |

### 3.4 Statuts de chantier

| Statut | Icône | Description | Actions possibles |
|--------|-------|-------------|-------------------|
| Ouvert | 🔵 | Chantier créé, en préparation | Planification, affectation équipe |
| En cours | 🟢 | Travaux en cours d'exécution | Toutes actions opérationnelles |
| Réceptionné | 🟡 | Travaux terminés, en attente clôture | SAV, levée réserves |
| Fermé | 🔴 | Chantier clôturé définitivement | Consultation uniquement |

---

## 4. Planning Opérationnel

### 4.1 Vue d'ensemble

Le Planning Opérationnel permet d'affecter les collaborateurs aux chantiers avec une vue multi-perspective (Chantiers, Utilisateurs, Interventions), un groupement par métier avec badges colorés, et une synchronisation temps réel mobile.

### 4.2 Fonctionnalités

| ID | Fonctionnalité | Description | Status |
|----|----------------|-------------|--------|
| PLN-01 | 3 onglets de vue | [Chantiers] [Utilisateurs] [Gestion des interventions] | ⏳ |
| PLN-02 | Onglet Utilisateurs par défaut | Vue ressource comme vue principale | ⏳ |
| PLN-03 | Bouton + Créer | Création rapide d'affectation en haut à droite | ⏳ |
| PLN-04 | Dropdown filtre utilisateurs | Utilisateurs planifiés / Non planifiés / Tous | ⏳ |
| PLN-05 | Icône entonnoir | Accès aux filtres avancés | ⏳ |
| PLN-06 | Icône engrenage | Paramètres d'affichage | ⏳ |
| PLN-07 | Bouton Filtrer | Filtrage textuel rapide | ⏳ |
| PLN-08 | Sélecteur période | [Semaine] [Mois] [Trimestre] | ⏳ |
| PLN-09 | Navigation temporelle | 21 - 27 juillet 2025 < [Aujourd'hui] > | ⏳ |
| PLN-10 | Indicateur semaine | Semaine 30 affiché au-dessus du tableau | ⏳ |
| PLN-11 | Section À Planifier | Badge compteur des ressources non affectées | ⏳ |
| PLN-12 | Groupement par métier | Arborescence repliable par type d'utilisateur | ⏳ |
| PLN-13 | Badges métier colorés | Employé, Charpentier, Couvreur, Électricien, Sous-traitant... | ⏳ |
| PLN-14 | Chevrons repliables | ▼ / > pour afficher/masquer les groupes | ⏳ |
| PLN-15 | Avatar utilisateur | Cercle avec initiales + code couleur personnel | ⏳ |
| PLN-16 | Icône duplication | 📋 pour dupliquer les affectations de la semaine | ⏳ |
| PLN-17 | Blocs affectation colorés | Couleur = chantier (cohérence visuelle globale) | ⏳ |
| PLN-18 | Format bloc | HH:MM - HH:MM + icône note + Nom chantier | ⏳ |
| PLN-19 | Icône note dans bloc | 📝 Indicateur de commentaire sur l'affectation | ⏳ |
| PLN-20 | Multi-affectations/jour | Plusieurs blocs possibles par utilisateur par jour | ⏳ |
| PLN-21 | Colonnes jours | Lundi 21 juil. / Mardi 22 juil. etc. | ⏳ |
| PLN-22 | Barre de recherche | Champ Rechercher dans la colonne utilisateurs | ⏳ |
| PLN-23 | Notification push | Alerte à chaque nouvelle affectation | ⏳ |
| PLN-24 | Mode Offline | Consultation planning sans connexion | ⏳ |
| PLN-25 | Notes privées | Commentaires visibles uniquement par l'affecté | ⏳ |
| PLN-26 | Accès profil utilisateur | Clic sur avatar → fiche profil + bouton appel | ⏳ |
| PLN-27 | Drag & Drop | Déplacer les blocs pour modifier les affectations | ⏳ |
| PLN-28 | Double-clic création | Double-clic cellule vide → création affectation | ⏳ |

### 4.3 Badges métiers (Groupement)

| Badge | Couleur | Description |
|-------|---------|-------------|
| Employé | 🔵 Bleu foncé | Compagnons internes polyvalents |
| Charpentier | 🟢 Vert | Spécialistes bois et charpente |
| Couvreur | 🟠 Orange | Spécialistes toiture |
| Électricien | 🟣 Magenta/Rose | Spécialistes électricité |
| Sous-traitant | 🔴 Rouge/Corail | Prestataires externes |
| Maçon | 🟤 Marron | Spécialistes maçonnerie (Greg) |
| Coffreur | 🟡 Jaune | Spécialistes coffrage (Greg) |
| Ferrailleur | ⚫ Gris foncé | Spécialistes ferraillage (Greg) |
| Grutier | 🩵 Cyan | Conducteurs d'engins (Greg) |

### 4.4 Structure d'une affectation

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| Utilisateur | Référence | Oui | Compagnon ou sous-traitant affecté |
| Chantier | Référence | Oui | Chantier d'affectation |
| Date | Date | Oui | Jour de l'affectation |
| Heure début | HH:MM | Non | Heure de prise de poste |
| Heure fin | HH:MM | Non | Heure de fin de journée |
| Note | Texte | Non | Commentaire privé pour l'affecté |
| Récurrence | Option | Non | Unique / Répéter (jours sélectionnés) |

### 4.5 Matrice des droits - Planning

| Action | Admin | Conducteur | Chef | Compagnon |
|--------|-------|------------|------|-----------|
| Voir planning global | ✅ | ✅ | ❌ | ❌ |
| Voir planning ses chantiers | ✅ | ✅ | ✅ | ❌ |
| Voir son planning personnel | ✅ | ✅ | ✅ | ✅ |
| Créer affectation | ✅ | ✅ | ❌ | ❌ |
| Modifier affectation | ✅ | ✅ | ❌ | ❌ |
| Supprimer affectation | ✅ | ✅ | ❌ | ❌ |
| Ajouter note | ✅ | ✅ | ✅ | ❌ |
| Dupliquer affectations | ✅ | ✅ | ❌ | ❌ |

### 4.6 Vue Mobile

Sur mobile, le planning s'affiche avec :
- Navigation par jour (L M M J V S D)
- Deux onglets [Chantiers] et [Utilisateurs]
- Vue Chantiers : liste les chantiers avec leurs collaborateurs affectés
- Vue Utilisateurs : liste les collaborateurs avec leurs affectations
- Chaque affectation peut être supprimée via le bouton ✕
- FAB (+) pour créer une nouvelle affectation

---

## 5. Planning de Charge

### 5.1 Vue d'ensemble

Le Planning de Charge est un tableau de bord stratégique permettant de visualiser la charge de travail par chantier et par semaine, avec gestion des besoins par type/métier et indicateurs de taux d'occupation.

### 5.2 Fonctionnalités

| ID | Fonctionnalité | Description | Status |
|----|----------------|-------------|--------|
| PDC-01 | Vue tabulaire | Chantiers en lignes, semaines en colonnes | ⏳ |
| PDC-02 | Compteur chantiers | Badge indiquant le nombre total (ex: 107 Chantiers) | ⏳ |
| PDC-03 | Barre de recherche | Filtrage dynamique par nom de chantier | ⏳ |
| PDC-04 | Toggle mode Avancé | Affichage des options avancées | ⏳ |
| PDC-05 | Toggle Hrs / J/H | Basculer entre Heures et Jours/Homme | ⏳ |
| PDC-06 | Navigation temporelle | < Aujourd'hui > pour défiler les semaines | ⏳ |
| PDC-07 | Colonnes semaines | Format SXX - YYYY (ex: S30 - 2025) | ⏳ |
| PDC-08 | Colonne Chargé | Budget total d'heures prévu par chantier | ⏳ |
| PDC-09 | Double colonne par semaine | Planifié (affecté) + Besoin (à couvrir) | ⏳ |
| PDC-10 | Cellules Besoin colorées | Violet pour les besoins non couverts | ⏳ |
| PDC-11 | Footer repliable | Indicateurs agrégés en bas du tableau | ⏳ |
| PDC-12 | Taux d'occupation | Pourcentage par semaine avec code couleur | ⏳ |
| PDC-13 | Alerte surcharge | ⚠️ si taux ≥ 100% | ⏳ |
| PDC-14 | À recruter | Nombre de personnes à embaucher par semaine | ⏳ |
| PDC-15 | À placer | Personnes disponibles à affecter | ⏳ |
| PDC-16 | Modal Planification besoins | Saisie détaillée par type/métier | ⏳ |
| PDC-17 | Modal Détails occupation | Taux par type avec code couleur | ⏳ |

### 5.3 Codes couleur - Taux d'occupation

| Seuil | Couleur | Signification |
|-------|---------|---------------|
| < 70% | 🟢 Vert | Sous-charge, capacité disponible |
| 70% - 90% | 🔵 Bleu clair | Charge normale, équilibrée |
| 90% - 100% | 🟡 Jaune/Orange | Charge haute, vigilance requise |
| ≥ 100% | 🔴 Rouge + ⚠️ | Surcharge, alerte critique |
| > 100% | 🔴 Rouge foncé | Dépassement critique, action urgente |

---

## 6. Feuilles d'Heures

### 6.1 Vue d'ensemble

Le module Feuilles d'heures permet la saisie, le suivi et l'export des heures travaillées avec deux vues complémentaires (Chantiers et Compagnons) et des variables de paie intégrées.

### 6.2 Fonctionnalités

| ID | Fonctionnalité | Description | Status |
|----|----------------|-------------|--------|
| FDH-01 | 2 onglets de vue | [Chantiers] [Compagnons/Sous-traitants] | ⏳ |
| FDH-02 | Navigation par semaine | Semaine X avec << < > >> pour naviguer | ⏳ |
| FDH-03 | Bouton Exporter | Export des données vers fichier ou ERP | ⏳ |
| FDH-04 | Filtre utilisateurs | Dropdown de sélection multi-critères | ⏳ |
| FDH-05 | Vue tabulaire hebdomadaire | Lundi à Vendredi avec dates complètes | ⏳ |
| FDH-06 | Multi-chantiers par utilisateur | Plusieurs lignes possibles | ⏳ |
| FDH-07 | Badges colorés par chantier | Cohérence avec le planning | ⏳ |
| FDH-08 | Total par ligne | Somme heures par utilisateur + chantier | ⏳ |
| FDH-09 | Total groupé | Somme heures utilisateur tous chantiers | ⏳ |
| FDH-10 | Création auto à l'affectation | Lignes pré-remplies depuis le planning | ⏳ |
| FDH-11 | Saisie mobile | Sélecteur roulette HH:MM intuitif | ⏳ |
| FDH-12 | Signature électronique | Validation des heures par le compagnon | ⏳ |
| FDH-13 | Variables de paie | Panier, transport, congés, primes, absences | ⏳ |
| FDH-14 | Jauge d'avancement | Comparaison planifié vs réalisé | ⏳ |
| FDH-15 | Comparaison inter-équipes | Détection automatique des écarts | ⏳ |
| FDH-16 | Import ERP auto | Synchronisation quotidienne/hebdomadaire | ⏳ |
| FDH-17 | Export ERP manuel | Période sélectionnée personnalisable | ⏳ |
| FDH-18 | Macros de paie | Calculs automatisés paramétrables | ⏳ |
| FDH-19 | Feuilles de route | Génération automatique PDF | ⏳ |
| FDH-20 | Mode Offline | Saisie sans connexion, sync auto | ⏳ |

### 6.3 Variables de paie

| Variable | Type | Description |
|----------|------|-------------|
| Heures normales | Nombre | Heures de travail standard |
| Heures supplémentaires | Nombre | Heures au-delà du contrat |
| Panier repas | Montant | Indemnité de repas |
| Indemnité transport | Montant | Frais de déplacement |
| Prime intempéries | Montant | Compensation météo |
| Congés payés | Jours | Absences congés |
| Maladie | Jours | Absences maladie |
| Absence injustifiée | Jours | Absences non justifiées |

---

## 7. Formulaires Chantier

### 7.1 Vue d'ensemble

Le module Formulaires permet de créer des templates personnalisés pour tous les documents terrain : rapports d'intervention, PV de réception, bons de livraison, formulaires de sécurité, etc.

### 7.2 Fonctionnalités

| ID | Fonctionnalité | Description | Status |
|----|----------------|-------------|--------|
| FOR-01 | Templates personnalisés | Création accompagnée par l'équipe Alobees | ⏳ |
| FOR-02 | Remplissage mobile | Saisie sur smartphone même hors ligne | ⏳ |
| FOR-03 | Champs auto-remplis | Date, heure, localisation, intervenant | ⏳ |
| FOR-04 | Ajout photos horodatées | Preuve visuelle avec timestamp GPS | ⏳ |
| FOR-05 | Signature électronique | Chef de chantier + client si nécessaire | ⏳ |
| FOR-06 | Centralisation automatique | Rattachement au chantier concerné | ⏳ |
| FOR-07 | Horodatage automatique | Date et heure de soumission enregistrées | ⏳ |
| FOR-08 | Historique complet | Toutes les versions conservées | ⏳ |
| FOR-09 | Export PDF | Génération du document final formaté | ⏳ |
| FOR-10 | Liste par chantier | Onglet dédié dans fiche chantier | ⏳ |
| FOR-11 | Lien direct | Bouton Remplir le formulaire → | ⏳ |

### 7.3 Types de formulaires

| Catégorie | Exemples de formulaires |
|-----------|------------------------|
| Interventions | Rapport d'intervention, Bon de SAV, Fiche dépannage |
| Réception | PV de réception, Constat de réserves, Attestation fin travaux |
| Sécurité | Formulaire sécurité, Visite PPSPS, Auto-contrôle, Quart d'heure sécurité |
| Incidents | Déclaration sinistre, Fiche non-conformité, Rapport accident |
| Approvisionnement | Commande matériel, Bon de livraison, Réception matériaux |
| Administratif | Demande de congés, CERFA, Attestation diverse |
| Gros Œuvre (Greg) | Rapport journalier, Bon de bétonnage, Contrôle ferraillage |

---

## 8. Gestion Documentaire (GED)

### 8.1 Vue d'ensemble

Le module Documents offre une gestion documentaire complète avec arborescence par dossiers numérotés, contrôle d'accès granulaire par rôle et nominatif, et synchronisation offline automatique.

### 8.2 Fonctionnalités

| ID | Fonctionnalité | Description | Status |
|----|----------------|-------------|--------|
| GED-01 | Onglet Documents intégré | Dans chaque fiche chantier | ⏳ |
| GED-02 | Arborescence par dossiers | Organisation hiérarchique numérotée | ⏳ |
| GED-03 | Tableau de gestion | Vue liste avec métadonnées (taille, date, auteur) | ⏳ |
| GED-04 | Rôle minimum par dossier | Compagnon / Chef / Conducteur / Admin | ⏳ |
| GED-05 | Autorisations spécifiques | Permissions nominatives additionnelles | ⏳ |
| GED-06 | Upload multiple | Jusqu'à 10 fichiers simultanés | ⏳ |
| GED-07 | Taille max 10 Go | Par fichier individuel | ⏳ |
| GED-08 | Zone Drag & Drop | Glisser-déposer intuitif | ⏳ |
| GED-09 | Barre de progression | Affichage % upload en temps réel | ⏳ |
| GED-10 | Sélection droits à l'upload | Rôles + Utilisateurs nominatifs | ⏳ |
| GED-11 | Transfert auto depuis ERP | Synchronisation Costructor/Graneet | ⏳ |
| GED-12 | Formats supportés | PDF, Images (PNG/JPG), XLS/XLSX, DOC/DOCX, Vidéos | ⏳ |
| GED-13 | Actions Éditer/Supprimer | Gestion complète des fichiers | ⏳ |
| GED-14 | Consultation mobile | Visualisation sur application | ⏳ |
| GED-15 | Synchronisation Offline | Plans téléchargés automatiquement | ⏳ |

### 8.3 Niveaux d'accès

| Rôle minimum | Qui peut voir | Cas d'usage |
|--------------|---------------|-------------|
| Compagnon/Sous-Traitant | Tous utilisateurs du chantier | Plans d'exécution, consignes sécurité |
| Chef de Chantier | Chefs + Conducteurs + Admin | Documents techniques sensibles |
| Conducteur | Conducteurs + Admin uniquement | Contrats, budgets, planning macro |
| Administrateur | Admin uniquement | Documents confidentiels, RH |

### 8.4 Arborescence type

| N° | Dossier | Contenu type |
|----|---------|--------------|
| 01 | Plans | Plans d'exécution, plans béton, réservations |
| 02 | Documents administratifs | Marchés, avenants, OS, situations |
| 03 | Sécurité | PPSPS, plan de prévention, consignes |
| 04 | Qualité | Fiches techniques, PV essais, autocontrôles |
| 05 | Photos | Photos chantier par date/zone |
| 06 | Comptes-rendus | CR réunions, CR chantier |
| 07 | Livraisons | Bons de livraison, bordereaux |

---

## 9. Mémos

### 9.1 Vue d'ensemble

Le module Mémos permet de signaler des urgences, problèmes ou informations importantes avec un système de fil de conversation type chat et de statuts ouvert/fermé.

### 9.2 Fonctionnalités

| ID | Fonctionnalité | Description | Status |
|----|----------------|-------------|--------|
| MEM-01 | Rattachement chantier | Mémo obligatoirement lié à un projet | ⏳ |
| MEM-02 | Liste chronologique | Affichage par date de création | ⏳ |
| MEM-03 | Indicateur statut | 🟢 Ouvert / 🔴 Fermé | ⏳ |
| MEM-04 | Photo chantier | Vignette d'identification visuelle | ⏳ |
| MEM-05 | Horodatage | Date + heure de création | ⏳ |
| MEM-06 | Fil de conversation | Mode chat pour échanges multiples | ⏳ |
| MEM-07 | Statut fermé avec badge | Ce mémo a été fermé le [date] | ⏳ |
| MEM-08 | Ajout photo/vidéo | Dans les réponses du fil | ⏳ |
| MEM-09 | Signature dans réponses | Validation des actions correctives | ⏳ |
| MEM-10 | Bouton Publier | Envoyer une réponse dans le fil | ⏳ |
| MEM-11 | Historique | X a ajouté un mémo sur Y le [date] | ⏳ |
| MEM-12 | Bouton + (FAB) | Création rapide sur mobile | ⏳ |
| MEM-13 | Notifications push | Alerte temps réel à la création | ⏳ |

### 9.3 Cas d'usage

| Type | Exemple | Priorité |
|------|---------|----------|
| Urgence sécurité | Échafaudage instable zone B | Critique |
| Problème technique | Fuite réseau eau potable | Haute |
| Approvisionnement | Rupture stock ferraille HA12 | Moyenne |
| Information | Visite client prévue demain 10h | Basse |
| Incident | Bris de matériel sur grue | Haute |
| Qualité | Non-conformité béton livré | Haute |

---

## 10. Logistique - Gestion du Matériel

### 10.1 Vue d'ensemble

Le module Logistique permet de gérer les engins et gros matériel de l'entreprise avec un système de réservation par chantier, validation hiérarchique optionnelle et visualisation calendrier.

### 10.2 Fonctionnalités

| ID | Fonctionnalité | Description | Status |
|----|----------------|-------------|--------|
| LOG-01 | Référentiel matériel | Liste des engins disponibles (Admin uniquement) | ⏳ |
| LOG-02 | Fiche ressource | Nom, code, photo, couleur, plage horaire par défaut | ⏳ |
| LOG-03 | Planning par ressource | Vue calendrier hebdomadaire 7 jours | ⏳ |
| LOG-04 | Navigation semaine | < [Semaine X] > avec 3 semaines visibles | ⏳ |
| LOG-05 | Axe horaire vertical | 08:00 → 18:00 (configurable) | ⏳ |
| LOG-06 | Blocs réservation colorés | Par demandeur avec nom + bouton ✕ | ⏳ |
| LOG-07 | Demande de réservation | Depuis mobile ou web | ⏳ |
| LOG-08 | Sélection chantier | Association obligatoire au projet | ⏳ |
| LOG-09 | Sélection créneau | Date + heure début / heure fin | ⏳ |
| LOG-10 | Option validation N+1 | Activation/désactivation par ressource | ⏳ |
| LOG-11 | Workflow validation | Demande 🟡 → Chef valide → Confirmé 🟢 | ⏳ |
| LOG-12 | Statuts réservation | En attente 🟡 / Validée 🟢 / Refusée 🔴 | ⏳ |
| LOG-13 | Notification demande | Push au valideur (chef/conducteur) | ⏳ |
| LOG-14 | Notification décision | Push au demandeur | ⏳ |
| LOG-15 | Rappel J-1 | Notification veille de réservation | ⏳ |
| LOG-16 | Motif de refus | Champ texte optionnel | ⏳ |
| LOG-17 | Conflit de réservation | Alerte si créneau déjà occupé | ⏳ |
| LOG-18 | Historique par ressource | Journal complet des réservations | ⏳ |

### 10.3 Types de ressources (Greg Constructions)

| Catégorie | Exemples | Validation |
|-----------|----------|------------|
| Engins de levage | Grue mobile, Manitou, Nacelle, Chariot élévateur | N+1 requis |
| Engins de terrassement | Mini-pelle, Pelleteuse, Compacteur, Dumper | N+1 requis |
| Véhicules | Camion benne, Fourgon, Véhicule utilitaire | Optionnel |
| Gros outillage | Bétonnière, Vibrateur, Pompe à béton | Optionnel |
| Équipements | Échafaudage, Étais, Banches, Coffrages | N+1 requis |

### 10.4 Matrice des droits - Logistique

| Action | Admin | Conducteur | Chef | Compagnon |
|--------|-------|------------|------|-----------|
| Créer ressource | ✅ | ❌ | ❌ | ❌ |
| Modifier ressource | ✅ | ❌ | ❌ | ❌ |
| Supprimer ressource | ✅ | ❌ | ❌ | ❌ |
| Voir planning ressource | ✅ | ✅ | ✅ | ✅ |
| Demander réservation | ✅ | ✅ | ✅ | ✅ |
| Valider/Refuser | ✅ | ✅ | ✅ | ❌ |

---

## 11. Gestion des Interventions

### 11.1 Vue d'ensemble

Le module Interventions est dédié à la gestion des interventions ponctuelles (SAV, maintenance, dépannages, levée de réserves) distinctes des chantiers de longue durée.

### 11.2 Différence Chantier vs Intervention

| Critère | Chantier | Intervention |
|---------|----------|--------------|
| Durée | Longue (semaines/mois) | Courte (heures/jours) |
| Équipe | Multiple collaborateurs | 1-2 techniciens |
| Récurrence | Continue | Ponctuelle |
| Usage | Gros œuvre, construction | SAV, maintenance, dépannage |
| Livrable | Suivi global projet | Rapport d'intervention signé |

### 11.3 Fonctionnalités

| ID | Fonctionnalité | Description | Status |
|----|----------------|-------------|--------|
| INT-01 | Onglet dédié Planning | 3ème onglet Gestion des interventions | ⏳ |
| INT-02 | Liste des interventions | Tableau Chantier/Client/Adresse/Statut | ⏳ |
| INT-03 | Création intervention | Bouton + pour nouvelle intervention | ⏳ |
| INT-04 | Fiche intervention | Client, adresse, contact, description, priorité | ⏳ |
| INT-05 | Statuts intervention | À planifier / Planifiée / En cours / Terminée / Annulée | ⏳ |
| INT-06 | Planning hebdomadaire | Utilisateurs en lignes, jours en colonnes | ⏳ |
| INT-07 | Blocs intervention colorés | Format HH:MM - HH:MM - Code - Nom client | ⏳ |
| INT-08 | Multi-interventions/jour | Plusieurs par utilisateur | ⏳ |
| INT-09 | Toggle Afficher les tâches | Activer/désactiver l'affichage | ⏳ |
| INT-10 | Affectation technicien | Drag & drop ou via modal | ⏳ |
| INT-11 | Fil d'actualité | Timeline actions, photos, commentaires | ⏳ |
| INT-12 | Chat intervention | Discussion instantanée équipe | ⏳ |
| INT-13 | Signature client | Sur mobile avec stylet/doigt | ⏳ |
| INT-14 | Rapport PDF | Génération automatique avec tous les détails | ⏳ |
| INT-15 | Sélection posts pour rapport | Choisir les éléments à inclure | ⏳ |
| INT-16 | Génération mobile | Créer le PDF depuis l'application | ⏳ |
| INT-17 | Affectation sous-traitants | Prestataires externes (PLB, CFA...) | ⏳ |

### 11.4 Contenu du rapport PDF

| Section | Contenu |
|---------|---------|
| En-tête | Logo entreprise, N° intervention, Date génération |
| Client | Nom, Adresse complète, Contact, Téléphone |
| Intervenant(s) | Nom(s) du/des technicien(s) affectés |
| Horaires | Heure début, heure fin, durée totale |
| Description | Motif de l'intervention |
| Travaux réalisés | Détail des actions effectuées |
| Photos | Avant / Pendant / Après (sélectionnées) |
| Anomalies | Problèmes constatés non résolus |
| Signatures | Client + Technicien avec horodatage |

---

## 12. Gestion des Tâches

### 12.1 Vue d'ensemble

Le module Tâches permet de créer des listes de travaux structurées par chantier avec un système de tâches/sous-tâches hiérarchiques, une bibliothèque de modèles réutilisables, et un suivi d'avancement.

### 12.2 Fonctionnalités

| ID | Fonctionnalité | Description | Status |
|----|----------------|-------------|--------|
| TAC-01 | Onglet Tâches par chantier | Accessible depuis la fiche chantier | ⏳ |
| TAC-02 | Structure hiérarchique | Tâches parentes + sous-tâches imbriquées | ⏳ |
| TAC-03 | Chevrons repliables | ▼ / > pour afficher/masquer | ⏳ |
| TAC-04 | Bibliothèque de modèles | Templates réutilisables avec sous-tâches | ⏳ |
| TAC-05 | Création depuis modèle | Importer un modèle dans un chantier | ⏳ |
| TAC-06 | Création manuelle | Tâche personnalisée libre | ⏳ |
| TAC-07 | Bouton + Ajouter | Création rapide de tâche | ⏳ |
| TAC-08 | Date d'échéance | Deadline pour la tâche | ⏳ |
| TAC-09 | Unité de mesure | m², litre, unité, ml, kg, m³... | ⏳ |
| TAC-10 | Quantité estimée | Volume/quantité prévu | ⏳ |
| TAC-11 | Heures estimées | Temps prévu pour réalisation | ⏳ |
| TAC-12 | Heures réalisées | Temps effectivement passé | ⏳ |
| TAC-13 | Statuts tâche | À faire ☐ / Terminé ✅ | ⏳ |
| TAC-14 | Barre de recherche | Filtrer par mot-clé | ⏳ |
| TAC-15 | Réorganiser les tâches | Drag & drop pour réordonner | ⏳ |
| TAC-16 | Export rapport PDF | Récapitulatif des tâches | ⏳ |
| TAC-17 | Vue mobile | Consultation et mise à jour | ⏳ |
| TAC-18 | Feuilles de tâches | Déclaration quotidienne travail réalisé | ⏳ |
| TAC-19 | Validation conducteur | Valide le travail déclaré | ⏳ |
| TAC-20 | Code couleur avancement | Vert/Jaune/Rouge selon progression | ⏳ |

### 12.3 Modèles de tâches - Gros Œuvre

| Nom | Description | Unité |
|-----|-------------|-------|
| Coffrage voiles | Mise en place des banches, réglage d'aplomb, serrage | m² |
| Ferraillage plancher | Pose des armatures, ligatures, vérification enrobage | kg |
| Coulage béton | Préparation, vibration, talochage, cure | m³ |
| Décoffrage | Retrait des banches, nettoyage, stockage | m² |
| Pose prédalles | Manutention, calage, étaiement provisoire | m² |
| Réservations | Mise en place des réservations techniques | unité |
| Traitement reprise | Préparation surfaces, application produit adhérence | ml |

### 12.4 Codes couleur - Avancement

| Couleur | Condition | Signification |
|---------|-----------|---------------|
| 🟢 Vert | Heures réalisées ≤ 80% estimées | Dans les temps |
| 🟡 Jaune | Heures réalisées entre 80% et 100% | Attention, limite proche |
| 🔴 Rouge | Heures réalisées > estimées | Dépassement, retard |
| ⚪ Gris | Heures réalisées = 0 | Non commencé |

---

## 13. Intégrations

### 13.1 ERP compatibles

| ERP | Import | Export | Données synchronisées |
|-----|--------|--------|----------------------|
| Costructor | ✅ | ✅ | Chantiers, heures, documents, tâches |
| Graneet | ✅ | ✅ | Chantiers, heures, documents |

### 13.2 Flux de données

| Données | Direction | Fréquence | Mode |
|---------|-----------|-----------|------|
| Chantiers | ERP → App | Temps réel ou quotidien | Automatique |
| Feuilles d'heures | App → ERP | Quotidien/Hebdo/Mensuel | Automatique |
| Documents | ERP ↔ App | À la demande | Automatique |
| Tâches | ERP → App | Import initial | Manuel |
| Variables paie | App → ERP | Hebdomadaire | Automatique |

### 13.3 Canaux de notification

| Canal | Utilisation | Délai |
|-------|-------------|-------|
| Push mobile | Affectations, validations, alertes, mémos | Temps réel |
| SMS | Invitations, urgences critiques | Temps réel |
| Email | Rapports, exports, récapitulatifs hebdo | Différé |

---

## 14. Sécurité et Conformité

### 14.1 Authentification

La connexion s'effectue de manière sécurisée par :
- SMS (code OTP)
- Identifiants classiques (email + mot de passe)

La révocation des accès est instantanée et n'affecte pas les données historiques.

### 14.2 Protection des données

| Mesure | Description |
|--------|-------------|
| Chiffrement en transit | HTTPS/TLS 1.3 pour toutes les communications |
| Chiffrement au repos | Données chiffrées AES-256 sur les serveurs |
| Sauvegarde | Backup quotidien avec rétention 30 jours minimum |
| RGPD | Conformité totale, droit d'accès et droit à l'oubli |
| Hébergement | Serveurs en Europe (France) |

### 14.3 Mode Offline

L'application permet :
- Consultation du planning sans connexion
- Saisie des heures hors ligne
- Synchronisation automatique au retour de la connexion
- Téléchargement automatique des plans

### 14.4 Niveaux de confidentialité

| Niveau | Description | Exemples |
|--------|-------------|----------|
| Public | Tous les utilisateurs du chantier | Plans d'exécution, consignes |
| Restreint | Chefs + Conducteurs + Admin | Documents techniques |
| Confidentiel | Conducteurs + Admin | Contrats, budgets |
| Secret | Admin uniquement | Documents RH, données sensibles |

---

## 15. Tableau de Bord & Feed d'Actualités

*(Section à détailler)*

### 15.1 Vue d'ensemble

Le tableau de bord centralise les informations essentielles pour chaque rôle avec un feed d'actualités temps réel.

### 15.2 Fonctionnalités prévues

- Dashboard personnalisé par rôle
- Feed d'actualités centralisé
- Widgets configurables
- Indicateurs KPIs
- Alertes et notifications

---

## 16. Glossaire

| Terme | Définition |
|-------|------------|
| **Affectation** | Attribution d'un utilisateur à un chantier pour une date/période |
| **Chantier** | Projet de construction avec durée, équipe et budget définis |
| **Compagnon** | Ouvrier qualifié intervenant sur les chantiers |
| **Conducteur** | Responsable de la coordination de plusieurs chantiers |
| **Chef de Chantier** | Responsable opérationnel d'un chantier spécifique |
| **ERP** | Enterprise Resource Planning - logiciel de gestion intégré |
| **GED** | Gestion Électronique des Documents |
| **Intervention** | Mission ponctuelle de courte durée (SAV, maintenance) |
| **Mémo** | Message d'alerte ou d'information rattaché à un chantier |
| **Planning de charge** | Vision capacitaire des ressources par période |
| **Planning opérationnel** | Affectation détaillée des équipes aux chantiers |
| **PPSPS** | Plan Particulier de Sécurité et de Protection de la Santé |
| **Sous-traitant** | Prestataire externe intervenant sur les chantiers |

---

## Historique des modifications

| Version | Date | Auteur | Modifications |
|---------|------|--------|---------------|
| 2.1 | Janvier 2026 | Greg Constructions | Version initiale CDC |
| 2.1-md | Janvier 2026 | Claude | Conversion en Markdown |

---

> **Note** : Ce document est la source de vérité pour le développement de Hub Chantier.
> Il sera mis à jour au fur et à mesure de l'implémentation des fonctionnalités.
> Le fichier Word original reste disponible dans `docs/CDC Greg Constructions v2.1.docx`.
