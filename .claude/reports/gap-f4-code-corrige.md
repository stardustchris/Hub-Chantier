# GAP-F4 : Code corrigé - Amélioration UX pour `allActive` vide

**Date**: 2026-01-31
**Option retenue**: Option 2 (modification minimale)

---

## Changements à appliquer

### 1. Modifier `TimesheetGrid.tsx`

**Fichier**: `/Users/aptsdae/Hub-Chantier/frontend/src/components/pointages/TimesheetGrid.tsx`

#### Changement 1: Ajouter `utilisateurs` à l'interface Props

```typescript
// AVANT (ligne 8-15)
interface TimesheetGridProps {
  currentDate: Date
  vueCompagnons: VueCompagnon[]
  onCellClick: (utilisateurId: number, chantierId: number | null, date: Date) => void
  onPointageClick: (pointage: Pointage) => void
  showWeekend?: boolean
  canEdit?: boolean
}

// APRÈS
interface TimesheetGridProps {
  currentDate: Date
  vueCompagnons: VueCompagnon[]
  utilisateurs: User[]  // NOUVEAU
  onCellClick: (utilisateurId: number, chantierId: number | null, date: Date) => void
  onPointageClick: (pointage: Pointage) => void
  showWeekend?: boolean
  canEdit?: boolean
}
```

#### Changement 2: Ajouter import de User

```typescript
// AVANT (ligne 5)
import type { VueCompagnon, Pointage, StatutPointage } from '../../types'

// APRÈS
import type { VueCompagnon, Pointage, StatutPointage, User } from '../../types'
```

#### Changement 3: Ajouter `utilisateurs` au destructuring

```typescript
// AVANT (ligne 17-24)
export default function TimesheetGrid({
  currentDate,
  vueCompagnons,
  onCellClick,
  onPointageClick,
  showWeekend = false,
  canEdit = false,
}: TimesheetGridProps) {

// APRÈS
export default function TimesheetGrid({
  currentDate,
  vueCompagnons,
  utilisateurs,  // NOUVEAU
  onCellClick,
  onPointageClick,
  showWeekend = false,
  canEdit = false,
}: TimesheetGridProps) {
```

#### Changement 4: Améliorer le message d'état vide

```typescript
// AVANT (lignes 139-149)
if (vueCompagnons.length === 0) {
  return (
    <div className="bg-white rounded-lg shadow p-8 text-center">
      <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune donnee</h3>
      <p className="text-gray-600">
        Aucun pointage pour cette semaine. Selectionnez des utilisateurs ou ajoutez des pointages.
      </p>
    </div>
  )
}

// APRÈS
if (vueCompagnons.length === 0) {
  // Déterminer la raison du tableau vide
  const hasUsers = utilisateurs.length > 0
  const hasChantierUsers = utilisateurs.some(u =>
    u.role === 'chef_chantier' || u.role === 'compagnon'
  )

  let message = {
    title: 'Aucune donnee',
    text: 'Aucun pointage pour cette semaine. Selectionnez des utilisateurs ou ajoutez des pointages.',
  }

  if (!hasUsers) {
    message = {
      title: 'Aucun utilisateur actif',
      text: 'Il n\'y a aucun utilisateur actif dans le systeme. Contactez un administrateur pour creer des utilisateurs.',
    }
  } else if (!hasChantierUsers) {
    message = {
      title: 'Aucun compagnon ou chef de chantier',
      text: 'Seuls les compagnons et chefs de chantier sont affiches par defaut. Utilisez les filtres ci-dessus pour afficher d\'autres roles.',
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-8 text-center">
      <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">{message.title}</h3>
      <p className="text-gray-600">{message.text}</p>
    </div>
  )
}
```

---

### 2. Modifier `FeuillesHeuresPage.tsx`

**Fichier**: `/Users/aptsdae/Hub-Chantier/frontend/src/pages/FeuillesHeuresPage.tsx`

#### Changement: Passer `utilisateurs` à TimesheetGrid

