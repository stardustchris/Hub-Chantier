/**
 * Tests pour ClockCard
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ClockCard from './ClockCard'

describe('ClockCard', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-01-25T10:30:00'))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('affiche la date et l\'heure actuelles', () => {
    render(<ClockCard />)

    // La date devrait etre affichee
    expect(screen.getByText(/dimanche 25 janvier 2026/i)).toBeInTheDocument()
    expect(screen.getByText('10:30')).toBeInTheDocument()
  })

  it('affiche le bouton pointer l\'arrivee quand non pointe', () => {
    render(<ClockCard isClockedIn={false} />)

    expect(screen.getByText("Pointer l'arrivee")).toBeInTheDocument()
    expect(screen.queryByText('Pointer le depart')).not.toBeInTheDocument()
  })

  it('affiche le bouton pointer le depart quand pointe', () => {
    render(<ClockCard isClockedIn={true} clockInTime="08:30" />)

    expect(screen.getByText('Pointer le depart')).toBeInTheDocument()
    expect(screen.queryByText("Pointer l'arrivee")).not.toBeInTheDocument()
  })

  it('affiche l\'heure d\'arrivee quand pointe', () => {
    render(<ClockCard isClockedIn={true} clockInTime="08:45" />)

    expect(screen.getByText('Arrivee pointee a')).toBeInTheDocument()
    expect(screen.getByText('08:45')).toBeInTheDocument()
  })

  it('affiche --:-- si pas d\'heure d\'arrivee', () => {
    render(<ClockCard isClockedIn={true} />)

    expect(screen.getByText('--:--')).toBeInTheDocument()
  })

  it('appelle onClockIn au clic sur pointer l\'arrivee', () => {
    const onClockIn = vi.fn()
    render(<ClockCard isClockedIn={false} onClockIn={onClockIn} />)

    const button = screen.getByText("Pointer l'arrivee")
    fireEvent.click(button)

    expect(onClockIn).toHaveBeenCalled()
  })

  it('appelle onClockOut au clic sur pointer le depart', () => {
    const onClockOut = vi.fn()
    render(<ClockCard isClockedIn={true} onClockOut={onClockOut} />)

    const button = screen.getByText('Pointer le depart')
    fireEvent.click(button)

    expect(onClockOut).toHaveBeenCalled()
  })

  it('affiche le bouton modifier si canEdit est true', () => {
    render(<ClockCard isClockedIn={true} clockInTime="08:30" canEdit={true} />)

    const editButton = screen.getByTitle("Modifier l'heure d'arrivee")
    expect(editButton).toBeInTheDocument()
  })

  it('n\'affiche pas le bouton modifier si canEdit est false', () => {
    render(<ClockCard isClockedIn={true} clockInTime="08:30" canEdit={false} />)

    expect(screen.queryByTitle("Modifier l'heure d'arrivee")).not.toBeInTheDocument()
  })

  it('appelle onEditTime au clic sur modifier', () => {
    const onEditTime = vi.fn()
    render(
      <ClockCard
        isClockedIn={true}
        clockInTime="08:30"
        canEdit={true}
        onEditTime={onEditTime}
      />
    )

    const editButton = screen.getByTitle("Modifier l'heure d'arrivee")
    fireEvent.click(editButton)

    expect(onEditTime).toHaveBeenCalledWith('arrival', '08:30')
  })

  it('affiche la derniere pointee', () => {
    render(<ClockCard lastClockIn="Hier 17:45" />)

    expect(screen.getByText('Derniere pointee : Hier 17:45')).toBeInTheDocument()
  })

  it('configure un intervalle pour mettre a jour l\'heure', () => {
    const setIntervalSpy = vi.spyOn(global, 'setInterval')
    const clearIntervalSpy = vi.spyOn(global, 'clearInterval')

    const { unmount } = render(<ClockCard />)

    // L'intervalle devrait etre configure
    expect(setIntervalSpy).toHaveBeenCalled()

    // Au demontage, l'intervalle devrait etre nettoye
    unmount()
    expect(clearIntervalSpy).toHaveBeenCalled()

    setIntervalSpy.mockRestore()
    clearIntervalSpy.mockRestore()
  })
})
