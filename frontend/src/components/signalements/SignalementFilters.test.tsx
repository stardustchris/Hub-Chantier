/**
 * Tests pour SignalementFilters
 *
 * Couvre:
 * - Affichage des filtres
 * - Barre de recherche conditionnelle
 * - Selection des filtres
 * - Boutons de raccourcis rapides
 * - Bouton de reinitialisation
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SignalementFilters from './SignalementFilters'

describe('SignalementFilters', () => {
  const mockOnFilterChange = vi.fn()

  const defaultProps = {
    statut: '' as const,
    priorite: '' as const,
    query: '',
    enRetardOnly: false,
    onFilterChange: mockOnFilterChange,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Affichage', () => {
    it('affiche le filtre par statut', () => {
      render(<SignalementFilters {...defaultProps} />)
      expect(screen.getByText('Statut:')).toBeInTheDocument()
    })

    it('affiche le filtre par priorite', () => {
      render(<SignalementFilters {...defaultProps} />)
      expect(screen.getByText('Priorité:')).toBeInTheDocument()
    })

    it('affiche la checkbox en retard', () => {
      render(<SignalementFilters {...defaultProps} />)
      expect(screen.getByText('En retard uniquement')).toBeInTheDocument()
    })

    it('affiche les raccourcis rapides', () => {
      render(<SignalementFilters {...defaultProps} />)
      expect(screen.getByText(/Ouverts/)).toBeInTheDocument()
      // "En cours" apparait plusieurs fois (select options + bouton)
      const enCoursButtons = screen.getAllByText(/En cours/)
      expect(enCoursButtons.length).toBeGreaterThanOrEqual(1)
      expect(screen.getByText(/Critiques/)).toBeInTheDocument()
    })
  })

  describe('Barre de recherche', () => {
    it('n affiche pas la barre de recherche par defaut', () => {
      render(<SignalementFilters {...defaultProps} />)
      expect(screen.queryByPlaceholderText(/Rechercher/)).not.toBeInTheDocument()
    })

    it('affiche la barre de recherche si showSearchBar est true', () => {
      render(<SignalementFilters {...defaultProps} showSearchBar />)
      expect(screen.getByPlaceholderText(/Rechercher/)).toBeInTheDocument()
    })

    it('appelle onFilterChange a la saisie dans la recherche', async () => {
      const user = userEvent.setup()
      render(<SignalementFilters {...defaultProps} showSearchBar />)

      await user.type(screen.getByPlaceholderText(/Rechercher/), 'test')

      expect(mockOnFilterChange).toHaveBeenCalledWith({ query: 't' })
    })
  })

  describe('Selection filtre statut', () => {
    it('appelle onFilterChange au changement de statut', async () => {
      const user = userEvent.setup()
      render(<SignalementFilters {...defaultProps} />)

      const statutSelect = screen.getAllByRole('combobox')[0]
      await user.selectOptions(statutSelect, 'ouvert')

      expect(mockOnFilterChange).toHaveBeenCalledWith({ statut: 'ouvert' })
    })

    it('affiche la valeur selectionnee', () => {
      render(<SignalementFilters {...defaultProps} statut="en_cours" />)

      const statutSelect = screen.getAllByRole('combobox')[0]
      expect(statutSelect).toHaveValue('en_cours')
    })
  })

  describe('Selection filtre priorite', () => {
    it('appelle onFilterChange au changement de priorite', async () => {
      const user = userEvent.setup()
      render(<SignalementFilters {...defaultProps} />)

      const prioriteSelect = screen.getAllByRole('combobox')[1]
      await user.selectOptions(prioriteSelect, 'critique')

      expect(mockOnFilterChange).toHaveBeenCalledWith({ priorite: 'critique' })
    })
  })

  describe('Checkbox en retard', () => {
    it('appelle onFilterChange au clic sur la checkbox', async () => {
      const user = userEvent.setup()
      render(<SignalementFilters {...defaultProps} />)

      const checkbox = screen.getByRole('checkbox')
      await user.click(checkbox)

      expect(mockOnFilterChange).toHaveBeenCalledWith({ enRetardOnly: true })
    })

    it('affiche la checkbox cochee si enRetardOnly est true', () => {
      render(<SignalementFilters {...defaultProps} enRetardOnly />)

      const checkbox = screen.getByRole('checkbox')
      expect(checkbox).toBeChecked()
    })
  })

  describe('Raccourcis rapides', () => {
    it('appelle onFilterChange au clic sur Ouverts', async () => {
      const user = userEvent.setup()
      render(<SignalementFilters {...defaultProps} />)

      await user.click(screen.getByText(/Ouverts/))

      expect(mockOnFilterChange).toHaveBeenCalledWith({
        statut: 'ouvert',
        priorite: '',
        enRetardOnly: false,
      })
    })

    it('appelle onFilterChange au clic sur En cours', async () => {
      const user = userEvent.setup()
      render(<SignalementFilters {...defaultProps} />)

      // Trouver le bouton En cours (pas l'option du select)
      const buttons = screen.getAllByRole('button')
      const enCoursButton = buttons.find(btn => btn.textContent?.includes('En cours'))
      if (enCoursButton) {
        await user.click(enCoursButton)
      }

      expect(mockOnFilterChange).toHaveBeenCalledWith({
        statut: 'en_cours',
        priorite: '',
        enRetardOnly: false,
      })
    })

    it('appelle onFilterChange au clic sur Critiques', async () => {
      const user = userEvent.setup()
      render(<SignalementFilters {...defaultProps} />)

      await user.click(screen.getByText(/Critiques/))

      expect(mockOnFilterChange).toHaveBeenCalledWith({
        statut: '',
        priorite: 'critique',
        enRetardOnly: false,
      })
    })

    it('appelle onFilterChange au clic sur En retard', async () => {
      const user = userEvent.setup()
      render(<SignalementFilters {...defaultProps} />)

      // Le dernier bouton "En retard"
      const buttons = screen.getAllByRole('button')
      const enRetardButton = buttons.find(btn => btn.textContent?.includes('En retard'))
      if (enRetardButton) {
        await user.click(enRetardButton)
      }

      expect(mockOnFilterChange).toHaveBeenCalledWith({
        statut: '',
        priorite: '',
        enRetardOnly: true,
      })
    })
  })

  describe('Reinitialisation', () => {
    it('n affiche pas le bouton reinitialiser si aucun filtre actif', () => {
      render(<SignalementFilters {...defaultProps} />)
      expect(screen.queryByText(/Réinitialiser/)).not.toBeInTheDocument()
    })

    it('affiche le bouton reinitialiser si filtre actif', () => {
      render(<SignalementFilters {...defaultProps} statut="ouvert" />)
      expect(screen.getByText(/Réinitialiser/)).toBeInTheDocument()
    })

    it('appelle onFilterChange pour reinitialiser', async () => {
      const user = userEvent.setup()
      render(<SignalementFilters {...defaultProps} statut="ouvert" />)

      await user.click(screen.getByText(/Réinitialiser/))

      expect(mockOnFilterChange).toHaveBeenCalledWith({
        statut: '',
        priorite: '',
        query: '',
        enRetardOnly: false,
      })
    })
  })
})
