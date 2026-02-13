# Plan d'amelioration UX — Hub Chantier

> Synthese de 4 audits d'experts (Accessibilite, Performance, React/UX, Business/Metier)
> Date : 2026-02-13

---

## Equipe d'experts mobilisee

| Expert | Role | Perimetre |
|--------|------|-----------|
| **Accessibility Tester** | Audit WCAG 2.1 AA + UX terrain | Contrastes, touch targets, navigation clavier, screen readers, mode exterieur |
| **Performance Engineer** | Audit performance frontend | Bundle, rendering, caching, PWA, images |
| **React Specialist** | Patterns UX React modernes | Design system, state management, animations, loading states |
| **Business Analyst** | Analyse metier BTP + benchmark concurrentiel | Workflows par role, Fieldwire/PlanGrid/Procore, gamification, onboarding |

---

## Diagnostic global

| Dimension | Score | Commentaire |
|-----------|-------|-------------|
| Accessibilite | 72/100 | Bonnes bases ARIA, mais contrastes et touch targets insuffisants pour le terrain |
| Performance | 55/100 | Code splitting OK, mais bundle Firebase 350KB, zero cache client, re-renders excessifs |
| Design System | 40/100 | Tailwind ad-hoc, pas de composants UI reutilisables formalises |
| UX Terrain (mobile) | 50/100 | PWA OK, mais pas de mode offline, widgets, ni markup photo |
| Onboarding | 10/100 | Aucun tutoriel, aucune aide contextuelle |
| Temps de reponse percu | 60/100 | Spinners generiques, zero squelettes, pas d'updates optimistes |

**Constat principal** : L'application est **fonctionnellement mature** (87% features) mais l'UX reste a un niveau **2020** plutot que **2026**. Les ouvriers terrain (60% des utilisateurs) subissent le plus d'impact.

---

## Phase 1 — Urgences terrain (Semaine 1-2)

> Objectif : Rendre l'app utilisable sur chantier (gants, soleil, reseau instable)

### 1.1 Touch targets pour mains gantees [CRITIQUE]

**Probleme** : Boutons < 44px inutilisables avec des gants de chantier.

| Composant | Taille actuelle | Cible | Fichier |
|-----------|----------------|-------|---------|
| Navigation chevrons | 32px | 48px min | `Layout.tsx:139` |
| Color picker | 32px (`w-8 h-8`) | 48px | `CreateUserModal.tsx:222` |
| Quick Actions | 48px | 56px | `QuickActions.tsx:73` |
| Planning cells (mois) | Variable < 48px | 48px min | `PlanningGrid.tsx:586` |

- [ ] 1.1.1 Augmenter tous les touch targets a 48px minimum (56px recommande)
- [ ] 1.1.2 Ajouter `min-w-[48px] min-h-[48px]` sur tous les boutons icones
- [ ] 1.1.3 Agrandir les handles de drag du planning

### 1.2 Contrastes et lisibilite exterieure [CRITIQUE]

**Probleme** : `text-gray-400`/`text-gray-500` sur fond blanc = ratio ~3.5:1 (WCAG exige 4.5:1). Illisible en plein soleil.

- [ ] 1.2.1 Auditer toutes les combinaisons couleur avec un outil de contraste
- [ ] 1.2.2 Remplacer `text-gray-400` par `text-gray-600` minimum partout
- [ ] 1.2.3 Ajouter les styles placeholder : `::placeholder { @apply text-gray-600; opacity: 1; }`
- [ ] 1.2.4 Implementer un mode "haute contraste" (toggle dans parametres utilisateur)

### 1.3 Navigation mobile par role [HAUTE]

**Probleme** : 13 items de navigation principal → surcharge cognitive sur mobile. Un compagnon voit "Devis", "Webhooks", "API Keys" qui ne le concernent pas.

