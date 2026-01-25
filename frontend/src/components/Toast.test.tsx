/**
 * Tests pour ToastContainer et ToastItem
 * Composants de notifications
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, act } from '@testing-library/react'
import ToastContainer from './Toast'
import type { Toast } from '../contexts/ToastContext'

const mockRemoveToast = vi.fn()
let mockToasts: Toast[] = []

vi.mock('../contexts/ToastContext', () => ({
  useToast: () => ({
    toasts: mockToasts,
    removeToast: mockRemoveToast,
  }),
}))

describe('ToastContainer', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockToasts = []
  })

  describe('Rendu conditionnel', () => {
    it('ne rend rien si aucun toast', () => {
      mockToasts = []
      const { container } = render(<ToastContainer />)
      expect(container.firstChild).toBeNull()
    })

    it('affiche les toasts quand il y en a', () => {
      mockToasts = [
        { id: '1', message: 'Message de test', type: 'info' }
      ]
      render(<ToastContainer />)
      expect(screen.getByText('Message de test')).toBeInTheDocument()
    })

    it('affiche plusieurs toasts', () => {
      mockToasts = [
        { id: '1', message: 'Premier message', type: 'success' },
        { id: '2', message: 'Deuxieme message', type: 'error' },
      ]
      render(<ToastContainer />)
      expect(screen.getByText('Premier message')).toBeInTheDocument()
      expect(screen.getByText('Deuxieme message')).toBeInTheDocument()
    })
  })

  describe('Types de toasts', () => {
    it('affiche un toast success avec les bonnes couleurs', () => {
      mockToasts = [{ id: '1', message: 'Succes!', type: 'success' }]
      render(<ToastContainer />)
      // Le toast container est le div avec les classes de couleur
      const toastContainer = screen.getByText('Succes!').closest('.bg-green-50')
      expect(toastContainer).toBeInTheDocument()
    })

    it('affiche un toast error avec les bonnes couleurs', () => {
      mockToasts = [{ id: '1', message: 'Erreur!', type: 'error' }]
      render(<ToastContainer />)
      const toastContainer = screen.getByText('Erreur!').closest('.bg-red-50')
      expect(toastContainer).toBeInTheDocument()
    })

    it('affiche un toast warning avec les bonnes couleurs', () => {
      mockToasts = [{ id: '1', message: 'Attention!', type: 'warning' }]
      render(<ToastContainer />)
      const toastContainer = screen.getByText('Attention!').closest('.bg-yellow-50')
      expect(toastContainer).toBeInTheDocument()
    })

    it('affiche un toast info avec les bonnes couleurs', () => {
      mockToasts = [{ id: '1', message: 'Info', type: 'info' }]
      render(<ToastContainer />)
      const toastContainer = screen.getByText('Info').closest('.bg-blue-50')
      expect(toastContainer).toBeInTheDocument()
    })
  })

  describe('Fermeture des toasts', () => {
    it('affiche le bouton de fermeture', () => {
      mockToasts = [{ id: '1', message: 'Test', type: 'info' }]
      render(<ToastContainer />)
      expect(screen.getByLabelText('Fermer la notification')).toBeInTheDocument()
    })

    it('appelle removeToast au clic sur fermer', () => {
      mockToasts = [{ id: '1', message: 'Test', type: 'info' }]
      render(<ToastContainer />)

      fireEvent.click(screen.getByLabelText('Fermer la notification'))
      expect(mockRemoveToast).toHaveBeenCalledWith('1')
    })
  })

  describe('Toast avec action', () => {
    it('affiche le bouton d\'action quand fourni', () => {
      const onClickAction = vi.fn()
      mockToasts = [{
        id: '1',
        message: 'Element supprime',
        type: 'info',
        action: {
          label: 'Annuler',
          onClick: onClickAction,
        }
      }]
      render(<ToastContainer />)

      expect(screen.getByText('Annuler')).toBeInTheDocument()
    })

    it('appelle l\'action au clic', () => {
      const onClickAction = vi.fn()
      mockToasts = [{
        id: '1',
        message: 'Element supprime',
        type: 'info',
        action: {
          label: 'Annuler',
          onClick: onClickAction,
        }
      }]
      render(<ToastContainer />)

      fireEvent.click(screen.getByText('Annuler'))
      expect(onClickAction).toHaveBeenCalled()
    })

    it('affiche la barre de progression pour les toasts avec action', () => {
      mockToasts = [{
        id: '1',
        message: 'Test',
        type: 'success',
        action: {
          label: 'Undo',
          onClick: vi.fn(),
        }
      }]
      render(<ToastContainer />)

      // La barre de progression doit etre presente
      const progressContainer = document.querySelector('.absolute.bottom-0')
      expect(progressContainer).toBeInTheDocument()
    })
  })

  describe('Barre de progression', () => {
    it('anime la barre de progression', async () => {
      vi.useFakeTimers()

      mockToasts = [{
        id: '1',
        message: 'Test',
        type: 'success',
        action: {
          label: 'Undo',
          onClick: vi.fn(),
        }
      }]
      render(<ToastContainer />)

      // Attendre que la progression diminue
      await act(async () => {
        vi.advanceTimersByTime(1000)
      })

      vi.useRealTimers()
    })
  })

  describe('Position et style', () => {
    it('est positionne en bas a droite', () => {
      mockToasts = [{ id: '1', message: 'Test', type: 'info' }]
      const { container } = render(<ToastContainer />)

      const toastContainer = container.firstChild as HTMLElement
      expect(toastContainer).toHaveClass('fixed', 'bottom-4', 'right-4')
    })

    it('a un z-index eleve', () => {
      mockToasts = [{ id: '1', message: 'Test', type: 'info' }]
      const { container } = render(<ToastContainer />)

      const toastContainer = container.firstChild as HTMLElement
      expect(toastContainer).toHaveClass('z-50')
    })
  })

  describe('Accessibilite', () => {
    it('le bouton fermer a un aria-label', () => {
      mockToasts = [{ id: '1', message: 'Test', type: 'info' }]
      render(<ToastContainer />)

      expect(screen.getByLabelText('Fermer la notification')).toBeInTheDocument()
    })
  })
})
