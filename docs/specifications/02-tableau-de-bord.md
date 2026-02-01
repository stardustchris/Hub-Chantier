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