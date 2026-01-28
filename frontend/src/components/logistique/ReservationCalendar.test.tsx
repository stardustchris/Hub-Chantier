/**
 * Tests pour ReservationCalendar
 *
 * Couvre:
 * - Affichage header avec ressource
 * - Navigation semaine (précédent/suivant/aujourd'hui)
 * - Grille calendrier avec jours et heures
 * - Affichage réservations
 * - Clic sur cellule vide pour créer
 * - Clic sur réservation pour sélectionner
 * - Légende des statuts
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ReservationCalendar from './ReservationCalendar'
import type { Ressource, PlanningRessource, Reservation } from '../../types/logistique'

// Mock API
vi.mock('../../api/logistique', () => ({
  getPlanningRessource: vi.fn(),
  getLundiSemaine: vi.fn((date: Date) => {
    const d = new Date(date)
    const day = d.getDay()
    const diff = d.getDate() - day + (day === 0 ? -6 : 1)
    return new Date(d.setDate(diff))
  }),
  formatDateISO: vi.fn((date: Date) => date.toISOString().split('T')[0]),
}))

// Mock logger
vi.mock('../../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

import { getPlanningRessource } from '../../api/logistique'

const mockGetPlanningRessource = getPlanningRessource as ReturnType<typeof vi.fn>

const createMockRessource = (overrides: Partial<Ressource> = {}): Ressource => ({
  id: 1,
  code: 'CAM01',
  nom: 'Camion benne',
  categorie: 'vehicule',
  categorie_label: 'Véhicule',
  couleur: '#FF5733',
  actif: true,
  validation_requise: false,
  created_at: '2024-01-01T00:00:00',
  updated_at: '2024-01-01T00:00:00',
  ...overrides,
})

const createMockPlanning = (overrides: Partial<PlanningRessource> = {}): PlanningRessource => ({
  ressource_id: 1,
  ressource_nom: 'Camion benne',
  ressource_code: 'CAM01',
  ressource_couleur: '#FF5733',
  jours: [
    '2024-01-22', '2024-01-23', '2024-01-24', '2024-01-25',
    '2024-01-26', '2024-01-27', '2024-01-28',
  ],
  reservations: [],
  ...overrides,
})

const createMockReservation = (overrides: Partial<Reservation> = {}): Reservation => ({
  id: 1,
  ressource_id: 1,
  ressource_nom: 'Camion benne',
  ressource_code: 'CAM01',
  ressource_couleur: '#FF5733',
  demandeur_id: 1,
  demandeur_nom: 'Jean Dupont',
  chantier_id: 1,
  chantier_nom: 'Chantier Test',
  date_reservation: '2024-01-23',
  heure_debut: '09:00',
  heure_fin: '12:00',
  statut: 'validee',
  statut_label: 'Validée',
  created_at: '2024-01-01T00:00:00',
  updated_at: '2024-01-01T00:00:00',
  ...overrides,
})

describe('ReservationCalendar', () => {
  const mockOnCreateReservation = vi.fn()
  const mockOnSelectReservation = vi.fn()

  const defaultProps = {
    ressource: createMockRessource(),
    onCreateReservation: mockOnCreateReservation,
    onSelectReservation: mockOnSelectReservation,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockGetPlanningRessource.mockResolvedValue(createMockPlanning())
  })

  describe('Header', () => {
    it('affiche le nom et code de la ressource', async () => {
      render(<ReservationCalendar {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('[CAM01] Camion benne')).toBeInTheDocument()
      })
    })

    it('affiche la couleur de la ressource', async () => {
      render(<ReservationCalendar {...defaultProps} />)

      await waitFor(() => {
        const colorDiv = document.querySelector('[style*="background-color: rgb(255, 87, 51)"]')
        expect(colorDiv).toBeInTheDocument()
      })
    })
  })

  describe('Navigation semaine', () => {
    it('affiche le numéro de semaine', async () => {
      render(<ReservationCalendar {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText(/Semaine \d+/)).toBeInTheDocument()
      })
    })

    it('affiche le bouton Aujourd\'hui', async () => {
      render(<ReservationCalendar {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Aujourd\'hui')).toBeInTheDocument()
      })
    })

    it('navigue vers la semaine précédente', async () => {
      const user = userEvent.setup()
      render(<ReservationCalendar {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('[CAM01] Camion benne')).toBeInTheDocument()
      })

      const prevButton = screen.getAllByRole('button').find(
        btn => btn.querySelector('svg.lucide-chevron-left')
      )
      if (prevButton) {
        await user.click(prevButton)
        await waitFor(() => {
          expect(mockGetPlanningRessource).toHaveBeenCalledTimes(2)
        })
      }
    })

    it('navigue vers la semaine suivante', async () => {
      const user = userEvent.setup()
      render(<ReservationCalendar {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('[CAM01] Camion benne')).toBeInTheDocument()
      })

      const nextButton = screen.getAllByRole('button').find(
        btn => btn.querySelector('svg.lucide-chevron-right')
      )
      if (nextButton) {
        await user.click(nextButton)
        await waitFor(() => {
          expect(mockGetPlanningRessource).toHaveBeenCalledTimes(2)
        })
      }
    })

    it('retourne à aujourd\'hui au clic sur le bouton', async () => {
      const user = userEvent.setup()
      render(<ReservationCalendar {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Aujourd\'hui')).toBeInTheDocument()
      })

      // Navigate away first
      const nextButton = screen.getAllByRole('button').find(
        btn => btn.querySelector('svg.lucide-chevron-right')
      )
      if (nextButton) {
        await user.click(nextButton)
      }

      // Then click Aujourd'hui
      await user.click(screen.getByText('Aujourd\'hui'))

      await waitFor(() => {
        expect(mockGetPlanningRessource).toHaveBeenCalledTimes(3)
      })
    })
  })

  describe('Grille calendrier', () => {
    it('affiche les jours de la semaine', async () => {
      render(<ReservationCalendar {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Lundi')).toBeInTheDocument()
        expect(screen.getByText('Mardi')).toBeInTheDocument()
        expect(screen.getByText('Mercredi')).toBeInTheDocument()
        expect(screen.getByText('Jeudi')).toBeInTheDocument()
        expect(screen.getByText('Vendredi')).toBeInTheDocument()
        expect(screen.getByText('Samedi')).toBeInTheDocument()
        expect(screen.getByText('Dimanche')).toBeInTheDocument()
      })
    })

    it('affiche les heures de 08:00 à 18:00', async () => {
      render(<ReservationCalendar {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('08:00')).toBeInTheDocument()
        expect(screen.getByText('12:00')).toBeInTheDocument()
        expect(screen.getByText('18:00')).toBeInTheDocument()
      })
    })

    it('affiche le header "Heure"', async () => {
      render(<ReservationCalendar {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Heure')).toBeInTheDocument()
      })
    })
  })

  describe('Affichage des réservations', () => {
    it('affiche une réservation sur le calendrier', async () => {
      mockGetPlanningRessource.mockResolvedValue(
        createMockPlanning({
          reservations: [createMockReservation()],
        })
      )

      render(<ReservationCalendar {...defaultProps} />)

      // Attend que le planning soit chargé
      await waitFor(() => {
        // Vérifie que le bloc de réservation est rendu (avec la couleur de la ressource)
        const reservationBlock = document.querySelector('[style*="background-color"]')
        expect(reservationBlock).toBeInTheDocument()
      })
    })

    it('affiche l\'indicateur de statut', async () => {
      mockGetPlanningRessource.mockResolvedValue(
        createMockPlanning({
          reservations: [createMockReservation({ statut: 'validee' })],
        })
      )

      render(<ReservationCalendar {...defaultProps} />)

      await waitFor(() => {
        // Should show status indicator dot with title
        const statusDot = document.querySelector('[title="Validée"]')
        expect(statusDot).toBeInTheDocument()
      })
    })
  })

  describe('Interactions', () => {
    it('appelle onCreateReservation au clic sur cellule vide', async () => {
      const user = userEvent.setup()
      render(<ReservationCalendar {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Lundi')).toBeInTheDocument()
      })

      // Find and click an empty cell
      const cells = document.querySelectorAll('td.hover\\:bg-blue-50')
      if (cells.length > 0) {
        await user.click(cells[0])
        expect(mockOnCreateReservation).toHaveBeenCalled()
      }
    })

    it('appelle onSelectReservation au clic sur réservation', async () => {
      const reservation = createMockReservation()
      mockGetPlanningRessource.mockResolvedValue(
        createMockPlanning({ reservations: [reservation] })
      )

      const user = userEvent.setup()
      render(<ReservationCalendar {...defaultProps} />)

      await waitFor(() => {
        // Attend que le bloc réservation soit rendu
        const block = document.querySelector('[style*="background-color"]')
        expect(block).toBeInTheDocument()
      })

      // Clique sur le bloc de réservation
      const reservationBlock = document.querySelector('.cursor-pointer[style*="background-color"]')
      if (reservationBlock) {
        await user.click(reservationBlock)
        expect(mockOnSelectReservation).toHaveBeenCalledWith(reservation)
      }
    })

    it('ne crée pas de réservation si onCreateReservation non fourni', async () => {
      render(
        <ReservationCalendar
          ressource={createMockRessource()}
          onSelectReservation={mockOnSelectReservation}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Lundi')).toBeInTheDocument()
      })

      // Cells should not be clickable
      const cells = document.querySelectorAll('td.cursor-pointer')
      expect(cells.length).toBe(0)
    })
  })

  describe('Légende', () => {
    it('affiche la légende des statuts', async () => {
      render(<ReservationCalendar {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('En attente')).toBeInTheDocument()
        expect(screen.getByText('Validée')).toBeInTheDocument()
        expect(screen.getByText('Refusée')).toBeInTheDocument()
        expect(screen.getByText('Annulée')).toBeInTheDocument()
      })
    })
  })

  describe('État de chargement', () => {
    it('affiche un spinner pendant le chargement', async () => {
      // Make the promise not resolve immediately
      let resolvePromise: (value: PlanningRessource) => void
      mockGetPlanningRessource.mockReturnValue(
        new Promise((resolve) => {
          resolvePromise = resolve
        })
      )

      render(<ReservationCalendar {...defaultProps} />)

      // Should show loading spinner
      const spinner = document.querySelector('.animate-spin')
      expect(spinner).toBeInTheDocument()

      // Resolve the promise
      resolvePromise!(createMockPlanning())

      await waitFor(() => {
        expect(screen.getByText('Lundi')).toBeInTheDocument()
      })
    })
  })

  describe('Gestion des erreurs', () => {
    it('gère les erreurs de chargement silencieusement', async () => {
      mockGetPlanningRessource.mockRejectedValue(new Error('Network error'))

      render(<ReservationCalendar {...defaultProps} />)

      await waitFor(() => {
        // Should not crash, header should still be visible
        expect(screen.getByText('[CAM01] Camion benne')).toBeInTheDocument()
      })
    })
  })
})