- [ ] 1.3.1 Filtrer les items de navigation selon le role utilisateur
- [ ] 1.3.2 Compagnon : Barre de navigation basse (4 items max : Accueil, Chantiers, Heures, Plus)
- [ ] 1.3.3 Chef : Sidebar simplifiee (Dashboard, Chantiers, Planning, Heures, Signalements)
- [ ] 1.3.4 Admin/Conducteur : Navigation complete actuelle

### 1.4 Mode offline timesheets [CRITIQUE]

**Probleme** : 30% des chantiers ont un reseau instable. Sans offline, les ouvriers abandonnent l'app.

- [ ] 1.4.1 Implementer la saisie heures offline (IndexedDB + queue de sync)
- [ ] 1.4.2 Indicateur visuel "mode hors ligne" sur les formulaires
- [ ] 1.4.3 Synchronisation automatique au retour du reseau
- [ ] 1.4.4 Gestion des conflits (version serveur vs locale)

### 1.5 FAB (Floating Action Button) mobile [HAUTE]

- [ ] 1.5.1 Ajouter un FAB sur mobile avec 4 actions : Pointer, Photo, Signalement, Heures
- [ ] 1.5.2 Bouton 56px, position bottom-right, au-dessus de la nav basse

---

## Phase 2 — Performance & reactivite (Semaine 3-4)

> Objectif : Passer de "ca charge" a "c'est instantane"

### 2.1 Cache client avec TanStack Query [CRITIQUE]

**Probleme** : Zero cache cote client. Chaque navigation remonte toutes les donnees au serveur. Le planning refetch 4 endpoints a chaque changement de date.

- [ ] 2.1.1 Installer `@tanstack/react-query`
- [ ] 2.1.2 Migrer `useDashboardFeed` → react-query (staleTime 1min)
- [ ] 2.1.3 Migrer `usePlanning` → react-query (cache users/chantiers 5min)
- [ ] 2.1.4 Migrer `useChantierDetail` → react-query
- [ ] 2.1.5 Configurer `persistQueryClient` pour persistence localStorage

**Impact attendu** : -70% appels API redondants, navigation retour instantanee.

### 2.2 Reduction du bundle initial [CRITIQUE]

**Probleme** : Firebase (~350KB gzip) charge au demarrage alors qu'il sert uniquement aux notifications push.

| Dependance | Taille estimee | Utilisation | Action |
|-----------|----------------|-------------|--------|
| `firebase` | ~350KB gzip | Notifications push uniquement | Lazy import conditionnel |
| `recharts` | ~120KB gzip | 3 composants (pages financier/devis) | Lazy load par page |
| `lucide-react` | ~50KB gzip | 115 fichiers | Verifier tree-shaking build |

- [ ] 2.2.1 Lazy-loader Firebase : `import('firebase/app')` uniquement quand notifications activees
- [ ] 2.2.2 Lazy-loader Recharts : chunk separe `vendor-charts` dans vite.config.ts
- [ ] 2.2.3 Ajouter chunk `vendor-firebase` dans manualChunks
- [ ] 2.2.4 Installer `rollup-plugin-visualizer` pour auditer le build

**Impact attendu** : -300-400KB sur le bundle initial (-47%).

### 2.3 Optimisation des re-renders [HAUTE]

**Probleme** : DashboardPage re-rend tout le feed a chaque interaction. PlanningGrid re-rend 1000+ cellules en vue mois.

- [ ] 2.3.1 `React.memo` sur `DashboardPostCard` (20+ instances dans le feed)
- [ ] 2.3.2 `useCallback` stable pour `handleLike`, `handleComment` dans `useDashboardFeed`
- [ ] 2.3.3 Virtualisation du PlanningGrid en vue mois (`@tanstack/react-virtual`)
- [ ] 2.3.4 `useMemo` sur `groupByCategory` dans PlanningGrid
- [ ] 2.3.5 Memoiser `AffectationBlock` avec `React.memo`

**Impact attendu** : -60-70% re-renders inutiles, vue mois planning : 3-5s → <1s.

### 2.4 Updates optimistes [HAUTE]

**Probleme** : Chaque action affiche un spinner. Les ouvriers terrain veulent un feedback instantane.

