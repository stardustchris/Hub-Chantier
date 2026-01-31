# GAP-F4 : Analyse cas `allActive` vide (frontend)

**Date**: 2026-01-31
**Contexte**: Vérification de la gestion du cas où `allActive` est vide dans `useFeuillesHeures.ts`

---

## Résumé exécutif

**STATUT: ✅ OK - Correction mineure recommandée**

Le code gère déjà le cas `allActive.length === 0` de manière acceptable, mais une amélioration UX est recommandée pour clarifier la situation à l'utilisateur.

---

## Analyse du code actuel

### 1. Code analysé (`useFeuillesHeures.ts` lignes 76-81)

```typescript
// Par défaut : exclure admin/conducteur de la vue (ne travaillent pas sur chantier)
// Mais si un filtre est actif, respecter la sélection de l'utilisateur
const ROLES_CHANTIER = ['chef_chantier', 'compagnon']
const utilisateurIds = filterUtilisateurs.length > 0
  ? filterUtilisateurs
  : allActive.filter((u) => ROLES_CHANTIER.includes(u.role)).map((u) => Number(u.id))
```

### 2. Scénarios identifiés

#### Scénario A: `allActive` est vide (aucun utilisateur actif)
- **Résultat**: `utilisateurIds = []`
- **Appel API**: `pointagesService.getVueCompagnons(semaineDebut, [])`
- **Réponse backend attendue**: `[]` (tableau vide)
- **Affichage**: Message "Aucune donnee" (géré par `TimesheetGrid.tsx` lignes 139-149)

#### Scénario B: `allActive` contient uniquement des admin/conducteur
- **Résultat**: `utilisateurIds = []` (filtrage exclut ces rôles)
- **Comportement**: Identique au Scénario A
- **Problème UX**: L'utilisateur ne comprend pas pourquoi il ne voit rien alors qu'il y a des utilisateurs actifs

#### Scénario C: Filtre manuel activé avec `allActive` vide
- **Résultat**: `utilisateurIds = filterUtilisateurs` (peut être vide ou non)
- **Comportement**: Respecte le filtre de l'utilisateur

---

## Gestion actuelle des cas d'erreur

### ✅ Points positifs

1. **Gestion UI du tableau vide** (`TimesheetGrid.tsx` lignes 139-149):
```typescript
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
```

2. **Gestion des erreurs réseau** (`useFeuillesHeures.ts` lignes 102-106):
```typescript
catch (err) {
  logger.error('Erreur chargement feuilles heures', err, { context: 'FeuillesHeuresPage' })
  setError('Erreur lors du chargement des donnees')
}
```

3. **État de chargement** (`useFeuillesHeures.ts` ligne 36):
```typescript
const [loading, setLoading] = useState(true)
```

### ⚠️ Points d'amélioration

1. **Scénario B non distingué**: Quand `allActive` contient uniquement des admin/conducteur, le message "Aucune donnée" est trompeur car il y a des utilisateurs, mais ils sont filtrés par design.

2. **Pas de message informatif**: L'utilisateur ne sait pas qu'il peut utiliser les filtres pour afficher les admin/conducteur s'il le souhaite.

---

## Proposition de correction

### Option 1: Message contextuel (RECOMMANDÉE)

Améliorer le message affiché quand `vueCompagnons` est vide en distinguant les cas:

**Localisation**: `useFeuillesHeures.ts` ligne 73 ou `TimesheetGrid.tsx`

```typescript
// Dans useFeuillesHeures.ts, ajouter un état
const [emptyReason, setEmptyReason] = useState<'no-users' | 'filtered' | 'no-data'>('no-data')

// Après le chargement des utilisateurs (ligne 73)
if (allActive.length === 0) {
  setEmptyReason('no-users')
} else if (utilisateurIds.length === 0 && filterUtilisateurs.length === 0) {
  setEmptyReason('filtered')
} else {
  setEmptyReason('no-data')
}

// Passer emptyReason à TimesheetGrid
```

**Dans `TimesheetGrid.tsx`** (modifier lignes 139-149):

```typescript
if (vueCompagnons.length === 0) {
  const messages = {
    'no-users': {
      title: 'Aucun utilisateur actif',
      text: 'Il n\'y a aucun utilisateur actif dans le système. Contactez un administrateur.',
    },
    'filtered': {
      title: 'Aucun compagnon ou chef de chantier',
      text: 'Seuls les compagnons et chefs de chantier sont affichés par défaut. Utilisez les filtres pour afficher d\'autres rôles.',
    },
    'no-data': {
      title: 'Aucune donnée',
      text: 'Aucun pointage pour cette semaine. Sélectionnez des utilisateurs ou ajoutez des pointages.',
    },
  }

  const message = messages[emptyReason] || messages['no-data']

  return (
    <div className="bg-white rounded-lg shadow p-8 text-center">
      <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">{message.title}</h3>
      <p className="text-gray-600">{message.text}</p>
    </div>
  )
}
```

