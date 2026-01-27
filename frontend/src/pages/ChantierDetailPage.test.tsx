/**
 * Tests unitaires pour ChantierDetailPage
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import ChantierDetailPage from './ChantierDetailPage'

// Mock chantier data
const mockChantier = {
  id: '1',
  nom: 'Chantier Test',
  code: 'CT001',
  statut: 'en_cours',
  adresse: '123 Rue Test',
  ville: 'Paris',
  code_postal: '75001',
  couleur: '#3498DB',
  date_debut: '2026-01-01',
  conducteurs: [{ id: 'u1', nom: 'Dupont', prenom: 'Jean' }],
  chefs: [{ id: 'u2', nom: 'Martin', prenom: 'Pierre' }],
  ouvriers: [],
}

// Mock chantiersService
vi.mock('../services/chantiers', () => ({
  chantiersService: {
    getById: vi.fn(),
    getNavigationIds: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    changeStatut: vi.fn(),
    addUser: vi.fn(),
    removeUser: vi.fn(),
  },
}))

// Mock usersService
vi.mock('../services/users', () => ({
  usersService: {
    list: vi.fn(),
  },
}))

// Mock planningService
vi.mock('../services/planning', () => ({
  planningService: {
    getByChantier: vi.fn(),
  },
}))

// Import mocked services
import { chantiersService } from '../services/chantiers'
import { usersService } from '../services/users'
import { planningService } from '../services/planning'

// Mock useAuth
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'admin-1', role: 'admin' },
  }),
}))

// Mock ToastContext
const mockAddToast = vi.fn()
const mockShowUndoToast = vi.fn()
vi.mock('../contexts/ToastContext', () => ({
  useToast: () => ({
    addToast: mockAddToast,
    showUndoToast: mockShowUndoToast,
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

vi.mock('../components/MiniMap', () => ({
  default: () => <div data-testid="mini-map">Map</div>,
}))

vi.mock('../components/taches', () => ({
  TaskList: () => <div data-testid="task-list">Tasks</div>,
}))

vi.mock('../components/chantiers', () => ({
  EditChantierModal: ({ onSubmit }: { onSubmit: (data: unknown) => void }) => (
    <div data-testid="edit-modal">
      <button onClick={() => onSubmit({ nom: 'Updated' })} data-testid="save-chantier">Save</button>
    </div>
  ),
  AddUserModal: ({ type, onSelect }: { type: string; onSelect: (id: string) => void }) => (
    <div data-testid="add-user-modal" data-type={type}>
      <button onClick={() => onSelect('user-1')} data-testid="select-user">Select</button>
    </div>
  ),
  ChantierEquipeTab: () => <div data-testid="equipe-tab">Equipe</div>,
  MesInterventions: () => <div data-testid="mes-interventions">Interventions</div>,
  ChantierLogistiqueSection: () => <div data-testid="logistique-section">Logistique</div>,
}))

const renderPage = (chantierId = '1') => {
  return render(
    <MemoryRouter initialEntries={[`/chantiers/${chantierId}`]}>
      <Routes>
        <Route path="/chantiers/:id" element={<ChantierDetailPage />} />
        <Route path="/chantiers" element={<div data-testid="chantiers-list">Chantiers List</div>} />
      </Routes>
    </MemoryRouter>
  )
}

describe('ChantierDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(chantiersService.getById).mockResolvedValue(mockChantier as any)
    vi.mocked(chantiersService.getNavigationIds).mockResolvedValue({ prevId: null, nextId: '2' })
    vi.mocked(chantiersService.delete).mockResolvedValue(undefined)
    vi.mocked(usersService.list).mockResolvedValue({ items: [], total: 0, page: 1, size: 50, pages: 1 })
    vi.mocked(planningService.getByChantier).mockResolvedValue([])
  })

  describe('loading', () => {
    it('affiche le loader pendant le chargement', () => {
      // Make getById return a pending promise
      vi.mocked(chantiersService.getById).mockImplementation(() => new Promise(() => {}))
      const { container } = renderPage()
      expect(container.querySelector('.animate-spin')).toBeTruthy()
    })
  })

  describe('rendering', () => {
    it('affiche le nom du chantier', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByText('Chantier Test')).toBeInTheDocument()
      })
    })

    it('affiche le code du chantier', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByText('CT001')).toBeInTheDocument()
      })
    })

    it('affiche l adresse', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByText('123 Rue Test')).toBeInTheDocument()
      })
    })

    it('affiche le statut du chantier', async () => {
      renderPage()
      await waitFor(() => {
        // Le statut en_cours est affiché via CHANTIER_STATUTS
        expect(screen.getByText(/en.cours/i)).toBeInTheDocument()
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

  describe('tabs', () => {
    it('affiche les onglets', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByText('Informations')).toBeInTheDocument()
        expect(screen.getByText('Taches')).toBeInTheDocument()
        expect(screen.getByText('Equipe')).toBeInTheDocument()
      })
    })

    it('change d onglet au clic sur taches', async () => {
      const user = userEvent.setup()
      renderPage()
      await waitFor(() => {
        expect(screen.getByText('Taches')).toBeInTheDocument()
      })
      await user.click(screen.getByText('Taches'))
      expect(screen.getByTestId('task-list')).toBeInTheDocument()
    })

    it('change d onglet au clic sur equipe', async () => {
      const user = userEvent.setup()
      renderPage()
      await waitFor(() => {
        expect(screen.getByText('Equipe')).toBeInTheDocument()
      })
      await user.click(screen.getByText('Equipe'))
      expect(screen.getByTestId('equipe-tab')).toBeInTheDocument()
    })
  })

  describe('admin features', () => {
    it('affiche le bouton modifier', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Modifier/i })).toBeInTheDocument()
      })
    })

    it('ouvre le modal edition au clic', async () => {
      const user = userEvent.setup()
      renderPage()
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Modifier/i })).toBeInTheDocument()
      })
      await user.click(screen.getByRole('button', { name: /Modifier/i }))
      await waitFor(() => {
        expect(screen.getByTestId('edit-modal')).toBeInTheDocument()
      })
    })

    it('affiche le bouton supprimer', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Supprimer/i })).toBeInTheDocument()
      })
    })

    it('navigue vers la liste et affiche le toast au clic supprimer', async () => {
      const user = userEvent.setup()
      renderPage()
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Supprimer/i })).toBeInTheDocument()
      })
      await user.click(screen.getByRole('button', { name: /Supprimer/i }))
      // Le composant navigue immédiatement et affiche un toast avec undo
      await waitFor(() => {
        expect(mockShowUndoToast).toHaveBeenCalledWith(
          expect.stringContaining('Chantier'),
          expect.any(Function),
          expect.any(Function),
          5000
        )
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
