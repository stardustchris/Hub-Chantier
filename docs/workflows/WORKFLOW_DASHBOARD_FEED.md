# Workflow Dashboard & Feed - Hub Chantier

> Document cree le 30 janvier 2026
> Analyse complete du workflow du fil d'actualites et du dashboard

---

## TABLE DES MATIERES

1. [Vue d'ensemble](#1-vue-densemble)
2. [Entites et objets metier](#2-entites-et-objets-metier)
3. [Statuts et ciblage](#3-statuts-et-ciblage)
4. [Flux de publication](#4-flux-de-publication)
5. [Medias et photos](#5-medias-et-photos)
6. [Commentaires et mentions](#6-commentaires-et-mentions)
7. [Likes](#7-likes)
8. [Epinglage et urgence](#8-epinglage-et-urgence)
9. [Archivage automatique](#9-archivage-automatique)
10. [Moderation et suppression](#10-moderation-et-suppression)
11. [Fil d'actualites (Feed)](#11-fil-dactualites-feed)
12. [Evenements domaine](#12-evenements-domaine)
13. [API REST - Endpoints](#13-api-rest---endpoints)
14. [Architecture technique](#14-architecture-technique)
15. [Frontend - Composants](#15-frontend---composants)
16. [Scenarios de test](#16-scenarios-de-test)
17. [Evolutions futures](#17-evolutions-futures)
18. [References CDC](#18-references-cdc)

---

## 1. VUE D'ENSEMBLE

### Objectif du module

Le module Dashboard/Feed est le reseau social interne de l'entreprise. Il permet aux equipes de publier des messages, partager des photos de chantier, commenter, liker, et recevoir des informations ciblees. C'est le point d'entree principal de l'application.

### Flux global simplifie

```
Utilisateur ouvre le Dashboard
    |
    v
[FEED] Fil d'actualites personnalise
    |   - Posts epingles en premier
    |   - Puis posts par date DESC
    |   - Filtre par ciblage (chantiers/personnes)
    |   - Scroll infini (20 posts/page)
    |
    v
[COMPOSER] Creer un nouveau post
    |
    +---> Texte + photos (max 5, max 2MB chacune)
    +---> Ciblage : Tout le monde / Chantiers / Personnes
    +---> Urgent : auto-epingle 48h
    |
    v
[PUBLISHED] Post visible dans le feed
    |
    +---> Commentaires avec @mentions
    +---> Likes (1 par utilisateur par post)
    +---> Epinglage (max 48h)
    |
    +---> Apres 7 jours : archivage automatique
    +---> Moderation : suppression par admin/auteur
```

### Fonctionnalites couvertes (CDC Section Feed)

| ID | Fonctionnalite | Description |
|----|----------------|-------------|
| FEED-01 | Publication posts | Texte avec emojis |
| FEED-02 | Photos jointes | Max 5 photos, max 2MB |
| FEED-03 | Ciblage audience | Tout le monde / Chantiers / Personnes |
| FEED-04 | Likes | 1 like par utilisateur par post |
| FEED-05 | Commentaires | Fil de discussion sous chaque post |
| FEED-07 | Indicateur ciblage | Icone + texte cible |
| FEED-08 | Posts urgents | Auto-epinglage 48h |
| FEED-09 | Auto-filtrage | Feed filtre par chantiers de l'utilisateur |
| FEED-10 | Emojis | Support natif dans texte |
| FEED-13 | Chargement progressif | Thumbnails pour photos |
| FEED-14 | @mentions | Mentions dans commentaires |
| FEED-16 | Moderation | Suppression par admin/auteur |
| FEED-18 | Scroll infini | 20 posts par page |
| FEED-19 | Compression auto | Limite 2MB par photo |
| FEED-20 | Archivage auto | 7 jours apres publication |

---

## 2. ENTITES ET OBJETS METIER

### 2.1 Post (entite principale)

**Fichier** : `backend/modules/dashboard/domain/entities/post.py`

| Champ | Type | Defaut | Notes |
|-------|------|--------|-------|
| id | Optional[int] | None | Cle primaire |
| author_id | int | - | FK user (pas de CASCADE, decouplage module) |
| content | str | - | Texte du post (requis, trimme) |
| targeting | PostTargeting | everyone | Value object ciblage |
| status | PostStatus | PUBLISHED | PUBLISHED, PINNED, ARCHIVED, DELETED |
| is_urgent | bool | False | Flag urgence (FEED-08) |
| pinned_until | Optional[datetime] | None | Expiration epinglage |
| created_at | datetime | now() | Horodatage creation |
| updated_at | datetime | now() | Derniere modification |
| archived_at | Optional[datetime] | None | Horodatage archivage |

**Constantes metier** :
- `MAX_PHOTOS_PER_POST = 5` (FEED-02)
- `URGENT_PIN_DURATION_HOURS = 48` (FEED-08)
- `ARCHIVE_AFTER_DAYS = 7` (FEED-20)

**Methodes cles** :
- `pin(duration_hours=48)` - Epingler (max 48h)
- `unpin()` - Desepingler
- `archive()` - Archiver
- `delete()` - Suppression logique (status → DELETED)
- `update_content(new_content)` - Modifier texte
- `update_targeting(new_targeting)` - Modifier ciblage
- `is_visible_to_user(user_id, user_chantier_ids)` - Verification visibilite

**Proprietes** :
- `is_pinned` - True si status=PINNED et pinned_until > maintenant
- `is_archived` - True si status=ARCHIVED
- `is_visible` - True si PUBLISHED ou PINNED
- `should_archive` - True si created_at + 7 jours < maintenant

### 2.2 PostMedia (FEED-02, FEED-13, FEED-19)

**Fichier** : `backend/modules/dashboard/domain/entities/post_media.py`

| Champ | Type | Defaut | Notes |
|-------|------|--------|-------|
| id | Optional[int] | None | Cle primaire |
| post_id | int | - | FK post (CASCADE delete) |
| media_type | MediaType | IMAGE | Type media (actuellement : IMAGE uniquement) |
| file_url | str | - | URL fichier stocke (requis) |
| thumbnail_url | Optional[str] | None | URL thumbnail (FEED-13 chargement progressif) |
| original_filename | Optional[str] | None | Nom fichier original |
| file_size_bytes | Optional[int] | None | Taille en octets |
| mime_type | Optional[str] | None | Ex: "image/jpeg" |
| width | Optional[int] | None | Largeur pixels |
| height | Optional[int] | None | Hauteur pixels |
| position | int | 0 | Ordre dans la galerie |
| created_at | datetime | now() | Horodatage upload |

**Constante** : `MAX_FILE_SIZE_MB = 2` (FEED-19)

**Proprietes** : `file_size_mb`, `is_over_size_limit`, `aspect_ratio`

### 2.3 Comment (FEED-05)

**Fichier** : `backend/modules/dashboard/domain/entities/comment.py`

| Champ | Type | Defaut | Notes |
|-------|------|--------|-------|
| id | Optional[int] | None | Cle primaire |
| post_id | int | - | FK post (CASCADE delete) |
| author_id | int | - | FK user (decouplage module) |
| content | str | - | Texte commentaire (requis, trimme) |
| is_deleted | bool | False | Suppression logique |
| created_at / updated_at | datetime | now() | Horodatages |

**Methodes** : `update_content(new_content)`, `delete()` (soft delete)

### 2.4 Like (FEED-04)

**Fichier** : `backend/modules/dashboard/domain/entities/like.py`

| Champ | Type | Defaut | Notes |
|-------|------|--------|-------|
| id | Optional[int] | None | Cle primaire |
| post_id | int | - | FK post (CASCADE delete) |
| user_id | int | - | FK user (decouplage module) |
| created_at | datetime | now() | Horodatage |

**Contrainte** : UNIQUE (post_id, user_id) - un like par utilisateur par post.

---

## 3. STATUTS ET CIBLAGE

### PostStatus (enum)

| Valeur | Description | Visible dans feed |
|--------|-------------|-------------------|
| PUBLISHED | Publie (defaut) | Oui |
| PINNED | Epingle (max 48h) | Oui (en premier) |
| ARCHIVED | Archive (>7 jours) | Non (consultable) |
| DELETED | Supprime (moderation) | Non |

**Methodes** :
- `is_visible()` - True pour PUBLISHED et PINNED
- `is_consultable()` - True pour tout sauf DELETED

### PostTargeting (value object)

**Fichier** : `backend/modules/dashboard/domain/value_objects/post_targeting.py`

| TargetType | Description | Champs supplementaires |
|-----------|-------------|----------------------|
| EVERYONE | Tout le monde | Aucun |
| SPECIFIC_CHANTIERS | Chantiers specifiques | chantier_ids: tuple[int] |
| SPECIFIC_PEOPLE | Personnes specifiques | user_ids: tuple[int] |

**Factory methods** :
- `PostTargeting.everyone()` - Ciblage global
- `PostTargeting.for_chantiers([1, 2, 3])` - Chantiers specifiques
- `PostTargeting.for_users([10, 20])` - Personnes specifiques

**Affichage** :
- EVERYONE → "Tout le monde"
- SPECIFIC_CHANTIERS → "X chantier(s)"
- SPECIFIC_PEOPLE → "X personne(s)"

### Tables de ciblage (junction tables)

Le ciblage utilise des tables de junction (et non des colonnes CSV) pour des requetes indexees :

- `post_target_chantiers` : (post_id, chantier_id) UNIQUE
- `post_target_users` : (post_id, user_id) UNIQUE

---

## 4. FLUX DE PUBLICATION

### Creation d'un post (FEED-01, FEED-03, FEED-08)

**Endpoint** : `POST /api/dashboard/posts`

**Corps** :
```json
{
  "contenu": "Message du post",
  "target_type": "tous",
  "target_chantier_ids": [],
  "target_utilisateur_ids": [],
  "is_urgent": false
}
```

### Regles metier

- Contenu non vide (validation dans `__post_init__`)
- Maximum 5 photos par post (FEED-02)
- Ciblage valide (au moins 1 ID si specifique)
- Si `is_urgent=true` → auto-epinglage 48h (FEED-08)
- Evenement `PostPublishedEvent` emis

### Post urgent (FEED-08)

Un post urgent est automatiquement epingle pour 48 heures. L'epinglage est plafonne a 48h maximum. Les posts urgents apparaissent en premier dans le feed.

---

## 5. MEDIAS ET PHOTOS

### Limites (FEED-02, FEED-19)

| Contrainte | Valeur | Constante |
|------------|--------|-----------|
| Nombre max photos | 5 par post | MAX_PHOTOS_PER_POST |
| Taille max par photo | 2 MB | MAX_FILE_SIZE_MB |

Ces valeurs sont des **constantes actuelles** definies dans l'entite Post et PostMedia.

### Chargement progressif (FEED-13)

Chaque media a un champ `thumbnail_url` optionnel. Le frontend peut afficher le thumbnail pendant le chargement de l'image pleine resolution.

### Metadata

Chaque photo stocke : `original_filename`, `file_size_bytes`, `mime_type`, `width`, `height`, `position` (ordre dans la galerie).

---

## 6. COMMENTAIRES ET MENTIONS

### Commentaires (FEED-05)

**Endpoint** : `POST /api/dashboard/posts/{post_id}/comments`

```json
{ "contenu": "Super photo @jean.dupont !" }
```

- Post doit exister
- Contenu non vide
- Support emojis natifs (FEED-10)
- Evenement `CommentAddedEvent` emis (declenche notification)

### @mentions (FEED-14)

Les mentions sont supportees dans les commentaires via le composant `MentionInput`.

**Frontend** : Composant `MentionInput` avec auto-completion des noms d'utilisateurs.

**Backend** : Parsing regex `@([a-zA-Z0-9_-]+)` pour extraire les mentions. Chaque mention genere une notification MENTION via le handler d'evenements.

**Rendu** : Fonction `renderContentWithMentions` pour afficher les mentions en surbrillance.

---

## 7. LIKES

### Mecanisme (FEED-04)

**Un seul like par utilisateur par post** (contrainte UNIQUE en base).

| Action | Endpoint | Evenement |
|--------|----------|-----------|
| Liker | `POST /posts/{post_id}/like` | LikeAddedEvent |
| Unliker | `DELETE /posts/{post_id}/like` | LikeRemovedEvent |

**Exceptions** :
- `PostNotFoundError` - Post inexistant
- `AlreadyLikedError` - Deja like

---

## 8. EPINGLAGE ET URGENCE

### Epinglage (FEED-08)

**Duree maximale** : 48 heures (constante URGENT_PIN_DURATION_HOURS).

| Action | Endpoint |
|--------|----------|
| Epingler | `POST /posts/{post_id}/pin?duration_hours=48` |
| Desepingler | `DELETE /posts/{post_id}/pin` |

- Seul l'auteur ou un moderateur (Admin/Conducteur) peut epingler
- Le champ `pinned_until` determine l'expiration
- `is_pinned` = True si status=PINNED ET pinned_until > maintenant

### Posts urgents

Un post marque `is_urgent=true` est automatiquement epingle pour 48h a la publication. L'evenement `PostPinnedEvent` est emis.

---

## 9. ARCHIVAGE AUTOMATIQUE

### Regle (FEED-20)

**Apres 7 jours** (constante ARCHIVE_AFTER_DAYS), un post PUBLISHED est automatiquement archive.

- `should_archive` : propriete calculee (created_at + 7 jours < now)
- `find_posts_to_archive()` : methode repository pour trouver les posts a archiver
- Statut : PUBLISHED → ARCHIVED
- `archived_at` renseigne

Les posts archives restent **consultables** mais ne sont plus visibles dans le feed par defaut (sauf `include_archived=True`).

---

## 10. MODERATION ET SUPPRESSION

### Suppression (FEED-16)

**Endpoint** : `DELETE /api/dashboard/posts/{post_id}`

**Regles** :
- **Auteur** : Peut supprimer ses propres posts
- **Moderateur** (Admin, Conducteur) : Peut supprimer tout post
- Suppression logique : status → DELETED
- Evenement `PostDeletedEvent` emis

**Exceptions** : `NotAuthorizedError` si ni auteur ni moderateur.

---

## 11. FIL D'ACTUALITES (FEED)

### Algorithme de tri

1. **Posts epingles** (PINNED) en premier
2. **Par date** de creation descendante (les plus recents en premier)

### Filtrage (FEED-09)

Le feed est automatiquement filtre selon les chantiers de l'utilisateur :
- Posts EVERYONE → visibles par tous
- Posts SPECIFIC_CHANTIERS → visibles si l'utilisateur est affecte a au moins un des chantiers cibles
- Posts SPECIFIC_PEOPLE → visibles si l'utilisateur est dans la liste

### Pagination (FEED-18)

**Endpoint** : `GET /api/dashboard/feed?page=1&size=20`

- **Defaut** : 20 posts par page (max 100)
- **Scroll infini** : Retourne limit+1 pour detecter `has_next`
- Parametres : `page` (>= 1), `size` (1-100)

### Reponse

```json
{
  "items": [PostResponse],
  "total": 42,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

---

## 12. EVENEMENTS DOMAINE

**Fichier** : `backend/modules/dashboard/domain/events/post_events.py`

| Evenement | Champs | Declencheur |
|-----------|--------|-------------|
| **PostPublishedEvent** | post_id, author_id, target_type, chantier_ids, user_ids, is_urgent | Publication |
| **PostPinnedEvent** | post_id, author_id, pinned_until | Epinglage |
| **PostArchivedEvent** | post_id | Archivage automatique |
| **PostDeletedEvent** | post_id, deleted_by_user_id | Suppression/moderation |
| **CommentAddedEvent** | comment_id, post_id, author_id, post_author_id | Nouveau commentaire |
| **LikeAddedEvent** | like_id, post_id, user_id, post_author_id | Like |
| **LikeRemovedEvent** | post_id, user_id | Unlike |

**Integration notifications** : `CommentAddedEvent` et `LikeAddedEvent` sont ecoutes par le module Notifications pour generer des notifications COMMENT_ADDED, MENTION et LIKE_ADDED.

---

## 13. API REST - ENDPOINTS

**Base** : `/api/dashboard`

### Feed

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/feed` | Fil d'actualites pagine (FEED-09, FEED-18) |

### Posts

| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/posts` | Publier un post (FEED-01, FEED-03, FEED-08) |
| GET | `/posts/{post_id}` | Detail d'un post |
| DELETE | `/posts/{post_id}` | Supprimer (FEED-16) |
| POST | `/posts/{post_id}/pin` | Epingler (FEED-08) |
| DELETE | `/posts/{post_id}/pin` | Desepingler |

### Commentaires

| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/posts/{post_id}/comments` | Ajouter commentaire (FEED-05) |

### Likes

| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/posts/{post_id}/like` | Liker (FEED-04) |
| DELETE | `/posts/{post_id}/like` | Unliker |

**Total : 9 endpoints**

---

## 14. ARCHITECTURE TECHNIQUE

### Clean Architecture

```
dashboard/
├── domain/
│   ├── entities/
│   │   ├── post.py              # Post + constantes metier
│   │   ├── post_media.py        # Photos/medias
│   │   ├── comment.py           # Commentaires
│   │   └── like.py              # Likes (unique par user/post)
│   ├── value_objects/
│   │   ├── post_status.py       # PUBLISHED/PINNED/ARCHIVED/DELETED
│   │   └── post_targeting.py    # PostTargeting + TargetType
│   ├── events/
│   │   └── post_events.py       # 7 evenements domaine
│   └── repositories/
│       ├── post_repository.py     # Interface abstraite
│       ├── comment_repository.py
│       ├── like_repository.py
│       └── post_media_repository.py
├── application/
│   ├── dtos/                    # PostDTO, CommentDTO, MediaDTO, etc.
│   └── use_cases/
│       ├── publish_post.py      # Creation + auto-pin urgent
│       ├── get_feed.py          # Feed pagine + filtre ciblage
│       ├── get_post.py          # Detail avec relations
│       ├── add_comment.py       # Commentaire + @mentions
│       ├── add_like.py          # Like + unicite
│       ├── remove_like.py       # Unlike
│       ├── delete_post.py       # Moderation
│       └── pin_post.py          # Epinglage
└── infrastructure/
    └── persistence/
        └── models.py            # 5 tables SQLAlchemy
```

### Schema base de donnees

**Tables** : posts, comments, likes, post_medias, post_target_chantiers, post_target_users

**Relations** :
```
posts (1) ──> (N) comments           [CASCADE delete]
posts (1) ──> (N) likes              [CASCADE delete]
posts (1) ──> (N) post_medias        [CASCADE delete]
posts (1) ──> (N) post_target_chantiers  [CASCADE delete]
posts (1) ──> (N) post_target_users      [CASCADE delete]
```

**Index cles** :
- `ix_posts_feed` (status, created_at) - Feed optimise
- `likes` UNIQUE (post_id, user_id) - Unicite like
- `post_target_chantiers` (chantier_id) et `post_target_users` (user_id) - Filtrage ciblage

### Decouplage inter-modules

Le module Dashboard n'a **aucune FK directe** vers les tables users ou chantiers. Les `author_id`, `user_id`, `chantier_id` sont stockes comme simples entiers sans contrainte FK, respectant le decouplage Clean Architecture entre modules.

---

## 15. FRONTEND - COMPOSANTS

### DashboardPage (page principale)

Point d'entree de l'application. Initialise les notifications Firebase, charge le feed, et orchestre les composants.

### Feed.tsx (fil d'actualites)

**Props** : `currentUserId, currentUserRole, isCompagnon?, mockPosts?, mockAuthors?`

**Fonctionnalites** :
- Scroll infini : detection a 500px du bas pour charger la suite (FEED-18)
- Tri : epingles en premier, puis par date DESC
- Likes/unlikes avec mise a jour optimiste
- Modal commentaires avec @mentions
- Donnees mock pour demo (5 posts exemples)

### PostComposer.tsx (composeur de post)

**Props** : `onSubmit, isCompagnon?, defaultChantier?`

**Fonctionnalites** :
- Zone de texte avec support @mentions (MentionInput)
- Selecteur de ciblage (FEED-03) :
  - "Tout le monde" (icone megaphone)
  - "Chantiers specifiques" (icone chantier)
  - "Personnes specifiques" (icone personnes)
- Bouton urgent (FEED-08) : marque comme urgent + auto-pin
- Bouton photo (FEED-02) : ouvre la capture
- Interface adaptee pour compagnons (plus limitee)

### PostCard.tsx (carte de post, memoizee)

**Props** : `post, author?, allAuthors?, currentUserId, onLike, onUnlike, onComment, onDelete?, isLiked?`

**Affichage** :
- Avatar auteur avec badge role colore :
  - Admin = violet, Conducteur = bleu, Chef chantier = vert, Compagnon = gris
- Date relative (il y a 5 min, 2h, 3j)
- Icone + texte ciblage (FEED-07)
- Contenu avec rendu des mentions
- Compteur medias (FEED-02)
- Compteurs likes et commentaires
- Indicateur epingle (FEED-08)
- Actions : like/unlike, commenter, supprimer (si auteur ou admin)

### CommentModal.tsx (modal commentaires)

**Props** : `isOpen, onClose, postId, postAuthor, onCommentAdded?`

- MentionInput pour @mentions (FEED-14)
- Appel `dashboardService.addComment(postId, {contenu})`
- Etat de chargement

---

## 16. SCENARIOS DE TEST

| # | Scenario | Resultat attendu |
|---|----------|-----------------|
| 1 | Publier post texte seul | OK, status PUBLISHED, dans le feed |
| 2 | Publier avec 6 photos | Erreur MaxPhotosExceededError |
| 3 | Publier post urgent | Status PINNED, pinned_until = now + 48h |
| 4 | Cibler 2 chantiers | PostTargeting avec 2 chantier_ids |
| 5 | Liker un post | Like cree, LikeAddedEvent emis |
| 6 | Liker un post deja like | Erreur AlreadyLikedError |
| 7 | Commenter avec @mention | Commentaire cree, notifications COMMENT_ADDED + MENTION |
| 8 | Supprimer post par auteur | Status DELETED |
| 9 | Supprimer post par non-auteur/non-admin | Erreur NotAuthorizedError |
| 10 | Feed filtre par chantier | Seuls les posts visibles pour l'utilisateur |
| 11 | Post > 7 jours | should_archive = true, archivable |
| 12 | Scroll infini page 2 | 20 posts suivants charges |
| 13 | Desepingler post | Status revient a PUBLISHED |

---

## 17. EVOLUTIONS FUTURES

| Evolution | Description | Priorite |
|-----------|-------------|----------|
| Upload photos reel | Integration stockage cloud (S3/GCS) | Haute |
| WebSocket / SSE | Remplacement du polling pour le feed temps reel | Moyenne |
| Reactions enrichies | Au-dela du simple like (coeur, bravo, etc.) | Basse |
| Sondages | Posts type sondage avec choix multiples | Basse |
| Partage de document | Lier un document GED a un post | Basse |
| Notifications push post | Handler pour PostPublishedEvent → notification ciblage | Moyenne |

---

## 18. REFERENCES CDC

| Section | Fonctionnalites | Status |
|---------|----------------|--------|
| FEED-01 | Publication posts | Backend + Frontend OK |
| FEED-02 | Photos (max 5, 2MB) | Backend OK, Frontend composant OK |
| FEED-03 | Ciblage audience | Backend + Frontend OK |
| FEED-04 | Likes | Backend + Frontend OK |
| FEED-05 | Commentaires | Backend + Frontend OK |
| FEED-07 | Indicateur ciblage | Frontend OK |
| FEED-08 | Posts urgents / epinglage | Backend + Frontend OK |
| FEED-09 | Auto-filtrage chantiers | Backend OK |
| FEED-10 | Emojis | OK (natif) |
| FEED-13 | Chargement progressif | Backend (thumbnail_url) OK |
| FEED-14 | @mentions | Backend + Frontend OK |
| FEED-16 | Moderation | Backend + Frontend OK |
| FEED-18 | Scroll infini | Backend + Frontend OK |
| FEED-19 | Compression auto 2MB | Backend (constante) OK |
| FEED-20 | Archivage 7 jours | Backend OK |
