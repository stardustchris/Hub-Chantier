/**
 * Tests pour AffectationModal
 *
 * Couvre:
 * - Mode création vs édition
 * - Initialisation du formulaire
 * - Sélection utilisateur/chantier
 * - Gestion des dates et horaires
 * - Affectations récurrentes
 * - Soumission et validation
 * - Gestion des erreurs
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AffectationModal from './AffectationModal'
import type { Affectation, User, Chantier } from '../../types'

// Helper to get form field by label text (since labels don't have htmlFor)
const getFieldByLabel = (labelText: string | RegExp): HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement => {
  const label = typeof labelText === 'string'
    ? screen.getByText(labelText)
    : screen.getByText(labelText)
  const container = label.parentElement
  if (!container) throw new Error(`Cannot find container for label: ${labelText}`)
  const input = container.querySelector('input, select, textarea')
  if (!input) throw new Error(`Cannot find input for label: ${labelText}`)
  return input as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
}

const createMockUser = (overrides: Partial<User> = {}): User => ({
  id: 'user-1',
  email: 'test@example.com',
  nom: 'Dupont',
  prenom: 'Jean',
  role: 'compagnon',
  type_utilisateur: 'employe',
  is_active: true,
  created_at: '2024-01-01',
  couleur: '#3498DB',
  ...overrides,
})

const createMockChantier = (overrides: Partial<Chantier> = {}): Chantier => ({
  id: 'ch-1',
  code: 'CH001',
  nom: 'Chantier Test',
  adresse: '123 Rue Test',
  statut: 'en_cours',
  conducteurs: [],
  chefs: [],
  created_at: '2024-01-01',
  ...overrides,
})

const createMockAffectation = (overrides: Partial<Affectation> = {}): Affectation => ({
  id: 'aff-1',
  utilisateur_id: 'user-1',
  chantier_id: 'ch-1',
  date: '2024-01-15',
  heure_debut: '08:00',
  heure_fin: '17:00',
  chantier_nom: 'Chantier Test',
  type_affectation: 'unique',
  created_at: '2024-01-01',
  updated_at: '2024-01-01',
  created_by: 'user-1',
  ...overrides,
})

describe('AffectationModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSave = vi.fn().mockResolvedValue(undefined)

  const defaultUsers = [
    createMockUser({ id: 'user-1', prenom: 'Jean', nom: 'Dupont' }),
    createMockUser({ id: 'user-2', prenom: 'Marie', nom: 'Martin' }),
  ]

  const defaultChantiers = [
    createMockChantier({ id: 'ch-1', code: 'CH001', nom: 'Chantier 1' }),
    createMockChantier({ id: 'ch-2', code: 'CH002', nom: 'Chantier 2' }),
  ]

  const defaultProps = {
    isOpen: true,
    onClose: mockOnClose,
    onSave: mockOnSave,
    utilisateurs: defaultUsers,
    chantiers: defaultChantiers,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendu conditionnel', () => {
    it('ne rend rien quand isOpen est false', () => {
      render(<AffectationModal {...defaultProps} isOpen={false} />)
      expect(screen.queryByText('Nouvelle affectation')).not.toBeInTheDocument()
    })

    it('rend le modal quand isOpen est true', () => {
      render(<AffectationModal {...defaultProps} />)
      expect(screen.getByText('Nouvelle affectation')).toBeInTheDocument()
    })
  })

  describe('Mode création', () => {
    it('affiche le titre "Nouvelle affectation"', () => {
      render(<AffectationModal {...defaultProps} />)
      expect(screen.getByText('Nouvelle affectation')).toBeInTheDocument()
    })

    it('affiche le sélecteur d\'utilisateur', () => {
      render(<AffectationModal {...defaultProps} />)
      expect(screen.getByText('Utilisateur *')).toBeInTheDocument()
      expect(screen.getByText('Sélectionner un utilisateur')).toBeInTheDocument()
    })

    it('affiche la liste des utilisateurs', () => {
      render(<AffectationModal {...defaultProps} />)
      expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
      expect(screen.getByText('Marie Martin')).toBeInTheDocument()
    })

    it('affiche le sélecteur de chantier', () => {
      render(<AffectationModal {...defaultProps} />)
      expect(screen.getByText('Chantier / Absence *')).toBeInTheDocument()
      expect(screen.getByText('Sélectionner...')).toBeInTheDocument()
    })

    it('affiche la liste des chantiers', () => {
      render(<AffectationModal {...defaultProps} />)
      expect(screen.getByText('CH001 - Chantier 1')).toBeInTheDocument()
      expect(screen.getByText('CH002 - Chantier 2')).toBeInTheDocument()
    })

    it('affiche les champs de date', () => {
      render(<AffectationModal {...defaultProps} />)
      expect(screen.getByText('Date début *')).toBeInTheDocument()
      expect(screen.getByText('Date fin')).toBeInTheDocument()
    })

    it('affiche les options de type d\'affectation', () => {
      render(<AffectationModal {...defaultProps} />)
      expect(screen.getByText("Type d'affectation")).toBeInTheDocument()
      expect(screen.getByText('Unique')).toBeInTheDocument()
      expect(screen.getByText('Récurrente')).toBeInTheDocument()
    })

    it('affiche le bouton Créer', () => {
      render(<AffectationModal {...defaultProps} />)
      expect(screen.getByRole('button', { name: 'Créer' })).toBeInTheDocument()
    })
  })

  describe('Mode édition', () => {
    const editAffectation = createMockAffectation()

    it('affiche le titre "Modifier l\'affectation"', () => {
      render(<AffectationModal {...defaultProps} affectation={editAffectation} />)
      expect(screen.getByText("Modifier l'affectation")).toBeInTheDocument()
    })

    it('n\'affiche pas le sélecteur d\'utilisateur', () => {
      render(<AffectationModal {...defaultProps} affectation={editAffectation} />)
      expect(screen.queryByText('Utilisateur *')).not.toBeInTheDocument()
    })

    it('n\'affiche pas les champs de date', () => {
      render(<AffectationModal {...defaultProps} affectation={editAffectation} />)
      expect(screen.queryByText('Date début *')).not.toBeInTheDocument()
    })

    it('n\'affiche pas le type d\'affectation', () => {
      render(<AffectationModal {...defaultProps} affectation={editAffectation} />)
      expect(screen.queryByText("Type d'affectation")).not.toBeInTheDocument()
    })

    it('affiche le bouton Modifier', () => {
      render(<AffectationModal {...defaultProps} affectation={editAffectation} />)
      expect(screen.getByRole('button', { name: 'Modifier' })).toBeInTheDocument()
    })

    it('initialise les horaires depuis l\'affectation', () => {
      render(<AffectationModal {...defaultProps} affectation={editAffectation} />)
      expect(screen.getByDisplayValue('08:00')).toBeInTheDocument()
      expect(screen.getByDisplayValue('17:00')).toBeInTheDocument()
    })

    it('initialise la note depuis l\'affectation', () => {
      const affWithNote = createMockAffectation({ note: 'Ma note importante' })
      render(<AffectationModal {...defaultProps} affectation={affWithNote} />)
      expect(screen.getByDisplayValue('Ma note importante')).toBeInTheDocument()
    })
  })

  describe('Initialisation avec données pré-sélectionnées', () => {
    it('initialise l\'utilisateur sélectionné', () => {
      render(<AffectationModal {...defaultProps} selectedUserId="user-2" />)
      const select = screen.getAllByRole('combobox')[0]
      expect(select).toHaveValue('user-2')
    })

    it('initialise le chantier sélectionné', () => {
      render(<AffectationModal {...defaultProps} selectedChantierId="ch-2" />)
      const select = screen.getAllByRole('combobox')[1]
      expect(select).toHaveValue('ch-2')
    })

    it('initialise la date sélectionnée', () => {
      const selectedDate = new Date('2024-03-20')
      render(<AffectationModal {...defaultProps} selectedDate={selectedDate} />)
      // Les deux champs date_debut et date_fin_recurrence devraient avoir la même valeur initialement
      const dateInputs = screen.getAllByDisplayValue('2024-03-20')
      expect(dateInputs.length).toBeGreaterThanOrEqual(1)
    })
  })

  describe('Affectation récurrente', () => {
    it('affiche les jours de récurrence quand type=recurrente', async () => {
      const user = userEvent.setup()
      render(<AffectationModal {...defaultProps} />)

      const recurrenteRadio = screen.getByLabelText('Récurrente')
      await user.click(recurrenteRadio)

      expect(screen.getByText('Jours de récurrence')).toBeInTheDocument()
      expect(screen.getByText('Lun')).toBeInTheDocument()
      expect(screen.getByText('Mar')).toBeInTheDocument()
      expect(screen.getByText('Mer')).toBeInTheDocument()
    })

    it('affiche le champ date fin de récurrence', async () => {
      const user = userEvent.setup()
      render(<AffectationModal {...defaultProps} />)

      const recurrenteRadio = screen.getByLabelText('Récurrente')
      await user.click(recurrenteRadio)

      expect(screen.getByText('Date fin de récurrence *')).toBeInTheDocument()
    })

    it('permet de sélectionner des jours de récurrence', async () => {
      const user = userEvent.setup()
      render(<AffectationModal {...defaultProps} />)

      const recurrenteRadio = screen.getByLabelText('Récurrente')
      await user.click(recurrenteRadio)

      const lunButton = screen.getByText('Lun')
      await user.click(lunButton)

      // Le bouton devrait avoir une classe indiquant qu'il est sélectionné
      expect(lunButton).toHaveClass('bg-primary-100')
    })

    it('permet de désélectionner des jours de récurrence', async () => {
      const user = userEvent.setup()
      render(<AffectationModal {...defaultProps} />)

      const recurrenteRadio = screen.getByLabelText('Récurrente')
      await user.click(recurrenteRadio)

      const lunButton = screen.getByText('Lun')
      await user.click(lunButton) // Select
      await user.click(lunButton) // Deselect

      expect(lunButton).not.toHaveClass('bg-primary-100')
    })
  })

  describe('Soumission du formulaire', () => {
    it('appelle onSave avec les données en création', async () => {
      const user = userEvent.setup()
      render(<AffectationModal {...defaultProps} />)

      // Sélectionner utilisateur
      const userSelect = screen.getAllByRole('combobox')[0]
      await user.selectOptions(userSelect, 'user-1')

      // Sélectionner chantier
      const chantierSelect = screen.getAllByRole('combobox')[1]
      await user.selectOptions(chantierSelect, 'ch-1')

      // Entrer la date
      const dateInput = getFieldByLabel('Date début *')
      await user.type(dateInput, '2024-03-15')

      // Soumettre
      const submitButton = screen.getByRole('button', { name: 'Créer' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSave).toHaveBeenCalledWith(
          expect.objectContaining({
            utilisateur_id: 'user-1',
            chantier_id: 'ch-1',
            date: '2024-03-15',
            type_affectation: 'unique',
          })
        )
      })
    })

    it('appelle onSave avec les données en édition', async () => {
      const user = userEvent.setup()
      const affectation = createMockAffectation()
      render(<AffectationModal {...defaultProps} affectation={affectation} />)

      // Modifier l'heure de début
      const heureDebutInput = screen.getByDisplayValue('08:00')
      await user.clear(heureDebutInput)
      await user.type(heureDebutInput, '09:00')

      // Soumettre
      const submitButton = screen.getByRole('button', { name: 'Modifier' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSave).toHaveBeenCalledWith(
          expect.objectContaining({
            heure_debut: '09:00',
          })
        )
      })
    })

    it('inclut jours_recurrence pour les affectations récurrentes', async () => {
      const user = userEvent.setup()
      render(<AffectationModal {...defaultProps} />)

      // Sélectionner utilisateur via fireEvent (optgroup incompatible avec selectOptions)
      const userSelect = getFieldByLabel('Utilisateur *') as HTMLSelectElement
      fireEvent.change(userSelect, { target: { value: 'user-1' } })

      // Sélectionner chantier
      const chantierSelect = getFieldByLabel('Chantier / Absence *') as HTMLSelectElement
      fireEvent.change(chantierSelect, { target: { value: 'ch-1' } })

      // Entrer la date
      const dateInput = getFieldByLabel('Date début *')
      fireEvent.change(dateInput, { target: { value: '2024-03-15' } })

      // Passer en mode récurrent
      const recurrenteRadio = screen.getByDisplayValue('recurrente')
      await user.click(recurrenteRadio)

      // Sélectionner lundi et mercredi
      await user.click(screen.getByText('Lun'))
      await user.click(screen.getByText('Mer'))

      // Date fin récurrence
      const dateFinInput = getFieldByLabel('Date fin de récurrence *')
      fireEvent.change(dateFinInput, { target: { value: '2024-04-15' } })

      // Soumettre
      const submitButton = screen.getByRole('button', { name: 'Créer' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSave).toHaveBeenCalledWith(
          expect.objectContaining({
            type_affectation: 'recurrente',
            jours_recurrence: expect.arrayContaining([0, 2]),
            date_fin_recurrence: '2024-04-15',
          })
        )
      })
    })

    it('ferme le modal après soumission réussie', async () => {
      const user = userEvent.setup()
      const affectation = createMockAffectation()
      render(<AffectationModal {...defaultProps} affectation={affectation} />)

      const submitButton = screen.getByRole('button', { name: 'Modifier' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnClose).toHaveBeenCalled()
      })
    })

    it('affiche le texte de chargement pendant la soumission', async () => {
      const user = userEvent.setup()
      mockOnSave.mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 1000)))

      const affectation = createMockAffectation()
      render(<AffectationModal {...defaultProps} affectation={affectation} />)

      const submitButton = screen.getByRole('button', { name: 'Modifier' })
      await user.click(submitButton)

      expect(screen.getByText('Enregistrement...')).toBeInTheDocument()
    })

    it('désactive les boutons pendant le chargement', async () => {
      const user = userEvent.setup()
      mockOnSave.mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 1000)))

      const affectation = createMockAffectation()
      render(<AffectationModal {...defaultProps} affectation={affectation} />)

      const submitButton = screen.getByRole('button', { name: 'Modifier' })
      await user.click(submitButton)

      expect(submitButton).toBeDisabled()
      expect(screen.getByRole('button', { name: 'Annuler' })).toBeDisabled()
    })
  })

  describe('Gestion des erreurs', () => {
    it('affiche le message d\'erreur si onSave échoue', async () => {
      const user = userEvent.setup()
      mockOnSave.mockRejectedValueOnce(new Error('Erreur de sauvegarde'))

      const affectation = createMockAffectation()
      render(<AffectationModal {...defaultProps} affectation={affectation} />)

      const submitButton = screen.getByRole('button', { name: 'Modifier' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Erreur de sauvegarde')).toBeInTheDocument()
      })
    })

    it('affiche un message générique pour les erreurs non-Error', async () => {
      const user = userEvent.setup()
      mockOnSave.mockRejectedValueOnce('Something went wrong')

      const affectation = createMockAffectation()
      render(<AffectationModal {...defaultProps} affectation={affectation} />)

      const submitButton = screen.getByRole('button', { name: 'Modifier' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
      })
    })

    it('ne ferme pas le modal si une erreur survient', async () => {
      const user = userEvent.setup()
      mockOnSave.mockRejectedValueOnce(new Error('Erreur'))

      const affectation = createMockAffectation()
      render(<AffectationModal {...defaultProps} affectation={affectation} />)

      const submitButton = screen.getByRole('button', { name: 'Modifier' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnClose).not.toHaveBeenCalled()
      })
    })
  })

  describe('Fermeture du modal', () => {
    it('appelle onClose quand on clique sur X', async () => {
      const user = userEvent.setup()
      render(<AffectationModal {...defaultProps} />)

      const closeButtons = screen.getAllByRole('button')
      const xButton = closeButtons[0] // Le premier bouton est le X
      await user.click(xButton)

      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose quand on clique sur Annuler', async () => {
      const user = userEvent.setup()
      render(<AffectationModal {...defaultProps} />)

      const cancelButton = screen.getByRole('button', { name: 'Annuler' })
      await user.click(cancelButton)

      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose quand on clique sur l\'overlay', async () => {
      const user = userEvent.setup()
      const { container } = render(<AffectationModal {...defaultProps} />)

      const overlay = container.querySelector('.bg-black\\/50')
      await user.click(overlay!)

      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  describe('Champs horaires', () => {
    it('affiche les horaires par défaut 08:00-17:00', () => {
      render(<AffectationModal {...defaultProps} />)
      expect(screen.getByDisplayValue('08:00')).toBeInTheDocument()
      expect(screen.getByDisplayValue('17:00')).toBeInTheDocument()
    })

    it('permet de modifier les horaires', async () => {
      const user = userEvent.setup()
      render(<AffectationModal {...defaultProps} />)

      const heureDebutInput = screen.getByDisplayValue('08:00')
      await user.clear(heureDebutInput)
      await user.type(heureDebutInput, '07:30')

      expect(screen.getByDisplayValue('07:30')).toBeInTheDocument()
    })
  })

  describe('Note', () => {
    it('affiche le champ note', () => {
      render(<AffectationModal {...defaultProps} />)
      expect(screen.getByText('Note privée')).toBeInTheDocument()
      expect(screen.getByPlaceholderText("Commentaire visible uniquement par l'affecté")).toBeInTheDocument()
    })

    it('permet de saisir une note', async () => {
      const user = userEvent.setup()
      render(<AffectationModal {...defaultProps} />)

      const noteInput = screen.getByPlaceholderText("Commentaire visible uniquement par l'affecté")
      await user.type(noteInput, 'Ceci est ma note')

      expect(screen.getByDisplayValue('Ceci est ma note')).toBeInTheDocument()
    })

    it('a une limite de 500 caractères', () => {
      render(<AffectationModal {...defaultProps} />)
      const noteInput = screen.getByPlaceholderText("Commentaire visible uniquement par l'affecté")
      expect(noteInput).toHaveAttribute('maxLength', '500')
    })
  })

  describe('Affectation multi-jours', () => {
    it('inclut date_fin pour les affectations uniques multi-jours', async () => {
      const user = userEvent.setup()
      render(<AffectationModal {...defaultProps} />)

      // Sélectionner utilisateur via fireEvent (optgroup incompatible avec selectOptions)
      const userSelect = getFieldByLabel('Utilisateur *') as HTMLSelectElement
      fireEvent.change(userSelect, { target: { value: 'user-1' } })

      // Sélectionner chantier
      const chantierSelect = getFieldByLabel('Chantier / Absence *') as HTMLSelectElement
      fireEvent.change(chantierSelect, { target: { value: 'ch-1' } })

      // Entrer la date début
      const dateDebutInput = getFieldByLabel('Date début *')
      fireEvent.change(dateDebutInput, { target: { value: '2024-03-15' } })

      // Entrer la date fin
      const dateFinInput = getFieldByLabel('Date fin')
      fireEvent.change(dateFinInput, { target: { value: '2024-03-20' } })

      // Soumettre
      const submitButton = screen.getByRole('button', { name: 'Créer' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSave).toHaveBeenCalledWith(
          expect.objectContaining({
            date: '2024-03-15',
            date_fin: '2024-03-20',
          })
        )
      })
    })
  })
})
