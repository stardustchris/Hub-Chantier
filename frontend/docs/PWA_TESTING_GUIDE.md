# Guide de Test - PWA Caching Strategies

## Prérequis

- Application déployée et accessible
- Chrome DevTools (ou Firefox Developer Tools)
- Connexion réseau contrôlable

## 1. Vérification initiale

### 1.1 Vérifier que le Service Worker est actif

```bash
# Ouvrir l'application dans Chrome
# DevTools (F12) > Application > Service Workers
# Statut doit être "activated and is running"
```

### 1.2 Vérifier les caches créés

```bash
# DevTools > Application > Cache Storage
# Vous devriez voir:
# - workbox-precache-v2-... (assets statiques)
# - uploads-cache (vide au début)
# - documents-cache (vide au début)
# - api-realtime-cache (vide au début)
# - api-cache (vide au début)
```

## 2. Test P.1 - CacheFirst (Uploads)

### 2.1 Charger des images

```bash
# 1. Se connecter à l'application
# 2. Naviguer vers Dashboard (posts avec images)
# 3. DevTools > Network > Img filter
# 4. Observer les requêtes vers /api/uploads/*
```

### 2.2 Vérifier le cache

```bash
# DevTools > Application > Cache Storage > uploads-cache
# Vous devriez voir les URLs des images chargées
# Format: http://localhost/api/uploads/posts/123/image.jpg
```

### 2.3 Test offline

```bash
# 1. DevTools > Network > Offline (checkbox)
# 2. Recharger la page (Ctrl+R)
# 3. Les images doivent s'afficher instantanément depuis le cache
# 4. DevTools > Network > Img filter → (from ServiceWorker)
```

**Résultat attendu:**
- ✅ Images chargées en <100ms
- ✅ Onglet Network affiche "(from ServiceWorker)"
- ✅ Pas d'erreur console

### 2.4 Performance comparée

```bash
# Test 1: Premier chargement (réseau)
# 1. Vider cache: DevTools > Application > Clear storage
# 2. Recharger page
# 3. Network > Img > Noter temps de chargement (ex: 450ms)

# Test 2: Deuxième chargement (cache)
# 1. Recharger page
# 2. Network > Img > Noter temps de chargement (ex: 35ms)

# Gain attendu: ~90% réduction temps
```

## 3. Test P.1 - CacheFirst (Documents)

### 3.1 Charger des documents

```bash
# 1. Naviguer vers Documents GED
# 2. Sélectionner un chantier
# 3. Prévisualiser un document PDF
# 4. DevTools > Network > XHR filter
# 5. Observer /api/documents/documents/*/preview
```

### 3.2 Vérifier le cache

```bash
# DevTools > Application > Cache Storage > documents-cache
# Vous devriez voir:
# - /api/documents/documents/42
# - /api/documents/documents/42/preview
```

### 3.3 Test offline prévisualisation

```bash
# 1. DevTools > Network > Offline
# 2. Cliquer sur un document déjà prévisualisé
# 3. La prévisualisation doit s'afficher
```

**Résultat attendu:**
- ✅ Prévisualisation instantanée (<200ms)
- ✅ Pas de requête réseau
- ✅ Aucune erreur

## 4. Test P.2 - StaleWhileRevalidate (Planning)

### 4.1 Charger le planning

```bash
# 1. Naviguer vers /planning
# 2. DevTools > Network > XHR filter
# 3. Observer /api/planning/affectations
# 4. Noter le temps de réponse (ex: 320ms)
```

### 4.2 Vérifier le cache

```bash
# DevTools > Application > Cache Storage > api-realtime-cache
# Vous devriez voir:
# - /api/planning/affectations?date_debut=...&date_fin=...
```

### 4.3 Test StaleWhileRevalidate

```bash
# 1. Recharger la page /planning
# 2. DevTools > Network > XHR
# 3. Observer DEUX requêtes:
#    a) Réponse instantanée du cache (<50ms) - affichage immédiat
#    b) Requête background vers serveur (revalidation)
# 4. Console devrait afficher logs Workbox
```

**Résultat attendu:**
- ✅ Planning affiché instantanément (cache)
- ✅ Requête background visible dans Network
- ✅ Cache mis à jour après revalidation

### 4.4 Test expiration 5 minutes

```bash
# 1. Charger planning
# 2. Attendre 6 minutes
# 3. Recharger → cache expiré, nouvelle requête réseau
# 4. Vérifier Network: requête normale (pas de cache)
```