- [ ] 2.4.1 Implementer optimistic update pour like/unlike feed
- [ ] 2.4.2 Implementer optimistic update pour creation de post
- [ ] 2.4.3 Implementer optimistic update pour deplacement d'affectation planning
- [ ] 2.4.4 Rollback automatique en cas d'erreur API

### 2.5 Optimisation images [HAUTE]

- [ ] 2.5.1 Convertir `logo.png` (154KB) en WebP/AVIF (~20KB)
- [ ] 2.5.2 Ajouter `loading="lazy" decoding="async"` sur toutes les `<img>`
- [ ] 2.5.3 Ajouter `aspect-ratio` pour eviter les layout shifts
- [ ] 2.5.4 Generer des thumbnails WebP cote upload service

---

## Phase 3 — Design system & polish (Semaine 5-6)

> Objectif : Passer de "utilitaire" a "professionnel"

### 3.1 Composants UI reutilisables [HAUTE]

**Probleme** : Pas de bibliotheque de composants. Chaque bouton, input, modal est reconstruit a la main. Incoherences visuelles entre modules.

- [ ] 3.1.1 Creer `components/ui/Button.tsx` (primary, secondary, outline, ghost, danger)
- [ ] 3.1.2 Creer `components/ui/Input.tsx` (text, number, date, avec etats validation)
- [ ] 3.1.3 Creer `components/ui/Modal.tsx` (base modale avec animations coherentes)
- [ ] 3.1.4 Creer `components/ui/Card.tsx` (conteneur standard)
- [ ] 3.1.5 Creer `components/ui/Badge.tsx` (statuts, roles)
- [ ] 3.1.6 Creer `components/ui/Skeleton.tsx` (placeholders de chargement)
- [ ] 3.1.7 Creer `components/ui/EmptyState.tsx` (etats vides avec CTA)

### 3.2 Squelettes de chargement (Skeleton loaders) [HAUTE]

**Probleme** : Spinners generiques partout. L'utilisateur ne voit pas la structure de la page pendant le chargement.

- [ ] 3.2.1 Skeleton pour le feed dashboard (PostSkeleton)
- [ ] 3.2.2 Skeleton pour la grille planning
- [ ] 3.2.3 Skeleton pour la liste de chantiers
- [ ] 3.2.4 Skeleton pour les cartes du dashboard
- [ ] 3.2.5 Remplacer `<PageLoader />` par des skeletons contextuels

### 3.3 Etats vides enrichis [MOYENNE]

**Probleme** : 20+ instances de "Aucun element" en texte brut, sans illustration ni action.

- [ ] 3.3.1 Designer des etats vides avec icone + message + bouton d'action
- [ ] 3.3.2 Deployer sur : chantiers, signalements, documents, taches, feed

### 3.4 Micro-interactions & animations [MOYENNE]

- [ ] 3.4.1 Animations d'entree/sortie sur les listes (feed, taches)
- [ ] 3.4.2 Hover lift sur les cartes (`shadow-lg -translate-y-0.5` au hover)
- [ ] 3.4.3 Transition de page entre routes (fade 150ms)
- [ ] 3.4.4 Feedback visuel de succes (checkmark anime apres action)
- [ ] 3.4.5 Support `prefers-reduced-motion` pour desactiver les animations

### 3.5 Tokens de design formalises [MOYENNE]

- [ ] 3.5.1 Creer `theme/tokens.ts` avec couleurs semantiques (success, error, warning, info)
- [ ] 3.5.2 Definir couleurs par statut (devis: brouillon/envoye/accepte/refuse)
- [ ] 3.5.3 Definir couleurs par statut chantier (planifie/en_cours/pause/termine)
- [ ] 3.5.4 Migrer les hardcoded colors vers les tokens

---

## Phase 4 — Onboarding & aide (Semaine 7-8)

> Objectif : Un nouvel utilisateur est productif en 30 minutes au lieu de 2-4 heures

### 4.1 Tutoriel interactif premiere connexion [HAUTE]

**Probleme** : Aucun onboarding. Les ouvriers sont livres a eux-memes.

