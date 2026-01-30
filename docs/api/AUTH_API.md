# API Authentification Hub Chantier

**Version** : 1.0
**Base URL** : `/api/auth`
**Dernière mise à jour** : 30 janvier 2026

---

## Vue d'ensemble

L'API d'authentification Hub Chantier fournit les endpoints nécessaires pour la gestion complète du cycle de vie des utilisateurs :

- ✅ Connexion / Inscription
- ✅ Réinitialisation de mot de passe (oublié)
- ✅ Changement de mot de passe (utilisateur connecté)
- ✅ Invitation d'utilisateurs (Admin/Conducteur)
- ✅ Gestion des tokens JWT
- ✅ RGPD : Droit à l'oubli

**Sécurité** :
- Rate limiting actif sur tous les endpoints sensibles (3-10 req/min selon endpoint)
- Hash BCrypt pour les mots de passe
- Tokens JWT HttpOnly cookies (+ Authorization header en fallback)
- Validation force mot de passe (8+ car, majuscule, minuscule, chiffre)

---

## Endpoints Publics (Sans authentification)

### 1. Connexion

**POST** `/api/auth/login`

Authentifie un utilisateur et génère un token JWT.

**Rate limit** : 10 requêtes/minute par IP

**Body** :
```json
{
  "username": "user@example.com",
  "password": "Password123"
}
```

**Response 200** :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "42",
    "email": "user@example.com",
    "nom": "Dupont",
    "prenom": "Jean",
    "nom_complet": "Jean Dupont",
    "role": "compagnon",
    "is_active": true
  }
}
```

**Erreurs** :
- `400` : Email ou mot de passe incorrect
- `403` : Compte désactivé
- `429` : Trop de tentatives (rate limit)

---

### 2. Inscription (Auto-registration Compagnon)

**POST** `/api/auth/register`

Crée un nouveau compte avec le rôle `COMPAGNON` par défaut.

**Rate limit** : 5 requêtes/minute par IP

**Body** :
```json
{
  "email": "nouveau@example.com",
  "password": "Password123",
  "nom": "Martin",
  "prenom": "Pierre",
  "code_utilisateur": "PM001",
  "telephone": "0612345678"
}
```

**Response 201** :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "43",
    "email": "nouveau@example.com",
    "nom": "Martin",
    "prenom": "Pierre",
    "nom_complet": "Pierre Martin",
    "role": "compagnon",
    "is_active": true
  }
}
```

**Erreurs** :
- `400` : Email déjà utilisé
- `400` : Code utilisateur déjà utilisé
- `400` : Mot de passe trop faible
- `429` : Trop de tentatives (rate limit)

---

### 3. Demande de réinitialisation de mot de passe

**POST** `/api/auth/reset-password/request`

Envoie un email avec un lien de réinitialisation de mot de passe.

**Rate limit** : 3 requêtes/minute par IP

**Body** :
```json
{
  "email": "user@example.com"
}
```

**Response 200** :
```json
{
  "message": "Si votre email est enregistré, vous recevrez un lien de réinitialisation"
}
```

**Note** : Retourne toujours un succès pour éviter l'énumération des comptes.

**Email envoyé** :
- Template HTML professionnel
- Lien : `https://hub-chantier.fr/reset-password?token=XXX`
- Expiration : 1 heure

---

### 4. Réinitialisation de mot de passe (avec token)

**POST** `/api/auth/reset-password`

Réinitialise le mot de passe avec un token valide reçu par email.

**Rate limit** : 5 requêtes/minute par IP

**Body** :
```json
{
  "token": "abc123def456...",
  "new_password": "NewPassword123"
}
```

**Response 200** :
```json
{
  "message": "Mot de passe réinitialisé avec succès"
}
```

**Erreurs** :
- `400` : Token invalide ou expiré
- `400` : Nouveau mot de passe trop faible
- `429` : Trop de tentatives (rate limit)

---

### 5. Acceptation d'invitation

**POST** `/api/auth/accept-invitation`

Active un compte créé par invitation et définit le mot de passe.

**Body** :
```json
{
  "token": "invite_abc123def456...",
  "password": "MyPassword123"
}
```

**Response 200** :
```json
{
  "message": "Invitation acceptée, votre compte est maintenant actif"
}
```

**Erreurs** :
- `400` : Token d'invitation invalide ou expiré
- `400` : Mot de passe trop faible

**Email reçu** :
- Template HTML d'invitation
- Lien : `https://hub-chantier.fr/invite?token=XXX`
- Expiration : 7 jours

---

## Endpoints Authentifiés (Token JWT requis)

### 6. Récupérer l'utilisateur connecté

**GET** `/api/auth/me`

Récupère les informations de l'utilisateur connecté.

