/**
 * Tests pour NotificationPreferences
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import NotificationPreferences, { loadNotificationPreferences } from './NotificationPreferences'

describe('NotificationPreferences', () => {
  beforeEach(() => {
    // Clear localStorage avant chaque test
    localStorage.clear()
  })

  it('affiche le modal quand isOpen est true', () => {
    render(<NotificationPreferences isOpen={true} onClose={() => {}} />)
    expect(screen.getByText('Préférences de notifications')).toBeInTheDocument()
  })

  it('n\'affiche pas le modal quand isOpen est false', () => {
    const { container } = render(<NotificationPreferences isOpen={false} onClose={() => {}} />)
    expect(container.firstChild).toBeNull()
  })

  it('affiche toutes les catégories de notifications', () => {
    render(<NotificationPreferences isOpen={true} onClose={() => {}} />)

    expect(screen.getByText('Mentions (@)')).toBeInTheDocument()
    expect(screen.getByText('Validations FdH')).toBeInTheDocument()
    expect(screen.getByText('Signalements')).toBeInTheDocument()
    expect(screen.getByText('Météo')).toBeInTheDocument()
    expect(screen.getByText('Pointages')).toBeInTheDocument()
    expect(screen.getByText('Documents')).toBeInTheDocument()
  })

  it('charge les préférences par défaut au démarrage', () => {
    render(<NotificationPreferences isOpen={true} onClose={() => {}} />)

    // Les toggles pour mentions devraient être activés par défaut (push + in-app)
    const checkboxes = screen.getAllByRole('checkbox')

    // Il y a 6 catégories × 3 canaux = 18 checkboxes
    expect(checkboxes).toHaveLength(18)
  })

  it('permet de toggler une préférence', async () => {
    render(<NotificationPreferences isOpen={true} onClose={() => {}} />)

    // Trouver le premier checkbox (mentions > push)
    const checkboxes = screen.getAllByRole('checkbox')
    const firstCheckbox = checkboxes[0]

    const initialState = firstCheckbox.checked

    // Toggle
    fireEvent.click(firstCheckbox)

    await waitFor(() => {
      expect(firstCheckbox.checked).toBe(!initialState)
    })
  })

  it('appelle onClose lors du clic sur Annuler', () => {
    const onClose = vi.fn()
    render(<NotificationPreferences isOpen={true} onClose={onClose} />)

    const cancelButton = screen.getByText('Annuler')
    fireEvent.click(cancelButton)

    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('sauvegarde les préférences dans localStorage lors de l\'enregistrement', async () => {
    const onClose = vi.fn()
    render(<NotificationPreferences isOpen={true} onClose={onClose} />)

    // Modifier une préférence
    const checkboxes = screen.getAllByRole('checkbox')
    fireEvent.click(checkboxes[0])

    // Enregistrer
    const saveButton = screen.getByText('Enregistrer')
    fireEvent.click(saveButton)

    // Vérifier que localStorage a été mis à jour
    await waitFor(() => {
      const saved = localStorage.getItem('hub_notification_preferences')
      expect(saved).toBeTruthy()
      expect(onClose).toHaveBeenCalledTimes(1)
    })
  })

  it('charge les préférences depuis localStorage si elles existent', () => {
    // Préparer des préférences dans localStorage
    const customPrefs = {
      mentions: { push: false, inApp: false, email: false },
      validations_fdh: { push: true, inApp: true, email: true },
      signalements: { push: true, inApp: true, email: false },
      meteo: { push: true, inApp: true, email: false },
      pointages: { push: false, inApp: true, email: false },
      documents: { push: true, inApp: true, email: false },
    }
    localStorage.setItem('hub_notification_preferences', JSON.stringify(customPrefs))

    const loaded = loadNotificationPreferences()

    expect(loaded.mentions.push).toBe(false)
    expect(loaded.validations_fdh.email).toBe(true)
  })

  it('utilise les préférences par défaut si localStorage est vide', () => {
    const loaded = loadNotificationPreferences()

    expect(loaded.mentions.push).toBe(true)
    expect(loaded.mentions.inApp).toBe(true)
    expect(loaded.mentions.email).toBe(false)
  })

  it('ferme le modal lors du clic sur le bouton X', () => {
    const onClose = vi.fn()
    render(<NotificationPreferences isOpen={true} onClose={onClose} />)

    // Trouver le bouton X (par aria-label)
    const closeButton = screen.getByLabelText('Fermer')
    fireEvent.click(closeButton)

    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('ferme le modal lors du clic sur l\'overlay', () => {
    const onClose = vi.fn()
    const { container } = render(<NotificationPreferences isOpen={true} onClose={onClose} />)

    // L'overlay est le premier div avec la classe fixed
    const overlay = container.querySelector('.fixed.inset-0.bg-black')
    expect(overlay).toBeTruthy()

    if (overlay) {
      fireEvent.click(overlay)
      expect(onClose).toHaveBeenCalledTimes(1)
    }
  })
})
