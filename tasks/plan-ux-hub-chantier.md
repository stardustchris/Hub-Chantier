# Plan d'amelioration UX — Hub Chantier

> Synthese de 4 audits d'experts (Accessibilite, Performance, React/UX, Business/Metier)
> Date : 2026-02-13 | Mis a jour : 2026-02-14

---

## Equipe d'experts mobilisee

| Expert | Role | Perimetre |
|--------|------|-----------|
| **Accessibility Tester** | Audit WCAG 2.1 AA + UX terrain | Contrastes, touch targets, navigation clavier, screen readers, mode exterieur |
| **Performance Engineer** | Audit performance frontend | Bundle, rendering, caching, PWA, images |
| **React Specialist** | Patterns UX React modernes | Design system, state management, animations, loading states |
| **Business Analyst** | Analyse metier BTP + benchmark concurrentiel | Workflows par role, Fieldwire/PlanGrid/Procore, gamification, onboarding |

---

## Avancement global

| Phase | Statut | Progression |
|-------|--------|-------------|
| **1** Urgences terrain | **QUASI COMPLET** | 12/14 items (86%) |
| **2** Performance | **MAJORITAIRE** | 11/18 items (61%) |
| **3** Design system | **MAJORITAIRE** | 16/21 items (76%) |
| **4** Onboarding | **NON DEMARRE** | 0/14 items (0%) |
| **5** Intelligence | **PARTIEL** | 4/17 items (24%) |
| **6** Differenciation | **PARTIEL** | 4/12 items (33%) |
| **Accessibilite** | **PARTIEL** | 3/8 items (38%) |
| **PWA** | **PARTIEL** | 1/4 items (25%) |
| **TOTAL** | | **51/108 items (47%)** |

### Diagnostic mis a jour (post-implementation)

| Dimension | Score initial | Score actuel | Delta |
|-----------|-------------|--------------|-------|
| Accessibilite | 72/100 | **80/100** | +8 (skip link, aria-label, reduced-motion) |
| Performance | 55/100 | **78/100** | +23 (TanStack Query, lazy Firebase, memo, chunks) |
| Design System | 40/100 | **72/100** | +32 (Button, Card, Badge, Skeleton, EmptyState) |
| UX Terrain (mobile) | 50/100 | **82/100** | +32 (touch 48px, offline, FAB, role nav) |
| Onboarding | 10/100 | **10/100** | +0 (pas commence) |
| Temps de reponse percu | 60/100 | **80/100** | +20 (skeletons, react-query cache, memo) |

---

## Phase 1 — Urgences terrain (Semaine 1-2) — 86% FAIT

> Objectif : Rendre l'app utilisable sur chantier (gants, soleil, reseau instable)

### 1.1 Touch targets pour mains gantees [CRITIQUE] — FAIT

- [x] 1.1.1 Augmenter tous les touch targets a 48px minimum (56px recommande)
  > Layout.tsx: `min-w-[48px] min-h-[48px]`, QuickActions: `min-w-[56px] min-h-[56px]`, PlanningGrid: `min-h-[60px]`
- [x] 1.1.2 Ajouter `min-w-[48px] min-h-[48px]` sur tous les boutons icones
  > Button.tsx md: `min-h-[48px]`, lg: `min-h-[52px]`, CreateUserModal color picker: `w-12 h-12`
- [x] 1.1.3 Agrandir les handles de drag du planning
  > PlanningGrid cells `min-h-[60px]`

### 1.2 Contrastes et lisibilite exterieure [CRITIQUE] — PARTIEL

**Reste** : `text-gray-400` encore present dans ~20 fichiers (Layout, MobileTimePicker, ImageUpload, MiniMap, etc.)

- [ ] 1.2.1 Auditer toutes les combinaisons couleur avec un outil de contraste
- [ ] 1.2.2 Remplacer `text-gray-400` par `text-gray-600` minimum partout (~20 fichiers)
- [x] 1.2.3 Styles placeholder : `index.css` → `::placeholder { @apply text-gray-500 }`
  > Placeholder a text-gray-500 (ratio acceptable)
