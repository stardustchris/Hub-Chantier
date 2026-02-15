# Optimisation des images - Guide rapide

## Modifications effectuées

### ✅ Optimisations appliquées

Toutes les balises `<img>` du frontend ont été optimisées:

1. **Attributs de performance**
   - `loading="lazy"` ou `loading="eager"` selon la position
   - `decoding="async"` sur toutes les images
   - `aspect-ratio` CSS pour éviter les layout shifts

2. **Support WebP avec fallback PNG**
   - Utilisation de `<picture>` pour le logo
   - Fallback automatique vers PNG
   - Réduction attendue: ~70% de la bande passante

3. **Stratégie de chargement intelligente**
   - Logo header (visible): `loading="eager"`
   - Logo sidebar mobile: `loading="lazy"` (chargé au clic)
   - Photos/avatars: `loading="lazy"`
   - Cartes: `loading="lazy"`

### 📊 Impact attendu

- **CLS**: Réduction grâce à `aspect-ratio`
- **LCP**: Amélioration avec lazy loading approprié
- **Bande passante**: -70% avec WebP (une fois généré)
- **Logo actuel**: 154KB → ~45KB estimé

## 🚀 Génération du logo WebP

### Étape 1: Installer un convertisseur

**Ubuntu/Debian:**
```bash
sudo apt-get install webp
```

**macOS:**
```bash
brew install webp
```

### Étape 2: Exécuter le script

```bash
cd frontend
./scripts/generate-webp.sh
```

Le script convertira automatiquement:
- `/public/logo.png` → `/public/logo.webp`
- `/public/pwa-*.png` → `/public/pwa-*.webp`
- `/public/apple-touch-icon.png` → `/public/apple-touch-icon.webp`

### Étape 3: Tester

1. Démarrer le serveur:
   ```bash
   npm run dev
   ```

2. Vider le cache navigateur: `Ctrl+Shift+R`

3. Ouvrir DevTools > Network et vérifier que `logo.webp` est chargé

## 📁 Fichiers modifiés

```
frontend/src/
├── components/
│   ├── Layout.tsx              # 3 logos optimisés (mobile sidebar, desktop sidebar, mobile header)
│   ├── ImageUpload.tsx         # Photos de profil/chantier optimisées
│   └── MiniMap.tsx             # Cartes statiques optimisées
├── services/
│   └── upload.ts               # Documentation ajoutée pour thumbnails backend
└── scripts/
    └── generate-webp.sh        # Script de génération WebP (nouveau)
```

## 🔍 Détails des modifications

### Layout.tsx - 3 instances du logo

**Avant:**
```tsx
<img src="/logo.png?v=2" alt="Hub Chantier" className="w-16 h-16 object-contain" />
```

**Après:**
```tsx
<picture>
  <source srcSet="/logo.webp?v=2" type="image/webp" />
  <img
    src="/logo.png?v=2"
    alt="Hub Chantier"
    className="w-16 h-16 object-contain aspect-square"
    loading="eager"  # ou "lazy" pour sidebar mobile
    decoding="async"
  />
</picture>
```

### ImageUpload.tsx - Photos utilisateur

**Avant:**
```tsx
<img src={displayImage} alt="Photo" className="w-full h-full object-cover" />
```

**Après:**
```tsx
<img
  src={displayImage}
  alt="Photo"
  className="w-full h-full object-cover aspect-square"
  loading="lazy"
  decoding="async"
/>
```

### MiniMap.tsx - Cartes statiques

**Avant:**
```tsx
<img
  src={staticUrl}
  alt={locationName}
  className="w-full h-full object-cover"
  loading="lazy"
/>
```

**Après:**
```tsx
<img
  src={staticUrl}
  alt={locationName}
  className="w-full h-full object-cover aspect-[2/1]"
  loading="lazy"
  decoding="async"
/>
```

## 🎯 Prochaines étapes recommandées

### Court terme

- [ ] Générer le logo WebP avec le script fourni
- [ ] Vérifier visuellement dans tous les navigateurs
- [ ] Audit Lighthouse pour mesurer l'amélioration

### Moyen terme

- [ ] Implémenter la génération de thumbnails WebP côté backend
- [ ] Ajouter des srcset responsive pour les photos de chantiers
- [ ] Configurer le cache HTTP pour les images statiques

### Long terme

- [ ] Migrer vers un CDN pour les images
- [ ] Implémenter le lazy loading pour les listes longues
- [ ] Considérer AVIF pour les navigateurs modernes (Chrome 85+)

## 📚 Ressources

- [WebP sur MDN](https://developer.mozilla.org/en-US/docs/Web/Media/Formats/Image_types#webp)
- [Lazy loading sur web.dev](https://web.dev/browser-level-image-lazy-loading/)
- [Aspect ratio sur CSS-Tricks](https://css-tricks.com/aspect-ratio-boxes/)
- [Core Web Vitals](https://web.dev/vitals/)

## ❓ Questions fréquentes

**Q: Pourquoi certains logos sont en `loading="eager"` et d'autres en `lazy`?**
R: Les logos visibles au chargement (header) doivent être en `eager` pour un affichage immédiat. Le logo de la sidebar mobile est en `lazy` car il n'est visible qu'après un clic.

**Q: Que se passe-t-il si le navigateur ne supporte pas WebP?**
R: Le navigateur utilisera automatiquement le fallback PNG grâce à la balise `<picture>`.

**Q: Pourquoi `aspect-ratio`?**
R: Pour éviter les Cumulative Layout Shifts (CLS) - le navigateur réserve l'espace avant le chargement de l'image.

**Q: Le script de génération WebP est-il obligatoire?**
R: Non, le code fonctionne déjà avec le PNG. Le WebP apporte juste une optimisation supplémentaire (~70% de réduction).

---

**Date**: 2026-02-15
**Auteur**: Claude (React Specialist)
