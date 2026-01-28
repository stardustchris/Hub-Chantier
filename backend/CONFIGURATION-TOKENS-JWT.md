# Configuration des Tokens JWT - Hub Chantier

## 📋 Configuration appliquée

### Environnement DEV (Développement/Tests)
- **Access Token** : 8 heures (480 minutes)
- **Objectif** : Confort pour les développeurs, pas de déconnexion pendant la journée
- **Configuration** : `.env` → `ACCESS_TOKEN_EXPIRE_MINUTES=480`

### Environnement PROD (Production)
- **Access Token** : 2 heures (120 minutes) avec refresh automatique
- **Refresh Token** : 24 heures
- **Admin** : 1 heure (60 minutes) - Plus strict pour les comptes sensibles
- **Configuration** : `.env` → `ACCESS_TOKEN_EXPIRE_MINUTES=120`

## 🔐 Rationale Sécurité

### Pourquoi 8h en DEV ?
- ✅ Pas d'interruption pendant les tests
- ✅ Pas de ressaisie fréquente du mot de passe
- ⚠️ Environnement non exposé (localhost uniquement)

### Pourquoi 2h en PROD ?
- ✅ **Fenêtre d'attaque réduite** : Si un token est volé, il n'est utilisable que 2h max
- ✅ **Refresh automatique** : L'utilisateur ne voit pas la déconnexion (transparent)
- ✅ **Détection d'inactivité** : Si pas utilisé pendant 24h, déconnexion automatique
- ✅ **RGPD compliance** : Session limitée dans le temps

### Pourquoi 1h pour les admins ?
- ✅ **Compte à privilèges élevés** : Plus sensible, nécessite plus de vigilance
- ✅ **Conformité** : Best practice sécurité (OWASP, ANSSI)

## 🔄 Fonctionnement du Refresh Token (à implémenter)

```
Timeline utilisateur :
10h00 : Connexion → Access token (2h) + Refresh token (24h)
11h55 : Token expire dans 5 min → Frontend demande refresh automatiquement
11h56 : Nouveau access token (2h) → Utilisateur reste connecté
18h00 : Inactivité 8h → Refresh token expire → Déconnexion

Avantages :
- Token court (2h) = sécurisé
- Pas de déconnexion surprise = confort
- Inactivité détectée (24h) = session zombie évitée
```

## 📝 Configuration actuelle

### Fichier `.env` (DEV)
```env
DEBUG=true
ACCESS_TOKEN_EXPIRE_MINUTES=480  # 8 heures
REFRESH_TOKEN_EXPIRE_HOURS=24
ADMIN_TOKEN_EXPIRE_MINUTES=60
```

### Fichier `.env` (PROD - à créer)
```env
DEBUG=false
ACCESS_TOKEN_EXPIRE_MINUTES=120  # 2 heures
REFRESH_TOKEN_EXPIRE_HOURS=24
ADMIN_TOKEN_EXPIRE_MINUTES=60
```

## ✅ Étapes réalisées

1. ✅ Configuration `.env` : Token 8h en DEV
2. ✅ Ajout paramètres `REFRESH_TOKEN_EXPIRE_HOURS` et `ADMIN_TOKEN_EXPIRE_MINUTES`
3. ✅ Mise à jour `config.py` avec les nouvelles variables
4. ✅ Documentation `.env.example`

## 🚧 À implémenter (optionnel)

### Refresh Token automatique (Frontend)
Le frontend doit intercepter les erreurs 401 et demander un refresh automatiquement :

```typescript
// Interceptor axios (frontend/src/services/api.ts)
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response.status === 401) {
      // Token expiré, demander refresh
      const newToken = await refreshToken();
      // Retry la requête avec le nouveau token
      return axios.request(error.config);
    }
    return Promise.reject(error);
  }
);
```

### Endpoint refresh token (Backend)
```python
@router.post("/auth/refresh")
def refresh_access_token(refresh_token: str):
    # Valider refresh token
    # Générer nouveau access token
    # Retourner nouveau token
```

## 📊 Impact utilisateur

### Avant
- Déconnexion toutes les heures
- Interruption du travail
- Frustration

### Après (DEV)
- Déconnexion après 8h (fin de journée)
- Pas d'interruption
- Confort optimal

### Après (PROD avec refresh)
- Apparence : "Jamais déconnecté" (refresh transparent)
- Réalité : Token renouvelé toutes les 2h
- Sécurité : Fenêtre d'attaque 2h max
- Inactivité : Déconnexion après 24h

---

**Date** : 28 janvier 2026
**Statut** : ✅ Configuration DEV appliquée, PROD documentée
