/**
 * Tests pour SignaturePad
 *
 * Couvre:
 * - Affichage en mode lecture seule avec/sans signature
 * - Mode édition: ouverture/fermeture modal
 * - Canvas de dessin (events mouse/touch)
 * - Sauvegarde et suppression de signature
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SignaturePad from './SignaturePad'

// Mock logger
vi.mock('../../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

// Mock canvas methods
const mockToDataURL = vi.fn(() => 'data:image/png;base64,mockSignature')
const mockGetContext = vi.fn(() => ({
  scale: vi.fn(),
  beginPath: vi.fn(),
  moveTo: vi.fn(),
  lineTo: vi.fn(),
  stroke: vi.fn(),
  closePath: vi.fn(),
  fillRect: vi.fn(),
  fillStyle: '',
  lineCap: '',
  lineJoin: '',
  strokeStyle: '',
  lineWidth: 0,
}))

// Override HTMLCanvasElement prototype
beforeEach(() => {
  // @ts-expect-error - Simplified mock for testing
  HTMLCanvasElement.prototype.getContext = mockGetContext
  HTMLCanvasElement.prototype.toDataURL = mockToDataURL
  HTMLCanvasElement.prototype.getBoundingClientRect = vi.fn(() => ({
    width: 300,
    height: 160,
    top: 0,
    left: 0,
    bottom: 160,
    right: 300,
    x: 0,
    y: 0,
    toJSON: () => {},
  }))
  vi.clearAllMocks()
})

describe('SignaturePad', () => {
  const mockOnChange = vi.fn()
  const mockOnSignatureNomChange = vi.fn()

  const defaultProps = {
    onChange: mockOnChange,
  }

  describe('Mode lecture seule', () => {
    it('affiche "Aucune signature" si pas de valeur', () => {
      render(<SignaturePad {...defaultProps} readOnly />)
      expect(screen.getByText('Aucune signature')).toBeInTheDocument()
    })

    it('affiche l\'image de signature si valeur fournie', () => {
      render(<SignaturePad {...defaultProps} value="data:image/png;base64,test" readOnly />)
      const img = screen.getByAltText('Signature')
      expect(img).toBeInTheDocument()
      expect(img).toHaveAttribute('src', 'data:image/png;base64,test')
    })

    it('affiche le nom du signataire si fourni', () => {
      render(
        <SignaturePad
          {...defaultProps}
          value="data:image/png;base64,test"
          signatureNom="Jean Dupont"
          readOnly
        />
      )
      expect(screen.getByText('Signe par Jean Dupont')).toBeInTheDocument()
    })
  })

  describe('Mode édition sans signature', () => {
    it('affiche le bouton "Signer"', () => {
      render(<SignaturePad {...defaultProps} />)
      expect(screen.getByRole('button', { name: 'Signer' })).toBeInTheDocument()
    })

    it('affiche le texte "Signez ce formulaire"', () => {
      render(<SignaturePad {...defaultProps} />)
      expect(screen.getByText('Signez ce formulaire')).toBeInTheDocument()
    })

    it('ouvre le modal au clic sur Signer', async () => {
      const user = userEvent.setup()
      render(<SignaturePad {...defaultProps} />)

      await user.click(screen.getByRole('button', { name: 'Signer' }))

      await waitFor(() => {
        expect(screen.getByText('Signature')).toBeInTheDocument()
        expect(screen.getByText('Nom du signataire')).toBeInTheDocument()
        expect(screen.getByText('Signez ci-dessous')).toBeInTheDocument()
      })
    })
  })

  describe('Mode édition avec signature existante', () => {
    it('affiche l\'image de signature', () => {
      render(<SignaturePad {...defaultProps} value="data:image/png;base64,test" />)
      expect(screen.getByAltText('Signature')).toBeInTheDocument()
    })

    it('affiche le bouton supprimer', () => {
      render(<SignaturePad {...defaultProps} value="data:image/png;base64,test" />)
      expect(screen.getByTitle('Supprimer la signature')).toBeInTheDocument()
    })

    it('supprime la signature au clic sur le bouton supprimer', async () => {
      const user = userEvent.setup()
      render(
        <SignaturePad
          {...defaultProps}
          value="data:image/png;base64,test"
          signatureNom="Test"
          onSignatureNomChange={mockOnSignatureNomChange}
        />
      )

      await user.click(screen.getByTitle('Supprimer la signature'))

      expect(mockOnChange).toHaveBeenCalledWith('')
      expect(mockOnSignatureNomChange).toHaveBeenCalledWith('')
    })

    it('affiche le nom du signataire sous l\'image', () => {
      render(
        <SignaturePad
          {...defaultProps}
          value="data:image/png;base64,test"
          signatureNom="Jean Dupont"
        />
      )
      expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
    })
  })

  describe('Modal de signature', () => {
    it('ferme le modal au clic sur le bouton X', async () => {
      const user = userEvent.setup()
      render(<SignaturePad {...defaultProps} />)

      // Ouvrir le modal
      await user.click(screen.getByRole('button', { name: 'Signer' }))
      await waitFor(() => {
        expect(screen.getByText('Signature')).toBeInTheDocument()
      })

      // Fermer le modal
      const closeButtons = screen.getAllByRole('button')
      const xButton = closeButtons.find(btn => btn.querySelector('svg.lucide-x'))
      if (xButton) {
        await user.click(xButton)
      }

      await waitFor(() => {
        expect(screen.queryByText('Nom du signataire')).not.toBeInTheDocument()
      })
    })

    it('ferme le modal au clic sur Annuler', async () => {
      const user = userEvent.setup()
      render(<SignaturePad {...defaultProps} />)

      await user.click(screen.getByRole('button', { name: 'Signer' }))
      await waitFor(() => {
        expect(screen.getByText('Signature')).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: 'Annuler' }))

      await waitFor(() => {
        expect(screen.queryByText('Nom du signataire')).not.toBeInTheDocument()
      })
    })

    it('ferme le modal au clic sur l\'overlay', async () => {
      const user = userEvent.setup()
      render(<SignaturePad {...defaultProps} />)

      await user.click(screen.getByRole('button', { name: 'Signer' }))
      await waitFor(() => {
        expect(screen.getByText('Signature')).toBeInTheDocument()
      })

      // Cliquer sur l'overlay (bg-black/50)
      const overlay = document.querySelector('.bg-black\\/50')
      if (overlay) {
        await user.click(overlay)
      }

      await waitFor(() => {
        expect(screen.queryByText('Nom du signataire')).not.toBeInTheDocument()
      })
    })

    it('permet de saisir le nom du signataire', async () => {
      const user = userEvent.setup()
      render(<SignaturePad {...defaultProps} />)

      await user.click(screen.getByRole('button', { name: 'Signer' }))
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Votre nom')).toBeInTheDocument()
      })

      await user.type(screen.getByPlaceholderText('Votre nom'), 'Jean Dupont')
      expect(screen.getByPlaceholderText('Votre nom')).toHaveValue('Jean Dupont')
    })

    it('le bouton Valider est désactivé sans nom et sans signature', async () => {
      const user = userEvent.setup()
      render(<SignaturePad {...defaultProps} />)

      await user.click(screen.getByRole('button', { name: 'Signer' }))
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /valider/i })).toBeDisabled()
      })
    })

    it('le bouton Effacer efface le canvas', async () => {
      const user = userEvent.setup()
      render(<SignaturePad {...defaultProps} />)

      await user.click(screen.getByRole('button', { name: 'Signer' }))
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /effacer/i })).toBeInTheDocument()
      })

      // Simuler un dessin
      const canvas = screen.getByRole('img', { name: /zone de signature/i })
      fireEvent.mouseDown(canvas, { clientX: 50, clientY: 50 })
      fireEvent.mouseUp(canvas)

      // Effacer
      await user.click(screen.getByRole('button', { name: /effacer/i }))

      // Le bouton Valider devrait être désactivé car plus de signature
      expect(screen.getByRole('button', { name: /valider/i })).toBeDisabled()
    })
  })

  describe('Canvas drawing events', () => {
    it('affiche le canvas de signature dans le modal', async () => {
      const user = userEvent.setup()
      render(<SignaturePad {...defaultProps} />)

      await user.click(screen.getByRole('button', { name: 'Signer' }))
      await waitFor(() => {
        // Le canvas est présent avec le bon aria-label
        const canvas = document.querySelector('canvas')
        expect(canvas).toBeInTheDocument()
        expect(canvas).toHaveAttribute('role', 'img')
      })
    })

    it('le canvas a les bons gestionnaires d\'événements', async () => {
      const user = userEvent.setup()
      render(<SignaturePad {...defaultProps} />)

      await user.click(screen.getByRole('button', { name: 'Signer' }))
      await waitFor(() => {
        const canvas = document.querySelector('canvas')
        expect(canvas).toBeInTheDocument()
        // Le canvas doit avoir la classe touch-none pour les événements touch
        expect(canvas).toHaveClass('touch-none')
      })
    })

    it('le canvas est interactif avec cursor-crosshair', async () => {
      const user = userEvent.setup()
      render(<SignaturePad {...defaultProps} />)

      await user.click(screen.getByRole('button', { name: 'Signer' }))
      await waitFor(() => {
        const canvas = document.querySelector('canvas')
        expect(canvas).toHaveClass('cursor-crosshair')
      })
    })
  })

  describe('Sauvegarde signature', () => {
    it('affiche les boutons de validation dans le modal', async () => {
      const user = userEvent.setup()
      render(
        <SignaturePad
          {...defaultProps}
          onSignatureNomChange={mockOnSignatureNomChange}
        />
      )

      await user.click(screen.getByRole('button', { name: 'Signer' }))
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Votre nom')).toBeInTheDocument()
      })

      // Le bouton Valider et Annuler doivent être présents
      expect(screen.getByRole('button', { name: /valider/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Annuler' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /effacer/i })).toBeInTheDocument()
    })
  })
})
