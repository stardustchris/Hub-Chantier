# Stratégies de Caching PWA - Hub Chantier

## Vue d'ensemble

Ce document décrit les stratégies de caching PWA implémentées dans Hub Chantier pour optimiser les performances offline et réduire la latence.

## Architecture de caching

Les stratégies sont implémentées via `vite-plugin-pwa` (Workbox) dans `/home/user/Hub-Chantier/frontend/vite.config.ts`.

### Ordre de priorité des règles

Les règles `runtimeCaching` sont évaluées dans l'ordre (premier match gagne) :

1. **NetworkOnly** - Endpoints sensibles (sécurité)
2. **CacheFirst** - Assets immuables (uploads, documents)
3. **StaleWhileRevalidate** - Données temps réel (planning, dashboard)
4. **NetworkFirst** - Autres API (fallback cache)

## Stratégies détaillées

### 1. NetworkOnly - Endpoints sensibles

```javascript
urlPattern: /\/api\/(auth|pointages|users|feuilles-heures)\/.*/i
handler: 'NetworkOnly'
```

**Endpoints concernés:**
- `/api/auth/*` - Authentication
- `/api/pointages/*` - Pointages (données temps réel critiques)
- `/api/users/*` - Gestion utilisateurs
- `/api/feuilles-heures/*` - Feuilles d'heures

**Raison:** Sécurité et données sensibles/critiques jamais en cache.

### 2. CacheFirst - Assets immuables (P.1)

#### Uploads (Photos, Images)

```javascript
urlPattern: /\/api\/uploads\/.*/i
handler: 'CacheFirst'
cacheName: 'uploads-cache'
maxEntries: 200
maxAgeSeconds: 30 * 24 * 60 * 60 // 30 jours
```

**Endpoints concernés:**
- `/api/uploads/profile` - Photos de profil (USR-02)
- `/api/uploads/posts/{id}` - Médias posts (FEED-02)
- `/api/uploads/chantiers/{id}` - Photos chantiers (CHT-01)

**Bénéfices:**
- Chargement instantané des images déjà vues
- Réduction de 90% de la bande passante sur les images récurrentes
- Mode offline fonctionnel pour les images cachées

#### Documents GED

```javascript
urlPattern: /\/api\/documents\/.*/i
handler: 'CacheFirst'
cacheName: 'documents-cache'
maxEntries: 100
maxAgeSeconds: 30 * 24 * 60 * 60 // 30 jours
```

**Endpoints concernés:**
- `/api/documents/documents/{id}` - Documents
- `/api/documents/documents/{id}/download` - Téléchargements
- `/api/documents/documents/{id}/preview` - Prévisualisations (GED-17)

**Bénéfices:**
- Documents accessibles offline
- Prévisualisation instantanée des documents déjà consultés
- Réduction charge serveur pour documents volumineux

### 3. StaleWhileRevalidate - Données temps réel (P.2)

```javascript
urlPattern: /\/api\/(planning|dashboard)\/.*/i
handler: 'StaleWhileRevalidate'
cacheName: 'api-realtime-cache'
maxEntries: 50
maxAgeSeconds: 5 * 60 // 5 minutes
```

**Endpoints concernés:**

**Planning:**
- `/api/planning/affectations` - Liste affectations (PLN-01)
- `/api/planning/chantiers/{id}/affectations` - Planning chantier
- `/api/planning/utilisateurs/{id}/affectations` - Planning utilisateur
- `/api/planning/non-planifies` - Non planifiés

**Dashboard:**
- `/api/dashboard/feed` - Fil d'actualité (FEED-01)
- `/api/dashboard/posts` - Posts (FEED-02)
- `/api/dashboard/posts/{id}/comments` - Commentaires (FEED-04)
- `/api/dashboard/posts/{id}/like` - Likes (FEED-05)

**Comportement:**
1. Renvoie immédiatement le cache si disponible
2. Rafraîchit en arrière-plan depuis le réseau
3. Met à jour le cache pour la prochaine requête

**Bénéfices:**
- Affichage instantané (cache)
- Données toujours à jour (revalidation background)
- Expérience utilisateur fluide même avec réseau lent
- Cache court (5min) pour éviter données obsolètes

### 4. NetworkFirst avec timeout - Fallback (P.3)

```javascript
urlPattern: /\/api\/.*/i
handler: 'NetworkFirst'
networkTimeoutSeconds: 3
cacheName: 'api-cache'
maxEntries: 100
maxAgeSeconds: 24 * 60 * 60 // 24 heures
```

