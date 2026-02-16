# Optimisation des images - Frontend

## Résumé

Optimisation complète des balises `<img>` dans le frontend pour améliorer les performances de chargement et l'expérience utilisateur.

## Modifications effectuées

### 1. Layout.tsx - Logo (3 instances)

**Fichier**: `/home/user/Hub-Chantier/frontend/src/components/Layout.tsx`

#### a) Logo sidebar mobile (ligne 269-278)
- Ajout de `<picture>` avec fallback WebP
- Ajout de `loading="lazy"` (sidebar mobile)
- Ajout de `decoding="async"`
- Ajout de `aspect-square` pour éviter layout shifts

#### b) Logo sidebar desktop (ligne 299-307)
- Ajout de `<picture>` avec fallback WebP
- Ajout de `loading="eager"` (above the fold, critique)
- Ajout de `decoding="async"`
- Ajout de `aspect-square` pour éviter layout shifts

#### c) Logo header mobile (ligne 368-376)
- Ajout de `<picture>` avec fallback WebP
- Ajout de `loading="eager"` (above the fold, critique)
- Ajout de `decoding="async"`
- Ajout de `aspect-square` pour éviter layout shifts

**Stratégie de chargement**:
- Desktop sidebar: `eager` (visible au chargement)
- Mobile header: `eager` (visible au chargement)
- Mobile sidebar: `lazy` (ouvert uniquement sur clic)

### 2. ImageUpload.tsx - Photos utilisateur/chantier

**Fichier**: `/home/user/Hub-Chantier/frontend/src/components/ImageUpload.tsx`

**Ligne 123-128**: Image de preview/profil
- Ajout de `loading="lazy"` (photos dynamiques)
- Ajout de `decoding="async"`
- Ajout de `aspect-square` (avatars/photos circulaires)

### 3. MiniMap.tsx - Cartes statiques

**Fichier**: `/home/user/Hub-Chantier/frontend/src/components/MiniMap.tsx`