**Headers** :
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response 200** :
```json
{
  "id": "42",
  "email": "user@example.com",
  "nom": "Dupont",
  "prenom": "Jean",
  "nom_complet": "Jean Dupont",
  "initiales": "JD",
  "role": "compagnon",
  "type_utilisateur": "employe",
  "is_active": true,
  "couleur": "#3B82F6",
  "telephone": "0612345678",
  "metier": "Maçon",
  "created_at": "2026-01-15T10:30:00Z"
}
```

**Erreurs** :
- `401` : Token manquant ou invalide

---

### 7. Changement de mot de passe

**POST** `/api/auth/change-password`

Change le mot de passe de l'utilisateur connecté.

**Rate limit** : 5 requêtes/minute par IP

**Headers** :
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Body** :
```json
{
  "old_password": "OldPassword123",
  "new_password": "NewPassword456"
}
```

**Response 200** :
```json
{
  "message": "Mot de passe modifié avec succès"
}
```

**Erreurs** :
- `400` : Ancien mot de passe incorrect
- `400` : Nouveau mot de passe trop faible
- `400` : Nouveau mot de passe identique à l'ancien
- `401` : Token manquant ou invalide
- `429` : Trop de tentatives (rate limit)

---

### 8. Déconnexion

**POST** `/api/auth/logout`

Supprime le cookie d'authentification.

**Headers** :
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response 200** :
```json
{
  "message": "Déconnexion réussie"
}
```

---

## Endpoints Admin/Conducteur (Rôles requis)

### 9. Invitation d'un utilisateur

**POST** `/api/auth/invite`

Crée un compte pré-rempli et envoie un email d'invitation.

**Rôles autorisés** : `admin`, `conducteur`

**Headers** :
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Body** :
```json
{
  "email": "nouveau.chef@example.com",
  "nom": "Bernard",
  "prenom": "Sophie",
  "role": "chef_chantier",
  "type_utilisateur": "employe",
  "code_utilisateur": "SB001",
  "metier": "Chef de chantier"
}
```

**Response 201** :
```json
{
  "message": "Invitation envoyée à nouveau.chef@example.com"
}
```

**Erreurs** :
- `400` : Email déjà utilisé
- `400` : Code utilisateur déjà utilisé
- `400` : Rôle ou type utilisateur invalide
- `401` : Non authentifié
- `403` : Droits insuffisants (rôle admin/conducteur requis)

**Rôles disponibles** :
- `admin` - Accès complet
- `conducteur` - Gestion chantiers + équipes
- `chef_chantier` - Gestion équipe chantier
- `compagnon` - Accès terrain

**Types utilisateur** :
- `employe` - Salarié permanent
- `interimaire` - Intérimaire
- `sous_traitant` - Sous-traitant externe

---

## RGPD : Droit à l'oubli

### 10. Suppression définitive des données

**DELETE** `/api/auth/users/{user_id}/gdpr`

Supprime définitivement toutes les données personnelles d'un utilisateur (RGPD Article 17).

**Rôles autorisés** : `admin` ou l'utilisateur lui-même

**Headers** :
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response 200** :
```json
{
  "message": "Données utilisateur supprimées définitivement",
  "user_id": 42,
  "deleted_at": "2026-01-30T14:30:00Z"
}
```

**Erreurs** :
- `401` : Non authentifié
- `403` : Permission refusée (vous ne pouvez supprimer que vos propres données ou être admin)
- `404` : Utilisateur non trouvé

**⚠️ ATTENTION** : Cette action est **irréversible** et supprime :
- Toutes les données personnelles de l'utilisateur
- Historique des actions
- Données associées (selon règles métier)

---

## Gestion des consentements RGPD

### 11. Récupérer les consentements

**GET** `/api/auth/consents`

Récupère les préférences de consentement RGPD.

**Response 200** :
```json
{
  "geolocation": true,
  "notifications": true,
  "analytics": false,
  "timestamp": "2026-01-30T10:00:00Z",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0..."
}
```

---

### 12. Mettre à jour les consentements

**POST** `/api/auth/consents`

Met à jour les préférences de consentement RGPD.

**Body** :
```json
{
  "geolocation": true,
  "notifications": true,
  "analytics": false
}
```

**Response 200** :
```json
{
  "geolocation": true,
  "notifications": true,
  "analytics": false,
  "timestamp": "2026-01-30T14:30:00Z",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0..."
}
```

---

## Validation des mots de passe

Tous les mots de passe doivent respecter ces règles :

- **Longueur** : Minimum 8 caractères
- **Majuscule** : Au moins 1 lettre majuscule
- **Minuscule** : Au moins 1 lettre minuscule
- **Chiffre** : Au moins 1 chiffre

**Exemple valide** : `Password123`
**Exemples invalides** :
- `password` (pas de majuscule, pas de chiffre)
- `PASSWORD123` (pas de minuscule)
- `Pass123` (moins de 8 caractères)

