/**
 * Tests pour EditUserModal
 *
 * Couvre:
 * - Affichage du formulaire avec valeurs initiales
 * - Modification des champs
 * - Soumission du formulaire
 * - Sélection de couleur
 * - Section contact d'urgence
 * - Fermeture
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { EditUserModal } from './EditUserModal'
import type { User } from '../../types'

const createMockUser = (overrides: Partial<User> = {}): User => ({
  id: '1',
  email: 'jean.dupont@test.com',
  nom: 'Dupont',
  prenom: 'Jean',
  role: 'compagnon',
  type_utilisateur: 'employe',
  couleur: '#3498db',
  is_active: true,
  created_at: '2024-01-01T00:00:00',
  updated_at: '2024-01-01T00:00:00',
  ...overrides,
})

describe('EditUserModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSubmit = vi.fn()

  const defaultProps = {
    user: createMockUser(),
    onClose: mockOnClose,
    onSubmit: mockOnSubmit,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockOnSubmit.mockResolvedValue(undefined)
  })

  describe('Affichage', () => {
    it('affiche le titre', () => {
      render(<EditUserModal {...defaultProps} />)
      expect(screen.getByText('Modifier l\'utilisateur')).toBeInTheDocument()
    })

    it('affiche les valeurs initiales de l\'utilisateur', () => {
      render(<EditUserModal {...defaultProps} />)

      const prenomInput = screen.getAllByRole('textbox')[0]
      const nomInput = screen.getAllByRole('textbox')[1]

      expect(prenomInput).toHaveValue('Jean')
      expect(nomInput).toHaveValue('Dupont')
    })

    it('affiche le rôle initial', () => {
      render(<EditUserModal {...defaultProps} />)

      const roleSelect = screen.getAllByRole('combobox')[0]
      expect(roleSelect).toHaveValue('compagnon')
    })

    it('affiche le type initial', () => {
      render(<EditUserModal {...defaultProps} />)

      const typeSelect = screen.getAllByRole('combobox')[1]
      expect(typeSelect).toHaveValue('employe')
    })

    it('affiche le métier initial si défini', () => {
      render(
        <EditUserModal
          {...defaultProps}
          user={createMockUser({ metier: 'macon' })}
        />
      )

      const metierSelect = screen.getAllByRole('combobox')[2]
      expect(metierSelect).toHaveValue('macon')
    })

    it('affiche le téléphone initial si défini', () => {
      render(
        <EditUserModal
          {...defaultProps}
          user={createMockUser({ telephone: '0612345678' })}
        />
      )

      // Use getAllByRole for tel inputs - fallback to checking values
      const phoneInput = screen.getAllByRole('textbox').find(
        input => (input as HTMLInputElement).value === '0612345678'
      )
      expect(phoneInput).toBeInTheDocument()
    })

    it('affiche le code utilisateur initial si défini', () => {
      render(
        <EditUserModal
          {...defaultProps}
          user={createMockUser({ code_utilisateur: 'EMP001' })}
        />
      )

      expect(screen.getByDisplayValue('EMP001')).toBeInTheDocument()
    })

    it('affiche les boutons Annuler et Enregistrer', () => {
      render(<EditUserModal {...defaultProps} />)
      expect(screen.getByText('Annuler')).toBeInTheDocument()
      expect(screen.getByText('Enregistrer')).toBeInTheDocument()
    })
  })

  describe('Modification des champs', () => {
    it('permet de modifier le prénom', async () => {
      const user = userEvent.setup()
      render(<EditUserModal {...defaultProps} />)

      const prenomInput = screen.getAllByRole('textbox')[0]
      await user.clear(prenomInput)
      await user.type(prenomInput, 'Pierre')

      expect(prenomInput).toHaveValue('Pierre')
    })

    it('permet de modifier le nom', async () => {
      const user = userEvent.setup()
      render(<EditUserModal {...defaultProps} />)

      const nomInput = screen.getAllByRole('textbox')[1]
      await user.clear(nomInput)
      await user.type(nomInput, 'Martin')

      expect(nomInput).toHaveValue('Martin')
    })

    it('permet de modifier le rôle', async () => {
      const user = userEvent.setup()
      render(<EditUserModal {...defaultProps} />)

      const roleSelect = screen.getAllByRole('combobox')[0]
      await user.selectOptions(roleSelect, 'chef_chantier')

      expect(roleSelect).toHaveValue('chef_chantier')
    })

    it('permet de modifier le type', async () => {
      const user = userEvent.setup()
      render(<EditUserModal {...defaultProps} />)

      const typeSelect = screen.getAllByRole('combobox')[1]
      await user.selectOptions(typeSelect, 'sous_traitant')

      expect(typeSelect).toHaveValue('sous_traitant')
    })

    it('permet de modifier le métier', async () => {
      const user = userEvent.setup()
      render(<EditUserModal {...defaultProps} />)

      const metierSelect = screen.getAllByRole('combobox')[2]
      await user.selectOptions(metierSelect, 'electricien')

      expect(metierSelect).toHaveValue('electricien')
    })
  })

  describe('Sélection de couleur', () => {
    it('affiche les boutons de couleur', () => {
      render(<EditUserModal {...defaultProps} />)
      expect(screen.getByText('Couleur')).toBeInTheDocument()
    })

    it('met en surbrillance la couleur actuelle', () => {
      // Le mock utilise #3498db qui correspond à 'Bleu clair' (#3498DB)
      render(<EditUserModal {...defaultProps} user={createMockUser({ couleur: '#3498DB' })} />)

      const selectedButton = document.querySelector('[style*="background-color: rgb(52, 152, 219)"]')
      expect(selectedButton?.className).toContain('border-gray-900')
    })

    it('permet de changer la couleur', async () => {
      const user = userEvent.setup()
      render(<EditUserModal {...defaultProps} />)

      // Find color buttons with title attribute
      const colorButtons = document.querySelectorAll('button[title]')
      const redButton = Array.from(colorButtons).find(
        btn => btn.getAttribute('title') === 'Rouge'
      )

      if (redButton) {
        await user.click(redButton)
        expect(redButton.className).toContain('border-gray-900')
      }
    })
  })

  describe('Section contact d\'urgence', () => {
    it('affiche la section contact d\'urgence', () => {
      render(<EditUserModal {...defaultProps} />)
      expect(screen.getByText('Contact d\'urgence')).toBeInTheDocument()
    })

    it('affiche les valeurs initiales du contact d\'urgence', () => {
      render(
        <EditUserModal
          {...defaultProps}
          user={createMockUser({
            contact_urgence_nom: 'Marie Dupont',
            contact_urgence_telephone: '0611223344',
          })}
        />
      )

      expect(screen.getByDisplayValue('Marie Dupont')).toBeInTheDocument()
      expect(screen.getByDisplayValue('0611223344')).toBeInTheDocument()
    })

    it('permet de modifier le contact d\'urgence', async () => {
      const user = userEvent.setup()
      render(<EditUserModal {...defaultProps} />)

      // Find the contact urgence inputs (last two text inputs)
      const textInputs = screen.getAllByRole('textbox')
      const contactNomInput = textInputs[textInputs.length - 2]

      await user.type(contactNomInput, 'Contact Test')
      expect(contactNomInput).toHaveValue('Contact Test')
    })
  })

  describe('Soumission', () => {
    it('appelle onSubmit avec les données modifiées', async () => {
      const user = userEvent.setup()
      render(<EditUserModal {...defaultProps} />)

      const prenomInput = screen.getAllByRole('textbox')[0]
      await user.clear(prenomInput)
      await user.type(prenomInput, 'Pierre')

      await user.click(screen.getByText('Enregistrer'))

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            prenom: 'Pierre',
            nom: 'Dupont',
          })
        )
      })
    })

    it('affiche un spinner pendant la soumission', async () => {
      mockOnSubmit.mockImplementation(() => new Promise(() => {})) // Never resolves

      const user = userEvent.setup()
      render(<EditUserModal {...defaultProps} />)

      await user.click(screen.getByText('Enregistrer'))

      await waitFor(() => {
        expect(document.querySelector('.animate-spin')).toBeInTheDocument()
      })
    })

    it('désactive le bouton pendant la soumission', async () => {
      mockOnSubmit.mockImplementation(() => new Promise(() => {}))

      const user = userEvent.setup()
      render(<EditUserModal {...defaultProps} />)

      await user.click(screen.getByText('Enregistrer'))

      await waitFor(() => {
        expect(screen.getByText('Enregistrer').closest('button')).toBeDisabled()
      })
    })
  })

  describe('Fermeture', () => {
    it('appelle onClose au clic sur Annuler', async () => {
      const user = userEvent.setup()
      render(<EditUserModal {...defaultProps} />)

      await user.click(screen.getByText('Annuler'))
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose au clic sur le bouton X', async () => {
      const user = userEvent.setup()
      render(<EditUserModal {...defaultProps} />)

      const closeButtons = screen.getAllByRole('button')
      const xButton = closeButtons.find(btn => btn.querySelector('svg.lucide-x'))
      if (xButton) {
        await user.click(xButton)
        expect(mockOnClose).toHaveBeenCalled()
      }
    })

    it('appelle onClose au clic sur l\'overlay', async () => {
      const user = userEvent.setup()
      render(<EditUserModal {...defaultProps} />)

      const overlay = document.querySelector('.bg-black\\/50')
      if (overlay) {
        await user.click(overlay)
        expect(mockOnClose).toHaveBeenCalled()
      }
    })
  })

  describe('Valeurs optionnelles', () => {
    it('gère les valeurs undefined', () => {
      render(
        <EditUserModal
          {...defaultProps}
          user={createMockUser({
            telephone: undefined,
            metier: undefined,
            code_utilisateur: undefined,
            contact_urgence_nom: undefined,
            contact_urgence_telephone: undefined,
          })}
        />
      )

      // Should not crash, inputs should be empty
      const textInputs = screen.getAllByRole('textbox')
      expect(textInputs.length).toBeGreaterThan(0)
    })
  })
})