## 5. Test P.2 - StaleWhileRevalidate (Dashboard)

### 5.1 Charger le feed

```bash
# 1. Naviguer vers / (Dashboard)
# 2. DevTools > Network > XHR
# 3. Observer /api/dashboard/feed
```

### 5.2 Test avec réseau lent

```bash
# 1. DevTools > Network > Slow 3G
# 2. Recharger la page
# 3. Le feed doit s'afficher instantanément (cache)
# 4. En arrière-plan, revalidation depuis réseau lent
```

**Résultat attendu:**
- ✅ Feed affiché <100ms
- ✅ UX fluide malgré réseau lent
- ✅ Données rafraîchies après revalidation

## 6. Test P.3 - NetworkFirst timeout

### 6.1 Simuler réseau lent

```bash
# 1. DevTools > Network > Slow 3G (ou Custom: 100ms delay, 50kb/s)
# 2. Naviguer vers page utilisant API non critique (ex: /chantiers)
# 3. Observer requête API dans Network
```

### 6.2 Test timeout 3s

```bash
# 1. Network > Custom throttling: 
#    - Download: 10 kb/s
#    - Upload: 10 kb/s
#    - Latency: 4000ms (>3s timeout)
# 2. Recharger page
# 3. Après 3s, fallback sur cache
```

**Résultat attendu:**
- ✅ Timeout après 3s
- ✅ Fallback sur cache (si disponible)
- ✅ Console Workbox: "Network timeout, falling back to cache"

### 6.3 Test mode offline

```bash
# 1. Charger page (cache l'API)
# 2. Network > Offline
# 3. Recharger → fallback cache instantané
```

**Résultat attendu:**
- ✅ Page affichée avec données cachées (max 24h old)
- ✅ Pas d'erreur réseau visible à l'utilisateur

## 7. Test Sécurité - NetworkOnly

### 7.1 Vérifier endpoints sensibles

```bash
# 1. Se connecter (POST /api/auth/login)
# 2. DevTools > Network > XHR > /api/auth/login
# 3. Vérifier qu'il n'y a PAS de cache
```

### 7.2 Vérifier les autres endpoints NetworkOnly

```bash
# Endpoints à tester:
# - /api/pointages/* → jamais en cache
# - /api/users/* → jamais en cache
# - /api/feuilles-heures/* → jamais en cache

# Vérification:
# DevTools > Application > Cache Storage
# Aucun de ces endpoints ne doit apparaître dans les caches
```

**Résultat attendu:**
- ✅ Aucun endpoint auth/pointages/users/feuilles-heures dans les caches
- ✅ Toujours requête réseau
- ✅ Mode offline → erreur réseau (pas de fallback)

## 8. Monitoring et Métriques

### 8.1 Logs Workbox

```javascript
// Console > Filter: "workbox"
// Vous devriez voir:
// - "Using CacheFirst for /api/uploads/..."
// - "Using StaleWhileRevalidate for /api/planning/..."
// - "Network timeout, falling back to cache"
```

### 8.2 Métriques cache

```javascript
// Console > Execute:
caches.keys().then(names => console.log(names))

caches.open('uploads-cache').then(cache => {
  cache.keys().then(keys => console.log('Uploads cache entries:', keys.length))
})

caches.open('documents-cache').then(cache => {
  cache.keys().then(keys => console.log('Documents cache entries:', keys.length))
})

caches.open('api-realtime-cache').then(cache => {
  cache.keys().then(keys => console.log('Realtime cache entries:', keys.length))
})
```

### 8.3 Taille totale des caches

```javascript
// Console:
navigator.storage.estimate().then(estimate => {
  console.log('Storage used:', (estimate.usage / 1024 / 1024).toFixed(2), 'MB')
  console.log('Storage quota:', (estimate.quota / 1024 / 1024).toFixed(2), 'MB')
  console.log('Usage %:', ((estimate.usage / estimate.quota) * 100).toFixed(2), '%')
})

// Recommandation: garder < 50MB total
```

## 9. Nettoyage et Reset

### 9.1 Vider un cache spécifique

```javascript
// Console:
caches.delete('uploads-cache')
caches.delete('documents-cache')
caches.delete('api-realtime-cache')
caches.delete('api-cache')
```

### 9.2 Reset complet

```bash
# DevTools > Application > Clear storage
# Cocher:
# - [x] Cache storage
# - [x] Service workers
# - [x] Unregister service workers
# Cliquer "Clear site data"
```