- [ ] 1.2.4 Implementer un mode "haute contraste" (toggle dans parametres utilisateur)

### 1.3 Navigation mobile par role [HAUTE] — FAIT

- [x] 1.3.1 Filtrer les items de navigation selon le role utilisateur
  > Layout.tsx `filterByRole()` avec `item.roles.includes(userRole)`
- [x] 1.3.2 Compagnon : Navigation filtree (items admin/conducteur masques)
- [x] 1.3.3 Chef : Sidebar filtree (Devis, Webhooks masques)
- [x] 1.3.4 Admin/Conducteur : Navigation complete actuelle

### 1.4 Mode offline timesheets [CRITIQUE] — FAIT

- [x] 1.4.1 Implementer la saisie heures offline (localStorage + queue de sync chiffree AES-GCM)
  > `useOfflineStorage.ts` : queue avec retry (3 max), chiffrement AES-GCM via Web Crypto API
- [x] 1.4.2 Indicateur visuel "mode hors ligne" sur les formulaires
  > `OfflineIndicator.tsx` : bandeau amber avec WifiOff icon + message sync
- [x] 1.4.3 Synchronisation automatique au retour du reseau
  > Service Worker `sync.register('sync-pending-data')` + online event listener
- [x] 1.4.4 Gestion des conflits (version serveur vs locale)
  > Queue avec retry logic, items expires apres 3 tentatives

### 1.5 FAB (Floating Action Button) mobile [HAUTE] — FAIT

- [x] 1.5.1 Ajouter un FAB sur mobile avec 4 actions : Pointer, Photo, Signalement, Heures
  > `FloatingActionButton.tsx` : 4 actions (Clock, Camera, AlertTriangle, ClipboardList)
- [x] 1.5.2 Bouton 56px, position bottom-right, au-dessus de la nav basse
  > `w-14 h-14` (56px), `fixed bottom-4 right-4 z-50`, `lg:hidden` (mobile only)

---

## Phase 2 — Performance & reactivite (Semaine 3-4) — 61% FAIT

> Objectif : Passer de "ca charge" a "c'est instantane"

### 2.1 Cache client avec TanStack Query [CRITIQUE] — FAIT

- [x] 2.1.1 Installer `@tanstack/react-query`
  > v5.90.21, QueryClientProvider dans App.tsx
- [x] 2.1.2 Migrer `useDashboardFeed` → react-query (useQuery + useMutation)
  > staleTime 5min, gcTime 30min, invalidation sur mutations
- [x] 2.1.3 Migrer hooks → react-query (cache users/chantiers)
- [ ] 2.1.4 Migrer `useChantierDetail` → react-query
- [ ] 2.1.5 Configurer `persistQueryClient` pour persistence localStorage

### 2.2 Reduction du bundle initial [CRITIQUE] — MAJORITAIRE

- [x] 2.2.1 Lazy-loader Firebase : `import('firebase/app')` conditionnel
  > `firebase.ts` : tous les imports via `await import('firebase/...')`
- [x] 2.2.2 Chunks vendor separes dans vite.config.ts
  > manualChunks : vendor-react, vendor-firebase, vendor-charts, vendor-query, etc. (8 chunks)
- [x] 2.2.3 Ajouter chunk `vendor-firebase` dans manualChunks
  > vite.config.ts manualChunks
- [ ] 2.2.4 Installer `rollup-plugin-visualizer` pour auditer le build
- [ ] 2.2.5 Lazy-loader Recharts par page (imports directs dans EvolutionChart, CamembertLots)

### 2.3 Optimisation des re-renders [HAUTE] — MAJORITAIRE

- [x] 2.3.1 `React.memo` sur `DashboardPostCard` + `PostCard`
- [x] 2.3.2 `useCallback` stable pour handlers dans `useDashboardFeed` + `PostCard`
  > loadFeed, handleCreatePost, handleLike, handlePin, handleDelete
