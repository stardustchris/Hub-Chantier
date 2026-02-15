/**
 * Tests unitaires pour LogistiquePage
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ReactNode } from 'react'
import LogistiquePage from './LogistiquePage'
import { createMockReservation } from '../fixtures'
import type { Reservation } from '../types/logistique'

// Mock Layout component to avoid AuthContext dependency
vi.mock('../components/Layout', () => ({
  default: ({ children }: { children: ReactNode }) => <div data-testid="layout">{children}</div>,
}))

// Mock useLogistique hook
const mockUseLogistique = {
  isAdmin: true,
  canValidate: true,
  activeTab: 'ressources' as 'ressources' | 'planning' | 'en-attente',
  setActiveTab: vi.fn(),
  chantiers: [],
  reservationsEnAttente: [] as Reservation[],
  selectedRessource: null as { id: number; nom: string; code: string } | null,
  setSelectedRessource: vi.fn(),
  showModal: false,
  modalInitialData: { date: '', heureDebut: '', heureFin: '' },
  selectedReservation: null,
  handleSelectRessource: vi.fn(),
  handleCreateReservation: vi.fn(),
  handleSelectReservation: vi.fn(),
  handleSelectPendingReservation: vi.fn(),
  handleModalClose: vi.fn(),
  handleModalSuccess: vi.fn(),
  tabs: [
    { id: 'ressources', label: 'Ressources' },
    { id: 'planning', label: 'Planning' },
    { id: 'en-attente', label: 'En attente', badge: 0 },
  ],
}

vi.mock('../hooks', () => ({
  useLogistique: () => mockUseLogistique,
}))

// Mock API and logger
vi.mock('../services/logistique', () => ({
  listRessources: vi.fn().mockResolvedValue({ items: [] }),
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

// Mock child components
vi.mock('../components/logistique', () => ({
  RessourceList: ({ isAdmin }: { isAdmin: boolean }) => (
    <div data-testid="ressource-list" data-admin={isAdmin}>
      Ressource List
    </div>
  ),
  RessourceModal: () => null,
  ReservationCalendar: ({ ressource }: { ressource: { nom: string } }) => (
    <div data-testid="reservation-calendar">
      Calendar for {ressource.nom}
    </div>
  ),
  ReservationModal: ({ isOpen }: { isOpen: boolean }) => (
    isOpen ? <div data-testid="reservation-modal">Reservation Modal</div> : null
  ),
}))

describe('LogistiquePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset mock values
    Object.assign(mockUseLogistique, {
      isAdmin: true,
      canValidate: true,
      activeTab: 'ressources',
      reservationsEnAttente: [],
      selectedRessource: null,
      showModal: false,
      tabs: [
        { id: 'ressources', label: 'Ressources' },
        { id: 'planning', label: 'Planning' },
        { id: 'en-attente', label: 'En attente', badge: 0 },
      ],
    })
  })

  describe('rendering', () => {
    it('affiche le titre', () => {
      render(<LogistiquePage />)
      expect(screen.getByRole('heading', { name: 'Logistique' })).toBeInTheDocument()
    })

    it('affiche la description', () => {
      render(<LogistiquePage />)
      expect(screen.getByText('Gestion du materiel et reservations')).toBeInTheDocument()
    })

    it('affiche les onglets', () => {
      render(<LogistiquePage />)
      expect(screen.getByText('Ressources')).toBeInTheDocument()
      expect(screen.getByText('Planning')).toBeInTheDocument()
      expect(screen.getByText('En attente')).toBeInTheDocument()
    })
  })

  describe('tabs', () => {
    it('affiche onglet ressources par defaut', () => {
      render(<LogistiquePage />)
      expect(screen.getByTestId('ressource-list')).toBeInTheDocument()
    })

    it('change d onglet au clic', async () => {
      const user = userEvent.setup()
      render(<LogistiquePage />)

      await user.click(screen.getByText('Planning'))

      expect(mockUseLogistique.setActiveTab).toHaveBeenCalledWith('planning')
    })

    it('affiche un badge sur onglet en attente', () => {
      mockUseLogistique.tabs = [
        { id: 'ressources', label: 'Ressources' },
        { id: 'planning', label: 'Planning' },
        { id: 'en-attente', label: 'En attente', badge: 5 },
      ]
      render(<LogistiquePage />)

      expect(screen.getByText('5')).toBeInTheDocument()
    })
  })

  describe('ressources tab', () => {
    it('affiche la liste des ressources', () => {
      render(<LogistiquePage />)
      expect(screen.getByTestId('ressource-list')).toBeInTheDocument()
    })

    it('passe isAdmin a la liste', () => {
      mockUseLogistique.isAdmin = true
      render(<LogistiquePage />)
      expect(screen.getByTestId('ressource-list')).toHaveAttribute('data-admin', 'true')
    })
  })

  describe('planning tab', () => {
    beforeEach(() => {
      mockUseLogistique.activeTab = 'planning'
    })

    it('affiche le selecteur de ressource', () => {
      render(<LogistiquePage />)
      expect(screen.getByLabelText('Ressource à afficher')).toBeInTheDocument()
    })

    it('affiche le planning toutes ressources par defaut', () => {
      render(<LogistiquePage />)
      expect(screen.getByText('Planning : Toutes les ressources')).toBeInTheDocument()
    })

    it('affiche lien vers la liste des ressources', () => {
      render(<LogistiquePage />)
      expect(screen.getByText('Voir la liste des ressources')).toBeInTheDocument()
    })

    it('navigue vers onglet ressources au clic sur le lien', async () => {
      const user = userEvent.setup()
      render(<LogistiquePage />)

      await user.click(screen.getByText('Voir la liste des ressources'))

      expect(mockUseLogistique.setActiveTab).toHaveBeenCalledWith('ressources')
    })

    it('affiche message si aucune ressource disponible', () => {
      render(<LogistiquePage />)
      expect(screen.getByText(/Aucune ressource disponible/)).toBeInTheDocument()
    })
  })

  describe('en-attente tab', () => {
    beforeEach(() => {
      mockUseLogistique.activeTab = 'en-attente'
    })

    it('affiche message si aucune reservation en attente', () => {
      mockUseLogistique.reservationsEnAttente = []
      render(<LogistiquePage />)
      expect(screen.getByText('Aucune reservation en attente')).toBeInTheDocument()
    })

    it('affiche les reservations en attente', () => {
      mockUseLogistique.reservationsEnAttente = [
        createMockReservation({
          id: 1,
          ressource_code: 'GRU001',
          ressource_nom: 'Grue',
          ressource_couleur: '#3B82F6',
          date_reservation: '2026-01-25',
          heure_debut: '08:00',
          heure_fin: '12:00',
          demandeur_id: 1,
          demandeur_nom: 'Jean Dupont',
          chantier_id: 1,
          chantier_nom: 'Chantier A',
        }),
      ]
      render(<LogistiquePage />)
      expect(screen.getByText('[GRU001] Grue')).toBeInTheDocument()
      expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
    })

    it('selectionne une reservation au clic', async () => {
      const user = userEvent.setup()
      const reservation = createMockReservation({
        id: 1,
        ressource_code: 'GRU001',
        ressource_nom: 'Grue',
        ressource_couleur: '#3B82F6',
        date_reservation: '2026-01-25',
        heure_debut: '08:00',
        heure_fin: '12:00',
        demandeur_id: 1,
        demandeur_nom: 'Jean Dupont',
        chantier_id: 1,
        chantier_nom: 'Chantier A',
      })
      mockUseLogistique.reservationsEnAttente = [reservation]
      render(<LogistiquePage />)

      await user.click(screen.getByText('[GRU001] Grue'))

      expect(mockUseLogistique.handleSelectPendingReservation).toHaveBeenCalledWith(reservation)
    })

    it('n affiche pas si pas canValidate', () => {
      mockUseLogistique.canValidate = false
      render(<LogistiquePage />)
      expect(screen.queryByText('Reservations en attente de validation')).not.toBeInTheDocument()
    })
  })

  describe('modal', () => {
    it('affiche le modal si showModal et ressource selectionnee', () => {
      mockUseLogistique.selectedRessource = { id: 1, nom: 'Grue', code: 'GRU001' }
      mockUseLogistique.showModal = true
      render(<LogistiquePage />)
      expect(screen.getByTestId('reservation-modal')).toBeInTheDocument()
    })

    it('n affiche pas le modal sans ressource', () => {
      mockUseLogistique.selectedRessource = null
      mockUseLogistique.showModal = true
      render(<LogistiquePage />)
      expect(screen.queryByTestId('reservation-modal')).not.toBeInTheDocument()
    })
  })
})
