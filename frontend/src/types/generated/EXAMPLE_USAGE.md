# Exemples d'utilisation des types générés

Ce fichier contient des exemples d'utilisation des types générés depuis l'API.

> **Note**: Ces exemples utilisent la structure supposée des types. Une fois les types générés via `npm run generate:types`, vous pourrez voir la structure réelle dans `api.ts`.

## Import de base

```typescript
import type { paths, components } from '@/types/generated'
```

## Utilisation des schémas (components)

Les schémas Pydantic du backend sont disponibles sous `components.schemas`:

```typescript
// Type User depuis le modèle Pydantic
type User = components['schemas']['User']

// Type Chantier
type Chantier = components['schemas']['Chantier']

// Type pour créer un chantier
type ChantierCreate = components['schemas']['ChantierCreate']

// Type pour mettre à jour un chantier
type ChantierUpdate = components['schemas']['ChantierUpdate']

// Exemple d'utilisation dans un composant
function UserProfile({ user }: { user: User }) {
  return (
    <div>
      <h1>{user.prenom} {user.nom}</h1>
      <p>Email: {user.email}</p>
      <p>Rôle: {user.role}</p>
    </div>
  )
}
```

## Utilisation des endpoints (paths)

Les types de requêtes et réponses par endpoint:

```typescript
// Type de la réponse GET /v1/chantiers
type GetChantiersResponse =
  paths['/v1/chantiers']['get']['responses']['200']['content']['application/json']

// Type de la requête POST /v1/chantiers
type CreateChantierRequest =
  paths['/v1/chantiers']['post']['requestBody']['content']['application/json']

// Type de la réponse d'erreur 422 (validation)
type ValidationError =
  paths['/v1/chantiers']['post']['responses']['422']['content']['application/json']
```

## Avec axios et React Query

```typescript
import axios from 'axios'
import { useQuery, useMutation } from '@tanstack/react-query'
import type { components } from '@/types/generated'

type Chantier = components['schemas']['Chantier']
type ChantierCreate = components['schemas']['ChantierCreate']

// GET - Liste des chantiers
export function useChantiers() {
  return useQuery<Chantier[]>({
    queryKey: ['chantiers'],
    queryFn: async () => {
      const { data } = await axios.get<Chantier[]>('/api/v1/chantiers')
      return data
    }
  })
}

// POST - Créer un chantier
export function useCreateChantier() {
  return useMutation({
    mutationFn: async (chantier: ChantierCreate) => {
      const { data } = await axios.post<Chantier>(
        '/api/v1/chantiers',
        chantier
      )
      return data
    }
  })
}

// Dans un composant
function ChantierForm() {
  const createChantier = useCreateChantier()

  const handleSubmit = (formData: ChantierCreate) => {
    createChantier.mutate(formData, {
      onSuccess: (newChantier) => {
        console.log('Chantier créé:', newChantier.id)
      }
    })
  }

  return <form onSubmit={handleSubmit}>...</form>
}
```

## Avec type guards et validation

```typescript
import type { components } from '@/types/generated'

type User = components['schemas']['User']

// Type guard pour vérifier si un objet est un User valide
function isUser(obj: unknown): obj is User {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'email' in obj &&
    'nom' in obj &&
    'prenom' in obj &&
    'role' in obj
  )
}

// Utilisation
const data: unknown = await fetchUser()

if (isUser(data)) {
  // TypeScript sait maintenant que data est de type User
  console.log(data.email)
} else {
  console.error('Format utilisateur invalide')
}
```

## Extraction de types utilitaires

```typescript
import type { components } from '@/types/generated'

// Extraire le type d'un role
type User = components['schemas']['User']
type UserRole = User['role']  // 'admin' | 'conducteur' | 'chef_chantier' | 'compagnon'

// Extraire le type d'un statut de chantier
type Chantier = components['schemas']['Chantier']
type ChantierStatut = Chantier['statut']

// Créer un type pour un sous-ensemble de propriétés
type UserIdentity = Pick<User, 'id' | 'nom' | 'prenom' | 'email'>

// Créer un type sans certaines propriétés
type UserWithoutDates = Omit<User, 'created_at' | 'updated_at'>

// Rendre toutes les propriétés optionnelles
type PartialUser = Partial<User>
```

