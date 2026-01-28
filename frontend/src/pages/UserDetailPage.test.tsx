/**
 * Tests unitaires pour UserDetailPage
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import UserDetailPage from './UserDetailPage'
import { usersService } from '../services/users'
import type { User } from '../types'

// Mocks
vi.mock('../services/users', () => ({
  usersService: {
    getById: vi.fn(),
    getNavigationIds: vi.fn(),
    update: vi.fn(),
    activate: vi.fn(),
    deactivate: vi.fn(),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
  },
}))

// Mock useAuth
const mockCurrentUser = { id: 'admin-1', role: 'admin' }
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: mockCurrentUser,
  }),
}))

// Mock Layout
vi.mock('../components/Layout', () => ({
  default: ({ children }: { children: React.ReactNode }) => <div data-testid="layout">{children}</div>,
}))

// Mock child components
vi.mock('../components/NavigationPrevNext', () => ({
  default: ({ prevId, nextId }: { prevId: string | null; nextId: string | null }) => (
    <div data-testid="nav-prev-next" data-prev={prevId} data-next={nextId}>Nav</div>
  ),
}))

vi.mock('../components/ImageUpload', () => ({
  default: ({ onUpload }: { onUpload: (url: string) => void }) => (
    <div data-testid="image-upload">
      <button onClick={() => onUpload('new-photo.jpg')} data-testid="upload-photo">Upload</button>
    </div>
  ),
}))

vi.mock('../components/users', () => ({
  EditUserModal: ({ isOpen, onSave }: { isOpen: boolean; onSave: (data: unknown) => void }) => (
    isOpen ? (
      <div data-testid="edit-modal">
        <button onClick={() => onSave({ nom: 'Updated' })} data-testid="save-user">Save</button>
      </div>
    ) : null
  ),
}))

const mockUser: User = {
  id: '1',
  email: 'jean.dupont@test.com',
  nom: 'Dupont',
  prenom: 'Jean',
  role: 'conducteur',
  type_utilisateur: 'employe',
  metier: 'autre',
  telephone: '0601020304',
  is_active: true,
  couleur: '#3498DB',
  created_at: '2026-01-01T00:00:00Z',
}

const mockNavIds = { prevId: null, nextId: '2' }

const renderPage = (userId = '1') => {
  return render(
    <MemoryRouter initialEntries={[`/utilisateurs/${userId}`]}>
      <Routes>
        <Route path="/utilisateurs/:id" element={<UserDetailPage />} />
        <Route path="/utilisateurs" element={<div data-testid="users-list">Users List</div>} />
      </Routes>
    </MemoryRouter>
  )
}

describe('UserDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(usersService.getById).mockResolvedValue(mockUser)
    vi.mocked(usersService.getNavigationIds).mockResolvedValue(mockNavIds)
  })

  describe('loading', () => {
    it('affiche le loader pendant le chargement', () => {
      vi.mocked(usersService.getById).mockImplementation(() => new Promise(() => {}))
      const { container } = renderPage()
      expect(container.querySelector('.animate-spin')).toBeTruthy()
    })

    it('charge l utilisateur au demarrage', async () => {
      renderPage()
      await waitFor(() => {
        expect(usersService.getById).toHaveBeenCalledWith('1')
      })
    })

    it('charge la navigation au demarrage', async () => {
      renderPage()
      await waitFor(() => {
        expect(usersService.getNavigationIds).toHaveBeenCalledWith('1')
      })
    })
  })

  describe('rendering', () => {
    it('affiche les informations de l utilisateur', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
      })
    })

    it('affiche l email', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByText('jean.dupont@test.com')).toBeInTheDocument()
      })
    })

    it('affiche le telephone', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByText('0601020304')).toBeInTheDocument()
      })
    })

    it('affiche le lien retour', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByText('Retour')).toBeInTheDocument()
      })
    })

    it('affiche la navigation', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByTestId('nav-prev-next')).toBeInTheDocument()
      })
    })
  })

  describe('admin features', () => {
    it('affiche le bouton modifier pour admin', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByTestId('image-upload')).toBeInTheDocument()
      })
    })

    it('met a jour la photo au upload', async () => {
      vi.mocked(usersService.update).mockResolvedValue({ ...mockUser, photo_profil: 'new-photo.jpg' })
      const user = userEvent.setup()
      renderPage()

      await waitFor(() => {
        expect(screen.getByTestId('upload-photo')).toBeInTheDocument()
      })

      await user.click(screen.getByTestId('upload-photo'))

      await waitFor(() => {
        expect(usersService.update).toHaveBeenCalledWith('1', { photo_profil: 'new-photo.jpg' })
      })
    })
  })

  describe('error handling', () => {
    it('redirige vers liste si erreur de chargement', async () => {
      vi.mocked(usersService.getById).mockRejectedValue(new Error('Not found'))
      renderPage()

      await waitFor(() => {
        expect(screen.getByTestId('users-list')).toBeInTheDocument()
      })
    })
  })

  describe('navigation', () => {
    it('passe les IDs de navigation', async () => {
      renderPage()
      await waitFor(() => {
        const nav = screen.getByTestId('nav-prev-next')
        expect(nav).toHaveAttribute('data-next', '2')
      })
    })
  })
})