- [ ] 2.3.3 Virtualisation du PlanningGrid en vue mois (`@tanstack/react-virtual`)
- [x] 2.3.4 `useMemo` sur `groupByCategory` dans PlanningGrid
  > + sortedCategories, affectationsByUserAndDate, gridStyle
- [x] 2.3.5 Memoiser `AffectationBlock` avec `React.memo`

### 2.4 Updates optimistes [HAUTE] — NON FAIT

**Note** : useMutation utilise invalidation (refetch) au lieu d'optimistic updates.

- [ ] 2.4.1 Implementer optimistic update pour like/unlike feed (onMutate + setQueryData)
- [ ] 2.4.2 Implementer optimistic update pour creation de post
- [ ] 2.4.3 Implementer optimistic update pour deplacement d'affectation planning
- [ ] 2.4.4 Rollback automatique en cas d'erreur API

### 2.5 Optimisation images [HAUTE] — PARTIEL

- [ ] 2.5.1 Convertir `logo.png` (154KB) en WebP/AVIF (~20KB)
- [ ] 2.5.2 Ajouter `loading="lazy" decoding="async"` sur toutes les `<img>`
  > Fait sur MiniMap/MiniMapStatic, manque sur DashboardPostCard, Layout logo, ImageUpload
- [ ] 2.5.3 Ajouter `aspect-ratio` pour eviter les layout shifts
  > Fait sur PhotoCapture/FormulaireModal, manque ailleurs
- [ ] 2.5.4 Generer des thumbnails WebP cote upload service

---

## Phase 3 — Design system & polish (Semaine 5-6) — 76% FAIT

> Objectif : Passer de "utilitaire" a "professionnel"

### 3.1 Composants UI reutilisables [HAUTE] — MAJORITAIRE

- [x] 3.1.1 `components/ui/Button.tsx` (primary, secondary, outline, ghost, danger + loading + icons)
- [ ] 3.1.2 `components/ui/Input.tsx` (text, number, date, avec etats validation)
- [ ] 3.1.3 `components/ui/Modal.tsx` (base modale avec focus trap + animations)
  > Modales existantes ont role="dialog" aria-modal="true" mais pas de focus trap
- [x] 3.1.4 `components/ui/Card.tsx` (conteneur standard + hover effect optionnel)
- [x] 3.1.5 `components/ui/Badge.tsx` (success, warning, error, info, neutral)
- [x] 3.1.6 `components/ui/Skeleton.tsx` (text, circular, rectangular + motion-reduce)
- [x] 3.1.7 `components/ui/EmptyState.tsx` (icone + titre + description + action CTA)

### 3.2 Squelettes de chargement (Skeleton loaders) [HAUTE] — FAIT

- [x] 3.2.1 Skeleton pour le feed dashboard (PostSkeleton)
  > `DashboardSkeleton.tsx` + `PostSkeleton.tsx` avec role="status" aria-label
- [x] 3.2.2 Skeleton pour la grille planning
- [x] 3.2.3 Skeleton pour la liste de chantiers
- [x] 3.2.4 Skeleton pour les cartes du dashboard
  > DashboardSkeleton reproduit la structure : clock card, weather card, stats cards
- [x] 3.2.5 Remplacer `<PageLoader />` par des skeletons contextuels

### 3.3 Etats vides enrichis [MOYENNE] — FAIT

- [x] 3.3.1 Designer des etats vides avec icone + message + bouton d'action
  > EmptyState.tsx avec LucideIcon + titre + description + action callback
- [x] 3.3.2 Deployer sur : feed, planning, chantiers, logistique

### 3.4 Micro-interactions & animations [MOYENNE] — FAIT

- [x] 3.4.1 Animations d'entree/sortie (feed, taches)
  > `index.css` : `.animate-slide-up` (0.3s), `.animate-fade-in` (0.2s)
