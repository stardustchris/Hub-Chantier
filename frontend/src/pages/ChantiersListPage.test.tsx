/**
 * Tests pour ChantiersListPage
 * CDC Section 4 - Gestion des Chantiers
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import ChantiersListPage from './ChantiersListPage'
import type { Chantier } from '../types'

// Mock services
vi.mock('../services/chantiers', () => ({
  chantiersService: {
    list: vi.fn(),
    create: vi.fn(),
    addContact: vi.fn(),
    addPhase: vi.fn(),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

// Mock useAuth
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: {
      id: '1',
      email: 'test@test.com',
      nom: 'Dupont',
      prenom: 'Jean',
      role: 'admin',
      is_active: true,
      couleur: '#3498DB',
    },
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
  }),
}))

// Mock Layout
vi.mock('../components/Layout', () => ({
  default: ({ children }: { children: React.ReactNode }) => <div data-testid="layout">{children}</div>,
}))

// Mock ChantierCard
vi.mock('../components/chantiers', () => ({
  ChantierCard: ({ chantier }: { chantier: Chantier }) => (
    <div data-testid={`chantier-${chantier.id}`}>{chantier.nom}</div>
  ),
  CreateChantierModal: ({ onClose }: { onClose: () => void }) => (
    <div data-testid="create-modal">
      <button onClick={onClose}>Fermer</button>
    </div>
  ),
}))

import { chantiersService } from '../services/chantiers'

const mockChantiers: any[] = [
  {
    id: '1',
    code: 'CH001',
    nom: 'Chantier Alpha',
    adresse: '123 rue Test',
    statut: 'en_cours',
    couleur: '#3498DB',
    heures_estimees: 100,
    date_debut_prevue: '2024-01-01',
    created_at: '2024-01-01',
    updated_at: '2024-01-01',
    conducteurs: [],
    chefs: [],
    contacts: [],
    phases: [],
  },
  {
    id: '2',
    code: 'CH002',
    nom: 'Chantier Beta',
    adresse: '456 avenue Test',
    statut: 'ouvert',
    couleur: '#E74C3C',
    heures_estimees: 200,
    date_debut_prevue: '2024-02-01',
    created_at: '2024-02-01',
    updated_at: '2024-02-01',
    conducteurs: [],
    chefs: [],
    contacts: [],
    phases: [],
  },
  {
    id: '3',
    code: 'CH003',
    nom: 'Chantier Gamma',
    adresse: '789 boulevard Test',
    statut: 'receptionne',
    couleur: '#2ECC71',
    heures_estimees: 150,
    date_debut_prevue: '2024-03-01',
    created_at: '2024-03-01',
    updated_at: '2024-03-01',
    conducteurs: [],
    chefs: [],
    contacts: [],
    phases: [],
  },
]

const renderPage = () => {
  return render(
    <MemoryRouter>
      <ChantiersListPage />
    </MemoryRouter>
  )
}

describe('ChantiersListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(chantiersService.list).mockResolvedValue({
      items: mockChantiers,
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
        expect(screen.getByText('Chantiers')).toBeInTheDocument()
        expect(screen.getByText('Gerez vos projets de construction')).toBeInTheDocument()
      })
    })

    it('affiche le bouton Nouveau chantier', async () => {
      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Nouveau chantier')).toBeInTheDocument()
      })
    })

    it('charge et affiche les chantiers', async () => {
      renderPage()

      await waitFor(() => {
        expect(chantiersService.list).toHaveBeenCalled()
        expect(screen.getByTestId('chantier-1')).toBeInTheDocument()
        expect(screen.getByTestId('chantier-2')).toBeInTheDocument()
        expect(screen.getByTestId('chantier-3')).toBeInTheDocument()
      })
    })

    it('affiche les compteurs de statut', async () => {
      renderPage()

      await waitFor(() => {
        // Les labels de statut peuvent apparaitre a plusieurs endroits (cartes + select)
        expect(screen.getAllByText('Tous').length).toBeGreaterThan(0)
        expect(screen.getAllByText('En cours').length).toBeGreaterThan(0)
        expect(screen.getAllByText('A lancer').length).toBeGreaterThan(0)
      })
    })
  })

  describe('Recherche', () => {
    it('affiche le champ de recherche', async () => {
      renderPage()

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Rechercher un chantier...')).toBeInTheDocument()
      })
    })

    it('permet de saisir une recherche', async () => {
      renderPage()

      await waitFor(() => {
        const searchInput = screen.getByPlaceholderText('Rechercher un chantier...')
        fireEvent.change(searchInput, { target: { value: 'Alpha' } })
        expect(searchInput).toHaveValue('Alpha')
      })
    })
  })

  describe('Filtres par statut', () => {
    it('affiche le selecteur de statut', async () => {
      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Tous les statuts')).toBeInTheDocument()
      })
    })

    it('filtre par statut via le selecteur', async () => {
      const user = userEvent.setup()
      renderPage()

      await waitFor(() => {
        expect(screen.getByRole('combobox')).toBeInTheDocument()
      })

      const select = screen.getByRole('combobox')
      await user.selectOptions(select, 'en_cours')

      await waitFor(() => {
        expect(chantiersService.list).toHaveBeenCalledWith(
          expect.objectContaining({ statut: 'en_cours' })
        )
      })
    })

    it('filtre par statut via les cartes de stats', async () => {
      renderPage()

      await waitFor(() => {
        // Attendre que les chantiers soient charges
        expect(screen.getByTestId('chantier-1')).toBeInTheDocument()
      })

      // Trouver la carte avec "En cours" et cliquer dessus
      const enCoursLabels = screen.getAllByText('En cours')
      const enCoursButton = enCoursLabels[0].closest('button')
      if (enCoursButton) {
        fireEvent.click(enCoursButton)
      }

      await waitFor(() => {
        expect(chantiersService.list).toHaveBeenCalledWith(
          expect.objectContaining({ statut: 'en_cours' })
        )
      })
    })
  })

  describe('Etat vide', () => {
    it('affiche un message quand aucun chantier', async () => {
      vi.mocked(chantiersService.list).mockResolvedValue({
        items: [],
        total: 0,
        page: 1,
        size: 12,
        pages: 0,
      })

      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Aucun chantier trouve')).toBeInTheDocument()
      })
    })

    it('affiche le bouton effacer filtres quand filtres actifs et aucun resultat', async () => {
      const user = userEvent.setup()
      vi.mocked(chantiersService.list)
        .mockResolvedValueOnce({
          items: mockChantiers,
          total: 3,
          page: 1,
          size: 12,
          pages: 1,
        })
        .mockResolvedValueOnce({
          items: mockChantiers,
          total: 3,
          page: 1,
          size: 12,
          pages: 1,
        })
        .mockResolvedValue({
          items: [],
          total: 0,
          page: 1,
          size: 12,
          pages: 0,
        })

      renderPage()

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Rechercher un chantier...')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText('Rechercher un chantier...')
      await user.type(searchInput, 'xyz')

      await waitFor(() => {
        expect(screen.getByText('Effacer les filtres')).toBeInTheDocument()
      })
    })
  })

  describe('Modal de creation', () => {
    it('ouvre la modal au clic sur Nouveau chantier', async () => {
      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Nouveau chantier')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('Nouveau chantier'))

      await waitFor(() => {
        expect(screen.getByTestId('create-modal')).toBeInTheDocument()
      })
    })

    it('ferme la modal au clic sur Fermer', async () => {
      renderPage()

      await waitFor(() => {
        fireEvent.click(screen.getByText('Nouveau chantier'))
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
      vi.mocked(chantiersService.list).mockResolvedValue({
        items: mockChantiers,
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
      vi.mocked(chantiersService.list).mockResolvedValue({
        items: mockChantiers,
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

    it('n\'affiche pas la pagination quand une seule page', async () => {
      renderPage()

      await waitFor(() => {
        expect(screen.queryByText('Precedent')).not.toBeInTheDocument()
        expect(screen.queryByText('Suivant')).not.toBeInTheDocument()
      })
    })
  })
})
