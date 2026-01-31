# GREG CONSTRUCTIONS

**Gros Oeuvre - Batiment**

## CAHIER DES CHARGES FONCTIONNEL

Application SaaS de Gestion de Chantiers

**Version 2.2 - Janvier 2026**

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
17. [Gestion Financiere et Budgetaire](#17-gestion-financiere-et-budgetaire)
18. [Gestion des Devis](#18-gestion-des-devis)
19. [Glossaire](#19-glossaire)

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
| FEED-14 | Mentions @ | Mentionner des utilisateurs avec autocomplete @ et affichage cliquable | ✅ |
| FEED-15 | Hashtags | Categoriser les posts (future) | 🔮 Future |
| FEED-16 | Moderation Direction | Supprimer posts d'autrui | ✅ |
| FEED-17 | Notifications push | Alerte nouvelles publications | ⏳ Infra |
| FEED-18 | Historique | Scroll infini pour charger plus | ✅ |
| FEED-19 | Compression photos | Automatique (max 2 Mo) | ✅ |
| FEED-20 | Archivage | Posts +7 jours archives mais consultables | ✅ |

#### 2.4.2 Fonctionnalites du Dashboard

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| DASH-01 | Carte pointage | Clock-in/out temps reel avec modification heure, persistance backend via pointagesService | ✅ |
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
| USR-14 | Invitation utilisateur | Envoi email invitation avec lien activation compte | ✅ |
| USR-15 | Reset password | Reinitialisation mot de passe via email avec token | ✅ |
| USR-16 | Change password | Modification mot de passe depuis parametres compte | ✅ |
| USR-17 | Statut is_active | Activation/desactivation compte apres invitation | ✅ |

### 3.3 Authentification et securite

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| AUTH-01 | Login email/password | Connexion avec email professionnel et mot de passe | ✅ |
| AUTH-02 | JWT tokens | Authentification par tokens (access + refresh) | ✅ |
| AUTH-03 | Invitation utilisateur | Admin envoie invitation avec lien activation 7j | ✅ |
| AUTH-04 | Acceptation invitation | Utilisateur cree mot de passe et active compte | ✅ |
| AUTH-05 | Reset password request | Demande reinitialisation avec envoi email token | ✅ |
| AUTH-06 | Reset password | Reinitialisation avec token valide 1h | ✅ |
| AUTH-07 | Change password | Modification depuis parametres (mot de passe actuel requis) | ✅ |
| AUTH-08 | Email verification | Templates HTML pour invitation, reset, verification | ✅ |
| AUTH-09 | Token expiration | Tokens invitation (7j), reset (1h) avec validation | ✅ |
| AUTH-10 | Password strength | Validation force mot de passe (8+ car, maj, min, chiffre) | ✅ |
| AUTH-11 | Droit a l'oubli RGPD | Suppression definitive donnees utilisateur (Art. 17 RGPD) | ✅ |

**AUTH-11 - Détails technique** :
- Endpoint: `DELETE /api/auth/users/{user_id}/gdpr`
- Permissions: Admin ou utilisateur lui-même uniquement
- Action: Hard delete définitif de toutes les données personnelles
- Conformité: RGPD Article 17 (Right to erasure)
- Auditabilité: Horodatage de suppression retourné

### 3.4 Matrice des roles et permissions

| Role | Web | Mobile | Perimetre | Droits principaux |
|------|-----|--------|-----------|-------------------|
| Administrateur | ✅ | ✅ | Global | Tous droits, configuration systeme, invitation utilisateurs |
| Conducteur | ✅ | ✅ | Ses chantiers | Planification, validation, export |
| Chef de Chantier | ❌ | ✅ | Ses chantiers assignes | Saisie, consultation, publication |
| Compagnon | ❌ | ✅ | Planning perso | Consultation, saisie heures |

### 3.5 Palette de couleurs utilisateurs

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
| CHT-19 | Code chantier | Identifiant unique (ex: A001, B023, 2026-01-MONTMELIAN) | ✅ |
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

### 4.4 Codes chantier

Le code chantier est l'identifiant unique obligatoire de chaque chantier. Deux formats sont supportes :

| Format | Pattern | Exemples | Usage |
|--------|---------|----------|-------|
| **Legacy** | `[A-Z]\d{3}` | A001, B023, Z999 | Chantiers anciens, absences (CONGES, MALADIE) |
| **Standard** | `\d{4}-[A-Z0-9_-]+` | 2026-01-MONTMELIAN, 2024-10-TOURNON-COMMERCIAL | Chantiers depuis 2024 |

**Regles** :
- Code unique par chantier (contrainte DB)
- Auto-generation si non fourni (A001, A002, ..., A999, B001, ...)
- Codes speciaux pour absences : CONGES, MALADIE, FORMATION, RTT, ABSENT
- Format annee-numero-nom recommande pour nouveaux chantiers

### 4.5 Statuts de chantier

| Statut | Icone | Description | Actions possibles |
|--------|-------|-------------|-------------------|
| Ouvert | 🔵 | Chantier cree, en preparation | Planification, affectation equipe |
| En cours | 🟢 | Travaux en cours d'execution | Toutes actions operationnelles |
| Receptionne | 🟡 | Travaux termines, en attente cloture | SAV, levee reserves |
| Ferme | 🔴 | Chantier cloture definitivement | Consultation uniquement |

**Transitions autorisees** :
- Ouvert → En cours, Ferme
- En cours → Receptionne, Ferme
- Receptionne → En cours (reouverture exceptionnelle), Ferme
- Ferme → (aucune transition, etat terminal)

### 4.6 Note technique - Améliorations qualité (31/01/2026)

**Session d'amélioration** : Type coverage, Test coverage, Architecture

**Résultats** :
- **Type coverage** : 85% → 95% (+10%) - 41 type hints ajoutés
- **Test coverage use cases + controller** : 88% → 99% (+11%) - 28 tests générés
- **Clean Architecture** : 6/10 → 10/10 (+4) - 4 violations HIGH résolues
- **Tests** : 120 → 148 (+28 tests, 100% pass)

**Type hints ajoutés** (41 issues):
- Events (4) : ChantierCreatedEvent, ChantierDeletedEvent, ChantierStatutChangedEvent, ChantierUpdatedEvent
- Exceptions (8) : CodeChantierAlreadyExistsError, InvalidDatesError, TransitionNonAutoriseeError, etc.
- Routes FastAPI (24) : Return types pour documentation OpenAPI
- Controller + Repository : Types méthodes __init__ et privées

**Tests controller** (28 tests):
- CRUD operations : create, list, get_by_id, get_by_code, update, delete
- Status management : change_statut, demarrer, receptionner, fermer
- Responsable assignment : conducteur, chef_chantier
- Error handling : ChantierNotFoundError, validation errors
- Fichier : `backend/tests/unit/modules/chantiers/adapters/controllers/test_chantier_controller.py`

**Architecture** (Service Registry pattern):
- Fichier créé : `backend/shared/infrastructure/service_registry.py` (114 lignes)
- Violations corrigées : Suppression imports directs cross-module (auth, formulaires, signalements, pointages)
- Pattern : Service Locator pour isolation stricte des modules
- Impact : Code plus propre (-16 lignes), couplage réduit, réutilisable

**Validation agents** :
- architect-reviewer : PASS (10/10 Clean Architecture, 0 violation)
- code-reviewer : PASS (10/10 qualité)
- security-auditor : PASS (0 critical/high)
- test-automator : 148/148 tests passed in 0.30s

**Commits** :
- `f58aebb` - Type hints (95% coverage)
- `7677c36` - Controller tests (99% coverage)
- `c1865ae` - Architecture fixes (Service Registry)

**Coverage détaillée module chantiers** :
- Use cases : 100%
- Controller : 99%
- Domain services : 100%
- Infrastructure routes : 41% (non testé)
- Infrastructure repository : 28% (non testé)

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

**Note technique (31/01/2026)** : Phase 1 - Corrections critiques workflow validation feuilles d'heures :
- ✅ **GAP-FDH-001** : Workflow "corriger" implémenté (`CorrectPointageUseCase` + route POST `/{pointage_id}/correct`)
- ✅ **GAP-FDH-002** : Verrouillage mensuel période de paie (`PeriodePaie` value object, clôture vendredi avant dernière semaine)
- ✅ **GAP-FDH-003** : Service de permissions domaine (`PointagePermissionService`, contrôles rôles compagnon/chef/conducteur/admin)
- ✅ **GAP-FDH-005** : Validation 24h par jour (méthode `Pointage.set_heures()` avec vérification total <= 24h)
- ✅ Tous les use cases intègrent la vérification `PeriodePaie.is_locked()` avant modification
- ✅ Tests : +74 tests générés (PeriodePaie, PermissionService, CorrectPointage, validation 24h), 214 tests total (100% pass)
- ✅ Validation agents : architect-reviewer (10/10), test-automator (90%+), code-reviewer (9.5/10), security-auditor (PASS, 0 CRITICAL/HIGH)
- ⏳ **SEC-PTG-001** (MEDIUM) : Regex validation heures à renforcer (accepte formats invalides 99:99)
- ⏳ **SEC-PTG-002** (MEDIUM) : Intégration `PointagePermissionService` dans routes POST/PUT (service créé mais pas encore utilisé)

**Note technique (31/01/2026)** : Phase 2 - Corrections critiques transmission heures_prevues (FDH-10) :
- ✅ **GAP-T5** : Transmission heures_prevues dans événements Planning → Pointages (ajout paramètre `heures_prevues: Optional[float]` dans `AffectationCreatedEvent`)
- ✅ **Type conversion** : Ajout `_convert_heures_to_string()` dans `event_handlers.py` pour convertir float (8.0) → string ("08:00")
- ✅ **Validation NaN/Infinity** : Ajout `field_validator` dans `planning_schemas.py` pour rejeter valeurs invalides (sécurité HIGH)
- ✅ **RGPD logs** : Passage logs sensibles (user_id, chantier_id, heures) de INFO → DEBUG dans `planning_controller.py`
- ✅ **Clean Architecture** : Correction ligne 99 `event_handlers.py` - injection dépendance `chantier_repo` au lieu import direct inter-modules
- ✅ **Security** : Remplacement `print()` par `logger.exception()` dans `planning_routes.py` (finding HIGH résolu)
- ✅ Tests : +43 tests générés (conversion heures, validators Pydantic), 92% couverture (objectif 90% dépassé)
- ✅ Validation agents finale : architect-reviewer (WARN, 0 CRITICAL), test-automator (92%), code-reviewer (APPROVED), security-auditor (PASS, 0 HIGH/CRITICAL)

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

**Note technique (29/01/2026)** : Refactorisation et corrections du téléchargement de documents :
- ✅ Clean Architecture respectée : use case retourne BinaryIO, routes utilisent le contrôleur
- ✅ Frontend : Token CSRF lu depuis le cookie, gestion blob response avec `responseType: 'blob'`
- ✅ Backend : Route `/download-zip` corrigée, téléchargements individuels et ZIP fonctionnels
- Tests manuels validés : 120KB PDF téléchargé, 103KB ZIP avec 2 documents

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
| LOG-06 | Blocs reservation colores | Par demandeur avec nom complet (ex: "Jean DUPONT") | ✅ Frontend + Backend |
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
| LOG-19 | Selecteur de ressource | Dropdown pour choisir quelle ressource afficher | ✅ Frontend |
| LOG-20 | Vue "Toutes les ressources" | Affichage empile de toutes les ressources avec leurs plannings | ✅ Frontend |
| LOG-21 | Basculement vue globale/detaillee | Bouton "Voir en detail →" pour passer d'une ressource a sa vue detaillee | ✅ Frontend |
| LOG-22 | Enrichissement noms utilisateurs | Affichage "Prenom NOM" au lieu de "User #X" dans les reservations | ✅ Backend |
| LOG-23 | Persistence selection ressource | Conservation de la ressource selectionnee lors de navigation entre onglets | ✅ Frontend |

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

### 14.4 API Publique v1 ✅

**Status**: Implémenté (2026-01-28)

#### API-01: Authentification par clés API ✅

**Description**: Système d'authentification par clés API (hbc_xxx) pour permettre aux systèmes externes d'accéder à l'API Hub Chantier de manière sécurisée et programmatique.

**Fonctionnalités**:
- Génération de clés API cryptographiquement sécurisées (256 bits)
- Authentification via header `Authorization: Bearer hbc_xxx...`
- Gestion de permissions granulaires (scopes: read, write, chantiers:*, planning:*, etc.)
- Expiration configurable (défaut: 90 jours)
- Révocation instantanée
- Audit trail complet (création, dernière utilisation, révocation)
- Rate limiting par clé (1000 req/heure configurables)

**Sécurité**:
- Secrets JAMAIS stockés en clair (hash SHA256)
- Génération via `secrets.token_urlsafe()` (CSPRNG)
- Clés révoquées immédiatement rejetées
- Isolation stricte par utilisateur (un utilisateur ne peut révoquer que ses clés)
- Conformité RGPD (CASCADE DELETE, traçabilité, minimisation données)

**UI de gestion**:
- Page `/api-keys` dans l'application
- Liste des clés actives avec statuts (active, révoquée, expirée, expire bientôt)
- Création de clé avec formulaire (nom, description, scopes, expiration)
- Affichage du secret UNE SEULE FOIS avec copie presse-papier
- Révocation avec confirmation

**Exemple d'utilisation**:
```bash
# Créer une clé via UI → copier le secret

# Utiliser la clé pour accéder à l'API
curl -H "Authorization: Bearer hbc_xxxxxxxxxxxxx" \
     https://api.hub-chantier.fr/api/v1/chantiers
```

**Endpoints**:
- `POST /api/auth/api-keys` - Créer une clé (JWT auth requis)
- `GET /api/auth/api-keys` - Lister mes clés
- `DELETE /api/auth/api-keys/{id}` - Révoquer une clé

**Authentification acceptée**:
- JWT Token (eyJ...) - Utilisateurs de l'application web/mobile
- API Key (hbc_...) - Systèmes externes, scripts, intégrations

**Phase 2 prévue**:
- Rate limiting Redis (protection DoS)
- Limite clés par utilisateur (10 max)
- Logs structurés JSON pour SOC
- Webhooks pour événements

**Tests**: 92 tests unitaires, 97% couverture
**Architecture**: Clean Architecture, séparation Domain/Application/Infrastructure
**Audits**: Security audit PASS (88/100, 0 finding critique), Code review APPROVED (100/100)

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
| Consentement RGPD | Banniere de consentement pour geolocalisation, notifications, analytics | ✅ |
| API Consentements | Endpoints GET/POST /api/auth/consents pour gestion consentements | ✅ |
| Consentement avant login | Possibilite de donner/retirer consentement meme sans authentification | ✅ |

### 15.3 Mode Offline

L'application mobile permet de consulter le planning, saisir les heures, remplir les formulaires et consulter les plans meme sans connexion internet. La synchronisation s'effectue automatiquement au retour de la connectivite, avec gestion des conflits.

### 15.4 Niveaux de confidentialite

| Niveau | Acces | Exemples de donnees |
|--------|-------|---------------------|
| Public chantier | Tous les affectes au chantier | Plans, consignes, planning |
| Restreint chef | Chefs + Conducteurs + Admin | Documents techniques |
| Confidentiel | Conducteurs + Admin | Budgets, contrats, situations |
| Secret | Admin uniquement | Documents RH, donnees sensibles |

### 15.5 Validation qualite (29 janvier 2026)

Audit complet du backend realise avec 7 agents de validation (4 rounds iteratifs).

| Metrique | Resultat |
|----------|----------|
| Tests unitaires backend | 2932 pass, 0 fail, 0 xfail |
| Couverture backend | 85% |
| Findings CRITICAL | 0 |
| Findings HIGH | 0 |
| architect-reviewer | 8/10 PASS |
| code-reviewer | 8/10 APPROVED |
| security-auditor | 8/10 PASS (RGPD PASS, OWASP PASS) |

Corrections appliquees :
- Escalade de privileges via register endpoint (champ role supprime)
- Path traversal incomplet (exists/move/copy proteges)
- IDOR sur GET /users/{id} (controle d'acces ajoute)
- Rate limiting bypassable via X-Forwarded-For (TRUSTED_PROXIES externalise)
- SessionLocal() dans routes (toutes migrees vers Depends(get_db))
- EventBus reecrit en API statique class-level
- N+1 query elimine dans chantier_provider
- 12 fichiers de tests ajoutes pour atteindre 85% couverture

---

## 17. GESTION FINANCIERE ET BUDGETAIRE

### 17.1 Vue d'ensemble

Le module Financier centralise le suivi economique des chantiers : budgets previsionnels par lots, achats fournisseurs, situations de travaux et analyse de rentabilite. Il s'integre aux modules Chantiers, Taches, Feuilles d'Heures et Logistique pour offrir une vision consolidee couts/avancement. Accessible depuis un onglet dedie sur chaque fiche chantier, il permet a la direction et aux conducteurs de piloter la marge en temps reel.

### 17.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| FIN-01 | Onglet Budget par chantier | Accessible depuis la fiche chantier, affiche budget + KPI + dernieres operations | ✅ Backend + Frontend |
| FIN-02 | Budget previsionnel par lots | Decomposition arborescente par lots et postes (code lot, libelle, unite, quantite, PU HT) | ✅ Backend + Frontend |
| FIN-03 | Affectation budgets aux taches | Liaison optionnelle taches <-> lignes budgetaires pour suivi avancement financier | 🔮 Phase 3 |
| FIN-04 | Avenants budgetaires | Creation d'avenants avec motif, montant et impact automatique sur budget revise | 🔮 Phase 2 |
| FIN-05 | Saisie achats / bons de commande | Creation achats avec fournisseur, lot, montant HT, TVA, statut et workflow validation | ✅ Backend + Frontend |
| FIN-06 | Validation hierarchique achats | Approbation requise par Conducteur/Admin si montant > seuil configurable (defaut 5 000 EUR HT) | ✅ Backend + Frontend |
| FIN-07 | Situations de travaux | Creation situations mensuelles basees sur avancement reel, workflow 5 etapes, generation PDF | 🔮 Phase 2 |
| FIN-08 | Facturation client | Generation factures/acomptes depuis situations validees avec retenue de garantie | 🔮 Phase 2 |
| FIN-09 | Suivi couts main-d'oeuvre | Integration automatique heures validees (module Pointages) x taux horaire par metier | 🔮 Phase 2 (champ taux_horaire ajouté sur users) |
| FIN-10 | Suivi couts materiel | Integration automatique reservations (module Logistique) x tarif journalier | 🔮 Phase 2 (champ tarif_journalier ajouté sur ressources) |
| FIN-11 | Tableau de bord financier | Cartes KPI + graphiques comparatifs Budget/Engage/Realise + dernieres operations | ✅ Backend + Frontend |
| FIN-12 | Alertes depassements | Notifications push si (Engage + Reste a faire) > Budget x seuil (defaut 110%) | ✅ Backend (DepassementBudgetEvent) |
| FIN-13 | Export comptable | Generation CSV/Excel avec codes analytiques chantier, compatible logiciels comptables | 🔮 Phase 3 |
| FIN-14 | Referentiel fournisseurs | Gestion fournisseurs (raison sociale, type, SIRET, contact, conditions paiement) | ✅ Backend + Frontend |
| FIN-15 | Historique et tracabilite | Journal complet des modifications budgetaires avec auteur, date et motif | ✅ Backend + Frontend |

### 17.3 Structure d'un budget

| Champ | Type | Description |
|-------|------|-------------|
| Code lot | Texte | Ex: LOT-01, LOT-02-MACON |
| Libelle | Texte | Description du poste |
| Unite | Liste | m2, m3, forfait, kg, heure, ml, u |
| Quantite prevue | Nombre | Volume budgete |
| Prix unitaire HT | Montant | Cout unitaire hors taxe |
| Total prevu HT | Calcule | Quantite x Prix unitaire |
| Engage | Montant | Somme bons de commande valides sur ce lot |
| Realise | Montant | Somme factures recues sur ce lot |
| Reste a faire | Calcule | Total prevu - Realise |
| Ecart | Calcule | Realise - Total prevu (positif = depassement) |

### 17.4 Tableau de bord financier

Le tableau de bord s'affiche dans l'onglet Budget de chaque chantier. Mobile-first, optimise pour consultation rapide sur le terrain.

#### 17.4.1 Zone superieure - Cartes KPI

| Indicateur | Formule | Couleur seuil |
|------------|---------|---------------|
| Budget revise HT | Budget initial + Avenants | — |
| Engage | Somme bons de commande valides | Orange > 90% budget |
| Realise | Somme factures + couts MO + couts materiel | Rouge > 100% budget |
| Marge estimee | Budget revise - (Realise + Reste a faire estime) | Rouge < 5% |

Chaque carte affiche le montant principal, le delta vs budget et une icone couleur (vert/orange/rouge).

#### 17.4.2 Zone centrale - Graphiques

- **Barres groupees par lot** : Budget / Engage / Realise avec surlignage rouge sur depassements
- **Donut repartition** : Couts par categorie (Main-d'oeuvre, Materiaux, Sous-traitance, Materiel)
- **Courbe en S** : Avancement physique (% taches) vs avancement financier (% realise/budget)

#### 17.4.3 Zone inferieure - Dernieres operations

- 5 derniers achats avec montant, fournisseur, statut
- 3 dernieres situations emises avec montant, date, statut paiement

### 17.5 Workflow situation de travaux

Une situation de travaux est un document contractuel recapitulant l'avancement des travaux sur une periode donnee (generalement mensuelle) et servant de base a la facturation.

#### 17.5.1 Etapes du workflow

| Etape | Responsable | Actions | Statut |
|-------|-------------|---------|--------|
| 1. Preparation | Conducteur | Saisie avancement par lot, calcul montant periode | Brouillon |
| 2. Validation interne | Admin/Direction | Verification coherence, correction si besoin | En validation |
| 3. Emission client | Conducteur | Generation PDF, envoi email client | Emise |
| 4. Validation client | — | Signature/validation du montant par le client | Validee |
| 5. Facturation | Admin | Creation facture, marquage "Facturee" | Facturee |

#### 17.5.2 Contenu du document PDF

- En-tete : Logo Greg Construction, coordonnees, numero situation (SIT-AAAA-NN)
- Client : Nom maitre d'ouvrage, projet, adresse chantier
- Tableau recapitulatif : Lot | Montant marche | % avancement | Montant periode | Montant cumule
- Totaux : Cumul precedent + Periode = Cumul total
- Retenue de garantie (parametrable : 0%, 5% ou 10%)
- Montant a facturer HT / TVA / TTC
- Signatures : Conducteur + Client

### 17.6 Gestion des achats

#### 17.6.1 Structure d'un achat

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| Type | Liste | Oui | Materiau / Materiel / Sous-traitance / Service |
| Fournisseur | Reference | Oui | Choix dans le referentiel fournisseurs |
| Chantier | Reference | Oui | Affectation au projet |
| Lot budgetaire | Reference | Non | Liaison avec la ligne de budget |
| Libelle | Texte | Oui | Description de l'achat |
| Quantite | Nombre | Oui | Quantite commandee |
| Unite | Liste | Oui | m2, kg, unite, forfait, ml, m3 |
| Prix unitaire HT | Montant | Oui | Cout unitaire hors taxe |
| Total HT | Calcule | — | Quantite x Prix unitaire |
| TVA | Taux | Oui | 20%, 10%, 5.5%, 0% |
| Total TTC | Calcule | — | Total HT x (1 + TVA) |
| Date commande | Date | Oui | Date du bon de commande |
| Date livraison prevue | Date | Non | Echeance de livraison |
| Statut | Liste | Oui | Demande / Valide / Commande / Livre / Facture |
| N facture fournisseur | Texte | Non | Reference facture fournisseur |
| Commentaire | Texte | Non | Notes complementaires |

#### 17.6.2 Workflow validation achats

- Montant >= seuil configurable (defaut 5 000 EUR HT) : approbation Conducteur/Admin requise
- Montant < seuil : passage direct au statut "Valide"
- Statut "Facture" est definitif (aucune modification autorisee ensuite)

Etapes si validation requise :

1. Chef de chantier cree la demande d'achat → Statut "Demande"
2. Conducteur recoit notification push pour validation
3. Conducteur approuve → Statut "Valide" → Chef peut passer commande
4. Conducteur refuse → Statut "Refuse" + motif → Chef doit modifier

### 17.7 Referentiel fournisseurs

| Champ | Type | Description |
|-------|------|-------------|
| Raison sociale | Texte | Nom officiel de l'entreprise |
| Type | Liste | Negoce materiaux / Loueur / Sous-traitant / Service |
| SIRET | Texte | Numero identification (14 chiffres) |
| Adresse | Texte | Adresse complete |
| Contact principal | Texte | Nom du commercial/responsable |
| Telephone | Texte | Numero direct |
| Email | Email | Adresse de contact |
| Conditions paiement | Texte | Ex: 30 jours fin de mois |
| Notes | Texte | Informations complementaires |
| Actif | Booleen | Fournisseur actif ou archive |

### 17.8 Matrice des droits - Financier

| Action | Admin | Conducteur | Chef chantier | Compagnon |
|--------|-------|------------|---------------|-----------|
| Voir budget chantier | ✅ | ✅ (ses chantiers) | ✅ (ses chantiers) | ❌ |
| Modifier budget | ✅ | ✅ (ses chantiers) | ❌ | ❌ |
| Creer avenant | ✅ | ✅ (ses chantiers) | ❌ | ❌ |
| Creer demande achat | ✅ | ✅ | ✅ | ❌ |
| Valider achat > seuil | ✅ | ✅ | ❌ | ❌ |
| Voir tous les achats | ✅ | ✅ (ses chantiers) | ✅ (ses achats) | ❌ |
| Creer situation travaux | ✅ | ✅ | ❌ | ❌ |
| Valider situation | ✅ | ❌ | ❌ | ❌ |
| Exporter comptabilite | ✅ | ❌ | ❌ | ❌ |
| Gerer fournisseurs | ✅ | ✅ (lecture) | ❌ | ❌ |

### 17.9 Regles metier

- Tous les montants sont saisis en HT ; TVA calculee automatiquement selon taux configurable par categorie
- Un achat est lie a un seul chantier
- Les situations de travaux sont numerotees automatiquement par chantier (SIT-2026-01, SIT-2026-02...)
- Les situations ne peuvent etre generees qu'apres validation des avancements (lien module Taches)
- L'alerte depassement se declenche si : (Engage + Reste a faire estime) > (Budget revise x seuil configurable)
- La retenue de garantie est parametrable par chantier (0%, 5% ou 10%)
- Les couts main-d'oeuvre sont calcules automatiquement depuis le module Feuilles d'Heures (heures validees x taux horaire metier)
- Les couts materiel sont calcules depuis le module Logistique (reservations x tarif journalier)
- L'export comptable genere un fichier CSV avec codes analytiques chantier pour lettrage comptable
- Tout document financier (situation, facture) est automatiquement reference dans la GED du chantier
- Journal d'audit : chaque modification budgetaire enregistre auteur + timestamp + motif
- Notifications push aux responsables lors de depassement ou validation requise

### 17.10 Integrations avec modules existants

| Module source | Donnees exploitees | Usage financier |
|---------------|-------------------|-----------------|
| Chantiers | ID chantier, nom, maitre d'ouvrage, dates | Rattachement budget, en-tete situations |
| Taches | Avancement %, heures realisees | Calcul avancement situations, courbe en S |
| Feuilles d'Heures (Pointages) | Heures validees par employe/chantier | Cout main-d'oeuvre = heures x taux horaire metier |
| Logistique | Reservations materiel par chantier | Cout materiel = jours reservation x tarif journalier |
| Documents (GED) | Stockage fichiers | Archivage automatique situations PDF et factures |
| Notifications | Push Firebase | Alertes depassement, validation requise |

---

## 18. GESTION DES DEVIS

### 18.1 Vue d'ensemble

Le module Gestion des Devis permet de créer, chiffrer, versionner et suivre les devis clients depuis la phase commerciale jusqu'à l'acceptation. Une fois accepté et signé, le devis peut être converti automatiquement en chantier avec transfert du budget détaillé, des lots et des sous-détails vers les modules Financier (§17) et Planning (§5).

Le module intègre des outils avancés de métrés numériques sur plans PDF, un système complet de consultations sous-traitants, et la gestion de bibliothèques de prix personnalisables avec import de bases externes (Batiprix, etc.). Il supporte un usage hors-ligne pour la consultation et la saisie partielle, avec synchronisation automatique des modifications.

Ce module se positionne **en amont** du cycle de vie actuel de Hub Chantier, couvrant la phase commerciale avant la création du chantier.

### 18.2 Fonctionnalités

| ID   | Fonctionnalité                              | Description                                                                 | Status |
|------|---------------------------------------------|-----------------------------------------------------------------------------|--------|
| DEV-01  | Bibliothèque d'articles et bordereaux       | Base de données d'articles (matériaux, main-d'œuvre, sous-traitance) avec prix unitaires, unités, codes et composants détaillés | 🔮     |
| DEV-02  | Import bibliothèques externes                | Import CSV/Excel ou connexion API vers bases standards (Batiprix 80 000+ ouvrages, etc.) pour prix marché actualisés mensuellement | 🔮     |
| DEV-03  | Création devis structuré                    | Arborescence par lots/chapitres/lignes avec quantités, prix unitaires et totaux automatiques | 🔮     |
| DEV-04  | Métrés numériques 2D intégrés               | Outils de mesure directe (longueur, surface, comptage) sur plans PDF du module Plans (§9), avec transfert automatique quantités et verrouillage | 🔮     |
| DEV-05  | Détail déboursés avancés                    | Breakdown par ligne : main-d'œuvre (heures × taux), matériaux, sous-traitance, matériel, frais avec calcul automatique prix de revient | 🔮     |
| DEV-06  | Gestion marges et coefficients              | Application de marges globales/par lot/par ligne, coefficients déboursés secs et prix de vente, avec règle de priorité (ligne > lot > global) | 🔮     |
| DEV-07  | Insertion multimédia                        | Ajout photos, fiches techniques ou documents par ligne/lot pour enrichissement visuel du devis client | 🔮     |
| DEV-08  | Variantes et révisions                      | Création de versions alternatives (économique/standard/premium) ou révisions avec comparatif détaillé automatique (écarts quantités/montants/marges) | 🔮     |
| DEV-09  | Gestion consultations sous-traitants        | Création packages par lot, envoi email automatisé avec plans/annexes, tracking réponses et dates limites | 🔮     |
| DEV-10  | Réception et comparaison offres             | Import offres reçues, tableau comparatif normalisé (prix, délais, conditions) avec sélection gagnante et mise à jour automatique déboursé lot | 🔮     |
| DEV-11  | Personnalisation présentation               | Modèles de mise en page configurables (avec/sans détail déboursés, avec/sans multimédia, avec/sans composants) | 🔮     |
| DEV-12  | Génération PDF devis                        | Export PDF professionnel avec entête personnalisé, conditions générales, annexes et multimédia intégré | 🔮     |
| DEV-13  | Envoi par email intégré                     | Envoi direct depuis l'app avec tracking ouverture/clics et lien signature sécurisé | 🔮     |
| DEV-14  | Signature électronique client               | Intégration signature simple (dessin tactile ou upload scan) avec validation légale horodatée et auditée | 🔮     |
| DEV-15  | Suivi statut devis                          | Workflow complet : Brouillon / En validation / Envoyé / Vu / En négociation / Accepté / Refusé / Perdu / Expiré | 🔮     |
| DEV-16  | Conversion en chantier                      | Transformation automatique devis accepté → création chantier avec budget, lots, déboursés et planning initial | 🔮     |
| DEV-17  | Tableau de bord devis                       | Vue liste/kanban des devis en cours par statut, client, montant, avec KPI pipeline commercial et alertes délais | 🔮     |
| DEV-18  | Historique modifications                    | Journal complet des changements avec auteur, timestamp, type modification et valeurs avant/après | 🔮     |
| DEV-19  | Recherche et filtres                        | Filtres avancés par client, date, montant, statut, commercial assigné, lot, marge | 🔮     |
| DEV-20  | Accès hors-ligne                            | Consultation/modification devis brouillons et métrés simples, synchronisation à la reconnexion avec gestion conflits | 🔮     |
| DEV-21  | Import DPGF automatique                     | Import fichier DPGF (Décomposition Prix Global Forfaitaire) Excel/CSV/PDF des appels d'offres avec mapping colonnes et pré-remplissage lots/lignes | 🔮     |
| DEV-22  | Retenue de garantie                         | Paramétrage retenue de garantie par devis (0%, 5%, 10%) avec affichage dans PDF client et report automatique lors conversion chantier | 🔮     |
| DEV-23  | Génération attestation TVA                  | Création automatique attestation TVA réglementaire selon taux appliqué (5.5% rénovation énergétique, 10% rénovation, 20% standard) | 🔮     |
| DEV-24  | Relances automatiques                       | Notifications push/email automatiques si délai de réponse dépassé (configurable : 7j, 15j, 30j) avec historique relances | 🔮     |
| DEV-25  | Frais de chantier                           | Ajout compte prorata, frais généraux, installations de chantier avec répartition globale ou par lot | 🔮     |

### 18.3 Déboursé sec et pilotage des marges

Le **déboursé sec** est l'indicateur central du chiffrage BTP. Il représente l'ensemble des coûts directs nécessaires à l'exécution des travaux, sans intégrer les frais de structure ni la marge bénéficiaire.

#### 18.3.1 Composantes du déboursé sec

| Composante | Description | Exemple |
|------------|-------------|---------|
| Main-d'œuvre | Heures × taux horaire par métier | 40h × 45€/h = 1 800€ |
| Matériaux | Quantité × prix unitaire achat | 50m² × 35€/m² = 1 750€ |
| Matériel | Location ou amortissement équipements | Bétonnière : 120€ |
| Sous-traitance | Montant forfaitaire ou métré sous-traitant | Électricité : 8 500€ |
| Déplacements | Frais de déplacement ressources | 3 jours × 65€ = 195€ |

#### 18.3.2 Formules de calcul

```
Déboursé sec = Σ (quantité composant × prix unitaire composant)
Prix de revient = Déboursé sec × (1 + coefficient frais généraux)
Prix de vente HT = Prix de revient × (1 + taux de marge)
Prix de vente TTC = Prix de vente HT × (1 + taux TVA applicable)
```

**Exemple concret - Lot maçonnerie** :

| Composant | Quantité | Prix unitaire | Montant |
|-----------|----------|---------------|---------|
| Maçon (MOE) | 120 h | 42€/h | 5 040€ |
| Parpaings | 800 u | 3,50€/u | 2 800€ |
| Mortier | 2 m³ | 85€/m³ | 170€ |
| **Déboursé sec lot** | | | **8 010€** |
| Frais généraux (12%) | | | 961€ |
| **Prix de revient** | | | **8 971€** |
| Marge (18%) | | | 1 615€ |
| **Prix de vente HT** | | | **10 586€** |
| TVA (20%) | | | 2 117€ |
| **Prix de vente TTC** | | | **12 703€** |

#### 18.3.3 Pilotage des marges multi-niveaux

Les marges sont pilotables à chaque niveau de la hiérarchie du devis avec règle de priorité :

| Niveau | Scope | Exemple | Priorité |
|--------|-------|---------|----------|
| Par ligne | Marge sur une ligne individuelle | Câble 3G2.5 : 10% | 1 (max) |
| Par lot | Marge spécifique à un lot | Lot électricité : 22% | 2 |
| Par type de débours | Marge différenciée selon nature | MOE : 20%, Matériaux : 12%, ST : 8% | 3 |
| Global | Marge par défaut sur tout le devis | 15% sur l'ensemble | 4 (min) |

**Règle de priorité** : Ligne > Lot > Type de débours > Global.

**Vues** :
- **Vue Débours** (interne uniquement) : Affiche coûts bruts (déboursé sec, prix de revient, marges détaillées)
- **Vue Vente** (PDF client) : Affiche uniquement prix commerciaux (prix de vente HT, TVA, TTC) sans révéler marges ni déboursés

### 18.4 Workflow du devis

| Étape | Responsable | Actions | Statut | Transitions |
|-------|-------------|---------|--------|-------------|
| 1. Création | Conducteur / Commercial | Création depuis template ou vierge, ajout lots/lignes | 🔵 Brouillon | → En validation |
| 2. Chiffrage | Conducteur | Saisie déboursés, métrés, ajustement marges | 🔵 Brouillon | → En validation |
| 3. Validation interne | Admin / Direction | Vérification marges minimales, cohérence prix | 🟡 En validation | → Approuvé / → Brouillon |
| 4. Génération PDF | Conducteur | PDF professionnel vue Vente uniquement | 🟢 Approuvé | → Envoyé |
| 5. Envoi client | Conducteur / Commercial | Email avec lien visibilité + signature | 🔵 Envoyé | → Vu |
| 6. Consultation | Client | Ouverture email/PDF (tracking) | 🟣 Vu | → En négociation / Accepté / Refusé |
| 7. Négociation | Conducteur + Client | Échanges, modifications, variantes | 🟠 En négociation | → Envoyé (nouvelle version) |
| 8. Acceptation | Client | Signature électronique | ✅ Accepté | → Conversion chantier |
| 9. Refus/Perte | Client / Interne | Motif obligatoire pour reporting | ❌ Refusé / Perdu | Final |
| 10. Expiration | Automatique | Si date validité dépassée sans réponse | ⏰ Expiré | → En négociation |

### 18.5 Matrice des droits - Devis

| Action | Admin | Conducteur | Commercial | Chef chantier | Compagnon |
|--------|-------|------------|------------|---------------|-----------|
| Créer devis | ✅ | ✅ | ✅ | ❌ | ❌ |
| Modifier devis (Brouillon) | ✅ | ✅ | ✅ | ❌ | ❌ |
| Valider devis (< 50k€) | ✅ | ✅ | ✅ | ❌ | ❌ |
| Valider devis (≥ 50k€) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Envoyer devis au client | ✅ | ✅ | ✅ | ❌ | ❌ |
| Voir tous les devis | ✅ | ✅ (ses chantiers) | ✅ (tous) | ❌ | ❌ |
| Gérer bibliothèque de prix | ✅ | ❌ | ❌ | ❌ | ❌ |
| Import bibliothèques externes | ✅ | ❌ | ❌ | ❌ | ❌ |
| Réaliser métrés numériques | ✅ | ✅ | ✅ | ✅ | ❌ |
| Gérer consultations ST | ✅ | ✅ | ❌ | ❌ | ❌ |
| Import DPGF | ✅ | ✅ | ✅ | ❌ | ❌ |
| Convertir en chantier | ✅ | ✅ | ❌ | ❌ | ❌ |
| Voir déboursés et marges | ✅ | ✅ | ✅ | ❌ | ❌ |

**Note** : Le rôle **Commercial** doit être ajouté au module Utilisateurs (§3).

### 18.6 Règles métier

- Accès complet réservé aux rôles Commercial/Conducteur/Administrateur
- Un devis ne peut être envoyé que s'il a été validé en validation interne (marge minimale vérifiée)
- La marge minimale par défaut est configurable au niveau entreprise (défaut 12%)
- La validation Direction est requise si montant total HT ≥ seuil configurable (défaut 50 000€)
- Le statut "Expiré" est déclenché automatiquement à la date de validité
- Les montants sont toujours saisis en HT ; TVA calculée automatiquement
- Le versioning conserve chaque état du devis (impossible de supprimer une version)
- Le PDF client ne contient jamais les déboursés secs ni les marges détaillées
- Les quantités issues de métrés numériques sont verrouillables pour éviter modifications accidentelles
- La conversion en chantier nécessite un devis en statut "Accepté" et signé
- La conversion transfère automatiquement lots/budget/déboursés vers module Financier (§17)
- Notification push/email aux commerciaux sur changement statut, signature, réception offre
- Relances automatiques configurables si délai de réponse dépassé (défaut : J+7, J+15, J+30)
- La signature électronique est horodatée, auditée et conservée pour valeur probante (conforme eIDAS)

### 18.7 Intégrations avec modules existants

| Module | Données exploitées | Usage dans Devis | Type intégration |
|--------|-------------------|------------------|------------------|
| §4 Chantiers | ID chantier, nom, dates | Association devis → chantier | EntityInfoService |
| §5 Planning | — | Création tâches lors conversion | Domain Event `DevisAccepteEvent` |
| §9 GED (Plans) | Plans PDF, échelle | Métrés numériques 2D | Domain Event `MetrageExtractedEvent` |
| §9 GED (Documents) | Stockage fichiers | Photos/fiches techniques, archivage PDF signés | EntityInfoService |
| §17 Financier | — | Génération budget chantier lors conversion | Domain Event `DevisAccepteEvent` |
| §20 Sous-Traitants | Référentiel ST, spécialités | Consultations ST, sélection offres | EntityInfoService |

### 18.8 Roadmap d'implémentation

Le module Devis est découpé en 4 phases successives (total 188 jours ≈ 9 mois).

#### Phase 1 : MVP Commercial (40 jours ~ 2 mois)

Bibliothèque interne, création structurée, déboursés avancés, marges, génération PDF, envoi email, suivi statuts, dashboard basique.

**Livrable** : Devis PDF professionnel avec déboursés, marges, envoi email et suivi.

#### Phase 2 : Automatisation (50 jours ~ 2.5 mois)

Variantes, personnalisation PDF, signature électronique, conversion chantier, historique, recherche, retenue garantie, attestation TVA, relances auto, frais chantier.

**Livrable** : Workflow complet Devis → Signature → Chantier avec budget.

#### Phase 3 : Productivité++ (45 jours ~ 2 mois)

Import bibliothèques externes (Batiprix), multimédia, consultations ST, comparaison offres, import DPGF, dashboard avancé.

**Livrable** : Réponse rapide aux marchés publics + consultations ST optimisées.

#### Phase 4 : Premium (53 jours ~ 2.5 mois)

Métrés numériques 2D intégrés, mode hors-ligne, optimisations performances.

**Livrable** : Fonctionnalités premium différenciantes (Autodesk Takeoff, Procore).

**Calendrier recommandé** :
```
FÉV - MARS 2026 : Module 17 (Financier)
AVRIL - MAI 2026 : Module 18 Phase 1 (MVP)
JUIN - JUIL 2026 : Module 18 Phase 2 (Automatisation)
SEPT - OCT 2026 : Module 18 Phase 3 (Productivité)
NOV - DÉC 2026 : Module 18 Phase 4 (Premium)
```

---

## 19. GLOSSAIRE

| Terme | Definition |
|-------|------------|
| Avenant | Modification contractuelle impactant le budget ou le perimetre du chantier |
| Banche | Coffrage metallique modulaire pour couler les murs en beton |
| Batiprix | Base de donnees de 80 000+ prix de reference BTP actualises mensuellement, integrable via API dans la bibliotheque de prix |
| Bon de commande | Document engageant l'entreprise aupres d'un fournisseur pour un achat |
| Chef de chantier | Responsable operationnel d'un chantier specifique |
| Compagnon | Ouvrier de chantier (macon, coffreur, ferrailleur, grutier...) |
| Conducteur de travaux | Responsable de plusieurs chantiers, gere planning et budgets |
| Debourse sec | Cout direct d'execution des travaux sans frais generaux ni marge (MO + materiaux + materiel + ST) |
| DPGF | Decomposition du Prix Global et Forfaitaire - document standard des appels d'offres publics detaillant les prestations |
| ERP | Enterprise Resource Planning - logiciel de gestion d'entreprise |
| FAB | Floating Action Button - bouton d'action flottant sur mobile |
| Ferraillage | Armatures metalliques noyees dans le beton arme |
| GED | Gestion Electronique des Documents |
| Gros oeuvre | Structure porteuse du batiment (fondations, murs, dalles, poteaux) |
| HT / TTC | Hors Taxe / Toutes Taxes Comprises |
| Lot | Subdivision budgetaire d'un chantier par corps de metier ou nature de travaux |
| Memo | Note d'urgence ou d'information importante a traiter |
| Metres numeriques | Extraction automatique de quantites depuis plans PDF via outils de mesure 2D (lineaire, surface, comptage) |
| N+1 | Superieur hierarchique direct (pour validation) |
| Offline | Mode deconnecte permettant de travailler sans internet |
| OS | Ordre de Service |
| PPSPS | Plan Particulier de Securite et de Protection de la Sante |
| Predalle | Dalle prefabriquee servant de coffrage perdu pour plancher |
| Prix de revient | Debourse sec + frais generaux (avant application de la marge beneficiaire) |
| Push | Notification instantanee envoyee sur le smartphone |
| PV de reception | Proces-verbal de fin de travaux signe par le client |
| Retenue de garantie | Pourcentage retenu sur chaque situation pour couvrir les reserves (0%, 5% ou 10%) |
| SAV | Service Apres-Vente |
| SIRET | Numero d'identification a 14 chiffres attribue aux entreprises francaises |
| Situation de travaux | Document contractuel recapitulant l'avancement et servant de base a la facturation |
| Sous-traitant | Prestataire externe intervenant ponctuellement sur chantier |
| TVA | Taxe sur la Valeur Ajoutee (taux BTP : 20%, 10%, 5.5%, 0%) |

---

*Greg Constructions - Cahier des Charges Fonctionnel v2.2 - Janvier 2026*
