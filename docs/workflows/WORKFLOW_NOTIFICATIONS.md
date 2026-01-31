# Workflow Notifications - Hub Chantier

> Document cree le 30 janvier 2026
> Analyse complete du systeme de notifications in-app et push

---

## TABLE DES MATIERES

1. [Vue d'ensemble](#1-vue-densemble)
2. [Entite Notification](#2-entite-notification)
3. [Types de notifications](#3-types-de-notifications)
4. [Systeme d'evenements (EventBus)](#4-systeme-devenements-eventbus)
5. [Handlers d'evenements](#5-handlers-devenements)
6. [Firebase Cloud Messaging (Push)](#6-firebase-cloud-messaging-push)
7. [Polling frontend (30s)](#7-polling-frontend-30s)
8. [Lecture et gestion](#8-lecture-et-gestion)
9. [API REST - Endpoints](#9-api-rest---endpoints)
10. [Architecture technique](#10-architecture-technique)
11. [Frontend - Composants](#11-frontend---composants)
12. [Scenarios de test](#12-scenarios-de-test)
13. [Handlers a implementer](#13-handlers-a-implementer)
14. [Evolutions futures](#14-evolutions-futures)
15. [References CDC](#15-references-cdc)

---

## 1. VUE D'ENSEMBLE

### Objectif du module

Le module Notifications centralise toutes les alertes de l'application : commentaires, mentions, likes, documents, signalements, taches, etc. Il combine un systeme de notifications **in-app** (polling 30 secondes) avec des **push notifications** via Firebase Cloud Messaging (FCM).

### Flux global simplifie

```
Evenement domaine (ex: CommentAddedEvent)
    |
    v
[EventBus] Route vers les handlers inscrits
    |
    +---> [Handler Notification]
    |     Cree une entite Notification en base
    |     +---> Notification in-app (polling 30s)
    |     +---> Push FCM (si token enregistre)
    |
    +---> [Autres handlers] (webhooks, etc.)
```

### Architecture event-driven

Le systeme repose sur un **EventBus** partage :
1. Les modules metier (Dashboard, Taches, etc.) publient des evenements domaine
2. Le module Notifications s'abonne aux evenements pertinents
3. Les handlers creent des notifications ciblees
4. Le frontend recupere les notifications par polling ou push FCM

### Etat actuel : 5 handlers cables

Sur les 10 types de notifications definis, **5 handlers** sont actuellement cables :
- `CommentAddedEvent` → COMMENT_ADDED + MENTION
- `LikeAddedEvent` → LIKE_ADDED
- `heures.validated` → SYSTEM (notification au compagnon quand ses heures sont validees)
- `chantier.created` → CHANTIER_ASSIGNMENT (notification aux conducteurs/chefs assignes)
- `chantier.statut_changed` → SYSTEM (notification a l'equipe lors d'un changement de statut)

Les 4 autres types (DOCUMENT_ADDED, SIGNALEMENT_CREATED, SIGNALEMENT_RESOLVED, TACHE_ASSIGNED, TACHE_DUE) existent dans l'enum mais **n'ont pas de handler implemente**.

---

## 2. ENTITE NOTIFICATION

**Fichier** : `backend/modules/notifications/domain/entities/notification.py`

| Champ | Type | Defaut | Requis | Notes |
|-------|------|--------|--------|-------|
| id | Optional[int] | None | Non | Cle primaire |
| user_id | int | - | Oui | Destinataire de la notification |
| type | NotificationType | - | Oui | Type de notification (enum) |
| title | str | - | Oui | Titre (non vide apres strip) |
| message | str | - | Oui | Message (non vide apres strip) |
| is_read | bool | False | Non | Lu ou non lu |
| read_at | Optional[datetime] | None | Non | Horodatage lecture |
| related_post_id | Optional[int] | None | Non | FK post lie |
| related_comment_id | Optional[int] | None | Non | FK commentaire lie |
| related_chantier_id | Optional[int] | None | Non | FK chantier lie |
| related_document_id | Optional[int] | None | Non | FK document lie |
| triggered_by_user_id | Optional[int] | None | Non | Qui a declenche |
| metadata | Dict[str, Any] | {} | Non | Donnees supplementaires JSON |
| created_at | datetime | now() | Non | Horodatage creation |

**Validations** :
- `title` non vide apres strip (ValueError)
- `message` non vide apres strip (ValueError)

**Methodes** :
- `mark_as_read()` - is_read=True, read_at=now()
- `mark_as_unread()` - is_read=False, read_at=None
- `is_unread` (propriete) - not is_read

---

## 3. TYPES DE NOTIFICATIONS

**Fichier** : `backend/modules/notifications/domain/value_objects/notification_type.py`

### 10 types definis

| Type | Label | Source module | Handler | Icone (lucide) |
|------|-------|--------------|---------|----------------|
| COMMENT_ADDED | "Quelqu'un a commente votre post" | Dashboard | ✅ Cable | MessageCircle |
| MENTION | "Quelqu'un vous a mentionne avec @" | Dashboard | ✅ Cable | AtSign |
| LIKE_ADDED | "Quelqu'un a aime votre post" | Dashboard | ✅ Cable | Heart |
| DOCUMENT_ADDED | "Nouveau document sur un chantier" | GED | ❌ Non cable | FileText |
| CHANTIER_ASSIGNMENT | "Affecte a un chantier" | Chantiers | ✅ Cable (`chantier.created`) | Building2 |
| SIGNALEMENT_CREATED | "Nouveau signalement" | Signalements | ❌ Non cable | AlertTriangle |
| SIGNALEMENT_RESOLVED | "Signalement resolu" | Signalements | ❌ Non cable | AlertTriangle |
| TACHE_ASSIGNED | "Tache assignee" | Taches | ❌ Non cable | CheckSquare |
| TACHE_DUE | "Tache bientot due" | Taches | ❌ Non cable | CheckSquare |
| SYSTEM | "Notification systeme" | Systeme | ✅ Cable (`heures.validated`, `chantier.statut_changed`) | Bell |

---

## 4. SYSTEME D'EVENEMENTS (EVENTBUS)

**Fichier** : `backend/shared/infrastructure/event_bus/event_bus.py`

### DomainEvent (frozen dataclass)

| Champ | Type | Description |
|-------|------|-------------|
| event_id | str | UUID auto-genere |
| event_type | str | Format '{module}.{action}' |
| aggregate_id | Optional[str] | ID de la ressource |
| data | Dict[str, Any] | Payload de l'evenement |
| metadata | Dict[str, Any] | user_id, ip_address, user_agent |
| occurred_at | datetime | Horodatage UTC |

### EventBus (singleton)

**Methodes** :

| Methode | Description |
|---------|-------------|
| `subscribe(event_type, handler)` | Inscription exacte : 'chantier.created' |
| `on(event_type)` | Decorateur : `@event_bus.on('chantier.created')` |
| `subscribe_all(handler)` | Inscription globale (webhooks) |
| `publish(event)` | Publication vers tous les handlers correspondants |
| `get_history(event_type?, limit=100)` | Historique debug (1000 derniers) |
| `get_subscribers_count(event_type?)` | Nombre de handlers |
| `clear_history()` | Vider l'historique (tests) |

### Patterns de souscription

| Pattern | Exemple | Correspond a |
|---------|---------|-------------|
| Exact | `'chantier.created'` | Uniquement chantier.created |
| Wildcard | `'chantier.*'` | chantier.created, chantier.updated, etc. |
| Global | `subscribe_all()` | Tous les evenements |

### Execution des handlers

- **Parallele** : `asyncio.gather()` - tous les handlers en parallele
- **Isolation** : L'echec d'un handler ne bloque pas les autres
- **Mixte** : Supporte handlers synchrones et asynchrones

---

## 5. HANDLERS D'EVENEMENTS

**Fichier** : `backend/modules/notifications/infrastructure/event_handlers.py`

### Handler CommentAddedEvent (cable)

```
Evenement : CommentAddedEvent
    |
    +---> Si comment.author_id != post.author_id :
    |     Creer notification COMMENT_ADDED pour post.author_id
    |
    +---> Parser @mentions dans le contenu (regex: @([a-zA-Z0-9_-]+))
          Pour chaque mention (sauf l'auteur du commentaire) :
          Creer notification MENTION pour l'utilisateur mentionne
```

**Donnees de la notification** :
- `user_id` = destinataire (auteur du post ou personne mentionnee)
- `triggered_by_user_id` = auteur du commentaire
- `related_post_id` = ID du post
- `related_comment_id` = ID du commentaire

### Handler LikeAddedEvent (cable)

```
Evenement : LikeAddedEvent
    |
    +---> Si like.user_id != post.author_id :
          Creer notification LIKE_ADDED pour post.author_id
```

**Regle** : Pas de notification pour les auto-likes (meme utilisateur).

### Enregistrement

```python
register_notification_handlers()  # Appele au demarrage dans main.py
```

Les decorateurs `@event_handler(EventType)` enregistrent automatiquement via `event_bus.subscribe()`.

---

## 6. FIREBASE CLOUD MESSAGING (PUSH)

### Service backend

**Fichier** : `backend/shared/infrastructure/notifications/notification_service.py`

**NotificationService** (singleton) :

| Methode | Description |
|---------|-------------|
| `send_to_token(token, payload)` | Envoyer a 1 terminal |
| `send_to_tokens(tokens, payload)` | Envoyer a N terminaux |
| `send_to_topic(topic, payload)` | Envoyer a un topic (ex: "chantier_123") |
| `is_available` (propriete) | Firebase initialise ou non |

**NotificationPayload** :
```
title: str (requis)
body: str (requis)
data: Dict[str, str] = {}
image_url: Optional[str] = None
click_action: Optional[str] = None
```

### Configuration

**Backend** :
- `FIREBASE_CREDENTIALS_PATH` : Chemin vers le fichier JSON de credentials
- `FIREBASE_CREDENTIALS` : JSON encode (fallback)
- Mode simulation possible sans credentials (dev)

**Frontend** (variables d'environnement) :
- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_PROJECT_ID`
- `VITE_FIREBASE_STORAGE_BUCKET`
- `VITE_FIREBASE_MESSAGING_SENDER_ID`
- `VITE_FIREBASE_APP_ID`
- `VITE_FIREBASE_VAPID_KEY` (Web Push)

### Service Worker

**Fichier** : `frontend/public/firebase-messaging-sw.js`

Gere les messages push lorsque l'application n'est pas au premier plan (background messages).

### Flux d'initialisation frontend

```
DashboardPage monte
    |
    v
Verifier consentement utilisateur (consent service)
    |
    v
isFirebaseConfigured() ? (toutes les vars d'env presentes)
    |
    v
requestNotificationPermission()
    |
    v
Token FCM obtenu → enregistre aupres du backend
    |
    v
onForegroundMessage(callback) → notifications en temps reel
```

---

## 7. POLLING FRONTEND (30s)

### Implementation actuelle

**Fichier** : `frontend/src/hooks/useNotifications.ts`

```typescript
// Polling toutes les 30 secondes
const interval = setInterval(fetchNotifications, 30000)
```

### Hook useNotifications()

**Retourne** :
| Champ | Type | Description |
|-------|------|-------------|
| notifications | Notification[] | 20 dernieres notifications |
| unreadCount | number | Compteur non lues |
| loading | boolean | Etat de chargement |
| error | string \| null | Erreur eventuelle |
| refresh | () => Promise | Rafraichir manuellement |
| markAsRead | (id) => Promise | Marquer une comme lue |
| markAllAsRead | () => Promise | Marquer toutes comme lues |
| deleteNotification | (id) => Promise | Supprimer une notification |

### Comportement

- Charge 20 notifications au montage du composant
- Rafraichit toutes les 30 secondes
- Mises a jour optimistes (mark as read, delete)
- Nettoyage a la destruction du composant (clearInterval)
- Logging des erreurs via le service logger

### Polling 30s vs WebSocket

L'implementation actuelle utilise le **polling a 30 secondes**. C'est une approche simple et robuste pour le nombre d'utilisateurs cible (20 employes). L'evolution vers **WebSocket ou SSE** (Server-Sent Events) est envisagee pour le futur si le nombre d'utilisateurs augmente significativement.

---

## 8. LECTURE ET GESTION

### Marquer comme lu

**Use case** : `MarkAsReadUseCase`

| Scenario | Comportement |
|----------|-------------|
| 1 notification | Verifie ownership (user_id match), marque is_read=True, read_at=now() |
| N notifications | Itere, verifie ownership pour chacune |
| Toutes | UPDATE batch WHERE user_id=X AND is_read=False |

### Supprimer

| Action | Endpoint |
|--------|----------|
| Supprimer 1 | `DELETE /notifications/{id}` |
| Supprimer tout | `DELETE /notifications` |

---

## 9. API REST - ENDPOINTS

**Base** : `/api/notifications`

| Methode | Endpoint | Description | Parametres |
|---------|----------|-------------|-----------|
| GET | `/notifications` | Lister notifications | unread_only (bool), skip (int, 0), limit (int, 50, max 100) |
| GET | `/notifications/unread-count` | Compteur non lues | - |
| PATCH | `/notifications/read` | Marquer comme lues | notification_ids (null = toutes) |
| PATCH | `/notifications/{id}/read` | Marquer 1 comme lue | - |
| DELETE | `/notifications/{id}` | Supprimer 1 | - |
| DELETE | `/notifications` | Supprimer toutes | - |
| POST | `/notifications/debug/seed` | Donnees de test | (mode DEBUG uniquement) |

**Total : 7 endpoints**

### DTO de reponse (NotificationDTO)

```
id: int
user_id: int
type: str (enum value)
title: str
message: str
is_read: bool
read_at: str | null
related_post_id: int | null
related_comment_id: int | null
related_chantier_id: int | null
related_document_id: int | null
triggered_by_user_id: int | null
triggered_by_user_name: str (enrichi)
chantier_name: str (enrichi)
metadata: Record<string, unknown>
created_at: str (ISO)
```

**Enrichissement** : Le DTO inclut `triggered_by_user_name` et `chantier_name` resolus cote serveur pour eviter des appels supplementaires au frontend.

---

## 10. ARCHITECTURE TECHNIQUE

### Clean Architecture

```
notifications/
├── domain/
│   ├── entities/
│   │   └── notification.py              # Entite Notification
│   ├── value_objects/
│   │   └── notification_type.py         # 10 types enum
│   └── repositories/
│       └── notification_repository.py   # Interface abstraite
├── application/
│   └── use_cases/
│       └── mark_as_read.py             # Lecture unitaire/batch
└── infrastructure/
    ├── event_handlers.py                # 5 handlers cables (comment, like, heures, chantier.created, chantier.statut_changed)
    ├── persistence/
    │   ├── models.py                    # Modele SQLAlchemy
    │   └── sqlalchemy_notification_repository.py
    └── web/
        └── routes.py                    # 7 endpoints API
```

### Schema base de donnees

**Table** : notifications

| Colonne | Type | Index |
|---------|------|-------|
| id | INTEGER PK | - |
| user_id | INTEGER NOT NULL | ix_notifications_user_unread (composite) |
| type | VARCHAR(50) NOT NULL | Oui |
| title | VARCHAR(255) NOT NULL | - |
| message | TEXT NOT NULL | - |
| is_read | BOOLEAN NOT NULL DEFAULT False | ix_notifications_user_unread (composite) |
| read_at | DATETIME | - |
| related_post_id | INTEGER | Oui |
| related_comment_id | INTEGER | - |
| related_chantier_id | INTEGER | Oui |
| related_document_id | INTEGER | - |
| triggered_by_user_id | INTEGER | Oui |
| extra_data | JSON | - |
| created_at | DATETIME NOT NULL | ix_notifications_user_created (composite) |

**Index composites** :
- `ix_notifications_user_unread` (user_id, is_read, created_at) - Requetes feed non lues
- `ix_notifications_user_created` (user_id, created_at) - Requetes chronologiques

### Infrastructure partagee

**EventBus** : `backend/shared/infrastructure/event_bus/event_bus.py` - Singleton partage entre tous les modules.

**NotificationService FCM** : `backend/shared/infrastructure/notifications/notification_service.py` - Singleton pour push Firebase.

---

## 11. FRONTEND - COMPOSANTS

### NotificationDropdown.tsx

**Fonctionnalites** :
- Dropdown affichant les 20 dernieres notifications
- Point bleu sur les non lues + fond bleu
- Clic → ouvre un modal de detail avec :
  - Texte complet de la notification
  - Apercu document (PDF/images) + telechargement
  - Nom du chantier
  - Boutons de navigation (Voir post, Voir chantier, Voir document GED)
- Bouton "Tout marquer comme lu"
- Lien "Voir toutes les notifications" → `/notifications`
- Fermeture au clic externe

### Icones par type

| Type | Icone (lucide-react) |
|------|---------------------|
| comment_added | MessageCircle |
| mention | AtSign |
| like_added | Heart |
| document_added | FileText |
| chantier_assignment | Building2 |
| signalement_created / signalement_resolved | AlertTriangle |
| tache_assigned / tache_due | CheckSquare |
| (defaut) | Bell |

### Temps relatif

Fonction `formatRelativeTime(dateString)` :
- < 60 min → "Il y a X min"
- < 24h → "Il y a Xh"
- < 7 jours → "Il y a Xj"
- Sinon → "30 dec" (date formatee)

### Service push frontend

**Fichier** : `frontend/src/services/notifications.ts`

| Fonction | Description |
|----------|-------------|
| `initNotifications()` | Initialise Firebase, demande permission, enregistre token |
| `subscribeToNotifications(callback)` | S'abonne aux messages foreground |
| `disableNotifications()` | Desactive et supprime le token |
| `areNotificationsEnabled()` | Verifie si actives |
| `areNotificationsSupported()` | Verifie support navigateur (Notification API + Service Worker) |

---

## 12. SCENARIOS DE TEST

| # | Scenario | Resultat attendu |
|---|----------|-----------------|
| 1 | Commentaire sur un post | Notification COMMENT_ADDED pour l'auteur du post |
| 2 | Commentaire par l'auteur du post | Pas de notification (self-check) |
| 3 | Commentaire avec @mention | Notification MENTION pour chaque mentionne |
| 4 | Like sur un post | Notification LIKE_ADDED pour l'auteur |
| 5 | Like par l'auteur du post | Pas de notification (self-check) |
| 6 | Marquer 1 notification comme lue | is_read=True, read_at renseigne |
| 7 | Marquer toutes comme lues | Batch update, compteur → 0 |
| 8 | Supprimer 1 notification | Supprimee de la base |
| 9 | Polling 30s | 20 notifications rechargees |
| 10 | Firebase non configure | Mode simulation, pas de push |
| 11 | Notification title vide | Erreur validation (ValueError) |

---

## 13. HANDLERS IMPLEMENTES ET A IMPLEMENTER

### Handlers cables (audit 30 janvier 2026)

| Type notification | Evenement ecoute | Module source | Handler |
|------------------|-----------------|--------------|---------|
| CHANTIER_ASSIGNMENT | `chantier.created` | Chantiers | `handle_chantier_created` — Notifie les conducteurs et chefs assignes |
| SYSTEM | `heures.validated` | Pointages | `handle_heures_validated` — Notifie le compagnon que ses heures sont validees |
| SYSTEM | `chantier.statut_changed` | Chantiers | `handle_chantier_statut_changed` — Notifie l'equipe (conducteurs + chefs) du changement de statut |

> Tous ces handlers sont dans `backend/modules/notifications/infrastructure/event_handlers.py` (Clean Architecture : le module notifications ecoute passivement).

### Handlers restant a implementer

| Type notification | Evenement a ecouter | Module source | Notes |
|------------------|---------------------|--------------|-------|
| DOCUMENT_ADDED | DocumentUploadedEvent | GED | Notifier les utilisateurs du chantier |
| SIGNALEMENT_CREATED | SignalementCreeEvent | Signalements | Notifier le chef de chantier |
| SIGNALEMENT_RESOLVED | SignalementTraiteEvent | Signalements | Notifier le createur |
| TACHE_ASSIGNED | TacheCreatedEvent | Taches | Notifier le compagnon (quand affectation existera) |
| TACHE_DUE | (cron/scheduler) | Taches | Alert J-1 avant echeance |

### Patron d'implementation

Pour chaque handler a implementer :

```python
@event_handler(NouvelEvenement)
def handle_nouvel_evenement(event):
    # 1. Determiner le(s) destinataire(s)
    # 2. Eviter l'auto-notification (triggered_by != destinataire)
    # 3. Creer la notification avec les related_*_id
    # 4. Persister via repository.save()
    # 5. (optionnel) Envoyer push FCM
```

---

## 14. EVOLUTIONS FUTURES

| Evolution | Description | Priorite |
|-----------|-------------|----------|
| Handlers manquants (5 types) | Implementer les event handlers restants (DOCUMENT, SIGNALEMENT x2, TACHE x2) | Haute |
| WebSocket / SSE | Remplacer le polling 30s par des connexions temps reel | Moyenne |
| Preferences notifications | Permettre a l'utilisateur de choisir ses notifications | Moyenne |
| Notifications email | Digest quotidien par email | Basse |
| Badges application | Badge compteur non lu sur l'icone de l'app | Basse |
| Groupement | Grouper les notifications similaires ("3 personnes ont aime votre post") | Basse |

---

## 15. REFERENCES CDC

| Section | Fonctionnalites | Status |
|---------|----------------|--------|
| Notifications in-app | Entite + API + frontend | Backend + Frontend OK |
| Push FCM | Service Firebase + Service Worker | Configure, operationnel |
| CommentAddedEvent handler | COMMENT_ADDED + MENTION | Cable et actif |
| LikeAddedEvent handler | LIKE_ADDED | Cable et actif |
| Handlers chantier + heures | CHANTIER_ASSIGNMENT, SYSTEM (heures.validated, chantier.statut_changed) | ✅ Cable et actif (audit 30 jan) |
| Handlers restants (5 types) | DOCUMENT, SIGNALEMENT x2, TACHE x2 | Types definis, handlers a implementer |
| Polling 30s | Hook useNotifications | Frontend OK |
| Lecture batch | Mark as read unitaire et global | Backend + Frontend OK |
