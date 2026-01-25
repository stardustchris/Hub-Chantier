/**
 * Tests unitaires pour ChantierDetailPage
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import ChantierDetailPage from './ChantierDetailPage'

// Mock useChantierDetail hook
const mockUseChantierDetail = {
  chantier: null as {
    id: string
    nom: string
    code: string
    statut: string
    adresse: string
    ville: string
    code_postal: string
    couleur: string
    date_debut: string
    conducteurs: unknown[]
    chefs: unknown[]
  } | null,
  navIds: { prevId: null, nextId: '2' },
  availableUsers: [],
  isLoading: false,
  showEditModal: false,
  showAddUserModal: null as 'conducteur' | 'chef' | null,
  setShowEditModal: vi.fn(),
  openAddUserModal: vi.fn(),
  closeAddUserModal: vi.fn(),
  handleUpdateChantier: vi.fn(),
  handleDeleteChantier: vi.fn(),
  handleChangeStatut: vi.fn(),
  handleAddUser: vi.fn(),
  handleRemoveUser: vi.fn(),
}

vi.mock('../hooks', () => ({
  useChantierDetail: () => mockUseChantierDetail,
}))

vi.mock('../services/chantiers', () => ({
  chantiersService: {},
}))

// Mock useAuth
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'admin-1', role: 'admin' },
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
}))

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
}

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
    Object.assign(mockUseChantierDetail, {
      chantier: mockChantier,
      isLoading: false,
      showEditModal: false,
      showAddUserModal: null,
    })
  })

  describe('loading', () => {
    it('affiche le loader pendant le chargement', () => {
      mockUseChantierDetail.isLoading = true
      mockUseChantierDetail.chantier = null
      const { container } = renderPage()
      expect(container.querySelector('.animate-spin')).toBeTruthy()
    })
  })

  describe('rendering', () => {
    it('affiche le nom du chantier', () => {
      renderPage()
      expect(screen.getByText('Chantier Test')).toBeInTheDocument()
    })

    it('affiche le code du chantier', () => {
      renderPage()
      expect(screen.getByText('CT001')).toBeInTheDocument()
    })

    it('affiche l adresse', () => {
      renderPage()
      expect(screen.getByText('123 Rue Test')).toBeInTheDocument()
    })

    it('affiche le statut du chantier', () => {
      renderPage()
      // Le statut en_cours est affiché via CHANTIER_STATUTS
      expect(screen.getByText(/en.cours/i)).toBeInTheDocument()
    })

    it('affiche le lien retour', () => {
      renderPage()
      expect(screen.getByText('Retour aux chantiers')).toBeInTheDocument()
    })

    it('affiche la navigation', () => {
      renderPage()
      expect(screen.getByTestId('nav-prev-next')).toBeInTheDocument()
    })
  })

  describe('tabs', () => {
    it('affiche les onglets', () => {
      renderPage()
      expect(screen.getByText('Informations')).toBeInTheDocument()
      expect(screen.getByText('Taches')).toBeInTheDocument()
      expect(screen.getByText('Equipe')).toBeInTheDocument()
    })

    it('change d onglet au clic sur taches', async () => {
      const user = userEvent.setup()
      renderPage()
      await user.click(screen.getByText('Taches'))
      expect(screen.getByTestId('task-list')).toBeInTheDocument()
    })

    it('change d onglet au clic sur equipe', async () => {
      const user = userEvent.setup()
      renderPage()
      await user.click(screen.getByText('Equipe'))
      expect(screen.getByTestId('equipe-tab')).toBeInTheDocument()
    })
  })

  describe('admin features', () => {
    it('affiche le bouton modifier', () => {
      renderPage()
      expect(screen.getByRole('button', { name: /Modifier/i })).toBeInTheDocument()
    })

    it('ouvre le modal edition au clic', async () => {
      const user = userEvent.setup()
      renderPage()
      await user.click(screen.getByRole('button', { name: /Modifier/i }))
      expect(mockUseChantierDetail.setShowEditModal).toHaveBeenCalledWith(true)
    })

    it('affiche le bouton supprimer', () => {
      renderPage()
      expect(screen.getByRole('button', { name: /Supprimer/i })).toBeInTheDocument()
    })

    it('appelle handleDeleteChantier au clic supprimer', async () => {
      const user = userEvent.setup()
      renderPage()
      await user.click(screen.getByRole('button', { name: /Supprimer/i }))
      expect(mockUseChantierDetail.handleDeleteChantier).toHaveBeenCalled()
    })
  })

  describe('modals', () => {
    it('affiche le modal edition si showEditModal', () => {
      mockUseChantierDetail.showEditModal = true
      renderPage()
      expect(screen.getByTestId('edit-modal')).toBeInTheDocument()
    })

    it('affiche le modal ajout utilisateur si showAddUserModal', () => {
      mockUseChantierDetail.showAddUserModal = 'conducteur'
      renderPage()
      expect(screen.getByTestId('add-user-modal')).toBeInTheDocument()
    })
  })

  describe('navigation', () => {
    it('passe les IDs de navigation', () => {
      renderPage()
      const nav = screen.getByTestId('nav-prev-next')
      expect(nav).toHaveAttribute('data-next', '2')
    })
  })
})
