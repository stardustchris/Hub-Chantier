/**
 * Tests pour UsersListPage
 * CDC Section 3 - Gestion des Utilisateurs
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import UsersListPage from './UsersListPage'
import type { User } from '../types'

// Mock services
vi.mock('../services/users', () => ({
  usersService: {
    list: vi.fn(),
    create: vi.fn(),
    activate: vi.fn(),
    deactivate: vi.fn(),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

// Mock user for auth context
let mockCurrentUser: User | null = null

vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: mockCurrentUser,
    isAuthenticated: !!mockCurrentUser,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
  }),
}))

// Mock Layout
vi.mock('../components/Layout', () => ({
  default: ({ children }: { children: React.ReactNode }) => <div data-testid="layout">{children}</div>,
}))

// Mock UserCard
vi.mock('../components/users', () => ({
  UserCard: ({ user, onToggleActive }: { user: User; onToggleActive: () => void }) => (
    <div data-testid={`user-${user.id}`}>
      <span>{user.prenom} {user.nom}</span>
      <button onClick={onToggleActive}>Toggle</button>
    </div>
  ),
  CreateUserModal: ({ onClose }: { onClose: () => void }) => (
    <div data-testid="create-modal">
      <button onClick={onClose}>Fermer</button>
    </div>
  ),
}))

import { usersService } from '../services/users'

const mockUsers: any[] = [
  {
    id: '1',
    email: 'admin@test.com',
    nom: 'Admin',
    prenom: 'Super',
    role: 'admin',
    type_utilisateur: 'employe',
    is_active: true,
    couleur: '#3498DB',
    created_at: '2024-01-01',
    updated_at: '2024-01-01',
  },
  {
    id: '2',
    email: 'conducteur@test.com',
    nom: 'Dupont',
    prenom: 'Jean',
    role: 'conducteur',
    type_utilisateur: 'employe',
    is_active: true,
    couleur: '#E74C3C',
    created_at: '2024-01-01',
    updated_at: '2024-01-01',
  },
  {
    id: '3',
    email: 'chef@test.com',
    nom: 'Martin',
    prenom: 'Pierre',
    role: 'chef_chantier',
    type_utilisateur: 'employe',
    is_active: false,
    couleur: '#2ECC71',
    created_at: '2024-01-01',
    updated_at: '2024-01-01',
  },
]

const adminUser: any = {
  id: '1',
  email: 'admin@test.com',
  nom: 'Admin',
  prenom: 'Super',
  role: 'admin',
  type_utilisateur: 'employe',
  is_active: true,
  couleur: '#3498DB',
  created_at: '2024-01-01',
  updated_at: '2024-01-01',
}

const conducteurUser: any = {
  id: '2',
  email: 'conducteur@test.com',
  nom: 'Dupont',
  prenom: 'Jean',
  role: 'conducteur',
  type_utilisateur: 'employe',
  is_active: true,
  couleur: '#E74C3C',
  created_at: '2024-01-01',
  updated_at: '2024-01-01',
}

const renderPage = (user: User = adminUser) => {
  mockCurrentUser = user
  return render(
    <MemoryRouter>
      <UsersListPage />
    </MemoryRouter>
  )
}

describe('UsersListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(usersService.list).mockResolvedValue({
      items: mockUsers,
      total: 3,
      page: 1,
      size: 12,
      pages: 1,
    })
  })

  describe('Rendu initial', () => {
    it('affiche le titre de la page', async () => {
      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Utilisateurs')).toBeInTheDocument()
        expect(screen.getByText('Gerez les membres de votre equipe')).toBeInTheDocument()
      })
    })

    it('charge et affiche les utilisateurs', async () => {
      renderPage()

      await waitFor(() => {
        expect(usersService.list).toHaveBeenCalled()
        expect(screen.getByTestId('user-1')).toBeInTheDocument()
        expect(screen.getByTestId('user-2')).toBeInTheDocument()
        expect(screen.getByTestId('user-3')).toBeInTheDocument()
      })
    })

    it('affiche les compteurs de role', async () => {
      renderPage()

      await waitFor(() => {
        // Les labels de role apparaissent dans les cartes de stats
        expect(screen.getAllByText('Administrateur').length).toBeGreaterThan(0)
        expect(screen.getAllByText('Conducteur de travaux').length).toBeGreaterThan(0)
        expect(screen.getAllByText('Chef de chantier').length).toBeGreaterThan(0)
        expect(screen.getAllByText('Compagnon').length).toBeGreaterThan(0)
      })
    })
  })

  describe('Bouton Nouvel utilisateur', () => {
    it('affiche le bouton pour un admin', async () => {
      renderPage(adminUser)

      await waitFor(() => {
        expect(screen.getByText('Nouvel utilisateur')).toBeInTheDocument()
      })
    })

    it('n\'affiche pas le bouton pour un non-admin', async () => {
      renderPage(conducteurUser)

      await waitFor(() => {
        expect(screen.queryByText('Nouvel utilisateur')).not.toBeInTheDocument()
      })
    })
  })

  describe('Recherche', () => {
    it('affiche le champ de recherche', async () => {
      renderPage()

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Rechercher un utilisateur...')).toBeInTheDocument()
      })
    })

    it('permet de saisir une recherche', async () => {
      renderPage()

      await waitFor(() => {
        const searchInput = screen.getByPlaceholderText('Rechercher un utilisateur...')
        fireEvent.change(searchInput, { target: { value: 'Dupont' } })
        expect(searchInput).toHaveValue('Dupont')
      })
    })
  })

  describe('Filtres', () => {
    it('affiche les selecteurs de filtre', async () => {
      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Tous les roles')).toBeInTheDocument()
        expect(screen.getByText('Tous')).toBeInTheDocument()
      })
    })

    it('filtre par role via le selecteur', async () => {
      const user = userEvent.setup()
      renderPage()

      await waitFor(() => {
        expect(screen.getAllByRole('combobox').length).toBeGreaterThan(0)
      })

      const selects = screen.getAllByRole('combobox')
      // Premier select = role
      await user.selectOptions(selects[0], 'conducteur')

      await waitFor(() => {
        expect(usersService.list).toHaveBeenCalledWith(
          expect.objectContaining({ role: 'conducteur' })
        )
      })
    })

    it('filtre par statut actif', async () => {
      const user = userEvent.setup()
      renderPage()

      await waitFor(() => {
        expect(screen.getAllByRole('combobox').length).toBeGreaterThan(1)
      })

      const selects = screen.getAllByRole('combobox')
      // Deuxieme select = actif
      await user.selectOptions(selects[1], 'active')

      await waitFor(() => {
        expect(usersService.list).toHaveBeenCalledWith(
          expect.objectContaining({ is_active: true })
        )
      })
    })

    it('filtre par role via les cartes de stats', async () => {
      renderPage()

      await waitFor(() => {
        // Attendre que les utilisateurs soient charges
        expect(screen.getByTestId('user-1')).toBeInTheDocument()
      })

      // Trouver la carte avec "Conducteur de travaux" et cliquer dessus
      const conducteurLabels = screen.getAllByText('Conducteur de travaux')
      const conducteurButton = conducteurLabels[0].closest('button')
      if (conducteurButton) {
        fireEvent.click(conducteurButton)
      }

      await waitFor(() => {
        expect(usersService.list).toHaveBeenCalledWith(
          expect.objectContaining({ role: 'conducteur' })
        )
      })
    })
  })

  describe('Etat vide', () => {
    it('affiche un message quand aucun utilisateur', async () => {
      vi.mocked(usersService.list).mockResolvedValue({
        items: [],
        total: 0,
        page: 1,
        size: 12,
        pages: 0,
      })

      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Aucun utilisateur trouve')).toBeInTheDocument()
      })
    })
  })

  describe('Toggle actif/inactif', () => {
    it('appelle deactivate pour un utilisateur actif', async () => {
      vi.mocked(usersService.deactivate).mockResolvedValue(undefined as any)

      renderPage()

      await waitFor(() => {
        expect(screen.getByTestId('user-1')).toBeInTheDocument()
      })

      // L'utilisateur 1 est actif
      const toggleButtons = screen.getAllByText('Toggle')
      fireEvent.click(toggleButtons[0])

      await waitFor(() => {
        expect(usersService.deactivate).toHaveBeenCalledWith('1')
      })
    })

    it('appelle activate pour un utilisateur inactif', async () => {
      vi.mocked(usersService.activate).mockResolvedValue(undefined as any)

      renderPage()

      await waitFor(() => {
        expect(screen.getByTestId('user-3')).toBeInTheDocument()
      })

      // L'utilisateur 3 est inactif
      const toggleButtons = screen.getAllByText('Toggle')
      fireEvent.click(toggleButtons[2])

      await waitFor(() => {
        expect(usersService.activate).toHaveBeenCalledWith('3')
      })
    })
  })

  describe('Modal de creation', () => {
    it('ouvre la modal au clic sur Nouvel utilisateur', async () => {
      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Nouvel utilisateur')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('Nouvel utilisateur'))

      await waitFor(() => {
        expect(screen.getByTestId('create-modal')).toBeInTheDocument()
      })
    })

    it('ferme la modal au clic sur Fermer', async () => {
      renderPage()

      await waitFor(() => {
        fireEvent.click(screen.getByText('Nouvel utilisateur'))
      })

      await waitFor(() => {
        expect(screen.getByTestId('create-modal')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('Fermer'))

      await waitFor(() => {
        expect(screen.queryByTestId('create-modal')).not.toBeInTheDocument()
      })
    })
  })

  describe('Pagination', () => {
    it('affiche la pagination quand plusieurs pages', async () => {
      vi.mocked(usersService.list).mockResolvedValue({
        items: mockUsers,
        total: 30,
        page: 1,
        size: 12,
        pages: 3,
      })

      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Precedent')).toBeInTheDocument()
        expect(screen.getByText('Page 1 sur 3')).toBeInTheDocument()
        expect(screen.getByText('Suivant')).toBeInTheDocument()
      })
    })

    it('desactive le bouton Precedent sur la premiere page', async () => {
      vi.mocked(usersService.list).mockResolvedValue({
        items: mockUsers,
        total: 30,
        page: 1,
        size: 12,
        pages: 3,
      })

      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Precedent')).toBeDisabled()
      })
    })
  })
})