- [ ] 4.1.1 Ecran d'accueil adapte au role : "Bonjour Jean, vous etes Compagnon"
- [ ] 4.1.2 Tutoriel 5 etapes (adapte au role) :
  - Compagnon : Pointer → Planning → Photo → Heures → Deconnexion
  - Chef : Planning → Validation → Signalements → Documents → Deconnexion
  - Conducteur : Dashboard financier → Planification → Achats → Devis → Deconnexion
- [ ] 4.1.3 Donnees de demo pour tester sans consequence
- [ ] 4.1.4 Persistance dans localStorage (ne pas reafficher)
- [ ] 4.1.5 Option "Revoir le tutoriel" dans les parametres

### 4.2 Aide contextuelle [HAUTE]

- [ ] 4.2.1 Icone `?` sur chaque en-tete de page → panneau lateral avec aide
- [ ] 4.2.2 Tooltips sur les boutons/filtres (desktop: hover, mobile: long-press)
- [ ] 4.2.3 Indices progressifs (affiches 3 premieres utilisations, puis masques)

### 4.3 Fil d'Ariane (breadcrumbs) [MOYENNE]

**Probleme** : Pas de breadcrumbs. Les utilisateurs sur des pages profondes (`/chantiers/:id/formulaires/:formId`) ne savent pas ou ils sont.

- [ ] 4.3.1 Composant `Breadcrumb` avec navigation semantique (`aria-label="Fil d'Ariane"`)
- [ ] 4.3.2 Deployer sur toutes les pages de detail

### 4.4 Raccourcis clavier (power users) [BASSE]

- [ ] 4.4.1 `Ctrl+P` → Planning, `Ctrl+H` → Heures, `Ctrl+D` → Documents
- [ ] 4.4.2 `Ctrl+/` → Afficher la liste des raccourcis
- [ ] 4.4.3 Fleches `←` `→` → Semaine precedente/suivante (Planning/FdH)
- [ ] 4.4.4 `Espace` → Pointer (clock in/out) depuis le dashboard

---

## Phase 5 — Intelligence & engagement (Semaine 9-10)

> Objectif : L'app anticipe les besoins et motive l'adoption

### 5.1 Notifications temps reel [HAUTE]

**Probleme** : Polling 30s pour les notifications. Pas de temps reel pour les alertes urgentes.

- [ ] 5.1.1 Evaluer migration vers WebSocket pour les notifications critiques
- [ ] 5.1.2 Regroupement intelligent ("Jean et 3 autres vous ont mentionne")
- [ ] 5.1.3 Boutons d'action dans les notifications ("Voir chantier", "Valider")
- [ ] 5.1.4 Badge de compteur non-lu dans la barre de navigation
- [ ] 5.1.5 Preferences de notification par categorie

### 5.2 Dashboard adaptatif [HAUTE]

**Probleme** : Le DevisPipelineCard est visible par les Compagnons/Chefs qui n'ont pas acces aux devis. Toutes les cartes ont le meme poids visuel.

- [ ] 5.2.1 Masquer DevisPipelineCard pour les roles non concernes (BUG)
- [ ] 5.2.2 Hierarchiser les cartes par priorite : Clock > Meteo alerte > Planning > Feed
- [ ] 5.2.3 Progressive disclosure : cartes secondaires repliees par defaut sur mobile
- [ ] 5.2.4 Carte "Alertes financieres" sur le dashboard pour Conducteur/Admin

### 5.3 Validation par lot (batch) [HAUTE]

**Probleme** : Le Chef doit valider les feuilles d'heures une par une.

- [ ] 5.3.1 Selection multiple (checkboxes) sur la page feuilles d'heures
- [ ] 5.3.2 Barre d'action contextuelle : "Valider X selections"
- [ ] 5.3.3 Tableau de bord validation : pending count, temps moyen, ecarts

### 5.4 Gamification legere [BASSE]