### Option 2: Détection automatique dans TimesheetGrid (PLUS SIMPLE)

Modifier uniquement `TimesheetGrid.tsx` pour accepter la liste `utilisateurs`:

```typescript
interface TimesheetGridProps {
  currentDate: Date
  vueCompagnons: VueCompagnon[]
  utilisateurs: User[]  // NOUVEAU
  onCellClick: (utilisateurId: number, chantierId: number | null, date: Date) => void
  onPointageClick: (pointage: Pointage) => void
  showWeekend?: boolean
  canEdit?: boolean
}

// Dans le rendu
if (vueCompagnons.length === 0) {
  const hasUsers = utilisateurs.length > 0
  const hasChantierUsers = utilisateurs.some(u => ['chef_chantier', 'compagnon'].includes(u.role))

  let message = {
    title: 'Aucune donnée',
    text: 'Aucun pointage pour cette semaine. Sélectionnez des utilisateurs ou ajoutez des pointages.',
  }

  if (!hasUsers) {
    message = {
      title: 'Aucun utilisateur actif',
      text: 'Il n\'y a aucun utilisateur actif dans le système. Contactez un administrateur.',
    }
  } else if (!hasChantierUsers) {
    message = {
      title: 'Aucun compagnon ou chef de chantier',
      text: 'Seuls les compagnons et chefs de chantier sont affichés par défaut. Utilisez les filtres pour afficher d\'autres rôles.',
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

## Tests recommandés

### Tests unitaires à ajouter

1. **Test `useFeuillesHeures.test.ts`**:
```typescript
it('devrait gérer le cas allActive vide', async () => {
  vi.mocked(usersService.list).mockResolvedValue({
    items: [],
    total: 0,
    page: 1,
    size: 100,
    pages: 0,
  })

  const { result } = renderHook(() => useFeuillesHeures())
  await waitFor(() => expect(result.current.loading).toBe(false))

  expect(result.current.vueCompagnons).toEqual([])
  expect(result.current.utilisateurs).toEqual([])
})

it('devrait gérer le cas avec uniquement admin/conducteur', async () => {
  vi.mocked(usersService.list).mockResolvedValue({
    items: [
      { id: '1', role: 'admin', is_active: true, /* ... */ },
      { id: '2', role: 'conducteur', is_active: true, /* ... */ },
    ],
    total: 2,
    page: 1,
    size: 100,
    pages: 1,
  })

  const { result } = renderHook(() => useFeuillesHeures())
  await waitFor(() => expect(result.current.loading).toBe(false))

  expect(result.current.utilisateurs).toHaveLength(2)
  expect(result.current.vueCompagnons).toEqual([])
})
```

2. **Test `TimesheetGrid.test.tsx`**:
```typescript
it('devrait afficher un message approprié quand vueCompagnons est vide', () => {
  render(
    <TimesheetGrid
      currentDate={new Date()}
      vueCompagnons={[]}
      utilisateurs={[]}
      onCellClick={vi.fn()}
      onPointageClick={vi.fn()}
    />
  )

  expect(screen.getByText('Aucun utilisateur actif')).toBeInTheDocument()
})

it('devrait afficher un message approprié quand seuls admin/conducteur existent', () => {
  const users = [
    { id: '1', role: 'admin', is_active: true, /* ... */ },
  ]

  render(
    <TimesheetGrid
      currentDate={new Date()}
      vueCompagnons={[]}
      utilisateurs={users}
      onCellClick={vi.fn()}
      onPointageClick={vi.fn()}
    />
  )

  expect(screen.getByText('Aucun compagnon ou chef de chantier')).toBeInTheDocument()
})
```

---

## Recommandations finales

### Priorité 1 (MAINTENANT)
- ✅ **Aucune action bloquante requise** - Le code gère déjà le cas de base

### Priorité 2 (AMÉLIORATION UX)
- Implémenter **Option 2** (plus simple, moins de changements)
- Ajouter les tests unitaires recommandés
- Vérifier le comportement avec `TimesheetChantierGrid` (vue par chantiers)

### Priorité 3 (BONUS)
- Ajouter un lien direct vers la page de création d'utilisateur dans le message "Aucun utilisateur actif"
- Ajouter un lien vers les filtres dans le message "Aucun compagnon ou chef de chantier"

---

## Conclusion

**Le code actuel ne présente PAS de bug critique**. Le cas `allActive === []` est géré correctement:
- ✅ Pas de crash
- ✅ Message affiché à l'utilisateur
- ✅ API appelée avec tableau vide (comportement valide)

**Cependant**, une amélioration UX est fortement recommandée pour distinguer les cas:
1. Aucun utilisateur actif (problème de configuration)
2. Aucun utilisateur avec rôle "chantier" (comportement normal, filtres disponibles)
3. Pas de pointage pour la semaine (situation normale)

**Action recommandée**: Implémenter Option 2 pour améliorer l'expérience utilisateur.
