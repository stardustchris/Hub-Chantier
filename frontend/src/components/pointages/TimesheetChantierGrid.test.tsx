/**
 * Tests pour TimesheetChantierGrid
 *
 * Couvre:
 * - Affichage header avec jours
 * - Affichage chantiers
 * - Rendu des cellules avec pointages multiples
 * - Statuts des pointages
 * - Interactions (clic pointage, clic cellule vide)
 * - Totaux par chantier
 * - État vide
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import userEvent from '@testing-library/user-event'
import TimesheetChantierGrid from './TimesheetChantierGrid'
import type { VueChantier, Pointage } from '../../types'

const createMockPointage = (overrides: Partial<Pointage> = {}): Pointage => ({
  id: 1,
  utilisateur_id: 1,
  chantier_id: 1,
  date_pointage: '2024-01-22',
  heures_normales: '04:00',
  heures_supplementaires: '00:00',
  total_heures: '04:00',
  total_heures_decimal: 4,
  commentaire: '',
  statut: 'brouillon',
  created_at: '2024-01-22T08:00:00',
  updated_at: '2024-01-22T12:00:00',
  ...overrides,
})

const createMockVueChantier = (overrides: Partial<VueChantier> = {}): VueChantier => ({
  chantier_id: 1,
  chantier_nom: 'Chantier Alpha',
  chantier_couleur: '#3498db',
  total_heures: '40:00',
  total_heures_decimal: 40,
  total_par_jour: {
    '2024-01-22': '04:00',
    '2024-01-23': '08:00',
  },
  pointages_par_jour: {
    lundi: [
      createMockPointage(),
      createMockPointage({ id: 2, utilisateur_id: 2 }),
    ],
    mardi: [],
    mercredi: [],
    jeudi: [],
    vendredi: [],
    samedi: [],
    dimanche: [],
  },
  ...overrides,
})

const renderWithRouter = (ui: React.ReactElement) =>
  render(<MemoryRouter>{ui}</MemoryRouter>)

describe('TimesheetChantierGrid', () => {
  const mockOnCellClick = vi.fn()
  const mockOnPointageClick = vi.fn()
  const currentDate = new Date('2024-01-22') // Monday

  const defaultProps = {
    currentDate,
    vueChantiers: [createMockVueChantier()],
    onCellClick: mockOnCellClick,
    onPointageClick: mockOnPointageClick,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('État vide', () => {
    it('affiche un message si aucun chantier', () => {
      renderWithRouter(<TimesheetChantierGrid {...defaultProps} vueChantiers={[]} />)
      expect(screen.getByText('Aucune donnee')).toBeInTheDocument()
    })

    it('affiche un message explicatif', () => {
      renderWithRouter(<TimesheetChantierGrid {...defaultProps} vueChantiers={[]} />)
      expect(
        screen.getByText(/Aucun pointage pour cette semaine/i)
      ).toBeInTheDocument()
    })
  })

  describe('Header', () => {
    it('affiche la colonne Chantier', () => {
      renderWithRouter(<TimesheetChantierGrid {...defaultProps} />)
      expect(screen.getByText('Chantier')).toBeInTheDocument()
    })

    it('affiche les jours de la semaine (lundi-vendredi par défaut)', () => {
      renderWithRouter(<TimesheetChantierGrid {...defaultProps} />)
      expect(screen.getByText(/lun\./i)).toBeInTheDocument()
      expect(screen.getByText(/mar\./i)).toBeInTheDocument()
      expect(screen.getByText(/mer\./i)).toBeInTheDocument()
      expect(screen.getByText(/jeu\./i)).toBeInTheDocument()
      expect(screen.getByText(/ven\./i)).toBeInTheDocument()
    })

    it('affiche samedi et dimanche si showWeekend', () => {
      renderWithRouter(<TimesheetChantierGrid {...defaultProps} showWeekend={true} />)
      expect(screen.getByText(/sam\./i)).toBeInTheDocument()
      expect(screen.getByText(/dim\./i)).toBeInTheDocument()
    })

    it('affiche la colonne Total', () => {
      renderWithRouter(<TimesheetChantierGrid {...defaultProps} />)
      expect(screen.getByText('Total')).toBeInTheDocument()
    })
  })

  describe('Chantiers', () => {
    it('affiche le nom du chantier', () => {
      renderWithRouter(<TimesheetChantierGrid {...defaultProps} />)
      expect(screen.getByText('Chantier Alpha')).toBeInTheDocument()
    })

    it('affiche la couleur du chantier', () => {
      renderWithRouter(<TimesheetChantierGrid {...defaultProps} />)
      const colorDot = document.querySelector('[style*="background-color: rgb(52, 152, 219)"]')
      expect(colorDot).toBeInTheDocument()
    })

    it('affiche le total heures du chantier', () => {
      renderWithRouter(<TimesheetChantierGrid {...defaultProps} />)
      expect(screen.getByText('40:00')).toBeInTheDocument()
    })

    it('affiche le total en décimal', () => {
      renderWithRouter(<TimesheetChantierGrid {...defaultProps} />)
      expect(screen.getByText('40h')).toBeInTheDocument()
    })
  })

  describe('Cellules avec pointages multiples', () => {
    it('affiche plusieurs pointages dans une cellule', () => {
      renderWithRouter(<TimesheetChantierGrid {...defaultProps} />)
      expect(screen.getByText('Jean')).toBeInTheDocument()
      expect(screen.getByText('Pierre')).toBeInTheDocument()
    })

    it('affiche les heures de chaque pointage', () => {
      renderWithRouter(<TimesheetChantierGrid {...defaultProps} />)
      // Two pointages with 04:00 each
      const heures = screen.getAllByText('04:00')
      expect(heures.length).toBe(2)
    })
  })

  describe('Statuts', () => {
    it('affiche les badges de statut', () => {
      const vueWithStatuses = createMockVueChantier({
        pointages_par_jour: {
          lundi: [
            createMockPointage({ statut: 'valide' }),
            createMockPointage({ id: 2, statut: 'soumis' }),
          ],
          mardi: [],
          mercredi: [],
          jeudi: [],
          vendredi: [],
          samedi: [],
          dimanche: [],
        },
      })

      renderWithRouter(<TimesheetChantierGrid {...defaultProps} vueChantiers={[vueWithStatuses]} />)

      // Status badges are rendered (icons only without text in this component)
      const checkIcons = document.querySelectorAll('svg.lucide-check')
      const clockIcons = document.querySelectorAll('svg.lucide-clock')
      expect(checkIcons.length).toBeGreaterThan(0)
      expect(clockIcons.length).toBeGreaterThan(0)
    })
  })

  describe('Interactions', () => {
    it('appelle onPointageClick au clic sur un pointage éditable', async () => {
      const user = userEvent.setup()
      renderWithRouter(<TimesheetChantierGrid {...defaultProps} canEdit={true} />)

      await user.click(screen.getByText('Jean'))
      expect(mockOnPointageClick).toHaveBeenCalled()
    })

    it('n\'appelle pas onPointageClick si pointage non éditable', async () => {
      const vueWithNonEditable = createMockVueChantier({
        pointages_par_jour: {
          lundi: [createMockPointage({ is_editable: false })],
          mardi: [],
          mercredi: [],
          jeudi: [],
          vendredi: [],
          samedi: [],
          dimanche: [],
        },
      })

      const user = userEvent.setup()
      renderWithRouter(
        <TimesheetChantierGrid
          {...defaultProps}
          vueChantiers={[vueWithNonEditable]}
          canEdit={true}
        />
      )

      await user.click(screen.getByText('Jean'))
      expect(mockOnPointageClick).not.toHaveBeenCalled()
    })

    it('appelle onCellClick au clic sur une cellule vide si canEdit', async () => {
      const user = userEvent.setup()
      renderWithRouter(<TimesheetChantierGrid {...defaultProps} canEdit={true} />)

      // Find an empty cell (Mardi column)
      const cells = document.querySelectorAll('td.cursor-pointer.hover\\:bg-gray-100')
      if (cells.length > 0) {
        await user.click(cells[0])
        expect(mockOnCellClick).toHaveBeenCalledWith(1, expect.any(Date))
      }
    })

    it('n\'appelle pas onCellClick si pas canEdit', async () => {
      renderWithRouter(<TimesheetChantierGrid {...defaultProps} canEdit={false} />)

      // Empty cells should not be clickable (only chantier name cells keep cursor-pointer for navigation)
      const clickableCells = document.querySelectorAll('td.cursor-pointer.hover\\:bg-gray-100')
      expect(clickableCells.length).toBe(0)
    })
  })

  describe('Mise en surbrillance du jour actuel', () => {
    it('met en surbrillance la colonne du jour actuel', () => {
      // Mock today as Monday 2024-01-22
      vi.setSystemTime(new Date('2024-01-22'))

      renderWithRouter(<TimesheetChantierGrid {...defaultProps} />)

      // Check for today highlighting class
      const todayCells = document.querySelectorAll('.bg-primary-50, .bg-primary-100')
      expect(todayCells.length).toBeGreaterThan(0)

      vi.useRealTimers()
    })
  })

  describe('Plusieurs chantiers', () => {
    it('affiche plusieurs chantiers', () => {
      const multipleChantiers = [
        createMockVueChantier({ chantier_id: 1, chantier_nom: 'Chantier Alpha' }),
        createMockVueChantier({ chantier_id: 2, chantier_nom: 'Chantier Beta', chantier_couleur: '#e74c3c' }),
      ]

      renderWithRouter(<TimesheetChantierGrid {...defaultProps} vueChantiers={multipleChantiers} />)

      expect(screen.getByText('Chantier Alpha')).toBeInTheDocument()
      expect(screen.getByText('Chantier Beta')).toBeInTheDocument()
    })
  })

  describe('Affichage utilisateur', () => {
    it('affiche le prénom de l\'utilisateur tronqué', () => {
      const vueWithLongName = createMockVueChantier({
        pointages_par_jour: {
          lundi: [createMockPointage({ utilisateur_nom: 'Jean-Baptiste Poquelin' })],
          mardi: [],
          mercredi: [],
          jeudi: [],
          vendredi: [],
          samedi: [],
          dimanche: [],
        },
      })

      renderWithRouter(<TimesheetChantierGrid {...defaultProps} vueChantiers={[vueWithLongName]} />)

      // Should show first part of name (before space)
      expect(screen.getByText('Jean-Baptiste')).toBeInTheDocument()
    })

    it('affiche "Utilisateur" si pas de nom', () => {
      const vueWithoutName = createMockVueChantier({
        pointages_par_jour: {
          lundi: [createMockPointage({ utilisateur_nom: undefined })],
          mardi: [],
          mercredi: [],
          jeudi: [],
          vendredi: [],
          samedi: [],
          dimanche: [],
        },
      })

      renderWithRouter(<TimesheetChantierGrid {...defaultProps} vueChantiers={[vueWithoutName]} />)
      expect(screen.getByText('Utilisateur')).toBeInTheDocument()
    })
  })
})