- [ ] 5.4.1 Streak de pointage (jours consecutifs) avec compteur visuel
- [ ] 5.4.2 Visualisation de progression personnelle (heures/semaine vs objectif)
- [ ] 5.4.3 Classement equipe hebdomadaire (heures loguees vs planifiees)
- [ ] 5.4.4 Option desactivable dans les parametres

### 5.5 Recherche globale [BASSE]

- [ ] 5.5.1 Barre de recherche `Cmd+K` multi-entites (chantiers, docs, users, signalements)
- [ ] 5.5.2 Recherche fuzzy tolerante aux fautes
- [ ] 5.5.3 Resultats recents sauvegardes

---

## Phase 6 — Fonctionnalites differenciantes (Semaine 11-12)

> Objectif : Combler les ecarts concurrentiels et se differencier

### 6.1 Markup photo [HAUTE]

**Probleme** : Les concurrents (Fieldwire, PlanGrid) permettent d'annoter les photos avant envoi. Hub Chantier ne fait que uploader.

- [ ] 6.1.1 Canvas d'annotation sur les photos (fleches, cercles, texte)
- [ ] 6.1.2 Integration dans le flux de creation de signalement
- [ ] 6.1.3 Integration dans le feed (posts avec photos annotees)

### 6.2 Widget home screen [HAUTE]

**Probleme** : 3 taps pour pointer vs 1 tap chez Fieldwire.

- [ ] 6.2.1 Evaluer les possibilites PWA pour widgets iOS/Android
- [ ] 6.2.2 Raccourci "Pointer" sur l'ecran d'accueil
- [ ] 6.2.3 Raccourci "Photo rapide" sur l'ecran d'accueil

### 6.3 Saisie heures par presets [MOYENNE]

**Probleme** : Le wheel picker HH:MM est quasi inutilisable avec des gants.

- [ ] 6.3.1 Boutons preset (07:00, 07:30, 08:00, 08:30, etc.) + "Autre"
- [ ] 6.3.2 Derniere heure utilisee en raccourci

### 6.4 Planning offline (lecture seule) [MOYENNE]

- [ ] 6.4.1 Cache du planning de la semaine courante dans IndexedDB
- [ ] 6.4.2 Affichage en lecture seule quand hors ligne
- [ ] 6.4.3 Indicateur "Donnees du [date] - actualisation au retour du reseau"

---

## Accessibilite — Correctifs transversaux

> A integrer en continu dans chaque phase

- [ ] A.1 Ajouter un lien "Aller au contenu principal" (skip link) dans `Layout.tsx`
- [ ] A.2 Support `prefers-reduced-motion` dans `index.css`
- [ ] A.3 Ajouter `aria-required="true"` sur tous les champs obligatoires
- [ ] A.4 Focus trap dans les modales (empecher le tab en dehors)
- [ ] A.5 Reset du focus sur changement de route (`useEffect` sur `location.pathname`)
- [ ] A.6 `<nav aria-label="Navigation principale">` dans Layout
- [ ] A.7 Gestion des titres de page dynamiques (`document.title = "Planning - Hub Chantier"`)
- [ ] A.8 Legende "Les champs * sont obligatoires" en haut des formulaires

---

## PWA — Ameliorations caching

- [ ] P.1 `CacheFirst` pour `/api/uploads/` et `/api/documents/` (assets immuables)
- [ ] P.2 Cache plus court (5min) pour `/api/planning/` et `/api/dashboard/` (donnees temps reel)
- [ ] P.3 `networkTimeoutSeconds: 3` pour fallback rapide sur cache
- [ ] P.4 Background sync pour les mutations (posts, affectations, pointages)

---

## Benchmark concurrentiel

| Fonctionnalite | Fieldwire | PlanGrid | Procore | Hub Chantier | Priorite comblement |
|----------------|-----------|----------|---------|--------------|---------------------|
| Mode offline | Full CRUD | Lecture | Limite | Aucun | CRITIQUE |
| Widget mobile | Oui | Oui | Oui | Non | CRITIQUE |
| Markup photo | Avance | Avance | Basic | Non | HAUTE |
| Onboarding interactif | Oui | Statique | Guide | Non | HAUTE |
| Actions par lot | Oui | Oui | Oui | Non | HAUTE |
| Saisie vocale | Oui | Non | Limite | Non | BASSE (Phase future) |
| Annotation PDF | Basic | Avance | Avance | Non | BASSE (Phase future) |