```typescript
// AVANT (lignes 189-197)
) : fh.viewTab === 'compagnons' ? (
  <TimesheetGrid
    currentDate={fh.currentDate}
    vueCompagnons={fh.vueCompagnons}
    onCellClick={fh.handleCellClick}
    onPointageClick={fh.handlePointageClick}
    showWeekend={fh.showWeekend}
    canEdit={fh.canEdit}
  />

// APRÈS
) : fh.viewTab === 'compagnons' ? (
  <TimesheetGrid
    currentDate={fh.currentDate}
    vueCompagnons={fh.vueCompagnons}
    utilisateurs={fh.utilisateurs}  // NOUVEAU
    onCellClick={fh.handleCellClick}
    onPointageClick={fh.handlePointageClick}
    showWeekend={fh.showWeekend}
    canEdit={fh.canEdit}
  />
```

---

### 3. Même traitement pour `TimesheetChantierGrid.tsx`

**Fichier**: `/Users/aptsdae/Hub-Chantier/frontend/src/components/pointages/TimesheetChantierGrid.tsx`

Pour cohérence, appliquer le même pattern au composant vue par chantiers.

#### Localiser la gestion du tableau vide

```bash
# Vérifier si le composant a déjà une gestion du tableau vide
grep -n "vueChantiers.length === 0" frontend/src/components/pointages/TimesheetChantierGrid.tsx
```

Si oui, appliquer la même logique:
1. Ajouter `chantiers: Chantier[]` aux props
2. Ajouter import de `Chantier` type
3. Améliorer le message si `chantiers.length === 0`

---

## Tests à ajouter/modifier

### 1. `TimesheetGrid.test.tsx`

**Fichier**: `/Users/aptsdae/Hub-Chantier/frontend/src/components/pointages/TimesheetGrid.test.tsx`

```typescript
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import TimesheetGrid from './TimesheetGrid'
import type { VueCompagnon, User } from '../../types'

describe('TimesheetGrid - Empty States', () => {
  const mockOnCellClick = vi.fn()
  const mockOnPointageClick = vi.fn()
  const currentDate = new Date('2026-01-27')

  it('affiche message "Aucun utilisateur actif" quand utilisateurs est vide', () => {
    render(
      <BrowserRouter>
        <TimesheetGrid
          currentDate={currentDate}
          vueCompagnons={[]}
          utilisateurs={[]}
          onCellClick={mockOnCellClick}
          onPointageClick={mockOnPointageClick}
        />
      </BrowserRouter>
    )

    expect(screen.getByText('Aucun utilisateur actif')).toBeInTheDocument()
    expect(screen.getByText(/Il n'y a aucun utilisateur actif dans le systeme/)).toBeInTheDocument()
  })

  it('affiche message spécifique quand seuls admin/conducteur existent', () => {
    const users: User[] = [
      {
        id: '1',
        email: 'admin@test.com',
        nom: 'Admin',
        prenom: 'Test',
        role: 'admin',
        type_utilisateur: 'employe',
        is_active: true,
        created_at: '2026-01-01',
      },
      {
        id: '2',
        email: 'conducteur@test.com',
        nom: 'Conducteur',
        prenom: 'Test',
        role: 'conducteur',
        type_utilisateur: 'employe',
        is_active: true,
        created_at: '2026-01-01',
      },
    ]

    render(
      <BrowserRouter>
        <TimesheetGrid
          currentDate={currentDate}
          vueCompagnons={[]}
          utilisateurs={users}
          onCellClick={mockOnCellClick}
          onPointageClick={mockOnPointageClick}
        />
      </BrowserRouter>
    )

    expect(screen.getByText('Aucun compagnon ou chef de chantier')).toBeInTheDocument()
    expect(screen.getByText(/Seuls les compagnons et chefs de chantier/)).toBeInTheDocument()
  })

  it('affiche message "Aucune donnee" quand utilisateurs chantier existent mais pas de pointages', () => {
    const users: User[] = [
      {
        id: '1',
        email: 'compagnon@test.com',
        nom: 'Dupont',
        prenom: 'Jean',
        role: 'compagnon',
        type_utilisateur: 'employe',
        is_active: true,
        created_at: '2026-01-01',
      },
    ]

    render(
      <BrowserRouter>
        <TimesheetGrid
          currentDate={currentDate}
          vueCompagnons={[]}
          utilisateurs={users}
          onCellClick={mockOnCellClick}
          onPointageClick={mockOnPointageClick}
        />
      </BrowserRouter>
    )

    expect(screen.getByText('Aucune donnee')).toBeInTheDocument()
    expect(screen.getByText(/Aucun pointage pour cette semaine/)).toBeInTheDocument()
  })

  it('affiche la grille normalement quand vueCompagnons contient des données', () => {
    const users: User[] = [
      {
        id: '1',
        email: 'compagnon@test.com',
        nom: 'Dupont',
        prenom: 'Jean',
        role: 'compagnon',
        type_utilisateur: 'employe',
        is_active: true,
        created_at: '2026-01-01',
      },
    ]

    const vueCompagnons: VueCompagnon[] = [
      {
        utilisateur_id: 1,
        utilisateur_nom: 'Jean Dupont',
        total_heures: '35:00',
        total_heures_decimal: 35,
        chantiers: [],
        totaux_par_jour: {},
      },
    ]

    render(
      <BrowserRouter>
        <TimesheetGrid
          currentDate={currentDate}
          vueCompagnons={vueCompagnons}
          utilisateurs={users}
          onCellClick={mockOnCellClick}
          onPointageClick={mockOnPointageClick}
        />
      </BrowserRouter>
    )

    expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
    expect(screen.queryByText('Aucune donnee')).not.toBeInTheDocument()
  })
})
```

