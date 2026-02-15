# TODO - Finalisation Optimisations Performance

## Installation Requise

### rollup-plugin-visualizer (2.2.4)

```bash
cd /home/user/Hub-Chantier/frontend
npm install -D rollup-plugin-visualizer
```

Puis décommenter dans `vite.config.ts`:
- Ligne 5: `import { visualizer } from 'rollup-plugin-visualizer'`
- Lignes 10-20: Configuration du plugin visualizer

## Tests à Effectuer

### 1. Vérifier le Build
```bash
cd /home/user/Hub-Chantier/frontend
npm run build
```

### 2. Tester les Composants Lazy en Dev
```bash
npm run dev
```

Naviguer vers:
- `/devis/dashboard` - Vérifier ConversionFunnelChart lazy
- `/finances` - Vérifier StatutPieChart, BudgetBarChart, MargesBarChart lazy

Observer dans DevTools:
- Network tab: chunks recharts chargés uniquement sur les pages avec graphiques
- Performance tab: amélioration du FCP

### 3. Analyser le Bundle
```bash
ANALYZE=true npm run build
```

Vérifier:
- Taille du chunk vendor-charts (Recharts)
- Taille des chunks lazy pour chaque graphique
- Gains par rapport à avant

### 4. Tester la Persistence localStorage

1. Ouvrir l'application
2. Naviguer vers plusieurs pages (chantiers, finances, devis)
3. Vérifier localStorage dans DevTools:
   - Clé: `hub-chantier-query-cache`
   - Contenu: queries sérialisées avec timestamp
4. Recharger la page (F5)
5. Vérifier dans Network tab: pas de requêtes API si cache valide
6. Attendre 30 minutes et recharger: requêtes API normales

### 5. Mesurer les Core Web Vitals

**Avant optimisations** (baseline):
```bash
# Lighthouse en mode incognito
npm run build && npm run preview
# Ouvrir Chrome DevTools > Lighthouse
# Sélectionner "Performance" et "Desktop"
# Lancer l'audit
```

Noter les métriques:
- FCP (First Contentful Paint)
- LCP (Largest Contentful Paint)
- TTI (Time to Interactive)
- TBT (Total Blocking Time)
- Bundle size

**Après optimisations** (comparer):
- Refaire l'audit Lighthouse
- Comparer les métriques
- Vérifier l'amélioration attendue: +15-20% performance

## Composants Lazy Non Utilisés

Les wrappers suivants ont été créés mais ne sont pas encore utilisés. À intégrer si nécessaire:

1. **RentabiliteSidebarLazy.tsx**
   - À utiliser dans `/pages/DevisGeneratorPage.tsx` ou similaire
   - Remplacer `import RentabiliteSidebar from './RentabiliteSidebar'`
   - Par `import RentabiliteSidebarLazy from './RentabiliteSidebarLazy'`

2. **EvolutionChartLazy.tsx**
   - À utiliser dans les pages affichant EvolutionChart
   - Chercher avec: `grep -r "import.*EvolutionChart" src/pages/`

3. **BarresComparativesLotsLazy.tsx**
   - À utiliser dans les pages affichant BarresComparativesLots
   - Chercher avec: `grep -r "import.*BarresComparativesLots" src/pages/`

4. **CamembertLotsLazy.tsx**
   - À utiliser dans les pages affichant CamembertLots
   - Chercher avec: `grep -r "import.*CamembertLots" src/pages/`

## Optimisations Futures Recommandées

### Lazy-loading Supplémentaire

1. **Modals complexes**
   - DevisGeneratorModal
   - MargesAdjustModal
   - Autres modals avec beaucoup de code

2. **Pages rarement visitées**
   - SecuritySettingsPage (déjà lazy)
   - WebhooksPage (déjà lazy)
   - APIKeysPage (déjà lazy)

3. **Bibliothèques lourdes**
   - firebase (lazy-loader uniquement si authentication utilisée)
   - date-fns (lazy-loader uniquement les fonctions nécessaires)

### Compression localStorage

Si le quota localStorage devient un problème:

```bash
npm install lz-string
```

Puis modifier `lib/queryClient.ts`:
```typescript
import LZString from 'lz-string'

// Dans persistQueryCache():
localStorage.setItem(
  CACHE_KEY,
  LZString.compress(JSON.stringify({ timestamp, queries }))
)

// Dans restoreQueryCache():
const cached = LZString.decompress(localStorage.getItem(CACHE_KEY) || '')
```

### Image Lazy-loading

Ajouter lazy-loading pour les images:
```typescript
<img loading="lazy" src="..." alt="..." />
```

### Service Worker Cache

Améliorer le cache Service Worker PWA pour les assets statiques.

## Monitoring à Mettre en Place

### 1. Bundle Size Monitoring

Ajouter dans `package.json`:
```json
{
  "scripts": {
    "analyze:size": "npm run build && du -sh dist/* | sort -h"
  }
}
```

### 2. localStorage Usage

Créer un hook `useLocalStorageQuota`:
```typescript
export function useLocalStorageQuota() {
  const [usage, setUsage] = useState(0)

  useEffect(() => {
    const estimate = async () => {
      if ('storage' in navigator && 'estimate' in navigator.storage) {
        const { usage, quota } = await navigator.storage.estimate()
        setUsage((usage / quota) * 100)
      }
    }
    estimate()
  }, [])

  return usage
}
```

### 3. Performance Metrics

Intégrer Web Vitals:
```bash
npm install web-vitals
```

```typescript
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

getCLS(console.log)
getFID(console.log)
getFCP(console.log)
getLCP(console.log)
getTTFB(console.log)
```

## Checklist Finale

- [ ] Installer rollup-plugin-visualizer
- [ ] Décommenter la configuration dans vite.config.ts
- [ ] Tester le build: `npm run build`
- [ ] Tester en dev: `npm run dev`
- [ ] Vérifier les composants lazy chargent correctement
- [ ] Analyser le bundle: `ANALYZE=true npm run build`
- [ ] Tester la persistence localStorage
- [ ] Mesurer les Core Web Vitals avec Lighthouse
- [ ] Comparer avant/après performance
- [ ] Documenter les gains réels
- [ ] Monitorer le quota localStorage
- [ ] Intégrer les composants lazy non utilisés (optionnel)
- [ ] Considérer les optimisations futures

## Support

En cas de problème:
1. Vérifier les erreurs de build: `npm run build`
2. Vérifier les erreurs de lint: `npm run lint`
3. Vérifier les logs de console dans le navigateur
4. Vérifier le Network tab pour les chunks lazy
5. Consulter la documentation: `PERFORMANCE_OPTIMIZATIONS.md`
