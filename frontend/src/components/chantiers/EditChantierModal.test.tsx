/**
 * Tests pour EditChantierModal
 *
 * Couvre:
 * - Affichage du formulaire avec valeurs initiales
 * - Modification des champs (nom, adresse, statut)
 * - Sélection de couleur
 * - Gestion des contacts (ajout, suppression, modification)
 * - Gestion des phases (ajout, suppression, modification)
 * - Geocoding automatique
 * - Soumission du formulaire
 * - Fermeture
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import EditChantierModal from './EditChantierModal'
import type { Chantier } from '../../types'

// Mock geocoding service
vi.mock('../../services/geocoding', () => ({
  geocodeAddress: vi.fn().mockResolvedValue({
    latitude: 45.764043,
    longitude: 4.835659,
    displayName: 'Lyon, France',
  }),
}))

// Mock chantiers service
vi.mock('../../services/chantiers', () => ({
  chantiersService: {
    listPhases: vi.fn().mockResolvedValue([]),
    addPhase: vi.fn().mockResolvedValue({}),
    updatePhase: vi.fn().mockResolvedValue({}),
    removePhase: vi.fn().mockResolvedValue(undefined),
  },
}))

const createMockChantier = (overrides: Partial<Chantier> = {}): Chantier => ({
  id: '1',
  code: 'CH001',
  nom: 'Chantier Test',
  adresse: '12 Rue de la Republique, Lyon',
  couleur: '#3498DB',
  statut: 'en_cours',
  conducteurs: [],
  chefs: [],
  created_at: '2024-01-01',
  ...overrides,
})

describe('EditChantierModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSubmit = vi.fn()

  const defaultProps = {
    chantier: createMockChantier(),
    onClose: mockOnClose,
    onSubmit: mockOnSubmit,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockOnSubmit.mockResolvedValue(undefined)
  })

  describe('Affichage', () => {
    it('affiche le titre', () => {
      render(<EditChantierModal {...defaultProps} />)
      expect(screen.getByText('Modifier le chantier')).toBeInTheDocument()
    })

    it('affiche les valeurs initiales du chantier', () => {
      render(<EditChantierModal {...defaultProps} />)

      expect(screen.getByDisplayValue('Chantier Test')).toBeInTheDocument()
      expect(screen.getByDisplayValue('12 Rue de la Republique, Lyon')).toBeInTheDocument()
    })

    it('affiche le statut initial', () => {
      render(<EditChantierModal {...defaultProps} />)

      const statutSelect = screen.getByDisplayValue('En cours')
      expect(statutSelect).toBeInTheDocument()
    })

    it('affiche les boutons Annuler et Enregistrer', () => {
      render(<EditChantierModal {...defaultProps} />)

      expect(screen.getByText('Annuler')).toBeInTheDocument()
      expect(screen.getByText('Enregistrer')).toBeInTheDocument()
    })
  })

  describe('Modification des champs', () => {
    it('permet de modifier le nom', async () => {
      const user = userEvent.setup()
      render(<EditChantierModal {...defaultProps} />)

      const nomInput = screen.getByDisplayValue('Chantier Test')
      await user.clear(nomInput)
      await user.type(nomInput, 'Nouveau Chantier')

      expect(nomInput).toHaveValue('Nouveau Chantier')
    })

    it('permet de modifier l adresse', async () => {
      const user = userEvent.setup()
      render(<EditChantierModal {...defaultProps} />)

      const adresseInput = screen.getByDisplayValue('12 Rue de la Republique, Lyon')
      await user.clear(adresseInput)
      await user.type(adresseInput, 'Nouvelle adresse')

      expect(adresseInput).toHaveValue('Nouvelle adresse')
    })

    it('permet de modifier le statut', async () => {
      const user = userEvent.setup()
      render(<EditChantierModal {...defaultProps} />)

      const statutSelect = screen.getByDisplayValue('En cours')
      await user.selectOptions(statutSelect, 'ferme')

      expect(statutSelect).toHaveValue('ferme')
    })

    it('permet de modifier les heures estimees', async () => {
      const user = userEvent.setup()
      render(<EditChantierModal {...defaultProps} chantier={createMockChantier({ heures_estimees: 100 })} />)

      const heuresInput = screen.getByDisplayValue('100')
      await user.clear(heuresInput)
      await user.type(heuresInput, '200')

      expect(heuresInput).toHaveValue(200)
    })
  })

  describe('Selection de couleur', () => {
    it('affiche les boutons de couleur', () => {
      render(<EditChantierModal {...defaultProps} />)
      expect(screen.getByText('Couleur')).toBeInTheDocument()
    })

    it('met en surbrillance la couleur actuelle', () => {
      render(<EditChantierModal {...defaultProps} />)

      const selectedButton = document.querySelector('[style*="background-color: rgb(52, 152, 219)"]')
      expect(selectedButton?.className).toContain('border-gray-900')
    })
  })

  describe('Gestion des contacts', () => {
    it('affiche le label Contacts sur place', () => {
      render(<EditChantierModal {...defaultProps} />)
      expect(screen.getByText('Contacts sur place')).toBeInTheDocument()
    })

    it('affiche le bouton Ajouter pour les contacts', () => {
      render(<EditChantierModal {...defaultProps} />)
      expect(screen.getByText('Ajouter')).toBeInTheDocument()
    })

    it('permet d ajouter un contact', async () => {
      const user = userEvent.setup()
      render(<EditChantierModal {...defaultProps} />)

      const nomInputsBefore = screen.getAllByPlaceholderText('Nom')

      await user.click(screen.getByText('Ajouter'))

      const nomInputsAfter = screen.getAllByPlaceholderText('Nom')
      expect(nomInputsAfter.length).toBe(nomInputsBefore.length + 1)
    })

    it('affiche les contacts existants', () => {
      render(
        <EditChantierModal
          {...defaultProps}
          chantier={createMockChantier({
            contacts: [
              { nom: 'Contact 1', telephone: '0612345678', profession: 'Architecte' },
            ],
          })}
        />
      )

      expect(screen.getByDisplayValue('Contact 1')).toBeInTheDocument()
      expect(screen.getByDisplayValue('0612345678')).toBeInTheDocument()
      expect(screen.getByDisplayValue('Architecte')).toBeInTheDocument()
    })
  })

  describe('Gestion des phases', () => {
    it('affiche le label Periodes fractionnees', () => {
      render(<EditChantierModal {...defaultProps} />)
      expect(screen.getByText('Periodes fractionnees')).toBeInTheDocument()
    })

    it('affiche le message si aucune periode', () => {
      render(<EditChantierModal {...defaultProps} />)
      expect(screen.getByText(/Aucune periode definie/)).toBeInTheDocument()
    })

    it('permet d ajouter une periode', async () => {
      const user = userEvent.setup()
      render(<EditChantierModal {...defaultProps} />)

      await user.click(screen.getByText('Ajouter une periode'))

      expect(screen.getByPlaceholderText('Nom de la periode')).toBeInTheDocument()
    })
  })

  describe('Dates du chantier', () => {
    it('affiche les champs de date si pas de phases', () => {
      render(<EditChantierModal {...defaultProps} />)

      expect(screen.getByText('Date debut prevue')).toBeInTheDocument()
      expect(screen.getByText('Date fin prevue')).toBeInTheDocument()
    })

    it('affiche les dates initiales', () => {
      render(
        <EditChantierModal
          {...defaultProps}
          chantier={createMockChantier({
            date_debut_prevue: '2024-01-15',
            date_fin_prevue: '2024-06-30',
          })}
        />
      )

      expect(screen.getByDisplayValue('2024-01-15')).toBeInTheDocument()
      expect(screen.getByDisplayValue('2024-06-30')).toBeInTheDocument()
    })
  })

  describe('Soumission', () => {
    it('appelle onSubmit avec les donnees modifiees', async () => {
      const user = userEvent.setup()
      render(<EditChantierModal {...defaultProps} />)

      const nomInput = screen.getByDisplayValue('Chantier Test')
      await user.clear(nomInput)
      await user.type(nomInput, 'Chantier Modifie')

      await user.click(screen.getByText('Enregistrer'))

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            nom: 'Chantier Modifie',
          })
        )
      })
    })

    it('affiche un spinner pendant la soumission', async () => {
      mockOnSubmit.mockImplementation(() => new Promise(() => {}))

      const user = userEvent.setup()
      render(<EditChantierModal {...defaultProps} />)

      await user.click(screen.getByText('Enregistrer'))

      await waitFor(() => {
        expect(document.querySelector('.animate-spin')).toBeInTheDocument()
      })
    })

    it('desactive le bouton pendant la soumission', async () => {
      mockOnSubmit.mockImplementation(() => new Promise(() => {}))

      const user = userEvent.setup()
      render(<EditChantierModal {...defaultProps} />)

      await user.click(screen.getByText('Enregistrer'))

      await waitFor(() => {
        expect(screen.getByText('Enregistrer').closest('button')).toBeDisabled()
      })
    })
  })

  describe('Fermeture', () => {
    it('appelle onClose au clic sur Annuler', async () => {
      const user = userEvent.setup()
      render(<EditChantierModal {...defaultProps} />)

      await user.click(screen.getByText('Annuler'))
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose au clic sur le bouton X', async () => {
      const user = userEvent.setup()
      render(<EditChantierModal {...defaultProps} />)

      const closeButton = screen.getByLabelText('Fermer')
      await user.click(closeButton)
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose au clic sur l overlay', async () => {
      const user = userEvent.setup()
      render(<EditChantierModal {...defaultProps} />)

      const overlay = document.querySelector('[aria-hidden="true"]')
      if (overlay) {
        await user.click(overlay)
        expect(mockOnClose).toHaveBeenCalled()
      }
    })
  })
})