---

## Tokens et expiration

### Token JWT

- **Durée de vie** : 24 heures par défaut
- **Stockage** : Cookie HttpOnly sécurisé (+ Authorization header en fallback)
- **Claims** :
  ```json
  {
    "sub": "42",
    "email": "user@example.com",
    "role": "compagnon",
    "exp": 1706630400
  }
  ```

### Token de réinitialisation

- **Durée de vie** : 1 heure
- **Format** : `secrets.token_urlsafe(32)` (URL-safe random string)
- **Usage unique** : Invalidé après utilisation
- **Stockage** : Colonne `password_reset_token` + `password_reset_token_expires`

### Token d'invitation

- **Durée de vie** : 7 jours
- **Format** : `secrets.token_urlsafe(32)`
- **Usage unique** : Invalidé après acceptation
- **Stockage** : Colonne `invitation_token` + `invitation_token_expires`

---

## Gestion des erreurs

Tous les endpoints retournent des erreurs au format JSON standard :

```json
{
  "detail": "Message d'erreur descriptif"
}
```

### Codes HTTP

| Code | Signification |
|------|---------------|
| 200 | Succès |
| 201 | Ressource créée |
| 400 | Requête invalide (validation échouée) |
| 401 | Non authentifié (token manquant/invalide) |
| 403 | Permission refusée (rôle insuffisant) |
| 404 | Ressource non trouvée |
| 429 | Trop de requêtes (rate limit dépassé) |
| 500 | Erreur serveur interne |

---

## Rate Limiting

Le rate limiting protège contre les attaques par force brute :

| Endpoint | Limite |
|----------|--------|
| POST `/login` | 10 req/min par IP |
| POST `/register` | 5 req/min par IP |
| POST `/reset-password/request` | 3 req/min par IP |
| POST `/reset-password` | 5 req/min par IP |
| POST `/change-password` | 5 req/min par IP |

**Réponse 429** :
```json
{
  "detail": "Rate limit exceeded"
}
```

---

## Exemples d'utilisation

### cURL

```bash
# Login
curl -X POST https://hub-chantier.fr/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user@example.com","password":"Password123"}'

# Changement de mot de passe
curl -X POST https://hub-chantier.fr/api/auth/change-password \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"old_password":"OldPass123","new_password":"NewPass456"}'

# Invitation utilisateur
curl -X POST https://hub-chantier.fr/api/auth/invite \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"new@example.com","nom":"Doe","prenom":"Jane","role":"chef_chantier"}'
```

### JavaScript (Fetch)

```javascript
// Login
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'user@example.com',
    password: 'Password123'
  })
});
const data = await response.json();

// Changement de mot de passe
await fetch('/api/auth/change-password', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    old_password: 'OldPass123',
    new_password: 'NewPass456'
  })
});
```

### Python (requests)

```python
import requests

# Login
response = requests.post(
    'https://hub-chantier.fr/api/auth/login',
    json={
        'username': 'user@example.com',
        'password': 'Password123'
    }
)
data = response.json()
token = data['access_token']

# Changement de mot de passe
requests.post(
    'https://hub-chantier.fr/api/auth/change-password',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'old_password': 'OldPass123',
        'new_password': 'NewPass456'
    }
)
```

---

## Sécurité

### Bonnes pratiques implémentées

✅ **Hash BCrypt** - Tous les mots de passe sont hashés avec BCrypt (12 rounds)
✅ **Rate limiting** - Protection contre brute force sur tous les endpoints sensibles
✅ **Tokens sécurisés** - `secrets.token_urlsafe(32)` pour tokens reset/invitation
✅ **Validation stricte** - Force des mots de passe vérifiée côté serveur
✅ **HttpOnly cookies** - Tokens JWT stockés en cookies HttpOnly (protection XSS)
✅ **Expiration tokens** - Reset 1h, invitation 7j, JWT 24h
✅ **Usage unique** - Tokens reset/invitation invalidés après utilisation
✅ **Énumération protégée** - Reset password retourne toujours succès
✅ **RGPD compliant** - Droit à l'oubli + consentements + export données

### Recommandations

- Utiliser HTTPS en production (obligatoire)
- Configurer CORS correctement (domaines autorisés)
- Monitorer les tentatives de connexion échouées
- Implémenter un système d'alerte pour activités suspectes
- Sauvegarder régulièrement la base de données

---

## Support

Pour toute question technique :
- Documentation : `/docs/workflows/WORKFLOW_AUTHENTIFICATION.md`
- Spécifications : `/docs/SPECIFICATIONS.md` (Section 3.3)
- Architecture : `/docs/architecture/CLEAN_ARCHITECTURE.md`

**Version** : 1.0 (30 janvier 2026)
**Statut** : ✅ Production Ready