**Endpoints concernés:** Tous les autres endpoints API non couverts ci-dessus.

**Comportement:**
1. Tente d'abord le réseau (max 3s)
2. Si timeout ou échec → fallback sur cache
3. Cache la réponse réseau pour 24h

**Bénéfices:**
- Résistance aux connexions lentes (timeout 3s)
- Mode dégradé offline sur données cachées
- Toujours la donnée la plus fraîche si réseau OK

## Tableau récapitulatif

| Pattern | Endpoints | Stratégie | Cache | Expiration | Use Case |
|---------|-----------|-----------|-------|------------|----------|
| NetworkOnly | auth, pointages, users, feuilles-heures | Réseau seul | ❌ | N/A | Sécurité/données critiques |
| CacheFirst | uploads, documents | Cache d'abord | ✅ | 30 jours | Assets immuables |
| StaleWhileRevalidate | planning, dashboard | Cache + revalidation | ✅ | 5 min | Données temps réel |
| NetworkFirst | Autres API | Réseau + fallback | ✅ | 24h | API génériques |

## Impact performance

### Métriques attendues

**Temps de chargement:**
- Images cachées: ~50ms (vs ~500ms réseau)
- Documents cachés: ~100ms (vs ~1-2s réseau)
- Planning/dashboard: affichage instantané (<100ms) avec rafraîchissement background

**Bande passante:**
- Réduction ~60-70% sur uploads récurrents
- Réduction ~40-50% sur documents consultés
- Réduction ~30% sur API planning/dashboard (cache 5min)

**Offline:**
- Images/documents cachés: 100% disponibles
- Planning/dashboard: affichage dernière version (max 5min périmée)
- Autres API: fallback cache 24h

## Tests de validation

### Test manuel

1. **CacheFirst (uploads):**
```bash
# 1. Charger une page avec images
# 2. DevTools > Application > Cache Storage > uploads-cache
# 3. Vérifier présence des images
# 4. Activer mode offline (DevTools > Network > Offline)
# 5. Recharger page → images doivent s'afficher
```

2. **StaleWhileRevalidate (planning):**
```bash
# 1. Ouvrir /planning
# 2. DevTools > Network > Slow 3G
# 3. Recharger → affichage instantané (cache)
# 4. Observer requête background de revalidation
```

3. **NetworkFirst timeout (autres API):**
```bash
# 1. DevTools > Network > Slow 3G
# 2. Charger une page API non cachée
# 3. Après 3s timeout → fallback cache
# 4. Vérifier message console Workbox
```

### Test automatisé (TODO)

```javascript
// tests/e2e/pwa-caching.spec.ts
describe('PWA Caching Strategies', () => {
  it('should cache uploads with CacheFirst', async () => {
    // Implémenter test Playwright
  })

  it('should use StaleWhileRevalidate for planning', async () => {
    // Implémenter test Playwright
  })

  it('should fallback to cache after 3s timeout', async () => {
    // Implémenter test Playwright
  })
})
```

## Maintenance

### Vider les caches

**Utilisateur:**
- DevTools > Application > Clear storage > Clear site data

**Administrateur (forcer tous les utilisateurs):**
- Modifier `CACHE_VERSION` dans `vite.config.ts` → rebuild
- Les anciens caches sont automatiquement supprimés

### Monitoring

**Métriques à surveiller:**
- Hit rate cache par stratégie (uploads, documents, planning)
- Taille totale caches (limit ~50MB recommandé)
- Temps moyen de revalidation (StaleWhileRevalidate)
- Fréquence timeouts réseau (NetworkFirst)

**Outils:**
- Chrome DevTools > Application > Cache Storage
- Workbox logging (console)
- Service Worker lifecycle events

## Dépendances

```json
{
  "vite-plugin-pwa": "^0.17.0",
  "workbox-window": "^7.0.0"
}
```

## Références

- [Workbox Strategies](https://developer.chrome.com/docs/workbox/modules/workbox-strategies/)
- [vite-plugin-pwa](https://vite-pwa-org.netlify.app/)
- [PWA Best Practices](https://web.dev/progressive-web-apps/)

## Changelog

### 2026-02-15 - Implémentation initiale

- ✅ P.1: CacheFirst pour uploads et documents (30j)
- ✅ P.2: StaleWhileRevalidate pour planning/dashboard (5min)
- ✅ P.3: NetworkFirst avec timeout 3s + fallback cache (24h)
- ✅ NetworkOnly maintenu pour endpoints sensibles

**Fichier modifié:** `/home/user/Hub-Chantier/frontend/vite.config.ts`