---

### 2. `FeuillesHeuresPage.test.tsx`

**Fichier**: `/Users/aptsdae/Hub-Chantier/frontend/src/pages/FeuillesHeuresPage.test.tsx`

Vérifier que le composant passe bien la prop `utilisateurs`:

```typescript
it('passe la prop utilisateurs à TimesheetGrid', async () => {
  const mockUsers = [
    { id: '1', role: 'compagnon', is_active: true, /* ... */ },
  ]

  vi.mocked(usersService.list).mockResolvedValue({
    items: mockUsers,
    total: 1,
    page: 1,
    size: 100,
    pages: 1,
  })

  render(
    <MemoryRouter>
      <AuthProvider>
        <FeuillesHeuresPage />
      </AuthProvider>
    </MemoryRouter>
  )

  await waitFor(() => {
    expect(screen.queryByText(/Chargement/)).not.toBeInTheDocument()
  })

  // Vérifier que TimesheetGrid reçoit bien les utilisateurs
  // (nécessite un spy ou vérification indirecte)
})
```

---

## Résumé des fichiers modifiés

| Fichier | Type de modification | Priorité |
|---------|---------------------|----------|
| `TimesheetGrid.tsx` | Amélioration UX (message contextuel) | 🟡 Moyenne |
| `FeuillesHeuresPage.tsx` | Ajout prop `utilisateurs` | 🟡 Moyenne |
| `TimesheetGrid.test.tsx` | Ajout tests empty states | 🟢 Basse |
| `TimesheetChantierGrid.tsx` | Amélioration UX (optionnel) | 🟢 Basse |

---

## Commandes pour appliquer les changements

```bash
# 1. Appliquer les modifications manuellement ou via Edit tool

# 2. Lancer les tests
cd frontend
npm run test TimesheetGrid.test.tsx
npm run test FeuillesHeuresPage.test.tsx

# 3. Lancer le linter
npm run lint

# 4. Build de vérification
npm run build
```

---

## Conclusion

Ces modifications sont **non-bloquantes** mais **fortement recommandées** pour améliorer l'expérience utilisateur. Elles clarifient les 3 cas possibles de tableau vide:
1. ❌ Problème de configuration (aucun utilisateur actif)
2. ℹ️ Comportement normal (filtrage automatique des admin/conducteur)
3. ✅ Situation normale (pas de pointages cette semaine)
