/**
 * Tests unitaires pour WeekNavigation
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import WeekNavigation from './WeekNavigation'

describe('WeekNavigation', () => {
  const defaultProps = {
    currentDate: new Date('2026-01-20'),
    onDateChange: vi.fn(),
    viewMode: 'semaine' as const,
    onViewModeChange: vi.fn(),
  }

  describe('mode semaine', () => {
    it('affiche le numero de semaine', () => {
      render(<WeekNavigation {...defaultProps} />)
      expect(screen.getByText(/Semaine \d+/)).toBeInTheDocument()
    })

    it('affiche la plage de dates', () => {
      render(<WeekNavigation {...defaultProps} />)
      expect(screen.getByText(/\d+ - \d+ .+ \d{4}/)).toBeInTheDocument()
    })

    it('applique le style actif au bouton semaine', () => {
      render(<WeekNavigation {...defaultProps} viewMode="semaine" />)
      const button = screen.getByRole('button', { name: 'Semaine' })
      expect(button).toHaveClass('bg-primary-100')
    })
  })

  describe('mode mois', () => {
    it('affiche le mois et l annee', () => {
      render(<WeekNavigation {...defaultProps} viewMode="mois" />)
      // En mode mois, le format du mois est affiché
      expect(screen.getByRole('button', { name: 'Mois' })).toBeInTheDocument()
    })

    it('applique le style actif au bouton mois', () => {
      render(<WeekNavigation {...defaultProps} viewMode="mois" />)
      const button = screen.getByRole('button', { name: 'Mois' })
      expect(button).toHaveClass('bg-primary-100')
    })
  })

  describe('navigation', () => {
    it('navigue vers la semaine precedente', () => {
      const handleDateChange = vi.fn()
      render(<WeekNavigation {...defaultProps} onDateChange={handleDateChange} />)

      fireEvent.click(screen.getByLabelText(/Semaine précédente/i))

      expect(handleDateChange).toHaveBeenCalled()
      const newDate = handleDateChange.mock.calls[0][0]
      expect(newDate.getTime()).toBeLessThan(defaultProps.currentDate.getTime())
    })

    it('navigue vers la semaine suivante', () => {
      const handleDateChange = vi.fn()
      render(<WeekNavigation {...defaultProps} onDateChange={handleDateChange} />)

      fireEvent.click(screen.getByLabelText(/Semaine suivante/i))

      expect(handleDateChange).toHaveBeenCalled()
      const newDate = handleDateChange.mock.calls[0][0]
      expect(newDate.getTime()).toBeGreaterThan(defaultProps.currentDate.getTime())
    })

    it('navigue vers le mois precedent en mode mois', () => {
      const handleDateChange = vi.fn()
      render(<WeekNavigation {...defaultProps} viewMode="mois" onDateChange={handleDateChange} />)

      fireEvent.click(screen.getByLabelText(/Mois précédent/i))

      expect(handleDateChange).toHaveBeenCalled()
      const newDate = handleDateChange.mock.calls[0][0]
      expect(newDate.getMonth()).not.toBe(defaultProps.currentDate.getMonth())
    })

    it('navigue vers le mois suivant en mode mois', () => {
      const handleDateChange = vi.fn()
      render(<WeekNavigation {...defaultProps} viewMode="mois" onDateChange={handleDateChange} />)

      fireEvent.click(screen.getByLabelText(/Mois suivant/i))

      expect(handleDateChange).toHaveBeenCalled()
    })

    it('navigue vers aujourd hui', () => {
      const handleDateChange = vi.fn()
      render(<WeekNavigation {...defaultProps} onDateChange={handleDateChange} />)

      fireEvent.click(screen.getByRole('button', { name: /Aujourd'hui/i }))

      expect(handleDateChange).toHaveBeenCalled()
    })
  })

  describe('changement de mode', () => {
    it('passe en mode semaine', () => {
      const handleViewModeChange = vi.fn()
      render(<WeekNavigation {...defaultProps} viewMode="mois" onViewModeChange={handleViewModeChange} />)

      fireEvent.click(screen.getByRole('button', { name: 'Semaine' }))

      expect(handleViewModeChange).toHaveBeenCalledWith('semaine')
    })

    it('passe en mode mois', () => {
      const handleViewModeChange = vi.fn()
      render(<WeekNavigation {...defaultProps} viewMode="semaine" onViewModeChange={handleViewModeChange} />)

      fireEvent.click(screen.getByRole('button', { name: 'Mois' }))

      expect(handleViewModeChange).toHaveBeenCalledWith('mois')
    })
  })
})