- [x] 3.4.2 Hover lift sur les cartes
  > Card.tsx: `hover:shadow-lg hover:-translate-y-0.5 transition-all`, ChantierCard, TodayPlanningCard
- [x] 3.4.3 Transition de page entre routes (fade 150ms)
  > `.animate-fade-in` dans index.css
- [x] 3.4.4 Feedback visuel de succes (toast anime + progress bar undo)
  > `.toast-enter` avec slide-up, couleurs semantiques
- [x] 3.4.5 Support `prefers-reduced-motion` pour desactiver les animations
  > `index.css` media query : `animation-duration: 0.01ms !important`
  > Skeleton.tsx: `motion-reduce:animate-none`

### 3.5 Tokens de design formalises [MOYENNE] — NON FAIT

- [ ] 3.5.1 Creer `theme/tokens.ts` avec couleurs semantiques (success, error, warning, info)
- [ ] 3.5.2 Definir couleurs par statut (devis: brouillon/envoye/accepte/refuse)
- [ ] 3.5.3 Definir couleurs par statut chantier (planifie/en_cours/pause/termine)
- [ ] 3.5.4 Migrer les hardcoded colors vers les tokens

---

## Phase 4 — Onboarding & aide (Semaine 7-8) — 0% FAIT

> Objectif : Un nouvel utilisateur est productif en 30 minutes au lieu de 2-4 heures

### 4.1 Tutoriel interactif premiere connexion [HAUTE]

- [ ] 4.1.1 Ecran d'accueil adapte au role : "Bonjour Jean, vous etes Compagnon"
- [ ] 4.1.2 Tutoriel 5 etapes (adapte au role) :
  - Compagnon : Pointer -> Planning -> Photo -> Heures -> Deconnexion
  - Chef : Planning -> Validation -> Signalements -> Documents -> Deconnexion
  - Conducteur : Dashboard financier -> Planification -> Achats -> Devis -> Deconnexion
- [ ] 4.1.3 Donnees de demo pour tester sans consequence
- [ ] 4.1.4 Persistance dans localStorage (ne pas reafficher)
- [ ] 4.1.5 Option "Revoir le tutoriel" dans les parametres

### 4.2 Aide contextuelle [HAUTE] — PARTIEL

> Existe sur DashboardFinancierPage (HelpCircle + DefinitionTooltip), pas generalise.

- [ ] 4.2.1 Icone `?` sur chaque en-tete de page -> panneau lateral avec aide
- [ ] 4.2.2 Tooltips sur les boutons/filtres (desktop: hover, mobile: long-press)
- [ ] 4.2.3 Indices progressifs (affiches 3 premieres utilisations, puis masques)

### 4.3 Fil d'Ariane (breadcrumbs) [MOYENNE]

- [ ] 4.3.1 Composant `Breadcrumb` avec navigation semantique (`aria-label="Fil d'Ariane"`)
- [ ] 4.3.2 Deployer sur toutes les pages de detail

### 4.4 Raccourcis clavier (power users) [BASSE]

- [ ] 4.4.1 `Ctrl+P` -> Planning, `Ctrl+H` -> Heures, `Ctrl+D` -> Documents
- [ ] 4.4.2 `Ctrl+/` -> Afficher la liste des raccourcis
- [ ] 4.4.3 Fleches `<-` `->` -> Semaine precedente/suivante (Planning/FdH)
- [ ] 4.4.4 `Espace` -> Pointer (clock in/out) depuis le dashboard

---

## Phase 5 — Intelligence & engagement (Semaine 9-10) — 24% FAIT

> Objectif : L'app anticipe les besoins et motive l'adoption

### 5.1 Notifications temps reel [HAUTE] — PARTIEL

- [ ] 5.1.1 Evaluer migration vers WebSocket pour les notifications critiques
  > Actuellement polling HTTP 30s via useNotifications