## Avec les enum et constantes

```typescript
import type { components } from '@/types/generated'

type User = components['schemas']['User']

// Fonction avec contrainte de type
function getUserLabel(role: User['role']): string {
  const labels: Record<User['role'], string> = {
    admin: 'Administrateur',
    conducteur: 'Conducteur de travaux',
    chef_chantier: 'Chef de chantier',
    compagnon: 'Compagnon'
  }
  return labels[role]
}

// Utilisation
const role: User['role'] = 'admin'
console.log(getUserLabel(role))  // "Administrateur"
```

## Gestion d'erreurs typées

```typescript
import type { components } from '@/types/generated'

type HTTPValidationError = components['schemas']['HTTPValidationError']

async function createChantier(data: ChantierCreate) {
  try {
    const response = await axios.post('/api/v1/chantiers', data)
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 422) {
      // TypeScript sait que c'est une erreur de validation
      const validationError = error.response.data as HTTPValidationError

      // Afficher les erreurs de validation
      validationError.detail?.forEach(err => {
        console.error(`Erreur sur ${err.loc}: ${err.msg}`)
      })
    }
    throw error
  }
}
```

## Types pour les formulaires

```typescript
import type { components } from '@/types/generated'
import { useForm } from 'react-hook-form'

type ChantierCreate = components['schemas']['ChantierCreate']

function ChantierForm() {
  const { register, handleSubmit } = useForm<ChantierCreate>({
    defaultValues: {
      nom: '',
      adresse: '',
      code_chantier: '',
      statut: 'en_attente'
    }
  })

  const onSubmit = (data: ChantierCreate) => {
    // data est automatiquement typé
    console.log(data.nom, data.adresse)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('nom')} />
      <input {...register('adresse')} />
      {/* Auto-complétion sur tous les champs */}
    </form>
  )
}
```

## Migration depuis les types manuels

```typescript
// AVANT (types manuels dans types/index.ts)
import { User, Chantier } from '@/types'

// APRÈS (types générés)
import type { components } from '@/types/generated'

type User = components['schemas']['User']
type Chantier = components['schemas']['Chantier']
```

## Astuces

### 1. Créer des alias pour simplifier les imports

```typescript
// types/aliases.ts
import type { components } from './generated'

// Alias pour les schémas principaux
export type User = components['schemas']['User']
export type Chantier = components['schemas']['Chantier']
export type Affectation = components['schemas']['Affectation']
export type FeuilleHeures = components['schemas']['FeuilleHeures']

// Puis dans vos composants
import { User, Chantier } from '@/types/aliases'
```

### 2. Utiliser des helper types pour les listes paginées

```typescript
type PaginatedResponse<T> = {
  items: T[]
  total: number
  limit: number
  offset: number
}

// Exemple
type PaginatedChantiers = PaginatedResponse<Chantier>
```

### 3. Combiner avec Zod pour validation runtime

```typescript
import { z } from 'zod'
import type { components } from '@/types/generated'

type ChantierCreate = components['schemas']['ChantierCreate']

// Schéma Zod basé sur le type généré
const chantierCreateSchema = z.object({
  nom: z.string().min(1),
  adresse: z.string().min(1),
  code_chantier: z.string().optional(),
  // ... autres champs
}) satisfies z.ZodType<ChantierCreate>
```

## Prochaines étapes

1. Générer les types: `npm run generate:types`
2. Explorer le fichier `api.ts` généré
3. Commencer à remplacer les imports de `@/types` par `@/types/generated`
4. Ajouter des alias dans `types/aliases.ts` pour simplifier
5. Mettre à jour progressivement les composants existants
