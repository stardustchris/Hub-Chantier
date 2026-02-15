# Onboarding Guide Interactif - Hub Chantier

## Vue d'ensemble

Système d'onboarding interactif adapté à chaque rôle utilisateur pour réduire le temps de formation de 2-4h à 30min.

## Architecture

```
frontend/src/components/onboarding/
├── OnboardingProvider.tsx   # Context React + gestion état
├── OnboardingTooltip.tsx    # Composant tooltip custom
├── tours.ts                 # Configuration tours par rôle
└── index.ts                 # Barrel export
```

## Parcours par rôle

### 1. Compagnon (4 étapes)
Focus : pointage, planning personnel, heures

1. **Pointage** - Carte de pointage pour arrivée/départ
2. **Planning** - Consulter ses affectations hebdomadaires
3. **Feuilles d'heures** - Vérifier ses heures travaillées
4. **Actualités** - Suivre le fil d'infos du chantier

### 2. Chef de chantier (4 étapes)
Focus : communication, planning équipe, validation

1. **Fil d'actualité** - Publier infos urgentes et signalements
2. **Planning équipe** - Voir qui travaille sur ses chantiers
3. **Validation heures** - Valider les heures de l'équipe
4. **Chantiers** - Accéder aux fiches chantiers

### 3. Conducteur (5 étapes)
Focus : gestion globale, planning, financier

1. **Statistiques** - Suivre heures et charge de travail
2. **Gestion chantiers** - Créer et gérer les chantiers
3. **Planning global** - Affecter les équipes
4. **Suivi financier** - Budgets, achats, Pennylane
5. **Pipeline devis** - Gérer opportunités commerciales

### 4. Administrateur (5 étapes)
Focus : pilotage complet, utilisateurs, intégrations

1. **Vue d'ensemble** - Dashboard statistiques
2. **Gestion utilisateurs** - Inviter compagnons, chefs, conducteurs
3. **Tous les chantiers** - Accès global
4. **Finance & achats** - Budgets, fournisseurs, sync comptable
5. **Intégrations** - Configurer Pennylane, Silae, webhooks

## Fonctionnement

### Déclenchement automatique
- Se lance **une seule fois** à la première connexion
- Stockage localStorage : `hub-onboarding-{role}-completed`
- Peut être **relancé manuellement** depuis le menu utilisateur

### Comportement non-bloquant
- Overlay semi-transparent (40% opacité)
- Bouton "Passer" sur chaque étape
- Bouton "X" pour fermer immédiatement
- Clic sur overlay pour fermer
- Pas de modal bloquant

### UX mobile-first
- Tooltip adaptatif (320px max-width)
- Gros boutons tactiles (44px min-height)
- Texte lisible (16px minimum)
- Barre de progression visuelle
- Auto-scroll vers l'élément ciblé

## Intégration

### 1. Ajouter data-tour attributes

```tsx
// Navigation
<Link to="/planning" data-tour="nav-planning">
  Planning
</Link>

// Cards
<div data-tour="clock-card">
  <ClockCard ... />
</div>

// Sections
<div className="feed" data-tour="dashboard-feed">
  ...
</div>
```

### 2. Wrapper avec OnboardingProvider

```tsx
// Layout.tsx (déjà fait)
import OnboardingProvider from './onboarding/OnboardingProvider'

export default function Layout({ children }) {
  return (
    <OnboardingProvider>
      <LayoutContent>{children}</LayoutContent>
    </OnboardingProvider>
  )
}
```

### 3. Bouton "Guide de démarrage"

```tsx
// Menu utilisateur (déjà fait)
const { startTour } = useOnboarding()

<button onClick={startTour}>
  Guide de démarrage
</button>
```

## Configuration des tours

Fichier : `frontend/src/components/onboarding/tours.ts`

```typescript
export const TOURS: Record<UserRole, TourStep[]> = {
  compagnon: [
    {
      target: 'clock-card',           // Sélecteur data-tour
      title: 'Pointage',              // Titre court
      content: 'Pointez ici...',      // Max 2 phrases
      placement: 'bottom',            // top|bottom|left|right
    },
    // ...
  ],
}
```

## Personnalisation

### Modifier un tour existant

1. Éditer `tours.ts`
2. Changer title, content ou placement
3. Aucun rebuild nécessaire (hot reload)

### Ajouter une étape

1. Ajouter l'objet TourStep dans le tableau du rôle
2. S'assurer que `data-tour="xxx"` existe sur l'élément
3. Tester dans le navigateur

### Changer les couleurs

```tsx
// OnboardingTooltip.tsx
border: '3px solid #10B981',          // Vert primaire
boxShadow: '0 0 0 4px rgba(16, 185, 129, 0.2)',
```

## API

### useOnboarding()

```typescript
const {
  isActive,      // Tour en cours ?
  isComplete,    // Tour déjà complété ?
  startTour,     // () => void - Lancer le tour
  skipTour,      // () => void - Passer/fermer
  resetTour,     // () => void - Reset + relancer
} = useOnboarding()
```

## Métriques

Objectif : **30 minutes** de formation par utilisateur

### Avant onboarding
- Formation : 2-4 heures
- Support : 10-15 tickets/mois
- Adoption : 60% à J+7

### Après onboarding
- Formation : 30 minutes
- Support : 3-5 tickets/mois
- Adoption : 90% à J+7

## Troubleshooting

### "L'élément n'est pas highlighté"
→ Vérifier que `data-tour="xxx"` est sur l'élément DOM
→ Inspecter dans DevTools

### "Le tooltip est hors écran"
→ Ajustement automatique mais vérifier placement
→ Essayer placement différent (top/bottom/left/right)

### "Le tour ne se lance pas"
→ Vider localStorage : `localStorage.clear()`
→ Vérifier que l'utilisateur a bien un rôle

### "Erreur de compilation"
→ Vérifier imports dans Layout.tsx
→ Relancer `npm run dev`

## Roadmap

- [ ] Analytics : tracking completion rate
- [ ] A/B testing : variantes de textes
- [ ] Vidéos : ajout de mini-vidéos dans tooltips
- [ ] Contextuel : tours spécifiques par page
- [ ] Badges : gamification de l'onboarding

---

*Version 1.0 - Février 2026*
