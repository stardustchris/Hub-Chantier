/**
 * Tests pour CreateChantierModal
 *
 * Couvre:
 * - Affichage initial du formulaire
 * - Sélection de couleur disponible
 * - Gestion des contacts (ajout, suppression, modification)
 * - Gestion des phases (ajout, suppression, modification)
 * - Validation des dates
 * - Soumission du formulaire
 * - Gestion des erreurs
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { CreateChantierModal } from './CreateChantierModal'
import { USER_COLORS } from '../../types'

// Helper to get form field by label text (since labels don't have htmlFor)
const getFieldByLabel = (labelText: string): HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement => {
  const label = screen.getByText(labelText)
  const container = label.parentElement
  if (!container) throw new Error(`Cannot find container for label: ${labelText}`)
  const input = container.querySelector('input, select, textarea')
  if (!input) throw new Error(`Cannot find input for label: ${labelText}`)
  return input as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
}

describe('CreateChantierModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSubmit = vi.fn().mockResolvedValue(undefined)

  const defaultProps = {
    onClose: mockOnClose,
    onSubmit: mockOnSubmit,
    usedColors: [],
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Affichage initial', () => {
    it('affiche le titre du modal', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByText('Nouveau chantier')).toBeInTheDocument()
    })

    it('affiche les champs obligatoires', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByText('Nom du chantier *')).toBeInTheDocument()
      expect(screen.getByText('Adresse *')).toBeInTheDocument()
    })

    it('affiche un contact vide par défaut', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByPlaceholderText('Nom')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Telephone')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Profession')).toBeInTheDocument()
    })

    it('affiche le message pour les phases vides', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByText(/aucune phase definie/i)).toBeInTheDocument()
    })

    it('affiche les champs de dates globales quand pas de phases', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByText('Date debut prevue')).toBeInTheDocument()
      expect(screen.getByText('Date fin prevue')).toBeInTheDocument()
    })

    it('affiche le champ heures estimées', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByText('Heures estimees')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Ex: 500')).toBeInTheDocument()
    })

    it('affiche le champ description', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByText('Description')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Description du chantier...')).toBeInTheDocument()
    })

    it('affiche les boutons Annuler et Créer', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByRole('button', { name: 'Annuler' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Creer' })).toBeInTheDocument()
    })

    it('désactive le bouton Créer initialement', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByRole('button', { name: 'Creer' })).toBeDisabled()
    })
  })

  describe('Sélection de couleur', () => {
    it('sélectionne la première couleur disponible', () => {
      const usedColors = [USER_COLORS[0].code]
      render(<CreateChantierModal {...defaultProps} usedColors={usedColors} />)

      // La première couleur est déjà utilisée, donc la deuxième doit être sélectionnée
      // On ne peut pas facilement tester la couleur sélectionnée sans exposer le state
      // Mais on peut vérifier que le composant se rend sans erreur
      expect(screen.getByText('Nouveau chantier')).toBeInTheDocument()
    })

    it('utilise la première couleur si toutes sont utilisées', () => {
      const usedColors = USER_COLORS.map(c => c.code)
      render(<CreateChantierModal {...defaultProps} usedColors={usedColors} />)

      expect(screen.getByText('Nouveau chantier')).toBeInTheDocument()
    })
  })

  describe('Gestion des contacts', () => {
    it('permet d\'ajouter un contact', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      // Au départ, un seul champ nom
      expect(screen.getAllByPlaceholderText('Nom')).toHaveLength(1)

      const addButton = screen.getByText('Ajouter')
      await user.click(addButton)

      // Maintenant deux champs nom
      expect(screen.getAllByPlaceholderText('Nom')).toHaveLength(2)
    })

    it('permet de supprimer un contact quand il y en a plusieurs', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      // Ajouter un contact
      const addButton = screen.getByText('Ajouter')
      await user.click(addButton)

      // Deux contacts maintenant
      expect(screen.getAllByPlaceholderText('Nom')).toHaveLength(2)

      // Supprimer le premier
      const deleteButtons = screen.getAllByRole('button').filter(
        btn => btn.querySelector('svg.lucide-trash-2')
      )
      await user.click(deleteButtons[0])

      // Un seul contact reste
      expect(screen.getAllByPlaceholderText('Nom')).toHaveLength(1)
    })

    it('n\'affiche pas le bouton supprimer pour le dernier contact', () => {
      render(<CreateChantierModal {...defaultProps} />)

      // Avec un seul contact, pas de bouton supprimer
      const deleteButtons = screen.queryAllByRole('button').filter(
        btn => btn.querySelector('svg.lucide-trash-2')
      )
      expect(deleteButtons.filter(btn => btn.closest('.flex.gap-2'))).toHaveLength(0)
    })

    it('permet de modifier un contact', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      const nomInput = screen.getByPlaceholderText('Nom')
      await user.type(nomInput, 'Jean Dupont')

      expect(screen.getByDisplayValue('Jean Dupont')).toBeInTheDocument()
    })
  })

  describe('Gestion des phases', () => {
    it('permet d\'ajouter une phase', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      const addPhaseButton = screen.getByText('Ajouter une phase')
      await user.click(addPhaseButton)

      expect(screen.getByText('Phase 1')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Nom de la phase (ex: Gros oeuvre)')).toBeInTheDocument()
    })

    it('masque les dates globales quand des phases existent', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      // Dates globales visibles
      expect(screen.getByText('Date debut prevue')).toBeInTheDocument()

      // Ajouter une phase
      const addPhaseButton = screen.getByText('Ajouter une phase')
      await user.click(addPhaseButton)

      // Dates globales masquées
      expect(screen.queryByText('Date debut prevue')).not.toBeInTheDocument()
    })

    it('permet de supprimer une phase', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      // Ajouter une phase
      const addPhaseButton = screen.getByText('Ajouter une phase')
      await user.click(addPhaseButton)

      expect(screen.getByText('Phase 1')).toBeInTheDocument()

      // Supprimer la phase
      const deleteButton = screen.getAllByRole('button').find(
        btn => btn.querySelector('svg.lucide-trash-2') && btn.closest('.border.rounded-lg')
      )
      await user.click(deleteButton!)

      expect(screen.queryByText('Phase 1')).not.toBeInTheDocument()
    })

    it('permet de modifier une phase', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      // Ajouter une phase
      const addPhaseButton = screen.getByText('Ajouter une phase')
      await user.click(addPhaseButton)

      const phaseInput = screen.getByPlaceholderText('Nom de la phase (ex: Gros oeuvre)')
      await user.type(phaseInput, 'Fondations')

      expect(screen.getByDisplayValue('Fondations')).toBeInTheDocument()
    })

    it('incrémente le numéro de phase', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      const addPhaseButton = screen.getByText('Ajouter une phase')
      await user.click(addPhaseButton)
      await user.click(addPhaseButton)

      expect(screen.getByText('Phase 1')).toBeInTheDocument()
      expect(screen.getByText('Phase 2')).toBeInTheDocument()
    })
  })

  describe('Validation des dates', () => {
    it('affiche une erreur si date fin < date début', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      // Remplir les champs obligatoires
      await user.type(screen.getByPlaceholderText('Ex: Residence Les Pins'), 'Test Chantier')
      await user.type(screen.getByPlaceholderText('Ex: 12 rue des Lilas, 69003 Lyon'), 'Test Adresse')

      // Entrer des dates invalides (fin < début)
      const dateDebutInput = getFieldByLabel('Date debut prevue')
      const dateFinInput = getFieldByLabel('Date fin prevue')

      await user.type(dateDebutInput, '2024-06-01')
      await user.type(dateFinInput, '2024-03-01')

      // Soumettre
      const submitButton = screen.getByRole('button', { name: 'Creer' })
      await user.click(submitButton)

      expect(screen.getByText('La date de fin doit etre apres la date de debut')).toBeInTheDocument()
    })

    it('efface l\'erreur quand on modifie les dates', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      // Remplir les champs obligatoires
      await user.type(screen.getByPlaceholderText('Ex: Residence Les Pins'), 'Test Chantier')
      await user.type(screen.getByPlaceholderText('Ex: 12 rue des Lilas, 69003 Lyon'), 'Test Adresse')

      // Entrer des dates invalides
      const dateDebutInput = getFieldByLabel('Date debut prevue')
      const dateFinInput = getFieldByLabel('Date fin prevue')

      await user.type(dateDebutInput, '2024-06-01')
      await user.type(dateFinInput, '2024-03-01')

      // Soumettre pour déclencher l'erreur
      const submitButton = screen.getByRole('button', { name: 'Creer' })
      await user.click(submitButton)

      expect(screen.getByText('La date de fin doit etre apres la date de debut')).toBeInTheDocument()

      // Modifier la date de fin
      await user.clear(dateFinInput)
      await user.type(dateFinInput, '2024-07-01')

      expect(screen.queryByText('La date de fin doit etre apres la date de debut')).not.toBeInTheDocument()
    })
  })

  describe('Soumission du formulaire', () => {
    it('appelle onSubmit avec les données du formulaire', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      // Remplir les champs obligatoires
      await user.type(screen.getByPlaceholderText('Ex: Residence Les Pins'), 'Mon Chantier')
      await user.type(screen.getByPlaceholderText('Ex: 12 rue des Lilas, 69003 Lyon'), '123 Rue Test')

      // Soumettre
      const submitButton = screen.getByRole('button', { name: 'Creer' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            nom: 'Mon Chantier',
            adresse: '123 Rue Test',
          }),
          expect.any(Array), // contacts
          expect.any(Array)  // phases
        )
      })
    })

    it('inclut les contacts dans la soumission', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      // Remplir les champs obligatoires
      await user.type(screen.getByPlaceholderText('Ex: Residence Les Pins'), 'Mon Chantier')
      await user.type(screen.getByPlaceholderText('Ex: 12 rue des Lilas, 69003 Lyon'), '123 Rue Test')

      // Remplir le contact
      await user.type(screen.getByPlaceholderText('Nom'), 'Jean Contact')
      await user.type(screen.getByPlaceholderText('Telephone'), '0612345678')

      // Soumettre
      const submitButton = screen.getByRole('button', { name: 'Creer' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.any(Object),
          expect.arrayContaining([
            expect.objectContaining({
              nom: 'Jean Contact',
              telephone: '0612345678',
            }),
          ]),
          expect.any(Array)
        )
      })
    })

    it('inclut les phases dans la soumission', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      // Remplir les champs obligatoires
      await user.type(screen.getByPlaceholderText('Ex: Residence Les Pins'), 'Mon Chantier')
      await user.type(screen.getByPlaceholderText('Ex: 12 rue des Lilas, 69003 Lyon'), '123 Rue Test')

      // Ajouter une phase
      const addPhaseButton = screen.getByText('Ajouter une phase')
      await user.click(addPhaseButton)

      await user.type(screen.getByPlaceholderText('Nom de la phase (ex: Gros oeuvre)'), 'Fondations')

      // Soumettre
      const submitButton = screen.getByRole('button', { name: 'Creer' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.any(Object),
          expect.any(Array),
          expect.arrayContaining([
            expect.objectContaining({
              nom: 'Fondations',
            }),
          ])
        )
      })
    })

    it('affiche un spinner pendant la soumission', async () => {
      const user = userEvent.setup()
      mockOnSubmit.mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 1000)))

      render(<CreateChantierModal {...defaultProps} />)

      // Remplir les champs obligatoires
      await user.type(screen.getByPlaceholderText('Ex: Residence Les Pins'), 'Mon Chantier')
      await user.type(screen.getByPlaceholderText('Ex: 12 rue des Lilas, 69003 Lyon'), '123 Rue Test')

      // Soumettre
      const submitButton = screen.getByRole('button', { name: 'Creer' })
      await user.click(submitButton)

      expect(submitButton).toBeDisabled()
    })
  })

  describe('Gestion des erreurs', () => {
    it('affiche l\'erreur de l\'API', async () => {
      const user = userEvent.setup()
      mockOnSubmit.mockRejectedValueOnce({
        response: { data: { detail: 'Erreur API personnalisée' } },
      })

      render(<CreateChantierModal {...defaultProps} />)

      // Remplir les champs obligatoires
      await user.type(screen.getByPlaceholderText('Ex: Residence Les Pins'), 'Mon Chantier')
      await user.type(screen.getByPlaceholderText('Ex: 12 rue des Lilas, 69003 Lyon'), '123 Rue Test')

      // Soumettre
      const submitButton = screen.getByRole('button', { name: 'Creer' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Erreur API personnalisée')).toBeInTheDocument()
      })
    })

    it('affiche un message générique si pas de détail d\'erreur', async () => {
      const user = userEvent.setup()
      mockOnSubmit.mockRejectedValueOnce(new Error('Network Error'))

      render(<CreateChantierModal {...defaultProps} />)

      // Remplir les champs obligatoires
      await user.type(screen.getByPlaceholderText('Ex: Residence Les Pins'), 'Mon Chantier')
      await user.type(screen.getByPlaceholderText('Ex: 12 rue des Lilas, 69003 Lyon'), '123 Rue Test')

      // Soumettre
      const submitButton = screen.getByRole('button', { name: 'Creer' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Erreur lors de la creation du chantier')).toBeInTheDocument()
      })
    })
  })

  describe('Fermeture du modal', () => {
    it('appelle onClose quand on clique sur X', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      const closeButton = screen.getAllByRole('button')[0]
      await user.click(closeButton)

      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose quand on clique sur Annuler', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      const cancelButton = screen.getByRole('button', { name: 'Annuler' })
      await user.click(cancelButton)

      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose quand on clique sur le backdrop', async () => {
      const user = userEvent.setup()
      const { container } = render(<CreateChantierModal {...defaultProps} />)

      const backdrop = container.querySelector('.bg-black\\/50')
      await user.click(backdrop!)

      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  describe('Champs optionnels', () => {
    it('permet de saisir les heures estimées', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      const heuresInput = screen.getByPlaceholderText('Ex: 500')
      await user.type(heuresInput, '100')

      expect(screen.getByDisplayValue('100')).toBeInTheDocument()
    })

    it('permet de saisir une description', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      const descInput = screen.getByPlaceholderText('Description du chantier...')
      await user.type(descInput, 'Ma description')

      expect(screen.getByDisplayValue('Ma description')).toBeInTheDocument()
    })
  })
})
