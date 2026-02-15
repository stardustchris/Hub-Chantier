# Optimisations Performance Frontend - Phase 2

Ce document décrit les 3 optimisations de performance implémentées selon le plan 2.1.5, 2.2.4 et 2.2.5.

## 1. Lazy-loading Recharts (2.2.5)

### Objectif
Réduire la taille du bundle initial en chargeant les composants de graphiques (Recharts) uniquement quand nécessaire.

### Implémentation
Les composants de graphiques ont été extraits dans des fichiers séparés et wrappés avec `React.lazy()` + `<Suspense>`:

#### Composants créés
- `/components/devis/generator/RentabiliteSidebarLazy.tsx` - Wrapper lazy pour la sidebar rentabilité
- `/components/devis/ConversionFunnelChart.tsx` - Graphique funnel de conversion (lazy)
- `/components/financier/EvolutionChartLazy.tsx` - Wrapper lazy pour le graphique d'évolution
- `/components/financier/BarresComparativesLotsLazy.tsx` - Wrapper lazy pour les barres comparatives
- `/components/financier/CamembertLotsLazy.tsx` - Wrapper lazy pour le camembert des lots
- `/components/financier/StatutPieChart.tsx` - Camembert statuts chantiers (lazy)
- `/components/financier/BudgetBarChart.tsx` - Barres Budget/Engagé/Déboursé (lazy)
- `/components/financier/MargesBarChart.tsx` - Barres marges par chantier (lazy)

#### Pages modifiées
- `pages/DevisDashboardPage.tsx` - Utilise ConversionFunnelChart en lazy
- `pages/DashboardFinancierPage.tsx` - Utilise StatutPieChart, BudgetBarChart, MargesBarChart en lazy

#### Bénéfices attendus
- Réduction du bundle initial de ~150-200KB (Recharts)
- Chargement plus rapide de la page d'accueil
- Les graphiques se chargent uniquement quand affichés

## 2. Persistence QueryClient localStorage (2.1.5)

### Objectif
Conserver le cache TanStack Query dans le localStorage pour éviter de recharger les données à chaque visite.

### Implémentation
Solution manuelle sans dépendance `@tanstack/react-query-persist-client` (non installé).

#### Fichier modifié
- `/lib/queryClient.ts`

#### Fonctionnalités
- `restoreQueryCache()` - Restaure le cache depuis localStorage au démarrage
- `persistQueryCache()` - Sauvegarde le cache dans localStorage
- Persistence automatique toutes les 30 secondes
- Persistence avant déchargement de la page (`beforeunload`)
- Expiration du cache après 30 minutes

#### Configuration
```typescript
const CACHE_KEY = 'hub-chantier-query-cache'
const CACHE_MAX_AGE = 30 * 60 * 1000 // 30 minutes
```

#### Bénéfices attendus
- Réduction des appels API lors des visites répétées
- Meilleure expérience utilisateur (données instantanées)
- Fonctionne bien avec la PWA pour le mode offline

#### Limitations
- Taille limitée par le quota localStorage (~5-10MB selon navigateur)
- Pas de compression (peut être ajoutée si nécessaire)
- Serialization JSON uniquement (pas de fonctions, Date, etc.)

## 3. Bundle Analyzer - rollup-plugin-visualizer (2.2.4)

### Objectif
Analyser la composition du bundle pour identifier les opportunités d'optimisation.

### Installation requise
```bash
cd /home/user/Hub-Chantier/frontend
npm install -D rollup-plugin-visualizer
```

### Configuration
Le plugin est configuré dans `vite.config.ts` mais commenté en attendant l'installation.

#### Pour activer
1. Installer le package: `npm install -D rollup-plugin-visualizer`
2. Décommenter les lignes dans `vite.config.ts`:
```typescript
import { visualizer } from 'rollup-plugin-visualizer'

// Dans plugins:
...(process.env.ANALYZE
  ? [
      visualizer({
        open: true,
        filename: 'dist/stats.html',
        gzipSize: true,
        brotliSize: true,
      }),
    ]
  : []),
```

#### Utilisation
```bash
ANALYZE=true npm run build
```

Cela générera `dist/stats.html` et l'ouvrira automatiquement dans le navigateur.

#### Bénéfices
- Visualisation interactive du bundle
- Identification des packages lourds
- Comparaison gzip/brotli
- Aide à optimiser le code splitting

## Résumé des gains attendus

| Optimisation | Gain bundle initial | Gain performance | Gain UX |
|--------------|---------------------|------------------|---------|
| Lazy Recharts | ~150-200KB | +15-20% FCP | ⭐⭐⭐ |
| QueryClient persist | 0KB | -50% API calls | ⭐⭐⭐⭐ |
| Bundle analyzer | 0KB | Diagnostic | ⭐⭐ |

## Prochaines étapes recommandées

1. **Installer rollup-plugin-visualizer** et analyser le bundle
2. **Monitorer** la taille du localStorage pour éviter les quotas dépassés
3. **Ajouter** plus de composants lazy si nécessaire (ex: modals, formulaires complexes)
4. **Considérer** l'installation de `@tanstack/react-query-persist-client` pour une solution plus robuste
5. **Mesurer** les Core Web Vitals avant/après avec Lighthouse

## Notes techniques

### React.lazy() et Suspense
- Fonctionne uniquement avec les default exports
- Nécessite un fallback pour l'état de chargement
- Compatible avec React 18+ concurrent features

### localStorage limitations
- 5-10MB selon navigateur
- Synchrone (peut bloquer le main thread)
- Pas de support natif pour expiration (implémenté manuellement)

### Recharts bundle size
- Recharts complet: ~180KB minified
- Composants individuels: 20-50KB chacun
- Recommandé de lazy-loader uniquement les pages avec graphiques