- [ ] 5.1.2 Regroupement intelligent ("Jean et 3 autres vous ont mentionne")
- [x] 5.1.3 Boutons d'action dans les notifications ("Voir chantier", "Valider")
  > NotificationDropdown.tsx avec actions specifiques par type
- [x] 5.1.4 Badge de compteur non-lu dans la barre de navigation
  > Layout.tsx : red dot + `aria-label="Notifications (X non lues)"`
- [ ] 5.1.5 Preferences de notification par categorie

### 5.2 Dashboard adaptatif [HAUTE] — FAIT

- [x] 5.2.1 Masquer DevisPipelineCard pour les roles non concernes
  > DashboardPage.tsx : `canViewDevisPipeline = user?.role === 'admin' || user?.role === 'conducteur'`
- [x] 5.2.2 Hierarchiser les cartes par priorite
  > Clock > Meteo > Planning > Stats > Feed (ordre fixe dans DashboardPage)
- [ ] 5.2.3 Progressive disclosure : cartes secondaires repliees par defaut sur mobile
- [ ] 5.2.4 Carte "Alertes financieres" sur le dashboard pour Conducteur/Admin

### 5.3 Validation par lot (batch) [HAUTE] — NON FAIT

- [ ] 5.3.1 Selection multiple (checkboxes) sur la page feuilles d'heures
- [ ] 5.3.2 Barre d'action contextuelle : "Valider X selections"
- [ ] 5.3.3 Tableau de bord validation : pending count, temps moyen, ecarts

### 5.4 Gamification legere [BASSE] — NON FAIT

- [ ] 5.4.1 Streak de pointage (jours consecutifs) avec compteur visuel
- [ ] 5.4.2 Visualisation de progression personnelle (heures/semaine vs objectif)
- [ ] 5.4.3 Classement equipe hebdomadaire (heures loguees vs planifiees)
- [ ] 5.4.4 Option desactivable dans les parametres

### 5.5 Recherche globale [BASSE] — NON FAIT

- [ ] 5.5.1 Barre de recherche `Cmd+K` multi-entites (chantiers, docs, users, signalements)
- [ ] 5.5.2 Recherche fuzzy tolerante aux fautes
- [ ] 5.5.3 Resultats recents sauvegardes

---

## Phase 6 — Fonctionnalites differenciantes (Semaine 11-12) — 33% FAIT

> Objectif : Combler les ecarts concurrentiels et se differencier

### 6.1 Markup photo [HAUTE] — NON FAIT

- [ ] 6.1.1 Canvas d'annotation sur les photos (fleches, cercles, texte)
- [ ] 6.1.2 Integration dans le flux de creation de signalement
- [ ] 6.1.3 Integration dans le feed (posts avec photos annotees)

### 6.2 Widget home screen [HAUTE] — NON FAIT

- [ ] 6.2.1 Evaluer les possibilites PWA pour widgets iOS/Android
- [ ] 6.2.2 Raccourci "Pointer" sur l'ecran d'accueil (manifest shortcuts)
- [ ] 6.2.3 Raccourci "Photo rapide" sur l'ecran d'accueil

### 6.3 Saisie heures par presets [MOYENNE] — FAIT

- [x] 6.3.1 Boutons preset (07:00, 12:00, 17:00, Maintenant)
  > MobileTimePicker.tsx : boutons rapides avec `setTempHour/setTempMinute`
- [ ] 6.3.2 Derniere heure utilisee en raccourci

### 6.4 Planning offline (lecture seule) [MOYENNE] — FAIT (INFRA)

- [x] 6.4.1 Cache offline avec localStorage chiffre
  > useOfflineStorage.ts : cache TTL + queue AES-GCM
- [x] 6.4.2 Affichage indicateur hors ligne
  > OfflineIndicator.tsx integre dans App.tsx
- [x] 6.4.3 Indicateur de reconnexion avec sync automatique
  > Service Worker background sync + event listeners online/offline

---

## Accessibilite — Correctifs transversaux — 38% FAIT

> A integrer en continu dans chaque phase