**Avantages Hub Chantier a preserver** :
- Module financier complet (unique vs Fieldwire/PlanGrid)
- Feed social (engagement equipe)
- Planning de charge (capacite)
- Formulaires custom avec signatures

---

## Metriques de succes

| Metrique | Baseline estime | Cible post-plan | Evolution |
|----------|-----------------|-----------------|-----------|
| Temps de formation par utilisateur | 2-4h | 30min | -75% |
| Utilisateurs actifs quotidiens | ~60% | 85% | +42% |
| Taux de soumission FdH a l'heure | ~70% | 90% | +29% |
| Actions par session | ~8 | 14 | +75% |
| Tickets support par semaine | ~12 | 5 | -58% |
| Taux d'abandon session mobile | ~35% | 15% | -57% |
| FCP (First Contentful Paint, 3G) | ~4.2s | 1.8s | -57% |
| Bundle initial (gzip) | ~850KB | ~450KB | -47% |
| Appels API (chargement dashboard) | ~12 | ~4 | -67% |

---

## Planning synthetique

| Phase | Semaines | Focus | Impact |
|-------|----------|-------|--------|
| **1** | S1-S2 | Urgences terrain (touch, contrastes, nav, offline, FAB) | Utilisable sur chantier |
| **2** | S3-S4 | Performance (cache, bundle, re-renders, optimistic, images) | App instantanee |
| **3** | S5-S6 | Design system (composants UI, skeletons, animations, tokens) | App professionnelle |
| **4** | S7-S8 | Onboarding (tutoriel, aide contextuelle, breadcrumbs) | Adoption acceleree |
| **5** | S9-S10 | Intelligence (notifications, dashboard, batch, gamification) | Engagement durable |
| **6** | S11-S12 | Differenciation (markup photo, widgets, presets, offline+) | Avantage concurrentiel |

---

## Decisions a prendre

- [ ] **Priorite offline** : Full CRUD offline (3 semaines) ou lecture seule (1 semaine) en Phase 1 ?
- [ ] **Librairie cache** : TanStack Query (recommande) ou SWR ?
- [ ] **Animations** : Framer Motion (puissant mais +30KB) ou CSS-only (leger) ?
- [ ] **Navigation mobile** : Bottom bar fixe ou FAB + drawer ?
- [ ] **Gamification** : Activer ou non ? Quel niveau (streaks seuls vs badges complets) ?
- [ ] **WebSocket** : Implementer en Phase 5 ou rester en polling optimise ?

---

## Fichiers cles references

| Fichier | Problemes identifies |
|---------|---------------------|
| `frontend/src/components/Layout.tsx` | Nav 13 items, touch targets 32px, pas de skip link, pas de `<nav>` semantique |
| `frontend/src/pages/DashboardPage.tsx` | Re-renders feed, DevisPipeline visible par tous les roles |
| `frontend/src/hooks/usePlanning.ts` | 4 endpoints refetch a chaque date, pas de cache |
| `frontend/src/hooks/useDashboardFeed.ts` | Pas de cache, pas de deduplication, pas d'optimistic |
| `frontend/src/components/planning/PlanningGrid.tsx` | 1000+ DOM nodes sans virtualisation (vue mois) |
| `frontend/src/services/firebase.ts` | 350KB charge au demarrage meme si notifications non activees |
| `frontend/src/index.css` | Pas de `prefers-reduced-motion`, animations non conditionnelles |
| `frontend/tailwind.config.js` | Palette limitee, pas de tokens semantiques |
| `frontend/vite.config.ts` | Chunks incomplets (manque firebase, recharts, zod) |
| `frontend/public/logo.png` | 154KB non optimise, pas de WebP/AVIF |
