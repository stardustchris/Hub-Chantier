# Mode Démonstration - Hub Chantier

## Vue d'ensemble

Le mode démonstration permet aux nouveaux utilisateurs de tester l'application avec des données fictives sans conséquence sur les données réelles.

## Architecture

### Fichiers créés

1. **`contexts/DemoContext.tsx`** - Contexte React pour gérer l'état du mode démo
2. **`data/demoData.ts`** - Données de démonstration (chantiers, users, affectations, pointages, posts)
3. **`components/onboarding/OnboardingWelcome.tsx`** - Écran de bienvenue avec option mode démo

### Modifications

- **`App.tsx`** - Ajout du `DemoProvider` et du bandeau jaune quand le mode est actif
- **`components/onboarding/OnboardingProvider.tsx`** - Affiche l'écran de bienvenue au premier lancement

## Utilisation

### Activation du mode démo

Le mode démo peut être activé de deux façons :

1. **Au premier lancement** : L'écran de bienvenue propose "Essayer avec des données de démo"
2. **Manuellement** : Via le contexte `useDemo().enableDemoMode()`

### Dans un composant

```tsx
import { useDemo } from '../../contexts/DemoContext'

function MyComponent() {
  const { isDemoMode, demoData, disableDemoMode } = useDemo()

  if (isDemoMode) {
    // Utiliser les données de démo
    return <div>Chantiers de démo : {demoData.chantiers.length}</div>
  }

  // Utiliser les données réelles
  return <div>Chantiers réels</div>
}
```

### Dans un hook de données

Pour brancher un hook existant sur le mode démo :

```tsx
import { useDemo } from '../../contexts/DemoContext'

export function useDashboardFeed() {
  const { isDemoMode, demoData } = useDemo()

  // Si mode démo, retourner les données fictives
  if (isDemoMode) {
    return {
      data: demoData.posts,
      isLoading: false,
      error: null,
    }
  }

  // Sinon, appeler l'API comme d'habitude
  return useQuery({
    queryKey: ['dashboard', 'feed'],
    queryFn: () => api.dashboard.getFeed(),
  })
}
```

### Toast pour les mutations

Quand le mode démo est actif, les mutations doivent afficher un toast :

```tsx
import { useDemo } from '../../contexts/DemoContext'
import { useToast } from '../../contexts/ToastContext'

function MyComponent() {
  const { isDemoMode } = useDemo()
  const { addToast } = useToast()

  const handleDelete = async (id: string) => {
    if (isDemoMode) {
      addToast({
        type: 'info',
        message: 'Action simulée en mode démo',
      })
      return
    }

    // Appel API réel
    await api.chantiers.delete(id)
  }
}
```

## Données de démo disponibles

### Utilisateurs (5)

- **Admin** : Pierre Dupont (admin@demo.fr)
- **Conducteur** : Sophie Martin (conducteur@demo.fr)
- **Chef de chantier** : Luc Bernard (chef@demo.fr)
- **Compagnon 1** : Jean Moreau (compagnon1@demo.fr)
- **Compagnon 2** : Marc Petit (compagnon2@demo.fr)

### Chantiers (3)

1. **Rénovation Maison Martin** (en cours, 45% avancement estimé)
2. **Extension Villa Dupont** (planifié, pas encore démarré)
3. **Réhabilitation Immeuble Centre** (en cours, 80% avancement estimé)

### Affectations

- Quelques affectations pour la semaine courante
- Mix d'affectations uniques et récurrentes

### Pointages

- Quelques pointages validés et en attente pour la semaine courante

### Posts (Dashboard)

- 2 posts de démonstration (1 normal, 1 urgent)

## Persistance

Le mode démo est persisté dans localStorage sous la clé `hub_demo_mode`.

## Désactivation

Deux façons de désactiver le mode démo :

1. Cliquer sur le bouton "Quitter" dans le bandeau jaune
2. Appeler `useDemo().disableDemoMode()`

## Prochaines étapes (non implémenté)

Pour compléter l'implémentation du mode démo :

1. **Brancher les hooks de données** : Modifier les hooks comme `useDashboardFeed`, `useChantiers`, etc. pour retourner les données de démo quand `isDemoMode` est true
2. **Simuler les mutations** : Intercepter les create/update/delete pour les simuler localement
3. **Ajouter plus de données** : Enrichir `demoData.ts` avec plus de données réalistes si nécessaire

## Notes techniques

- Les IDs des données de démo utilisent le préfixe `demo-` pour éviter les conflits avec les IDs réels
- Les dates sont calculées dynamiquement pour la semaine courante
- Le bandeau de mode démo a un z-index élevé (9997) pour rester visible