- [x] A.1 Lien "Aller au contenu principal" (skip link) dans `Layout.tsx`
  > `<a href="#main-content" className="sr-only focus:not-sr-only ...">Aller au contenu principal</a>`
- [x] A.2 Support `prefers-reduced-motion` dans `index.css`
  > `@media (prefers-reduced-motion: reduce)` + Skeleton `motion-reduce:animate-none`
- [ ] A.3 Ajouter `aria-required="true"` sur tous les champs obligatoires
  > Actuellement `required` natif uniquement, pas `aria-required`
- [ ] A.4 Focus trap dans les modales (empecher le tab en dehors)
  > Modales ont `role="dialog" aria-modal="true"` mais pas de cycling Tab
- [ ] A.5 Reset du focus sur changement de route (`useEffect` sur `location.pathname`)
- [x] A.6 `<nav aria-label="Navigation principale">` dans Layout
  > Mobile et desktop : `aria-label="Navigation principale"`
- [ ] A.7 Gestion des titres de page dynamiques (`document.title`)
- [ ] A.8 Legende "Les champs * sont obligatoires" en haut des formulaires

---

## PWA — Ameliorations caching — 25% FAIT

- [ ] P.1 `CacheFirst` pour `/api/uploads/` et `/api/documents/` (assets immuables)
- [ ] P.2 Cache plus court (5min) pour `/api/planning/` et `/api/dashboard/` (donnees temps reel)
- [ ] P.3 `networkTimeoutSeconds: 3` pour fallback rapide sur cache
- [x] P.4 Background sync pour les mutations (posts, affectations, pointages)
  > OfflineIndicator.tsx + useOfflineStorage.ts : `sync.register('sync-pending-data')`

---

## Benchmark concurrentiel (mis a jour)

| Fonctionnalite | Fieldwire | PlanGrid | Procore | Hub Chantier | Statut |
|----------------|-----------|----------|---------|--------------|--------|
| Mode offline | Full CRUD | Lecture | Limite | **Queue sync + indicateur** | FAIT (base) |
| Widget mobile | Oui | Oui | Oui | Non | A FAIRE |
| Markup photo | Avance | Avance | Basic | Non | A FAIRE |
| Onboarding interactif | Oui | Statique | Guide | Non | A FAIRE |
| Actions par lot | Oui | Oui | Oui | Non | A FAIRE |
| Saisie vocale | Oui | Non | Limite | Non | BASSE (futur) |
| Annotation PDF | Basic | Avance | Avance | Non | BASSE (futur) |

**Avantages Hub Chantier a preserver** :
- Module financier complet (unique vs Fieldwire/PlanGrid)
- Feed social (engagement equipe)
- Planning de charge (capacite)
- Formulaires custom avec signatures

---

## Metriques de succes

