/**
 * Tests unitaires pour SignalementFilters
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import SignalementFilters from './SignalementFilters'

describe('SignalementFilters', () => {
  const defaultProps = {
    statut: '' as const,
    priorite: '' as const,
    query: '',
    enRetardOnly: false,
    onFilterChange: vi.fn(),
  }

  describe('rendering', () => {
    it('affiche les selecteurs de statut et priorite', () => {
      render(<SignalementFilters {...defaultProps} />)

      expect(screen.getByText('Statut:')).toBeInTheDocument()
      expect(screen.getByText('Priorité:')).toBeInTheDocument()
      expect(screen.getAllByRole('combobox')).toHaveLength(2)
    })

    it('affiche la checkbox en retard', () => {
      render(<SignalementFilters {...defaultProps} />)

      expect(screen.getByText(/En retard uniquement/i)).toBeInTheDocument()
    })

    it('affiche les raccourcis rapides', () => {
      render(<SignalementFilters {...defaultProps} />)

      expect(screen.getByRole('button', { name: /⚠️ Ouverts/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /🔄 En cours/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /🔴 Critiques/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /🚨 En retard/i })).toBeInTheDocument()
    })

    it('n affiche pas la barre de recherche par defaut', () => {
      render(<SignalementFilters {...defaultProps} />)

      expect(screen.queryByPlaceholderText(/Rechercher/i)).not.toBeInTheDocument()
    })

    it('affiche la barre de recherche si showSearchBar', () => {
      render(<SignalementFilters {...defaultProps} showSearchBar />)

      expect(screen.getByPlaceholderText(/Rechercher/i)).toBeInTheDocument()
    })
  })

  describe('filtre statut', () => {
    it('appelle onFilterChange quand le statut change', () => {
      const handleFilterChange = vi.fn()
      render(<SignalementFilters {...defaultProps} onFilterChange={handleFilterChange} />)

      const selects = screen.getAllByRole('combobox')
      fireEvent.change(selects[0], { target: { value: 'ouvert' } })

      expect(handleFilterChange).toHaveBeenCalledWith({ statut: 'ouvert' })
    })

    it('affiche la valeur selectionnee', () => {
      render(<SignalementFilters {...defaultProps} statut="en_cours" />)

      const selects = screen.getAllByRole('combobox')
      expect(selects[0]).toHaveValue('en_cours')
    })
  })

  describe('filtre priorite', () => {
    it('appelle onFilterChange quand la priorite change', () => {
      const handleFilterChange = vi.fn()
      render(<SignalementFilters {...defaultProps} onFilterChange={handleFilterChange} />)

      const selects = screen.getAllByRole('combobox')
      fireEvent.change(selects[1], { target: { value: 'haute' } })

      expect(handleFilterChange).toHaveBeenCalledWith({ priorite: 'haute' })
    })

    it('affiche la valeur selectionnee', () => {
      render(<SignalementFilters {...defaultProps} priorite="critique" />)

      const selects = screen.getAllByRole('combobox')
      expect(selects[1]).toHaveValue('critique')
    })
  })

  describe('filtre en retard', () => {
    it('appelle onFilterChange quand la checkbox change', () => {
      const handleFilterChange = vi.fn()
      render(<SignalementFilters {...defaultProps} onFilterChange={handleFilterChange} />)

      fireEvent.click(screen.getByRole('checkbox'))

      expect(handleFilterChange).toHaveBeenCalledWith({ enRetardOnly: true })
    })

    it('affiche l etat coche', () => {
      render(<SignalementFilters {...defaultProps} enRetardOnly />)

      expect(screen.getByRole('checkbox')).toBeChecked()
    })
  })

  describe('barre de recherche', () => {
    it('appelle onFilterChange quand la recherche change', () => {
      const handleFilterChange = vi.fn()
      render(<SignalementFilters {...defaultProps} onFilterChange={handleFilterChange} showSearchBar />)

      fireEvent.change(screen.getByPlaceholderText(/Rechercher/i), { target: { value: 'test' } })

      expect(handleFilterChange).toHaveBeenCalledWith({ query: 'test' })
    })

    it('affiche la valeur de recherche', () => {
      render(<SignalementFilters {...defaultProps} query="ma recherche" showSearchBar />)

      expect(screen.getByPlaceholderText(/Rechercher/i)).toHaveValue('ma recherche')
    })
  })

  describe('bouton reinitialiser', () => {
    it('n affiche pas le bouton si aucun filtre actif', () => {
      render(<SignalementFilters {...defaultProps} />)

      expect(screen.queryByText(/Réinitialiser/i)).not.toBeInTheDocument()
    })

    it('affiche le bouton si un statut est selectionne', () => {
      render(<SignalementFilters {...defaultProps} statut="ouvert" />)

      expect(screen.getByText(/Réinitialiser/i)).toBeInTheDocument()
    })

    it('affiche le bouton si une priorite est selectionnee', () => {
      render(<SignalementFilters {...defaultProps} priorite="haute" />)

      expect(screen.getByText(/Réinitialiser/i)).toBeInTheDocument()
    })

    it('affiche le bouton si enRetardOnly est actif', () => {
      render(<SignalementFilters {...defaultProps} enRetardOnly />)

      expect(screen.getByText(/Réinitialiser/i)).toBeInTheDocument()
    })

    it('reinitialise tous les filtres au clic', () => {
      const handleFilterChange = vi.fn()
      render(<SignalementFilters {...defaultProps} statut="ouvert" onFilterChange={handleFilterChange} />)

      fireEvent.click(screen.getByText(/Réinitialiser/i))

      expect(handleFilterChange).toHaveBeenCalledWith({
        statut: '',
        priorite: '',
        query: '',
        enRetardOnly: false,
      })
    })
  })

  describe('raccourcis rapides', () => {
    it('filtre les ouverts au clic', () => {
      const handleFilterChange = vi.fn()
      render(<SignalementFilters {...defaultProps} onFilterChange={handleFilterChange} />)

      // Use the button with emoji
      fireEvent.click(screen.getByRole('button', { name: /⚠️ Ouverts/i }))

      expect(handleFilterChange).toHaveBeenCalledWith({ statut: 'ouvert', priorite: '', enRetardOnly: false })
    })

    it('filtre les en cours au clic', () => {
      const handleFilterChange = vi.fn()
      render(<SignalementFilters {...defaultProps} onFilterChange={handleFilterChange} />)

      // Use the button with emoji
      fireEvent.click(screen.getByRole('button', { name: /🔄 En cours/i }))

      expect(handleFilterChange).toHaveBeenCalledWith({ statut: 'en_cours', priorite: '', enRetardOnly: false })
    })

    it('filtre les critiques au clic', () => {
      const handleFilterChange = vi.fn()
      render(<SignalementFilters {...defaultProps} onFilterChange={handleFilterChange} />)

      // Use the button with emoji
      fireEvent.click(screen.getByRole('button', { name: /🔴 Critiques/i }))

      expect(handleFilterChange).toHaveBeenCalledWith({ statut: '', priorite: 'critique', enRetardOnly: false })
    })

    it('filtre les en retard au clic', () => {
      const handleFilterChange = vi.fn()
      render(<SignalementFilters {...defaultProps} onFilterChange={handleFilterChange} />)

      // Use the button with emoji
      fireEvent.click(screen.getByRole('button', { name: /🚨 En retard/i }))

      expect(handleFilterChange).toHaveBeenCalledWith({ statut: '', priorite: '', enRetardOnly: true })
    })

    it('applique le style actif au raccourci selectionne', () => {
      render(<SignalementFilters {...defaultProps} statut="ouvert" />)

      const button = screen.getByRole('button', { name: /⚠️ Ouverts/i })
      expect(button).toHaveClass('bg-red-100')
    })
  })
})
