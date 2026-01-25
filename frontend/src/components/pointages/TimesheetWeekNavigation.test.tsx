/**
 * Tests unitaires pour TimesheetWeekNavigation
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import TimesheetWeekNavigation from './TimesheetWeekNavigation'

describe('TimesheetWeekNavigation', () => {
  const defaultProps = {
    currentDate: new Date('2026-01-20'),
    onDateChange: vi.fn(),
  }

  describe('rendering', () => {
    it('affiche le titre', () => {
      render(<TimesheetWeekNavigation {...defaultProps} />)
      expect(screen.getByText("Feuilles d'heures")).toBeInTheDocument()
    })

    it('affiche le numero de semaine et l annee', () => {
      render(<TimesheetWeekNavigation {...defaultProps} />)
      expect(screen.getByText(/Semaine \d+ - \d{4}/)).toBeInTheDocument()
    })

    it('affiche la plage de dates', () => {
      render(<TimesheetWeekNavigation {...defaultProps} />)
      // Format: d - d MMMM yyyy
      expect(screen.getByText(/\d+ - \d+ .+ \d{4}/)).toBeInTheDocument()
    })

    it('affiche le bouton Aujourd hui', () => {
      render(<TimesheetWeekNavigation {...defaultProps} />)
      expect(screen.getByRole('button', { name: /Aujourd'hui/i })).toBeInTheDocument()
    })
  })

  describe('navigation', () => {
    it('navigue vers la semaine precedente', () => {
      const handleDateChange = vi.fn()
      render(<TimesheetWeekNavigation {...defaultProps} onDateChange={handleDateChange} />)

      fireEvent.click(screen.getByTitle('Semaine precedente'))

      expect(handleDateChange).toHaveBeenCalled()
      const newDate = handleDateChange.mock.calls[0][0]
      expect(newDate.getTime()).toBeLessThan(defaultProps.currentDate.getTime())
    })

    it('navigue vers la semaine suivante', () => {
      const handleDateChange = vi.fn()
      render(<TimesheetWeekNavigation {...defaultProps} onDateChange={handleDateChange} />)

      fireEvent.click(screen.getByTitle('Semaine suivante'))

      expect(handleDateChange).toHaveBeenCalled()
      const newDate = handleDateChange.mock.calls[0][0]
      expect(newDate.getTime()).toBeGreaterThan(defaultProps.currentDate.getTime())
    })

    it('navigue vers aujourd hui', () => {
      const handleDateChange = vi.fn()
      render(<TimesheetWeekNavigation {...defaultProps} onDateChange={handleDateChange} />)

      fireEvent.click(screen.getByRole('button', { name: /Aujourd'hui/i }))

      expect(handleDateChange).toHaveBeenCalled()
    })
  })

  describe('export', () => {
    it('n affiche pas le bouton export sans onExport', () => {
      render(<TimesheetWeekNavigation {...defaultProps} />)
      expect(screen.queryByText('Exporter')).not.toBeInTheDocument()
    })

    it('affiche le bouton export si onExport fourni', () => {
      render(<TimesheetWeekNavigation {...defaultProps} onExport={vi.fn()} />)
      expect(screen.getByText('Exporter')).toBeInTheDocument()
    })

    it('appelle onExport au clic', () => {
      const handleExport = vi.fn()
      render(<TimesheetWeekNavigation {...defaultProps} onExport={handleExport} />)

      fireEvent.click(screen.getByText('Exporter'))

      expect(handleExport).toHaveBeenCalled()
    })

    it('affiche le texte d export en cours', () => {
      render(<TimesheetWeekNavigation {...defaultProps} onExport={vi.fn()} isExporting />)
      expect(screen.getByText('Export...')).toBeInTheDocument()
    })

    it('desactive le bouton pendant l export', () => {
      render(<TimesheetWeekNavigation {...defaultProps} onExport={vi.fn()} isExporting />)
      const button = screen.getByRole('button', { name: /Export/i })
      expect(button).toBeDisabled()
    })
  })
})