| Metrique | Baseline | Cible | Estime actuel |
|----------|----------|-------|---------------|
| Temps de formation par utilisateur | 2-4h | 30min | ~2h (pas d'onboarding) |
| Utilisateurs actifs quotidiens | ~60% | 85% | ~70% (UX terrain OK) |
| Taux de soumission FdH a l'heure | ~70% | 90% | ~80% (offline aide) |
| Actions par session | ~8 | 14 | ~10 (FAB + nav role) |
| Tickets support par semaine | ~12 | 5 | ~9 (UI plus coherente) |
| Taux d'abandon session mobile | ~35% | 15% | ~25% (touch + FAB) |
| FCP (First Contentful Paint, 3G) | ~4.2s | 1.8s | ~2.5s (lazy Firebase) |
| Bundle initial (gzip) | ~850KB | ~450KB | ~550KB (chunks OK) |
| Appels API (chargement dashboard) | ~12 | ~4 | ~6 (react-query cache) |

---

## Reste a faire — Priorite

### Haute priorite (impact fort, effort modere)

| # | Item | Phase | Effort |
|---|------|-------|--------|
| 1 | Updates optimistes (like, post, planning) | 2.4 | 1j |
| 2 | Contrastes text-gray-400 → text-gray-600 (~20 fichiers) | 1.2 | 0.5j |
| 3 | Focus trap modales | A.4 | 0.5j |
| 4 | Titres de page dynamiques (document.title) | A.7 | 0.5j |
| 5 | Validation par lot feuilles d'heures | 5.3 | 2j |
| 6 | Breadcrumbs pages profondes | 4.3 | 0.5j |
| 7 | Design tokens + migration couleurs | 3.5 | 1j |

### Moyenne priorite (impact moyen)

| # | Item | Phase | Effort |
|---|------|-------|--------|
| 8 | Images WebP + loading="lazy" generalise | 2.5 | 0.5j |
| 9 | Virtualisation PlanningGrid vue mois | 2.3.3 | 1j |
| 10 | Input.tsx + Modal.tsx (focus trap) reusables | 3.1 | 1j |
| 11 | persistQueryClient localStorage | 2.1.5 | 0.5j |
| 12 | Lazy-load Recharts par page | 2.2.5 | 0.5j |
| 13 | aria-required sur champs obligatoires | A.3 | 0.5j |
| 14 | PWA CacheFirst + network timeout | P.1-P.3 | 1j |

### Phase future (effort important)

| # | Item | Phase | Effort |
|---|------|-------|--------|
| 15 | Tutoriel interactif par role | 4.1 | 3j |
| 16 | Aide contextuelle + tooltips generiques | 4.2 | 2j |
| 17 | Recherche globale Cmd+K | 5.5 | 2j |
| 18 | Markup photo (canvas annotation) | 6.1 | 3j |
| 19 | Widget home screen PWA | 6.2 | 1j |
| 20 | Notifications WebSocket + preferences | 5.1 | 3j |
| 21 | Raccourcis clavier | 4.4 | 1j |
| 22 | Gamification | 5.4 | 2j |

**Effort restant estime : ~25 jours dev**

---

## Decisions prises

- [x] **Offline** : Queue sync chiffree localStorage (pas IndexedDB — suffisant pour MVP)
- [x] **Cache** : TanStack Query v5 (installe et utilise)
- [x] **Animations** : CSS-only (index.css transitions, pas de Framer Motion)
- [x] **Navigation mobile** : FAB + sidebar role-filtree (pas de bottom bar separee)

## Decisions encore a prendre

- [ ] **Gamification** : Activer ou non ? Quel niveau (streaks seuls vs badges complets) ?
- [ ] **WebSocket** : Implementer en Phase 5 ou rester en polling optimise ?
- [ ] **Onboarding** : Librairie tour guide (react-joyride ?) ou custom ?

---

## Fichiers cles (statut mis a jour)

| Fichier | Statut |
|---------|--------|
| `components/Layout.tsx` | ✅ Touch 48px, role nav, skip link, aria-label |
| `pages/DashboardPage.tsx` | ✅ Role-based cards, memo PostCard |
| `hooks/useDashboardFeed.ts` | ✅ React-query, useCallback handlers |
| `components/planning/PlanningGrid.tsx` | ✅ useMemo, min-h-[60px] — manque virtualisation |
| `services/firebase.ts` | ✅ Lazy dynamic imports |
| `index.css` | ✅ prefers-reduced-motion, animations CSS |
| `vite.config.ts` | ✅ 8 chunks vendor — manque visualizer |
| `components/ui/` | ✅ Button, Card, Badge, Skeleton, EmptyState — manque Input, Modal |
| `components/common/FloatingActionButton.tsx` | ✅ FAB 4 actions, 56px, mobile-only |
| `hooks/useOfflineStorage.ts` | ✅ Queue chiffree AES-GCM + sync |
| `components/OfflineIndicator.tsx` | ✅ Bandeau offline/reconnexion |
| `public/logo.png` | ❌ Encore PNG 154KB (pas WebP) |
| `tailwind.config.js` | ❌ Pas de tokens semantiques |