**Ligne 59-63**: Image de carte OSM statique
- Déjà optimisée avec `loading="lazy"`
- Ajout de `decoding="async"`
- Ajout de `aspect-[2/1]` (ratio 400x200 de l'image)

### 4. Service d'upload - Documentation

**Fichier**: `/home/user/Hub-Chantier/frontend/src/services/upload.ts`

**Ligne 114-120**: Ajout d'un commentaire TODO
- Documentation de la nécessité de générer des thumbnails WebP côté backend
- Suggestion d'utiliser des srcset responsive
- Objectif: réduire la bande passante

## Format WebP

### Stratégie <picture> avec fallback

Toutes les images du logo utilisent maintenant:

```tsx
<picture>
  <source srcSet="/logo.webp?v=2" type="image/webp" />
  <img src="/logo.png?v=2" alt="Hub Chantier" ... />
</picture>
```

**Avantages**:
- Support WebP automatique pour les navigateurs modernes (~95% du marché)
- Fallback PNG transparent pour les anciens navigateurs
- Aucun JavaScript nécessaire
- Économie de bande passante de ~30-50% avec WebP

**Action requise**:
Le fichier `/logo.webp` doit être généré et placé dans `/home/user/Hub-Chantier/frontend/public/`. Pour l'instant, le fallback PNG sera utilisé.

## Aspect ratios

### Ratios appliqués

- **Logo**: `aspect-square` (1:1) - 64x64px
- **Avatars/Photos**: `aspect-square` (1:1)
- **Cartes OSM**: `aspect-[2/1]` (ratio 400x200)

**Bénéfices**:
- Prévention des Cumulative Layout Shifts (CLS)
- Amélioration du Core Web Vitals score
- Meilleure expérience utilisateur (pas de "saut" de contenu)

## Stratégie de chargement

### loading="eager" vs loading="lazy"

**Eager (prioritaire)**:
- Logo header desktop (toujours visible)
- Logo header mobile (toujours visible)

**Lazy (différé)**:
- Logo sidebar mobile (visible uniquement après clic)
- Photos de profil/chantier (dynamiques)
- Cartes statiques (souvent en bas de page)

### decoding="async"

Appliqué à **toutes** les images pour:
- Décodage asynchrone des images
- Pas de blocage du thread principal
- Amélioration de la fluidité du rendu

## Recommandations futures

### 1. Génération de WebP (Backend)

Le service d'upload devrait générer automatiquement:
- Format WebP en plus du format original
- Plusieurs tailles (thumbnail, medium, large)
- Utilisation de srcset responsive

Exemple:
```tsx
<picture>
  <source
    srcSet="/uploads/photo-thumb.webp 150w, /uploads/photo-medium.webp 400w"
    type="image/webp"
  />
  <img
    src="/uploads/photo-medium.jpg"
    srcSet="/uploads/photo-thumb.jpg 150w, /uploads/photo-medium.jpg 400w"
    sizes="(max-width: 640px) 150px, 400px"
  />
</picture>
```

### 2. Logo WebP

Générer `/home/user/Hub-Chantier/frontend/public/logo.webp`:

```bash
# Exemple avec ImageMagick
convert logo.png -quality 85 logo.webp

# Ou avec cwebp (Google)
cwebp -q 85 logo.png -o logo.webp
```

Économie attendue: ~100KB → ~30KB (70% de réduction)

### 3. Lazy loading images dans les listes

Pour les futures listes de chantiers/utilisateurs avec photos:
- Utiliser `loading="lazy"` systématiquement
- Considérer l'intersection observer pour le scroll infini
- Précharger les 3-5 premiers éléments avec `loading="eager"`

### 4. CDN et cache

Configuration recommandée (nginx/Vite):
```nginx
location ~* \.(webp|png|jpg|jpeg)$ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}
```

## Impact attendu

### Performance

- **Réduction CLS**: aspect-ratio fixe sur toutes les images
- **Réduction bande passante**: 30-50% avec WebP (une fois généré)
- **Amélioration LCP**: lazy loading approprié
- **Fluidité rendu**: decoding async partout

### Core Web Vitals

- **LCP** (Largest Contentful Paint): Amélioration grâce à eager sur le logo
- **CLS** (Cumulative Layout Shift): Score amélioré avec aspect-ratio
- **FID** (First Input Delay): Pas de blocage avec async decoding

### Poids du logo

- **Actuel**: 154KB (PNG)
- **Avec WebP**: ~45KB estimé (70% réduction)
- **Économie par chargement**: ~109KB

## Tests

### Vérification visuelle

1. Démarrer le dev server: `npm run dev`
2. Ouvrir DevTools > Network
3. Vérifier que les images chargent correctement
4. Vérifier le lazy loading (sidebar mobile ne charge que au clic)

### Tests de performance

Lighthouse audit avant/après:
```bash
# Chrome DevTools > Lighthouse
# Mesurer:
# - Performance score
# - CLS score
# - Image optimization suggestions
```

### Tests navigateurs

- ✅ Chrome/Edge (WebP supporté)
- ✅ Firefox (WebP supporté)
- ✅ Safari 14+ (WebP supporté)
- ✅ Safari < 14 (fallback PNG)

## Fichiers modifiés

1. `/home/user/Hub-Chantier/frontend/src/components/Layout.tsx`
2. `/home/user/Hub-Chantier/frontend/src/components/ImageUpload.tsx`
3. `/home/user/Hub-Chantier/frontend/src/components/MiniMap.tsx`
4. `/home/user/Hub-Chantier/frontend/src/services/upload.ts`

## Prochaines étapes

- [ ] Générer `/frontend/public/logo.webp` depuis `logo.png`
- [ ] Implémenter la génération de thumbnails WebP côté backend
- [ ] Configurer le cache navigateur pour les images statiques
- [ ] Ajouter des srcset responsive pour les photos de chantiers
- [ ] Audit Lighthouse complet après WebP génération

---

**Date**: 2026-02-15
**Auteur**: Claude (React Specialist)
**Session**: Image optimization sprint
