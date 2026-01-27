# GREG CONSTRUCTIONS

**Gros Oeuvre - Batiment**

## CAHIER DES CHARGES FONCTIONNEL

Application SaaS de Gestion de Chantiers

**Version 2.1 - Janvier 2026**

---

## TABLE DES MATIERES

1. [Introduction](#1-introduction)
2. [Tableau de Bord & Feed d'Actualites](#2-tableau-de-bord--feed-dactualites)
3. [Gestion des Utilisateurs](#3-gestion-des-utilisateurs)
4. [Gestion des Chantiers](#4-gestion-des-chantiers)
5. [Planning Operationnel](#5-planning-operationnel)
6. [Planning de Charge](#6-planning-de-charge)
7. [Feuilles d'Heures](#7-feuilles-dheures)
8. [Formulaires Chantier](#8-formulaires-chantier)
9. [Gestion Documentaire (GED)](#9-gestion-documentaire-ged)
10. [Signalements](#10-signalements)
11. [Logistique - Gestion du Materiel](#11-logistique---gestion-du-materiel)
12. [Gestion des Interventions](#12-gestion-des-interventions)
13. [Gestion des Taches](#13-gestion-des-taches)
14. [Integrations](#14-integrations)
15. [Securite et Conformite](#15-securite-et-conformite)
16. [Glossaire](#16-glossaire)

---

## 1. INTRODUCTION

### 1.1 Contexte du projet

Greg Constructions est une entreprise specialisee dans le gros oeuvre et la construction de batiments. Ce cahier des charges definit les specifications fonctionnelles d'une application SaaS permettant de gerer l'ensemble des operations de chantier, depuis la planification des equipes jusqu'au suivi documentaire.

### 1.2 Objectifs

L'application vise a :
- Centraliser la gestion des chantiers et des equipes
- Optimiser la planification des ressources humaines et materielles
- Faciliter la communication terrain/bureau en temps reel
- Automatiser la gestion des heures et la preparation de la paie
- Assurer la tracabilite documentaire et le suivi qualite

### 1.3 Perimetre fonctionnel

| Module | Description |
|--------|-------------|
| Utilisateurs | Gestion des comptes, roles et permissions |
| Chantiers | Creation et suivi des projets de construction |
| Planning Operationnel | Affectation des equipes aux chantiers |
| Planning de Charge | Vision capacitaire et besoins par metier |
| Feuilles d'heures | Saisie et validation du temps de travail |
| Taches | Gestion des travaux et avancement |
| Formulaires | Templates personnalisables (rapports, PV...) |
| Documents | GED avec gestion des droits d'acces |
| Memos | Communication d'urgence et suivi problemes |
| Interventions | Gestion SAV et maintenance ponctuelle |
| Logistique | Reservation engins et gros materiel |

### 1.4 References

Ce cahier des charges s'inspire des meilleures pratiques de l'application Alobees, solution de reference dans le secteur du BTP, tout en etant adapte aux besoins specifiques du gros oeuvre et de la construction.

---

## 2. TABLEAU DE BORD & FEED D'ACTUALITES

Le tableau de bord est la page d'accueil de l'application apres connexion. Il s'adapte au role de l'utilisateur (Direction, Chef de chantier, Compagnon) et integre un feed d'actualites type reseau social interne.

### 2.1 Vue d'ensemble

Le tableau de bord combine :
- Statistiques et KPI adaptes au role
- Planning personnel de la journee
- Feed d'actualites social avec publication et interactions
- Alertes et notifications importantes
- Actions rapides contextuelles

### 2.2 Tableau de bord Direction / Chef de chantier

#### 2.2.1 Zone de publication avec ciblage

Zone de publication permettant de :
- Saisir un message texte
- Ajouter des photos (bouton dedie)
- Cibler les destinataires (IMPORTANT) :
  - 📢 Tout le monde (tous les utilisateurs)
  - 🏗️ Chantiers specifiques (selection multiple)
  - 👥 Personnes/Equipes (selection multiple avec recherche)

#### 2.2.2 Types de posts affiches

**1. MESSAGE DIRECTION :**
- Badge violet "Direction" + badge verifie
- Indicateur de ciblage visible : "→ Tout le monde" ou "→ Equipe Villa Lyon"
- Compteurs de likes et commentaires

**2. POST AVEC PHOTO :**
- Avatar et badge metier de l'auteur
- Indicateur du chantier : "→ Villa Lyon 3eme"
- Photo integree avec interactions (Like, Commenter)

### 2.3 Tableau de bord Compagnon

Version simplifiee et orientee terrain pour les employes.

#### 2.3.1 Cartes prioritaires

**1. CARTE POINTAGE (verte) :**
- Horloge en temps reel + Date du jour
- Bouton "Pointer l'arrivee" bien visible
- Affichage de la derniere pointee

**2. CARTE METEO (dynamique) :**
- Temperature actuelle + Icone meteo (6 conditions : ensoleille, nuageux, pluvieux, orageux, neigeux, brumeux)
- Geolocalisation automatique du device (fallback Lyon si refusee)
- Donnees reelles via API Open-Meteo (gratuite, sans cle API)
- Vent (vitesse + direction), probabilite de pluie, Min/Max, indice UV
- Degradé de couleur dynamique selon la condition meteo
- Badge d'alerte meteo vigilance (jaune/orange/rouge) si conditions dangereuses
- Clic ouvre l'application meteo native (iOS/Android) ou Meteo-France (desktop)
- Cache 15 minutes avec rafraichissement automatique

**3. CARTE STATISTIQUES :**
- Heures travaillees cette semaine / objectif
- Taches completees / total
- Clic navigue vers les feuilles d'heures

**4. BULLETIN METEO (dans le feed d'actualites) :**
- Affiche en premier dans le feed chaque jour
- Resume textuel du bulletin meteo genere automatiquement
- Details : temperature, vent, pluie, UV, lever/coucher soleil
- Alerte meteo detaillee si vigilance active (phenomenes, description, recommandations BTP)

**5. CARTE EQUIPE DU JOUR :**
- Membres de l'equipe charges depuis les affectations du planning du jour
- Affiche les collegues assignes aux memes chantiers (excluant soi-meme)
- Initiales colorees + role + bouton appel si telephone disponible
- Etat vide si aucun collegue affecte

**6. CARTE MES DOCUMENTS :**
- Documents recents lies aux chantiers presents dans le planning du jour
- Ouverture cross-platform (iOS/Android/Desktop)
- Pagination avec "Voir plus" (4 documents initialement)
- Lien "Voir tout" vers la GED

#### 2.3.2 Planning de la journee

Affichage timeline visuel :
- Horaires : 08:00 - 12:00 (Matin) / 13:30 - 17:00 (Apres-midi)
- Nom et adresse du chantier + Taches assignees avec priorite
- Statut reel du chantier affiche (A lancer / En cours / Receptionne / Ferme)
- Boutons : "Itineraire" (GPS) et "Appeler chef de chantier"
- "Voir plus" si plus de 3 chantiers planifies (pagination)
- Badge "Equipe" pour les affectations non-personnelles (admin/conducteur)
- Pause dejeuner (grisee) + Apercu planning lendemain

#### 2.3.3 Zone de publication compagnon

- Champ : "Partager une photo, signaler un probleme..."
- Bouton "Prendre une photo" (orange, mis en evidence)
- Pas de ciblage (publication automatique pour leur chantier)

### 2.4 Fonctionnalites du feed

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| FEED-01 | Publication posts | Creer et publier des messages texte | ✅ |
| FEED-02 | Ajout photos | Joindre jusqu'a 5 photos par post | ✅ |
| FEED-03 | Ciblage destinataires | Tout le monde / Chantiers / Personnes | ✅ |
| FEED-04 | Likes | Reagir aux publications | ✅ |
| FEED-05 | Commentaires | Repondre aux publications | ✅ |
| FEED-06 | Badges utilisateurs | Affichage role et metier | ✅ |
| FEED-07 | Indicateur ciblage | Afficher la cible du post | ✅ |
| FEED-08 | Posts urgents | Epingler en haut du feed (48h max) | ✅ |
| FEED-09 | Filtrage automatique | Compagnons voient uniquement leurs chantiers | ✅ |
| FEED-10 | Emojis | Support des emojis dans les posts | ✅ |
| FEED-11 | Mise en forme | Texte enrichi basique (retours a la ligne) | ✅ |
| FEED-12 | Horodatage | Date et heure de publication | ✅ |
| FEED-13 | Photos placeholder | Chargement progressif des images | ✅ |
| FEED-14 | Mentions @ | Mentionner des utilisateurs (future) | 🔮 Future |
| FEED-15 | Hashtags | Categoriser les posts (future) | 🔮 Future |
| FEED-16 | Moderation Direction | Supprimer posts d'autrui | ✅ |
| FEED-17 | Notifications push | Alerte nouvelles publications | ⏳ Infra |
| FEED-18 | Historique | Scroll infini pour charger plus | ✅ |
| FEED-19 | Compression photos | Automatique (max 2 Mo) | ✅ |
| FEED-20 | Archivage | Posts +7 jours archives mais consultables | ✅ |

#### 2.4.2 Fonctionnalites du Dashboard

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| DASH-01 | Carte pointage | Clock-in/out temps reel avec modification heure | ✅ |
| DASH-02 | Carte meteo reelle | Geolocalisation + API Open-Meteo + 6 conditions | ✅ |
| DASH-03 | Alertes meteo | Vigilance jaune/orange/rouge avec notification push | ✅ |
| DASH-04 | Bulletin meteo feed | Post automatique resume meteo dans actualites | ✅ |
| DASH-05 | Carte statistiques | Heures + taches, clic vers feuilles heures | ✅ |
| DASH-06 | Planning du jour | Affectations reelles, statut chantier reel | ✅ |
| DASH-07 | Voir plus planning | Pagination si + de 3 chantiers | ✅ |
| DASH-08 | Equipe du jour | Collegues charges depuis planning affectations | ✅ |
| DASH-09 | Mes documents | Documents recents des chantiers planifies | ✅ |
| DASH-10 | Voir plus documents | Pagination avec chargement incremental | ✅ |
| DASH-11 | Actions rapides | Heures, Chantiers, Documents, Photo | ✅ |
| DASH-12 | Navigation GPS | Itineraire via Waze/Google Maps/Apple Maps | ✅ |
| DASH-13 | Appel chef chantier | Bouton appel depuis le planning du jour | ✅ |
| DASH-14 | Badge equipe | Indicateur affectations non-personnelles | ✅ |
| DASH-15 | Notifications push meteo | Alerte auto si conditions dangereuses | ✅ |

**Legende**: ✅ Complet | ⏳ En attente (Infra) | 🔮 Future version

### 2.5 Regles metier

- Compagnons ne voient que posts cibles sur leur(s) chantier(s)
- Posts Direction "Tout le monde" visibles par tous
- Photos compressees automatiquement (max 2 Mo), Maximum 5 photos par post
- Posts +7 jours archives mais consultables
- Posts urgents epingles 48h maximum
- Seule Direction peut supprimer posts d'autrui
- Feed affiche 20 posts par defaut avec scroll infini

---

## 3. GESTION DES UTILISATEURS

### 3.1 Vue d'ensemble

Le module Utilisateurs permet de gerer l'ensemble des collaborateurs (employes et sous-traitants) avec un systeme de roles et permissions granulaires. Chaque utilisateur dispose d'une fiche complete avec photo, couleur d'identification et informations de contact.

### 3.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| USR-01 | Ajout illimite | Nombre d'utilisateurs non plafonne | ✅ |
| USR-02 | Photo de profil | Upload d'une photo personnelle | ✅ |
| USR-03 | Couleur utilisateur | Palette 16 couleurs pour identification visuelle | ✅ |
| USR-04 | Statut Active/Desactive | Toggle pour activer/desactiver l'acces | ✅ |
| USR-05 | Type utilisateur | Employe ou Sous-traitant | ✅ |
| USR-06 | Role | Administrateur / Conducteur / Chef de Chantier / Compagnon | ✅ |
| USR-07 | Code utilisateur | Matricule optionnel pour export paie | ✅ |
| USR-08 | Numero mobile | Format international avec selecteur pays | ✅ |
| USR-09 | Navigation precedent/suivant | Parcourir les fiches utilisateurs | ✅ |
| USR-10 | Revocation instantanee | Desactivation sans suppression des donnees historiques | ✅ |
| USR-11 | Metier/Specialite | Classification par corps de metier | ✅ |
| USR-12 | Email professionnel | Adresse email (requis pour l'authentification) | ✅ |
| USR-13 | Coordonnees d'urgence | Contact en cas d'accident | ✅ |

### 3.3 Matrice des roles et permissions

| Role | Web | Mobile | Perimetre | Droits principaux |
|------|-----|--------|-----------|-------------------|
| Administrateur | ✅ | ✅ | Global | Tous droits, configuration systeme |
| Conducteur | ✅ | ✅ | Ses chantiers | Planification, validation, export |
| Chef de Chantier | ❌ | ✅ | Ses chantiers assignes | Saisie, consultation, publication |
| Compagnon | ❌ | ✅ | Planning perso | Consultation, saisie heures |

### 3.4 Palette de couleurs utilisateurs

16 couleurs disponibles pour l'identification visuelle des utilisateurs. Ces couleurs sont utilisees de maniere coherente dans tout l'ecosysteme : planning, feuilles d'heures, fil d'actualite, affectations.

| Couleur | Code | Couleur | Code |
|---------|------|---------|------|
| Rouge | `#E74C3C` | Bleu fonce | `#2C3E50` |
| Orange | `#E67E22` | Bleu clair | `#3498DB` |
| Jaune | `#F1C40F` | Cyan | `#1ABC9C` |
| Vert clair | `#2ECC71` | Violet | `#9B59B6` |
| Vert fonce | `#27AE60` | Rose | `#E91E63` |
| Marron | `#795548` | Gris | `#607D8B` |
| Corail | `#FF7043` | Indigo | `#3F51B5` |
| Magenta | `#EC407A` | Lime | `#CDDC39` |

---

## 4. GESTION DES CHANTIERS

### 4.1 Vue d'ensemble

Le module Chantiers centralise toutes les informations d'un projet de construction avec un fil d'actualite temps reel, une gestion documentaire integree et un suivi des equipes affectees. Chaque chantier dispose d'onglets dedies pour une navigation fluide.

### 4.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| CHT-01 | Photo de couverture | Image representative du chantier | ✅ |
| CHT-02 | Couleur chantier | Palette 16 couleurs pour coherence visuelle globale | ✅ |
| CHT-03 | Statut chantier | Ouvert / En cours / Receptionne / Ferme | ✅ |
| CHT-04 | Coordonnees GPS | Latitude + Longitude pour geolocalisation | ✅ |
| CHT-05 | Multi-conducteurs | Affectation de plusieurs conducteurs de travaux | ✅ |
| CHT-06 | Multi-chefs de chantier | Affectation de plusieurs chefs | ✅ |
| CHT-07 | Contact chantier | Nom et telephone du contact sur place | ✅ |
| CHT-08 | Navigation GPS | Bouton direct vers Google Maps / Waze | ✅ |
| CHT-09 | Mini carte | Apercu cartographique avec marqueur de localisation | ✅ |
| CHT-10 | Fil d'actualite | Via module Dashboard avec ciblage chantier (FEED-03) | ✅ |
| CHT-11 | Publications photos/videos | Via module Dashboard (FEED-02) - max 5 photos | ✅ |
| CHT-12 | Commentaires | Via module Dashboard (FEED-05) | ✅ |
| CHT-13 | Signature dans publication | Option de signature electronique | 🔮 Future |
| CHT-14 | Navigation precedent/suivant | Parcourir les fiches chantiers | ✅ |
| CHT-15 | Stockage illimite | Aucune limite sur les documents et medias | ✅ |
| CHT-16 | Liste equipe affectee | Visualisation des collaborateurs assignes | ✅ |
| CHT-17 | Alertes signalements | Indicateur visuel si signalement actif | ⏳ Module signalements |
| CHT-18 | Heures estimees | Budget temps previsionnel du chantier | ✅ |
| CHT-19 | Code chantier | Identifiant unique (ex: A001, B023) | ✅ |
| CHT-20 | Dates debut/fin previsionnelles | Planning macro du projet | ✅ |
| CHT-21 | Onglet Logistique | Reservations materiel, stats et planning dans la fiche | ✅ |

**Note**: CHT-10 a CHT-12 sont implementes via le module Dashboard avec ciblage par chantier. Les posts cibles sur un chantier specifique apparaissent dans le fil d'actualite de ce chantier.

### 4.3 Onglets de la fiche chantier

| N° | Onglet | Description | Acces |
|----|--------|-------------|-------|
| 1 | Resume | Informations generales + fil d'actualite temps reel | Tous |
| 2 | Documents | GED - Gestion documentaire avec droits d'acces | Selon droits |
| 3 | Formulaires | Templates a remplir (rapports, PV...) | Tous |
| 4 | Planning | Affectations equipe semaine par semaine | Chef+ |
| 5 | Taches | Liste des travaux hierarchiques avec avancement | Tous |
| 6 | Feuilles de taches | Declarations quotidiennes par compagnon | Conducteur+ |
| 7 | Feuilles d'heures | Saisie et validation du temps de travail | Tous |
| 8 | Logistique | Reservations materiel, stats et planning | Tous |
| 9 | Arrivees/Departs | Pointage et geolocalisation | Conducteur+ |

### 4.4 Statuts de chantier

| Statut | Icone | Description | Actions possibles |
|--------|-------|-------------|-------------------|
| Ouvert | 🔵 | Chantier cree, en preparation | Planification, affectation equipe |
| En cours | 🟢 | Travaux en cours d'execution | Toutes actions operationnelles |
| Receptionne | 🟡 | Travaux termines, en attente cloture | SAV, levee reserves |
| Ferme | 🔴 | Chantier cloture definitivement | Consultation uniquement |

---

## 5. PLANNING OPERATIONNEL

### 5.1 Vue d'ensemble

Le Planning Operationnel permet d'affecter les collaborateurs aux chantiers avec une vue multi-perspective (Chantiers, Utilisateurs, Interventions), un groupement par metier avec badges colores, et une synchronisation temps reel mobile. Les affectations sont visualisees sous forme de blocs colores indiquant les horaires et le chantier.

### 5.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| PLN-01 | 2 onglets de vue | [Chantiers] [Utilisateurs] | ✅ |
| PLN-02 | Onglet Utilisateurs par defaut | Vue ressource comme vue principale | ✅ |
| PLN-03 | Bouton + Creer | Creation rapide d'affectation en haut a droite | ✅ |
| PLN-04 | Dropdown filtre utilisateurs | Utilisateurs planifies / Non planifies / Tous | ✅ |
| PLN-05 | Dropdown filtre chantier | Filtrer par chantier (simplifie vs entonnoir) | ✅ |
| PLN-06 | Toggle weekend | Afficher/masquer samedi-dimanche (simplifie) | ✅ |
| PLN-07 | Filtres par metier | Filtrage par badges metier | ✅ |
| PLN-08 | Selecteur periode | Vue semaine uniquement (mois/trimestre: future) | ✅ |
| PLN-09 | Navigation temporelle | Semaine < [Aujourd'hui] > Semaine | ✅ |
| PLN-10 | Indicateur semaine | Numero et dates de la semaine affichee | ✅ |
| PLN-11 | Badge non planifies | Compteur des ressources non affectees | ✅ |
| PLN-12 | Groupement par metier | Arborescence repliable par type d'utilisateur | ✅ |
| PLN-13 | Badges metier colores | Employe, Charpentier, Couvreur, Electricien, Sous-traitant... | ✅ |
| PLN-14 | Chevrons repliables | ▼ / > pour afficher/masquer les groupes | ✅ |
| PLN-15 | Avatar utilisateur | Cercle avec initiales + code couleur personnel | ✅ |
| PLN-16 | Bouton duplication | Dupliquer les affectations vers semaine suivante | ✅ |
| PLN-17 | Blocs affectation colores | Couleur = chantier (coherence visuelle globale) | ✅ |
| PLN-18 | Format bloc | HH:MM - HH:MM + icone note + Nom chantier | ✅ |
| PLN-19 | Icone note dans bloc | 📝 Indicateur de commentaire sur l'affectation | ✅ |
| PLN-20 | Multi-affectations/jour | Plusieurs blocs possibles par utilisateur par jour | ✅ |
| PLN-21 | Colonnes jours | Lundi 21 juil. / Mardi 22 juil. etc. | ✅ |
| PLN-22 | Filtres metiers | Filtrage par selection de metiers | ✅ |
| PLN-23 | Notification push | Alerte a chaque nouvelle affectation | ⏳ Infra |
| PLN-24 | Mode Offline | Consultation planning sans connexion | ⏳ Infra |
| PLN-25 | Notes privees | Commentaires visibles uniquement par l'affecte | ✅ |
| PLN-26 | Bouton appel | Icone telephone sur hover utilisateur | ✅ |
| PLN-27 | Drag & Drop | Deplacer les blocs pour modifier les affectations | ✅ |
| PLN-28 | Double-clic creation | Double-clic cellule vide → creation affectation | ✅ |

**Legende**: ✅ Complet | ⏳ Infra = Infrastructure requise

**Notes d'implementation**:
- PLN-05 simplifie : dropdown chantier au lieu d'icone entonnoir avec modal
- PLN-06 simplifie : toggle weekend au lieu d'icone engrenage avec parametres
- PLN-22 : filtre par metiers via panel depliable (pas barre de recherche texte)

### 5.3 Badges metiers (Groupement)

| Badge | Couleur | Description |
|-------|---------|-------------|
| Employe | 🔵 Bleu fonce | Compagnons internes polyvalents |
| Charpentier | 🟢 Vert | Specialistes bois et charpente |
| Couvreur | 🟠 Orange | Specialistes toiture |
| Electricien | 🟣 Magenta/Rose | Specialistes electricite |
| Sous-traitant | 🔴 Rouge/Corail | Prestataires externes |
| Macon | 🟤 Marron | Specialistes maconnerie (Greg) |
| Coffreur | 🟡 Jaune | Specialistes coffrage (Greg) |
| Ferrailleur | ⚫ Gris fonce | Specialistes ferraillage (Greg) |
| Grutier | 🩵 Cyan | Conducteurs d'engins (Greg) |

### 5.4 Structure d'une affectation

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| Utilisateur | Reference | Oui | Compagnon ou sous-traitant affecte |
| Chantier | Reference | Oui | Chantier d'affectation |
| Date | Date | Oui | Jour de l'affectation |
| Heure debut | HH:MM | Non | Heure de prise de poste |
| Heure fin | HH:MM | Non | Heure de fin de journee |
| Note | Texte | Non | Commentaire prive pour l'affecte |
| Recurrence | Option | Non | Unique / Repeter (jours selectionnes) |

### 5.5 Matrice des droits - Planning

| Action | Admin | Conducteur | Chef | Compagnon |
|--------|-------|------------|------|-----------|
| Voir planning global | ✅ | ✅ | ❌ | ❌ |
| Voir planning ses chantiers | ✅ | ✅ | ✅ | ❌ |
| Voir son planning personnel | ✅ | ✅ | ✅ | ✅ |
| Creer affectation | ✅ | ✅ | ❌ | ❌ |
| Modifier affectation | ✅ | ✅ | ❌ | ❌ |
| Supprimer affectation | ✅ | ✅ | ❌ | ❌ |
| Ajouter note | ✅ | ✅ | ✅ | ❌ |
| Dupliquer affectations | ✅ | ✅ | ❌ | ❌ |

### 5.6 Vue Mobile

Sur mobile, le planning s'affiche avec une navigation par jour (L M M J V S D) et deux onglets [Chantiers] et [Utilisateurs]. La vue Chantiers liste les chantiers avec leurs collaborateurs affectes. La vue Utilisateurs liste les collaborateurs avec leurs affectations. Chaque affectation peut etre supprimee via le bouton ✕. Le FAB (+) permet de creer une nouvelle affectation.

---

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

## 7. FEUILLES D'HEURES

### 7.1 Vue d'ensemble

Le module Feuilles d'heures permet la saisie, le suivi et l'export des heures travaillees avec deux vues complementaires (Chantiers et Compagnons) et des variables de paie integrees. Il s'interface avec les ERP pour l'export automatise.

### 7.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| FDH-01 | 2 onglets de vue | [Chantiers] [Compagnons/Sous-traitants] | ✅ |
| FDH-02 | Navigation par semaine | Semaine X avec << < > >> pour naviguer | ✅ |
| FDH-03 | Bouton Exporter | Export des donnees vers fichier ou ERP | ✅ |
| FDH-04 | Filtre utilisateurs | Dropdown de selection multi-criteres | ✅ |
| FDH-05 | Vue tabulaire hebdomadaire | Lundi a Vendredi avec dates completes | ✅ |
| FDH-06 | Multi-chantiers par utilisateur | Plusieurs lignes possibles | ✅ |
| FDH-07 | Badges colores par chantier | Coherence avec le planning | ✅ |
| FDH-08 | Total par ligne | Somme heures par utilisateur + chantier | ✅ |
| FDH-09 | Total groupe | Somme heures utilisateur tous chantiers | ✅ |
| FDH-10 | Creation auto a l'affectation | Lignes pre-remplies depuis le planning | ✅ |
| FDH-11 | Saisie mobile | Selecteur roulette HH:MM intuitif | ⏳ Frontend |
| FDH-12 | Signature electronique | Validation des heures par le compagnon | ✅ |
| FDH-13 | Variables de paie | Panier, transport, conges, primes, absences | ✅ |
| FDH-14 | Jauge d'avancement | Comparaison planifie vs realise | ✅ |
| FDH-15 | Comparaison inter-equipes | Detection automatique des ecarts | ✅ |
| FDH-16 | Import ERP auto | Synchronisation quotidienne/hebdomadaire | ⏳ Infra |
| FDH-17 | Export ERP manuel | Periode selectionnee personnalisable | ✅ |
| FDH-18 | Macros de paie | Calculs automatises parametrables | ⏳ Frontend |
| FDH-19 | Feuilles de route | Generation automatique PDF | ✅ |
| FDH-20 | Mode Offline | Saisie sans connexion, sync auto | ⏳ Frontend |

### 7.3 Variables de paie

| Variable | Type | Description |
|----------|------|-------------|
| Heures normales | Nombre | Heures de travail standard |
| Heures supplementaires | Nombre | Heures au-dela du contrat |
| Panier repas | Montant | Indemnite de repas |
| Indemnite transport | Montant | Frais de deplacement |
| Prime intemperies | Montant | Compensation meteo |
| Conges payes | Jours | Absences conges |
| Maladie | Jours | Absences maladie |
| Absence injustifiee | Jours | Absences non justifiees |

---

## 8. FORMULAIRES CHANTIER

### 8.1 Vue d'ensemble

Le module Formulaires permet de creer des templates personnalises pour tous les documents terrain : rapports d'intervention, PV de reception, bons de livraison, formulaires de securite, etc. Les formulaires sont remplis sur mobile et centralises automatiquement.

### 8.2 Fonctionnalites

| ID | Fonctionnalite | Description | Statut |
|----|----------------|-------------|--------|
| FOR-01 | Templates personnalises | Creation et gestion des templates via API | ✅ |
| FOR-02 | Remplissage mobile | Infrastructure backend pour saisie mobile | ✅ |
| FOR-03 | Champs auto-remplis | Date, heure, localisation, intervenant | ✅ |
| FOR-04 | Ajout photos horodatees | Preuve visuelle avec timestamp GPS | ✅ |
| FOR-05 | Signature electronique | Chef de chantier + client si necessaire | ✅ |
| FOR-06 | Centralisation automatique | Rattachement au chantier concerne | ✅ |
| FOR-07 | Horodatage automatique | Date et heure de soumission enregistrees | ✅ |
| FOR-08 | Historique complet | Toutes les versions conservees | ✅ |
| FOR-09 | Export PDF | Structure pour generation du document final | ✅ |
| FOR-10 | Liste par chantier | Endpoint liste par chantier | ✅ |
| FOR-11 | Lien direct | Creation formulaire depuis template | ✅ |

### 8.3 Types de formulaires

| Categorie | Exemples de formulaires |
|-----------|-------------------------|
| Interventions | Rapport d'intervention, Bon de SAV, Fiche depannage |
| Reception | PV de reception, Constat de reserves, Attestation fin travaux |
| Securite | Formulaire securite, Visite PPSPS, Auto-controle, Quart d'heure securite |
| Incidents | Declaration sinistre, Fiche non-conformite, Rapport accident |
| Approvisionnement | Commande materiel, Bon de livraison, Reception materiaux |
| Administratif | Demande de conges, CERFA, Attestation diverse |
| Gros Oeuvre (Greg) | Rapport journalier, Bon de betonnage, Controle ferraillage |

---

## 9. GESTION DOCUMENTAIRE (GED)

### 9.1 Vue d'ensemble

Le module Documents offre une gestion documentaire complete avec arborescence par dossiers numerotes, controle d'acces granulaire par role et nominatif, et synchronisation offline automatique des plans pour consultation terrain.

### 9.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| GED-01 | Onglet Documents integre | Dans chaque fiche chantier | ✅ |
| GED-02 | Arborescence par dossiers | Organisation hierarchique numerotee | ✅ |
| GED-03 | Tableau de gestion | Vue liste avec metadonnees (taille, date, auteur) | ✅ |
| GED-04 | Role minimum par dossier | Compagnon / Chef / Conducteur / Admin | ✅ |
| GED-05 | Autorisations specifiques | Permissions nominatives additionnelles | ✅ |
| GED-06 | Upload multiple | Jusqu'a 10 fichiers simultanes | ✅ |
| GED-07 | Taille max 10 Go | Par fichier individuel | ✅ |
| GED-08 | Zone Drag & Drop | Glisser-deposer intuitif | ✅ |
| GED-09 | Barre de progression | Affichage % upload en temps reel | ✅ |
| GED-10 | Selection droits a l'upload | Roles + Utilisateurs nominatifs | ✅ |
| GED-11 | Transfert auto depuis ERP | Synchronisation Costructor/Graneet | ⏳ Infra |
| GED-12 | Formats supportes | PDF, Images (PNG/JPG), XLS/XLSX, DOC/DOCX, Videos | ✅ |
| GED-13 | Actions Editer/Supprimer | Gestion complete des fichiers | ✅ |
| GED-14 | Consultation mobile | Visualisation sur application (responsive) | ✅ |
| GED-15 | Synchronisation Offline | Plans telecharges automatiquement | ⏳ Infra |
| GED-16 | Telechargement groupe ZIP | Selection multiple + archive ZIP a telecharger | ✅ |
| GED-17 | Previsualisation integree | Visionneuse PDF/images/videos dans l'application | ✅ |

**Module COMPLET** - Backend + Frontend implementes (15/17 fonctionnalites, 2 en attente infra)

### 9.3 Niveaux d'acces

| Role minimum | Qui peut voir | Cas d'usage |
|--------------|---------------|-------------|
| Compagnon/Sous-Traitant | Tous utilisateurs du chantier | Plans d'execution, consignes securite |
| Chef de Chantier | Chefs + Conducteurs + Admin | Documents techniques sensibles |
| Conducteur | Conducteurs + Admin uniquement | Contrats, budgets, planning macro |
| Administrateur | Admin uniquement | Documents confidentiels, RH |

### 9.4 Arborescence type

| N° | Dossier | Contenu type |
|----|---------|--------------|
| 01 | Plans | Plans d'execution, plans beton, reservations |
| 02 | Documents administratifs | Marches, avenants, OS, situations |
| 03 | Securite | PPSPS, plan de prevention, consignes |
| 04 | Qualite | Fiches techniques, PV essais, autocontroles |
| 05 | Photos | Photos chantier par date/zone |
| 06 | Comptes-rendus | CR reunions, CR chantier |
| 07 | Livraisons | Bons de livraison, bordereaux |

---

## 10. SIGNALEMENTS

### 10.1 Vue d'ensemble

Le module Signalements permet de signaler des urgences, problemes ou informations importantes avec un systeme de fil de conversation type chat, de statuts ouvert/ferme, et d'alertes automatiques pour les signalements non traites. Les signalements sont rattaches a un chantier et generent des notifications push avec escalade hierarchique.

### 10.2 Fonctionnalites de base

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| SIG-01 | Rattachement chantier | Signalement obligatoirement lie a un projet | ✅ |
| SIG-02 | Liste chronologique | Affichage par date de creation | ✅ |
| SIG-03 | Indicateur statut | 🟢 Ouvert / 🔴 Ferme | ✅ |
| SIG-04 | Photo chantier | Vignette d'identification visuelle | ✅ |
| SIG-05 | Horodatage | Date + heure de creation | ✅ |
| SIG-06 | Fil de conversation | Mode chat pour echanges multiples | ✅ |
| SIG-07 | Statut ferme avec badge | Ce signalement a ete ferme le [date] | ✅ |
| SIG-08 | Ajout photo/video | Dans les reponses du fil | ✅ |
| SIG-09 | Signature dans reponses | Validation des actions correctives | ✅ |
| SIG-10 | Bouton Publier | Envoyer une reponse dans le fil | ✅ |
| SIG-11 | Historique | X a ajoute un signalement sur Y le [date] | ✅ |
| SIG-12 | Bouton + (FAB) | Creation rapide sur mobile | ✅ |
| SIG-13 | Notifications push | Alerte temps reel a la creation | ⏳ Infra |

### 10.3 Fonctionnalites d'alertes et escalade

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| SIG-14 | Priorite signalement | 4 niveaux : Critique / Haute / Moyenne / Basse | ✅ |
| SIG-15 | Date resolution souhaitee | Echeance optionnelle fixee par le createur | ✅ |
| SIG-16 | Alertes retard | Notification si signalement non traite dans les delais | ⏳ Infra |
| SIG-17 | Escalade automatique | Remontee hierarchique progressive | ⏳ Infra |
| SIG-18 | Tableau de bord alertes | Vue des signalements en retard (Admin/Conducteur) | ✅ |
| SIG-19 | Filtres avances | Par chantier, statut, periode, priorite (Admin/Conducteur) | ✅ |
| SIG-20 | Vue globale | Tous les signalements tous chantiers (Admin/Conducteur) | ✅ |

### 10.4 Delais d'escalade par defaut

Si aucune date de resolution n'est fixee, les delais par defaut s'appliquent :

| Priorite | Delai alerte | Couleur | Cas d'usage |
|----------|--------------|---------|-------------|
| Critique | 4h | 🔴 Rouge | Securite, arret chantier |
| Haute | 24h | 🟠 Orange | Probleme technique bloquant |
| Moyenne | 48h | 🟡 Jaune | Approvisionnement, qualite |
| Basse | 72h | 🔵 Bleu | Information, amelioration |

### 10.5 Regles d'escalade

Un signalement est considere "en retard" si :
- Une date de resolution est fixee ET la date actuelle depasse cette echeance
- OU aucune date n'est fixee ET le delai par defaut (selon priorite) est depasse depuis la derniere activite

Notifications d'escalade :

| Declencheur | Destinataires | Canal |
|-------------|---------------|-------|
| 50% du delai ecoule | Createur + Chef de chantier | Push |
| 100% du delai (en retard) | + Conducteur de travaux | Push + Email |
| 200% du delai (critique) | + Administrateur | Push + Email + SMS |

### 10.6 Cas d'usage

| Type | Exemple | Priorite |
|------|---------|----------|
| Urgence securite | Echafaudage instable zone B - STOP travaux | Critique |
| Probleme technique | Fuite reseau eau potable niveau -1 | Haute |
| Approvisionnement | Rupture stock ferraille HA12, livraison retardee | Moyenne |
| Qualite | Non-conformite beton livre (slump trop eleve) | Haute |
| Incident | Bris de cable sur grue tour, arret maintenance | Haute |
| Information | Visite client prevue demain 10h - preparer zone A | Basse |

### 10.7 Matrice des droits - Signalements

| Action | Admin | Conducteur | Chef de Chantier | Compagnon |
|--------|-------|------------|------------------|-----------|
| Voir signalements (global) | ✅ | ✅ | ❌ | ❌ |
| Voir signalements (ses chantiers) | ✅ | ✅ | ✅ | ✅ |
| Creer un signalement | ✅ | ✅ | ✅ | ✅ |
| Repondre dans le fil | ✅ | ✅ | ✅ | ✅ |
| Ajouter photo/video | ✅ | ✅ | ✅ | ✅ |
| Signer une reponse | ✅ | ✅ | ✅ | ❌ |
| Fermer un signalement | ✅ | ✅ | ✅ | ❌ |
| Rouvrir un signalement | ✅ | ✅ | ❌ | ❌ |
| Supprimer un signalement | ✅ | ✅ | ❌ | ❌ |
| Filtres avances | ✅ | ✅ | ❌ | ❌ |

### 10.8 Vues par role

**Admin / Conducteur** : Vue globale avec filtres (chantier, statut, periode, priorite) + tableau de bord des alertes

**Chef de Chantier / Compagnon** : Vue par chantier uniquement (onglet Signalements de la fiche chantier)

---

## 11. LOGISTIQUE - GESTION DU MATERIEL

### 11.1 Vue d'ensemble

Le module Logistique permet de gerer les engins et gros materiel de l'entreprise avec un systeme de reservation par chantier, validation hierarchique optionnelle et visualisation calendrier. Chaque ressource dispose de son planning propre.

### 11.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| LOG-01 | Referentiel materiel | Liste des engins disponibles (Admin uniquement) | ✅ Backend + Frontend |
| LOG-02 | Fiche ressource | Nom, code, photo, couleur, plage horaire par defaut | ✅ Backend + Frontend |
| LOG-03 | Planning par ressource | Vue calendrier hebdomadaire 7 jours | ✅ Backend + Frontend |
| LOG-04 | Navigation semaine | < [Semaine X] > avec 3 semaines visibles | ✅ Backend + Frontend |
| LOG-05 | Axe horaire vertical | 08:00 → 18:00 (configurable) | ✅ Frontend |
| LOG-06 | Blocs reservation colores | Par demandeur avec nom + bouton ✕ | ✅ Frontend |
| LOG-07 | Demande de reservation | Depuis mobile ou web | ✅ Backend + Frontend |
| LOG-08 | Selection chantier | Association obligatoire au projet | ✅ Backend |
| LOG-09 | Selection creneau | Date + heure debut / heure fin | ✅ Backend + Frontend |
| LOG-10 | Option validation N+1 | Activation/desactivation par ressource | ✅ Backend |
| LOG-11 | Workflow validation | Demande 🟡 → Chef valide → Confirme 🟢 | ✅ Backend + Frontend |
| LOG-12 | Statuts reservation | En attente 🟡 / Validee 🟢 / Refusee 🔴 | ✅ Backend + Frontend |
| LOG-13 | Notification demande | Push au valideur (chef/conducteur) | ✅ Firebase FCM |
| LOG-14 | Notification decision | Push au demandeur | ✅ Firebase FCM |
| LOG-15 | Rappel J-1 | Notification veille de reservation | ✅ APScheduler |
| LOG-16 | Motif de refus | Champ texte optionnel | ✅ Backend + Frontend |
| LOG-17 | Conflit de reservation | Alerte si creneau deja occupe | ✅ Backend |
| LOG-18 | Historique par ressource | Journal complet des reservations | ✅ Backend + Frontend |

### 11.3 Types de ressources (Greg Constructions)

| Categorie | Exemples | Validation |
|-----------|----------|------------|
| Engins de levage | Grue mobile, Manitou, Nacelle, Chariot elevateur | N+1 requis |
| Engins de terrassement | Mini-pelle, Pelleteuse, Compacteur, Dumper | N+1 requis |
| Vehicules | Camion benne, Fourgon, Vehicule utilitaire | Optionnel |
| Gros outillage | Betonniere, Vibrateur, Pompe a beton | Optionnel |
| Equipements | Echafaudage, Etais, Banches, Coffrages | N+1 requis |

### 11.4 Matrice des droits - Logistique

| Action | Admin | Conducteur | Chef | Compagnon |
|--------|-------|------------|------|-----------|
| Creer ressource | ✅ | ❌ | ❌ | ❌ |
| Modifier ressource | ✅ | ❌ | ❌ | ❌ |
| Supprimer ressource | ✅ | ❌ | ❌ | ❌ |
| Voir planning ressource | ✅ | ✅ | ✅ | ✅ |
| Demander reservation | ✅ | ✅ | ✅ | ✅ |
| Valider/Refuser | ✅ | ✅ | ✅ | ❌ |

---

## 12. GESTION DES INTERVENTIONS

### 12.1 Vue d'ensemble

Le module Interventions est dedie a la gestion des interventions ponctuelles (SAV, maintenance, depannages, levee de reserves) distinctes des chantiers de longue duree. Il dispose d'un planning specifique et permet la generation de rapports d'intervention signes.

### 12.2 Difference Chantier vs Intervention

| Critere | Chantier | Intervention |
|---------|----------|--------------|
| Duree | Longue (semaines/mois) | Courte (heures/jours) |
| Equipe | Multiple collaborateurs | 1-2 techniciens |
| Recurrence | Continue | Ponctuelle |
| Usage | Gros oeuvre, construction | SAV, maintenance, depannage |
| Livrable | Suivi global projet | Rapport d'intervention signe |

### 12.3 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| INT-01 | Onglet dedie Planning | 3eme onglet Gestion des interventions | ✅ |
| INT-02 | Liste des interventions | Tableau Chantier/Client/Adresse/Statut | ✅ |
| INT-03 | Creation intervention | Bouton + pour nouvelle intervention | ✅ |
| INT-04 | Fiche intervention | Client, adresse, contact, description, priorite | ✅ |
| INT-05 | Statuts intervention | A planifier / Planifiee / En cours / Terminee / Annulee | ✅ |
| INT-06 | Planning hebdomadaire | Utilisateurs en lignes, jours en colonnes | ✅ |
| INT-07 | Blocs intervention colores | Format HH:MM - HH:MM - Code - Nom client | ✅ |
| INT-08 | Multi-interventions/jour | Plusieurs par utilisateur | ✅ |
| INT-09 | Toggle Afficher les taches | Activer/desactiver l'affichage | ✅ |
| INT-10 | Affectation technicien | Drag & drop ou via modal | ✅ |
| INT-11 | Fil d'actualite | Timeline actions, photos, commentaires | ✅ |
| INT-12 | Chat intervention | Discussion instantanee equipe | ✅ |
| INT-13 | Signature client | Sur mobile avec stylet/doigt | ✅ |
| INT-14 | Rapport PDF | Generation automatique avec tous les details | ⏳ Infra |
| INT-15 | Selection posts pour rapport | Choisir les elements a inclure | ⏳ Infra |
| INT-16 | Generation mobile | Creer le PDF depuis l'application | ⏳ Infra |
| INT-17 | Affectation sous-traitants | Prestataires externes (PLB, CFA...) | ✅ |

### 12.4 Contenu du rapport PDF

| Section | Contenu |
|---------|---------|
| En-tete | Logo entreprise, N° intervention, Date generation |
| Client | Nom, Adresse complete, Contact, Telephone |
| Intervenant(s) | Nom(s) du/des technicien(s) affectes |
| Horaires | Heure debut, heure fin, duree totale |
| Description | Motif de l'intervention |
| Travaux realises | Detail des actions effectuees |
| Photos | Avant / Pendant / Apres (selectionnees) |
| Anomalies | Problemes constates non resolus |
| Signatures | Client + Technicien avec horodatage |

---

## 13. GESTION DES TACHES

### 13.1 Vue d'ensemble

Le module Taches permet de creer des listes de travaux structurees par chantier avec un systeme de taches/sous-taches hierarchiques, une bibliotheque de modeles reutilisables, et un suivi d'avancement en temps reel avec code couleur.

### 13.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| TAC-01 | Onglet Taches par chantier | Accessible depuis la fiche chantier | ✅ |
| TAC-02 | Structure hierarchique | Taches parentes + sous-taches imbriquees | ✅ |
| TAC-03 | Chevrons repliables | ▼ / > pour afficher/masquer | ✅ |
| TAC-04 | Bibliotheque de modeles | Templates reutilisables avec sous-taches | ✅ |
| TAC-05 | Creation depuis modele | Importer un modele dans un chantier | ✅ |
| TAC-06 | Creation manuelle | Tache personnalisee libre | ✅ |
| TAC-07 | Bouton + Ajouter | Creation rapide de tache | ✅ |
| TAC-08 | Date d'echeance | Deadline pour la tache | ✅ |
| TAC-09 | Unite de mesure | m², litre, unite, ml, kg, m³... | ✅ |
| TAC-10 | Quantite estimee | Volume/quantite prevu | ✅ |
| TAC-11 | Heures estimees | Temps prevu pour realisation | ✅ |
| TAC-12 | Heures realisees | Temps effectivement passe | ✅ |
| TAC-13 | Statuts tache | A faire ☐ / Termine ✅ | ✅ |
| TAC-14 | Barre de recherche | Filtrer par mot-cle | ✅ |
| TAC-15 | Reorganiser les taches | Drag & drop pour reordonner | ✅ |
| TAC-16 | Export rapport PDF | Recapitulatif des taches | ✅ |
| TAC-17 | Vue mobile | Consultation et mise a jour (responsive) | ✅ |
| TAC-18 | Feuilles de taches | Declaration quotidienne travail realise | ✅ |
| TAC-19 | Validation conducteur | Valide le travail declare | ✅ |
| TAC-20 | Code couleur avancement | Vert/Jaune/Rouge selon progression | ✅ |

**Module COMPLET** - Backend + Frontend implementes (20/20 fonctionnalites)

### 13.3 Modeles de taches - Gros Oeuvre

| Nom | Description | Unite |
|-----|-------------|-------|
| Coffrage voiles | Mise en place des banches, reglage d'aplomb, serrage | m² |
| Ferraillage plancher | Pose des armatures, ligatures, verification enrobages | kg |
| Coulage beton | Preparation, vibration, talochage, cure | m³ |
| Decoffrage | Retrait des banches, nettoyage, stockage | m² |
| Pose predalles | Manutention, calage, etaiement provisoire | m² |
| Reservations | Mise en place des reservations techniques | unite |
| Traitement reprise | Preparation surfaces, application produit adherence | ml |

### 13.4 Codes couleur - Avancement

| Couleur | Condition | Signification |
|---------|-----------|---------------|
| 🟢 Vert | Heures realisees <= 80% estimees | Dans les temps |
| 🟡 Jaune | Heures realisees entre 80% et 100% | Attention, limite proche |
| 🔴 Rouge | Heures realisees > estimees | Depassement, retard |
| ⚪ Gris | Heures realisees = 0 | Non commence |

---

## 14. INTEGRATIONS

### 14.1 ERP compatibles

| ERP | Import | Export | Donnees synchronisees |
|-----|--------|--------|----------------------|
| Costructor | ✅ | ✅ | Chantiers, heures, documents, taches |
| Graneet | ✅ | ✅ | Chantiers, heures, documents |

### 14.2 Flux de donnees

| Donnees | Direction | Frequence | Mode |
|---------|-----------|-----------|------|
| Chantiers | ERP → App | Temps reel ou quotidien | Automatique |
| Feuilles d'heures | App → ERP | Quotidien/Hebdo/Mensuel | Automatique |
| Documents | ERP ↔ App | A la demande | Automatique |
| Taches | ERP → App | Import initial | Manuel |
| Variables paie | App → ERP | Hebdomadaire | Automatique |

### 14.3 Canaux de notification

| Canal | Utilisation | Delai |
|-------|-------------|-------|
| Push mobile | Affectations, validations, alertes, memos | Temps reel |
| Push meteo | Alertes meteo vigilance (vent, orages, canicule, verglas) | Temps reel |
| SMS | Invitations, urgences critiques | Temps reel |
| Email | Rapports, exports, recapitulatifs hebdo | Differe |

---

## 15. SECURITE ET CONFORMITE

### 15.1 Authentification

La connexion s'effectue de maniere securisee par SMS (code OTP) ou par identifiants classiques (email + mot de passe). La revocation des acces est instantanee et n'affecte pas les donnees historiques.

### 15.2 Protection des donnees

| Mesure | Description | Status |
|--------|-------------|--------|
| Chiffrement en transit | HTTPS/TLS 1.3 pour toutes les communications | ✅ |
| Chiffrement au repos | Donnees chiffrees AES-256 sur les serveurs | ✅ |
| Sauvegarde | Backup quotidien avec retention 30 jours minimum | ✅ |
| RGPD | Conformite totale, droit d'acces et droit a l'oubli | ✅ |
| Hebergement | Serveurs en Europe (France) certifies ISO 27001 | ✅ |
| Journalisation | Logs d'audit de toutes les actions sensibles | ✅ |
| Protection CSRF | Token CSRF pour requetes mutables (POST/PUT/DELETE) | ✅ |
| Consentement RGPD | Modal de consentement pour geolocalisation | ✅ |

### 15.3 Mode Offline

L'application mobile permet de consulter le planning, saisir les heures, remplir les formulaires et consulter les plans meme sans connexion internet. La synchronisation s'effectue automatiquement au retour de la connectivite, avec gestion des conflits.

### 15.4 Niveaux de confidentialite

| Niveau | Acces | Exemples de donnees |
|--------|-------|---------------------|
| Public chantier | Tous les affectes au chantier | Plans, consignes, planning |
| Restreint chef | Chefs + Conducteurs + Admin | Documents techniques |
| Confidentiel | Conducteurs + Admin | Budgets, contrats, situations |
| Secret | Admin uniquement | Documents RH, donnees sensibles |

---

## 16. GLOSSAIRE

| Terme | Definition |
|-------|------------|
| Compagnon | Ouvrier de chantier (macon, coffreur, ferrailleur, grutier...) |
| Conducteur de travaux | Responsable de plusieurs chantiers, gere planning et budgets |
| Chef de chantier | Responsable operationnel d'un chantier specifique |
| Sous-traitant | Prestataire externe intervenant ponctuellement sur chantier |
| Gros oeuvre | Structure porteuse du batiment (fondations, murs, dalles, poteaux) |
| Banche | Coffrage metallique modulaire pour couler les murs en beton |
| Predalle | Dalle prefabriquee servant de coffrage perdu pour plancher |
| Ferraillage | Armatures metalliques noyees dans le beton arme |
| PV de reception | Proces-verbal de fin de travaux signe par le client |
| Memo | Note d'urgence ou d'information importante a traiter |
| FAB | Floating Action Button - bouton d'action flottant sur mobile |
| Push | Notification instantanee envoyee sur le smartphone |
| Offline | Mode deconnecte permettant de travailler sans internet |
| ERP | Enterprise Resource Planning - logiciel de gestion d'entreprise |
| GED | Gestion Electronique des Documents |
| PPSPS | Plan Particulier de Securite et de Protection de la Sante |
| N+1 | Superieur hierarchique direct (pour validation) |
| SAV | Service Apres-Vente |
| OS | Ordre de Service |

---

*Greg Constructions - Cahier des Charges Fonctionnel v2.1 - Janvier 2026*
