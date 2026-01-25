/**
 * Tests pour MobileTimePicker
 * FDH-11: Saisie mobile roulette HH:MM
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import MobileTimePicker from './MobileTimePicker'

describe('MobileTimePicker', () => {
  const defaultProps = {
    value: '08:30',
    onChange: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    // Reset body overflow
    document.body.style.overflow = ''
  })

  describe('Rendu', () => {
    it('affiche le bouton avec la valeur actuelle', () => {
      render(<MobileTimePicker {...defaultProps} />)
      expect(screen.getByText('08:30')).toBeInTheDocument()
    })

    it('affiche le placeholder si pas de valeur', () => {
      render(<MobileTimePicker {...defaultProps} value="" />)
      expect(screen.getByText('--:--')).toBeInTheDocument()
    })

    it('affiche le label si fourni', () => {
      render(<MobileTimePicker {...defaultProps} label="Heure de debut" />)
      expect(screen.getByText('Heure de debut')).toBeInTheDocument()
    })

    it('desactive le bouton si disabled', () => {
      render(<MobileTimePicker {...defaultProps} disabled />)
      const button = screen.getByRole('button')
      expect(button).toBeDisabled()
      expect(button).toHaveClass('bg-gray-100')
    })

    it('affiche l\'icone horloge', () => {
      render(<MobileTimePicker {...defaultProps} />)
      const button = screen.getByRole('button')
      expect(button.querySelector('svg')).toBeInTheDocument()
    })
  })

  describe('Ouverture du picker', () => {
    it('ouvre le modal au clic sur le bouton', () => {
      render(<MobileTimePicker {...defaultProps} />)
      fireEvent.click(screen.getByRole('button'))
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('n\'ouvre pas si disabled', () => {
      render(<MobileTimePicker {...defaultProps} disabled />)
      fireEvent.click(screen.getByRole('button'))
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('affiche les colonnes heures et minutes', () => {
      render(<MobileTimePicker {...defaultProps} />)
      fireEvent.click(screen.getByRole('button'))

      // Verifier que les heures sont affichees (00 apparait dans heures ET minutes)
      expect(screen.getAllByText('00').length).toBeGreaterThanOrEqual(2)
      expect(screen.getByText('23')).toBeInTheDocument()
    })

    it('affiche le separateur deux-points', () => {
      render(<MobileTimePicker {...defaultProps} />)
      fireEvent.click(screen.getByRole('button'))
      expect(screen.getByText(':')).toBeInTheDocument()
    })

    it('bloque le scroll du body quand ouvert', () => {
      render(<MobileTimePicker {...defaultProps} />)
      fireEvent.click(screen.getByRole('button'))
      expect(document.body.style.overflow).toBe('hidden')
    })
  })

  describe('Actions du modal', () => {
    it('ferme le modal au clic sur X', () => {
      render(<MobileTimePicker {...defaultProps} />)
      fireEvent.click(screen.getByRole('button'))
      expect(screen.getByRole('dialog')).toBeInTheDocument()

      fireEvent.click(screen.getByLabelText('Annuler'))
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('ferme le modal au clic sur le backdrop', () => {
      render(<MobileTimePicker {...defaultProps} />)
      fireEvent.click(screen.getByRole('button'))

      const backdrop = document.querySelector('.bg-black\\/50')
      if (backdrop) {
        fireEvent.click(backdrop)
      }
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('ferme le modal avec la touche Escape', () => {
      render(<MobileTimePicker {...defaultProps} />)
      fireEvent.click(screen.getByRole('button'))
      expect(screen.getByRole('dialog')).toBeInTheDocument()

      fireEvent.keyDown(document, { key: 'Escape' })
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('confirme la selection au clic sur Confirmer', async () => {
      const onChange = vi.fn()
      render(<MobileTimePicker {...defaultProps} onChange={onChange} />)
      fireEvent.click(screen.getByRole('button'))

      fireEvent.click(screen.getByLabelText('Confirmer'))

      await waitFor(() => {
        expect(onChange).toHaveBeenCalled()
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
      })
    })
  })

  describe('Boutons rapides', () => {
    it('affiche les boutons de selection rapide', () => {
      render(<MobileTimePicker {...defaultProps} />)
      fireEvent.click(screen.getByRole('button'))

      expect(screen.getByText('Maintenant')).toBeInTheDocument()
      expect(screen.getByText('07:00')).toBeInTheDocument()
      expect(screen.getByText('12:00')).toBeInTheDocument()
      expect(screen.getByText('17:00')).toBeInTheDocument()
    })

    it('applique 07:00 au clic sur le bouton correspondant', async () => {
      const onChange = vi.fn()
      render(<MobileTimePicker {...defaultProps} onChange={onChange} value="10:00" />)
      fireEvent.click(screen.getByRole('button'))

      fireEvent.click(screen.getByText('07:00'))
      fireEvent.click(screen.getByLabelText('Confirmer'))

      await waitFor(() => {
        expect(onChange).toHaveBeenCalledWith('07:00')
      })
    })

    it('applique 12:00 au clic sur le bouton correspondant', async () => {
      const onChange = vi.fn()
      render(<MobileTimePicker {...defaultProps} onChange={onChange} />)
      fireEvent.click(screen.getByRole('button'))

      fireEvent.click(screen.getByText('12:00'))
      fireEvent.click(screen.getByLabelText('Confirmer'))

      await waitFor(() => {
        expect(onChange).toHaveBeenCalledWith('12:00')
      })
    })

    it('applique 17:00 au clic sur le bouton correspondant', async () => {
      const onChange = vi.fn()
      render(<MobileTimePicker {...defaultProps} onChange={onChange} />)
      fireEvent.click(screen.getByRole('button'))

      fireEvent.click(screen.getByText('17:00'))
      fireEvent.click(screen.getByLabelText('Confirmer'))

      await waitFor(() => {
        expect(onChange).toHaveBeenCalledWith('17:00')
      })
    })
  })

  describe('Configuration', () => {
    it('respecte le step pour les minutes', () => {
      render(<MobileTimePicker {...defaultProps} step={15} />)
      fireEvent.click(screen.getByRole('button'))

      // Avec step=15, on devrait avoir 00, 15, 30, 45
      expect(screen.getAllByText('00').length).toBeGreaterThan(0)
      expect(screen.getAllByText('15').length).toBeGreaterThan(0)
      expect(screen.getAllByText('30').length).toBeGreaterThan(0)
      expect(screen.getAllByText('45').length).toBeGreaterThan(0)
    })

    it('applique la className personnalisee', () => {
      const { container } = render(
        <MobileTimePicker {...defaultProps} className="custom-class" />
      )
      expect(container.firstChild).toHaveClass('custom-class')
    })

    it('gere les valeurs invalides gracieusement', () => {
      render(<MobileTimePicker {...defaultProps} value="invalid" />)
      expect(screen.getByText('invalid')).toBeInTheDocument()
    })
  })

  describe('Accessibilite', () => {
    it('le bouton a un aria-label correct', () => {
      render(<MobileTimePicker {...defaultProps} label="Heure arrivee" />)
      expect(screen.getByLabelText('Heure arrivee: 08:30')).toBeInTheDocument()
    })

    it('le dialog a les attributs ARIA corrects', () => {
      render(<MobileTimePicker {...defaultProps} />)
      fireEvent.click(screen.getByRole('button'))

      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-modal', 'true')
      expect(dialog).toHaveAttribute('aria-label', "Sélecteur d'heure")
    })

    it('les boutons d\'action ont des aria-labels', () => {
      render(<MobileTimePicker {...defaultProps} />)
      fireEvent.click(screen.getByRole('button'))

      expect(screen.getByLabelText('Annuler')).toBeInTheDocument()
      expect(screen.getByLabelText('Confirmer')).toBeInTheDocument()
    })
  })
})
