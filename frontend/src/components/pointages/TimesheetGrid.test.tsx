/**
 * Tests pour TimesheetGrid
 *
 * Couvre:
 * - Affichage header avec jours de la semaine
 * - Affichage utilisateurs et chantiers
 * - Rendu des cellules de pointage
 * - Statuts des pointages
 * - Clic sur pointage existant
 * - Clic sur cellule vide (création)
 * - Totaux par jour et par utilisateur
 * - Mode weekend
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import userEvent from '@testing-library/user-event'
import TimesheetGrid from './TimesheetGrid'
import type { VueCompagnon, Pointage } from '../../types'

const createMockPointage = (overrides: Partial<Pointage> = {}): Pointage => ({
  id: 1,
  utilisateur_id: 1,
  chantier_id: 1,
  date_pointage: '2024-01-22',
  heure_debut: '08:00',
  heure_fin: '12:00',
  total_heures: '04:00',
  heures_supplementaires: '00:00',
  statut: 'brouillon',
  is_editable: true,
  created_at: '2024-01-22T08:00:00',
  updated_at: '2024-01-22T12:00:00',
  ...overrides,
})

const createMockVueCompagnon = (overrides: Partial<VueCompagnon> = {}): VueCompagnon => ({
  utilisateur_id: 1,
  utilisateur_nom: 'Jean Dupont',
  total_heures: '40:00',
  total_heures_decimal: 40,
  totaux_par_jour: {
    lundi: '08:00',
    mardi: '08:00',
    mercredi: '08:00',
    jeudi: '08:00',
    vendredi: '08:00',
    samedi: '00:00',
    dimanche: '00:00',
  },
  chantiers: [
    {
      chantier_id: 1,
      chantier_nom: 'Chantier Alpha',
      chantier_couleur: '#3498db',
      total_heures: '40:00',
      pointages_par_jour: {
        lundi: [createMockPointage({ date_pointage: '2024-01-22' })],
        mardi: [createMockPointage({ date_pointage: '2024-01-23', id: 2 })],
        mercredi: [],
        jeudi: [],
        vendredi: [],
        samedi: [],
        dimanche: [],
      },
    },
  ],
  ...overrides,
})

const renderWithRouter = (ui: React.ReactElement) =>
  render(<MemoryRouter>{ui}</MemoryRouter>)

describe('TimesheetGrid', () => {
  const mockOnCellClick = vi.fn()
  const mockOnPointageClick = vi.fn()
  const currentDate = new Date('2024-01-22') // Monday

  const defaultProps = {
    currentDate,
    vueCompagnons: [createMockVueCompagnon()],
    onCellClick: mockOnCellClick,
    onPointageClick: mockOnPointageClick,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('État vide', () => {
    it('affiche un message si aucun compagnon', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} vueCompagnons={[]} />)
      expect(screen.getByText('Aucune donnee')).toBeInTheDocument()
    })

    it('affiche un message explicatif', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} vueCompagnons={[]} />)
      expect(
        screen.getByText(/Aucun pointage pour cette semaine/i)
      ).toBeInTheDocument()
    })
  })

  describe('Header', () => {
    it('affiche la colonne Chantier', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} />)
      expect(screen.getByText('Chantier')).toBeInTheDocument()
    })

    it('affiche les jours de la semaine (lundi-vendredi par défaut)', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} />)
      expect(screen.getByText(/lun\./i)).toBeInTheDocument()
      expect(screen.getByText(/mar\./i)).toBeInTheDocument()
      expect(screen.getByText(/mer\./i)).toBeInTheDocument()
      expect(screen.getByText(/jeu\./i)).toBeInTheDocument()
      expect(screen.getByText(/ven\./i)).toBeInTheDocument()
    })

    it('affiche samedi et dimanche si showWeekend', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} showWeekend={true} />)
      expect(screen.getByText(/sam\./i)).toBeInTheDocument()
      expect(screen.getByText(/dim\./i)).toBeInTheDocument()
    })

    it('affiche la colonne Total', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} />)
      expect(screen.getAllByText('Total').length).toBeGreaterThan(0)
    })
  })

  describe('Utilisateurs', () => {
    it('affiche le nom de l\'utilisateur', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} />)
      expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
    })

    it('affiche le total heures de l\'utilisateur', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} />)
      // Total appears in multiple places (header and cells)
      expect(screen.getAllByText(/40:00/).length).toBeGreaterThan(0)
    })
  })

  describe('Chantiers', () => {
    it('affiche le nom du chantier', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} />)
      expect(screen.getByText('Chantier Alpha')).toBeInTheDocument()
    })

    it('affiche la couleur du chantier', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} />)
      const colorDot = document.querySelector('[style*="background-color: rgb(52, 152, 219)"]')
      expect(colorDot).toBeInTheDocument()
    })
  })

  describe('Cellules de pointage', () => {
    it('affiche les heures du pointage', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} />)
      // Il peut y avoir plusieurs pointages avec 04:00
      expect(screen.getAllByText('04:00').length).toBeGreaterThan(0)
    })

    it('affiche le badge de statut', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} />)
      expect(screen.getAllByText('Brouillon').length).toBeGreaterThan(0)
    })

    it('affiche les heures supplémentaires si présentes', () => {
      const vueWithOvertime = createMockVueCompagnon({
        chantiers: [{
          chantier_id: 1,
          chantier_nom: 'Chantier Alpha',
          chantier_couleur: '#3498db',
          total_heures: '40:00',
          pointages_par_jour: {
            lundi: [createMockPointage({ heures_supplementaires: '02:00' })],
            mardi: [],
            mercredi: [],
            jeudi: [],
            vendredi: [],
            samedi: [],
            dimanche: [],
          },
        }],
      })

      renderWithRouter(<TimesheetGrid {...defaultProps} vueCompagnons={[vueWithOvertime]} />)
      expect(screen.getByText('+02:00')).toBeInTheDocument()
    })
  })

  describe('Statuts', () => {
    it('affiche le badge pour statut validé', () => {
      const vueWithValidated = createMockVueCompagnon({
        chantiers: [{
          chantier_id: 1,
          chantier_nom: 'Chantier Alpha',
          chantier_couleur: '#3498db',
          total_heures: '40:00',
          pointages_par_jour: {
            lundi: [createMockPointage({ statut: 'valide' })],
            mardi: [],
            mercredi: [],
            jeudi: [],
            vendredi: [],
            samedi: [],
            dimanche: [],
          },
        }],
      })

      renderWithRouter(<TimesheetGrid {...defaultProps} vueCompagnons={[vueWithValidated]} />)
      expect(screen.getByText('Valide')).toBeInTheDocument()
    })

    it('affiche le badge pour statut soumis', () => {
      const vueWithSubmitted = createMockVueCompagnon({
        chantiers: [{
          chantier_id: 1,
          chantier_nom: 'Chantier Alpha',
          chantier_couleur: '#3498db',
          total_heures: '40:00',
          pointages_par_jour: {
            lundi: [createMockPointage({ statut: 'soumis' })],
            mardi: [],
            mercredi: [],
            jeudi: [],
            vendredi: [],
            samedi: [],
            dimanche: [],
          },
        }],
      })

      renderWithRouter(<TimesheetGrid {...defaultProps} vueCompagnons={[vueWithSubmitted]} />)
      expect(screen.getByText('En attente')).toBeInTheDocument()
    })
  })

  describe('Interactions', () => {
    it('appelle onPointageClick au clic sur un pointage éditable', async () => {
      const user = userEvent.setup()
      renderWithRouter(<TimesheetGrid {...defaultProps} canEdit={true} />)

      const pointages = screen.getAllByText('04:00')
      await user.click(pointages[0])
      expect(mockOnPointageClick).toHaveBeenCalled()
    })

    it('n\'appelle pas onPointageClick si pointage non éditable', async () => {
      const vueWithNonEditable = createMockVueCompagnon({
        chantiers: [{
          chantier_id: 1,
          chantier_nom: 'Chantier Alpha',
          chantier_couleur: '#3498db',
          total_heures: '40:00',
          pointages_par_jour: {
            lundi: [createMockPointage({ is_editable: false })],
            mardi: [],
            mercredi: [],
            jeudi: [],
            vendredi: [],
            samedi: [],
            dimanche: [],
          },
        }],
      })

      const user = userEvent.setup()
      renderWithRouter(
        <TimesheetGrid
          {...defaultProps}
          vueCompagnons={[vueWithNonEditable]}
          canEdit={true}
        />
      )

      await user.click(screen.getByText('04:00'))
      expect(mockOnPointageClick).not.toHaveBeenCalled()
    })
  })

  describe('Ajout chantier', () => {
    it('affiche le bouton "Ajouter un chantier" si canEdit', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} canEdit={true} />)
      expect(screen.getByText('Ajouter un chantier')).toBeInTheDocument()
    })

    it('n\'affiche pas le bouton si pas canEdit', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} canEdit={false} />)
      expect(screen.queryByText('Ajouter un chantier')).not.toBeInTheDocument()
    })

    it('appelle onCellClick au clic sur le bouton', async () => {
      const user = userEvent.setup()
      renderWithRouter(<TimesheetGrid {...defaultProps} canEdit={true} />)

      await user.click(screen.getByText('Ajouter un chantier'))
      expect(mockOnCellClick).toHaveBeenCalledWith(1, null, expect.any(Date))
    })
  })

  describe('Totaux par jour', () => {
    it('affiche la ligne Total journalier', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} />)
      expect(screen.getByText('Total journalier')).toBeInTheDocument()
    })

    it('affiche les totaux par jour', () => {
      renderWithRouter(<TimesheetGrid {...defaultProps} />)
      // Multiple occurrences of 08:00 in totaux_par_jour
      const totals = screen.getAllByText('08:00')
      expect(totals.length).toBeGreaterThan(0)
    })
  })

  describe('Mise en surbrillance du jour actuel', () => {
    it('met en surbrillance la colonne du jour actuel', () => {
      // Mock today as Monday 2024-01-22
      vi.setSystemTime(new Date('2024-01-22'))

      renderWithRouter(<TimesheetGrid {...defaultProps} />)

      // Check for today highlighting class
      const todayCells = document.querySelectorAll('.bg-primary-50, .bg-primary-100')
      expect(todayCells.length).toBeGreaterThan(0)

      vi.useRealTimers()
    })
  })
})