## 10. Tests automatisés (Playwright)

### 10.1 Installation

```bash
cd /home/user/Hub-Chantier/frontend
npm install -D @playwright/test
npx playwright install
```

### 10.2 Exemple test CacheFirst

```typescript
// tests/e2e/pwa-cache-uploads.spec.ts
import { test, expect } from '@playwright/test'

test.describe('PWA Cache - Uploads (CacheFirst)', () => {
  test('should cache uploaded images', async ({ page, context }) => {
    // Enable service worker
    await context.route('**/*', async (route) => {
      await route.continue()
    })

    // Load page with images
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // Check cache storage
    const cacheKeys = await page.evaluate(async () => {
      const cache = await caches.open('uploads-cache')
      const keys = await cache.keys()
      return keys.map(k => k.url)
    })

    expect(cacheKeys.some(url => url.includes('/api/uploads/'))).toBeTruthy()

    // Test offline mode
    await context.setOffline(true)
    await page.reload()

    // Images should still load from cache
    const images = page.locator('img[src*="/api/uploads/"]')
    await expect(images.first()).toBeVisible()
  })
})
```

### 10.3 Exemple test StaleWhileRevalidate

```typescript
// tests/e2e/pwa-cache-planning.spec.ts
import { test, expect } from '@playwright/test'

test.describe('PWA Cache - Planning (StaleWhileRevalidate)', () => {
  test('should show cached planning instantly and revalidate', async ({ page }) => {
    // First load
    await page.goto('/planning')
    await page.waitForResponse(response => 
      response.url().includes('/api/planning/affectations') && response.status() === 200
    )

    // Second load should use cache + revalidate
    const responsePromise = page.waitForResponse(response => 
      response.url().includes('/api/planning/affectations')
    )

    await page.reload()
    
    // Planning should be visible immediately (from cache)
    await expect(page.locator('[data-testid="planning-grid"]')).toBeVisible({ timeout: 500 })

    // Background revalidation should happen
    const response = await responsePromise
    expect(response.fromServiceWorker()).toBeTruthy()
  })
})
```

### 10.4 Exécuter les tests

```bash
npx playwright test tests/e2e/pwa-*.spec.ts
npx playwright test --headed # Mode visuel
npx playwright test --debug # Mode debug
```

## 11. Checklist validation complète

- [ ] Service Worker activé (DevTools > Application)
- [ ] 4 caches créés (uploads, documents, api-realtime, api)
- [ ] Images chargées en <100ms (cache)
- [ ] Documents accessibles offline
- [ ] Planning affichage instantané + revalidation
- [ ] Dashboard feed fluide avec Slow 3G
- [ ] Timeout 3s fonctionne (fallback cache)
- [ ] Endpoints sensibles jamais en cache
- [ ] Storage usage < 50MB
- [ ] Aucune erreur console
- [ ] Tests Playwright passent

## Troubleshooting

### Problème: Service Worker ne s'active pas

```bash
# Solution 1: Hard refresh
Ctrl+Shift+R (ou Cmd+Shift+R sur Mac)

# Solution 2: Unregister manually
DevTools > Application > Service Workers > Unregister
Puis recharger la page

# Solution 3: Vider tous les caches
DevTools > Application > Clear storage > Clear site data
```

### Problème: Cache non utilisé (toujours requête réseau)

```bash
# Vérifier:
1. DevTools > Network > Disable cache (doit être décoché)
2. Console > Filtrer "workbox" → vérifier les logs
3. Application > Cache Storage → vérifier contenu
4. Vérifier urlPattern dans vite.config.ts (regex correcte?)
```

### Problème: Données obsolètes affichées

```bash
# Normal pour StaleWhileRevalidate (affiche cache puis revalide)
# Si problème persiste:
1. Vérifier expiration dans vite.config.ts
2. Forcer refresh: vider cache
3. Vérifier que revalidation background fonctionne (Network tab)
```

### Problème: Storage quota dépassé

```bash
# Console:
navigator.storage.estimate().then(e => console.log(e))

# Si usage > 80% quota:
caches.keys().then(names => {
  names.forEach(name => caches.delete(name))
})

# Ajuster maxEntries dans vite.config.ts
```

## Références

- [Chrome DevTools - Service Workers](https://developer.chrome.com/docs/devtools/progressive-web-apps/)
- [Workbox Debugging](https://developer.chrome.com/docs/workbox/troubleshooting-and-logging/)
- [Playwright Testing](https://playwright.dev/docs/test-pwa)
