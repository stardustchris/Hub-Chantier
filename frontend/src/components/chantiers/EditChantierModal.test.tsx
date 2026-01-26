/**
 * Tests pour EditChantierModal
 *
 * Couvre:
 * - Initialisation du formulaire avec les données du chantier
 * - Gestion des contacts (ajout, suppression, modification)
 * - Gestion des phases (ajout, suppression, modification)
 * - Geocoding automatique
 * - Soumission du formulaire
 * - Fermeture du modal
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import EditChantierModal from './EditChantierModal'
import type { Chantier } from '../../types'

// Mock des services
vi.mock('../../services/chantiers', () => ({
  chantiersService: {
    listPhases: vi.fn().mockResolvedValue([]),
    addPhase: vi.fn().mockResolvedValue({ id: 1 }),
    updatePhase: vi.fn().mockResolvedValue({}),
    removePhase: vi.fn().mockResolvedValue({}),
  },
}))

vi.mock('../../services/geocoding', () => ({
  geocodeAddress: vi.fn().mockResolvedValue({ latitude: 48.8566, longitude: 2.3522 }),
}))

// Import après le mock
import { chantiersService } from '../../services/chantiers'
import { geocodeAddress } from '../../services/geocoding'

const createMockChantier = (overrides: Partial<Chantier> = {}): Chantier => ({
  id: 1,
  code: 'CH001',
  nom: 'Chantier Test',
  adresse: '123 Rue de Test, 75001 Paris',
  statut: 'en_cours',
  couleur: '#3498DB',
  conducteurs: [],
  chefs: [],
  created_at: '2024-01-01',
  heures_estimees: 100,
  date_debut_prevue: '2024-03-01',
  date_fin_prevue: '2024-06-30',
  description: 'Description du chantier test',
  ...overrides,
})

describe('EditChantierModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSubmit = vi.fn().mockResolvedValue(undefined)

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers({ shouldAdvanceTime: true })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('Initialisation', () => {
    it('affiche le titre du modal', () => {
      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      expect(screen.getByText('Modifier le chantier')).toBeInTheDocument()
    })

    it('initialise le formulaire avec les données du chantier', () => {
      const chantier = createMockChantier({
        nom: 'Mon Chantier',
        adresse: '456 Avenue Test',
        heures_estimees: 200,
        description: 'Ma description',
      })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      expect(screen.getByDisplayValue('Mon Chantier')).toBeInTheDocument()
      expect(screen.getByDisplayValue('456 Avenue Test')).toBeInTheDocument()
      expect(screen.getByDisplayValue('200')).toBeInTheDocument()
      expect(screen.getByDisplayValue('Ma description')).toBeInTheDocument()
    })

    it('initialise les contacts depuis le chantier', () => {
      const chantier = createMockChantier({
        contacts: [
          { nom: 'Jean Dupont', profession: 'Architecte', telephone: '0612345678' },
        ],
      })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      expect(screen.getByDisplayValue('Jean Dupont')).toBeInTheDocument()
      expect(screen.getByDisplayValue('Architecte')).toBeInTheDocument()
      expect(screen.getByDisplayValue('0612345678')).toBeInTheDocument()
    })

    it('utilise contact_nom si contacts est vide', () => {
      const chantier = createMockChantier({
        contacts: [],
        contact_nom: 'Marie Martin',
        contact_telephone: '0698765432',
      })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      expect(screen.getByDisplayValue('Marie Martin')).toBeInTheDocument()
      expect(screen.getByDisplayValue('0698765432')).toBeInTheDocument()
    })

    it('charge les phases existantes depuis l\'API', async () => {
      const mockPhases = [
        { id: 1, nom: 'Phase 1', description: '', ordre: 1, date_debut: '2024-03-01', date_fin: '2024-04-01' },
        { id: 2, nom: 'Phase 2', description: '', ordre: 2, date_debut: '2024-04-02', date_fin: '2024-05-01' },
      ]
      vi.mocked(chantiersService.listPhases).mockResolvedValueOnce(mockPhases)

      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      await waitFor(() => {
        expect(chantiersService.listPhases).toHaveBeenCalledWith('1')
      })

      await waitFor(() => {
        expect(screen.getByDisplayValue('Phase 1')).toBeInTheDocument()
        expect(screen.getByDisplayValue('Phase 2')).toBeInTheDocument()
      })
    })
  })

  describe('Gestion des contacts', () => {
    it('permet d\'ajouter un contact', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      // Trouver le bouton "Ajouter" dans la section contacts (pas "Ajouter une periode")
      const addButtons = screen.getAllByRole('button', { name: /ajouter$/i })
      const addContactButton = addButtons[0]
      await user.click(addContactButton)

      // Devrait maintenant avoir 2 contacts (1 vide par défaut + 1 nouveau)
      const nomInputs = screen.getAllByPlaceholderText('Nom')
      expect(nomInputs.length).toBeGreaterThanOrEqual(2)
    })

    it('permet de supprimer un contact quand il y en a plusieurs', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier({
        contacts: [
          { nom: 'Contact 1', profession: '', telephone: '' },
          { nom: 'Contact 2', profession: '', telephone: '' },
        ],
      })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const deleteButtons = screen.getAllByRole('button', { name: /supprimer le contact/i })
      expect(deleteButtons).toHaveLength(2)

      await user.click(deleteButtons[0])

      expect(screen.queryByDisplayValue('Contact 1')).not.toBeInTheDocument()
      expect(screen.getByDisplayValue('Contact 2')).toBeInTheDocument()
    })

    it('ne permet pas de supprimer le dernier contact', () => {
      const chantier = createMockChantier({
        contacts: [{ nom: 'Seul Contact', profession: '', telephone: '' }],
      })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const deleteButton = screen.queryByRole('button', { name: /supprimer le contact/i })
      expect(deleteButton).not.toBeInTheDocument()
    })

    it('met à jour un contact', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier({
        contacts: [{ nom: 'Ancien Nom', profession: '', telephone: '' }],
      })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const nomInput = screen.getByDisplayValue('Ancien Nom')
      await user.clear(nomInput)
      await user.type(nomInput, 'Nouveau Nom')

      expect(screen.getByDisplayValue('Nouveau Nom')).toBeInTheDocument()
    })
  })

  describe('Gestion des phases', () => {
    it('affiche un message quand aucune phase n\'est définie', () => {
      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      expect(screen.getByText(/aucune periode definie/i)).toBeInTheDocument()
    })

    it('permet d\'ajouter une phase', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const addPhaseButton = screen.getByRole('button', { name: /ajouter une periode/i })
      await user.click(addPhaseButton)

      expect(screen.getByDisplayValue('Phase 1')).toBeInTheDocument()
    })

    it('incrémente le numéro de phase automatiquement', async () => {
      const mockPhases = [
        { id: 1, nom: 'Phase 2', description: '', ordre: 1, date_debut: '', date_fin: '' },
      ]
      vi.mocked(chantiersService.listPhases).mockResolvedValueOnce(mockPhases)

      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      await waitFor(() => {
        expect(screen.getByDisplayValue('Phase 2')).toBeInTheDocument()
      })

      const addPhaseButton = screen.getByRole('button', { name: /ajouter une periode/i })
      await user.click(addPhaseButton)

      // Devrait créer Phase 3 car Phase 2 existe
      expect(screen.getByDisplayValue('Phase 3')).toBeInTheDocument()
    })

    it('permet de supprimer une phase', async () => {
      const mockPhases = [
        { id: 1, nom: 'Phase 1', description: '', ordre: 1, date_debut: '', date_fin: '' },
      ]
      vi.mocked(chantiersService.listPhases).mockResolvedValueOnce(mockPhases)

      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      await waitFor(() => {
        expect(screen.getByDisplayValue('Phase 1')).toBeInTheDocument()
      })

      const deleteButton = screen.getByRole('button', { name: /supprimer la periode 1/i })
      await user.click(deleteButton)

      expect(screen.queryByDisplayValue('Phase 1')).not.toBeInTheDocument()
    })

    it('permet de modifier une phase', async () => {
      const mockPhases = [
        { id: 1, nom: 'Phase 1', description: '', ordre: 1, date_debut: '', date_fin: '' },
      ]
      vi.mocked(chantiersService.listPhases).mockResolvedValueOnce(mockPhases)

      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      await waitFor(() => {
        expect(screen.getByDisplayValue('Phase 1')).toBeInTheDocument()
      })

      const phaseInput = screen.getByDisplayValue('Phase 1')
      await user.clear(phaseInput)
      await user.type(phaseInput, 'Demolition')

      expect(screen.getByDisplayValue('Demolition')).toBeInTheDocument()
    })
  })

  describe('Geocoding', () => {
    it('déclenche le geocoding quand l\'adresse change', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier({ adresse: 'Ancienne adresse' })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const adresseInput = screen.getByDisplayValue('Ancienne adresse')
      await user.clear(adresseInput)
      await user.type(adresseInput, 'Nouvelle adresse, Paris')

      // Attendre le debounce de 800ms
      await act(async () => {
        vi.advanceTimersByTime(900)
      })

      await waitFor(() => {
        expect(geocodeAddress).toHaveBeenCalledWith('Nouvelle adresse, Paris')
      })
    })

    it('affiche le statut de succès après geocoding', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      vi.mocked(geocodeAddress).mockResolvedValueOnce({ latitude: 48.8566, longitude: 2.3522 })

      const chantier = createMockChantier({ adresse: 'Ancienne adresse' })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const adresseInput = screen.getByDisplayValue('Ancienne adresse')
      await user.clear(adresseInput)
      await user.type(adresseInput, 'Paris')

      await act(async () => {
        vi.advanceTimersByTime(900)
      })

      await waitFor(() => {
        expect(screen.getByText(/localisation mise a jour/i)).toBeInTheDocument()
      })
    })

    it('affiche le statut d\'erreur si le geocoding échoue', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      vi.mocked(geocodeAddress).mockResolvedValueOnce(null)

      const chantier = createMockChantier({ adresse: 'Ancienne adresse' })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const adresseInput = screen.getByDisplayValue('Ancienne adresse')
      await user.clear(adresseInput)
      await user.type(adresseInput, 'Adresse invalide XYZ')

      await act(async () => {
        vi.advanceTimersByTime(900)
      })

      await waitFor(() => {
        expect(screen.getByText(/adresse non trouvee/i)).toBeInTheDocument()
      })
    })

    it('ne déclenche pas le geocoding si l\'adresse est identique', async () => {
      const chantier = createMockChantier({ adresse: 'Même adresse' })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      await act(async () => {
        vi.advanceTimersByTime(1000)
      })

      expect(geocodeAddress).not.toHaveBeenCalled()
    })
  })

  describe('Soumission du formulaire', () => {
    it('appelle onSubmit avec les données du formulaire', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier({
        nom: 'Chantier Initial',
        contacts: [{ nom: 'Contact Test', profession: 'Test', telephone: '0600000000' }],
      })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const nomInput = screen.getByDisplayValue('Chantier Initial')
      await user.clear(nomInput)
      await user.type(nomInput, 'Chantier Modifie')

      const submitButton = screen.getByRole('button', { name: /enregistrer/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            nom: 'Chantier Modifie',
            contacts: [{ nom: 'Contact Test', profession: 'Test', telephone: '0600000000' }],
          })
        )
      })
    })

    it('filtre les contacts vides avant soumission', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier({
        contacts: [
          { nom: 'Contact Valide', profession: '', telephone: '' },
          { nom: '', profession: '', telephone: '' },
        ],
      })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const submitButton = screen.getByRole('button', { name: /enregistrer/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            contacts: [{ nom: 'Contact Valide', profession: '', telephone: '' }],
          })
        )
      })
    })

    it('synchronise les phases lors de la soumission', async () => {
      const mockPhases = [
        { id: 1, nom: 'Phase 1', description: '', ordre: 1, date_debut: '2024-01-01', date_fin: '2024-02-01' },
      ]
      vi.mocked(chantiersService.listPhases).mockResolvedValueOnce(mockPhases)

      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      await waitFor(() => {
        expect(screen.getByDisplayValue('Phase 1')).toBeInTheDocument()
      })

      const submitButton = screen.getByRole('button', { name: /enregistrer/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(chantiersService.updatePhase).toHaveBeenCalledWith(
          1,
          1,
          expect.objectContaining({ nom: 'Phase 1' })
        )
      })
    })

    it('supprime les phases marquées pour suppression', async () => {
      const mockPhases = [
        { id: 1, nom: 'Phase 1', description: '', ordre: 1, date_debut: '2024-01-01', date_fin: '2024-02-01' },
      ]
      vi.mocked(chantiersService.listPhases).mockResolvedValueOnce(mockPhases)

      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      await waitFor(() => {
        expect(screen.getByDisplayValue('Phase 1')).toBeInTheDocument()
      })

      // Supprimer la phase
      const deleteButton = screen.getByRole('button', { name: /supprimer la periode 1/i })
      await user.click(deleteButton)

      const submitButton = screen.getByRole('button', { name: /enregistrer/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(chantiersService.removePhase).toHaveBeenCalledWith(1, 1)
      })
    })

    it('crée les nouvelles phases', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      // Ajouter une phase
      const addPhaseButton = screen.getByRole('button', { name: /ajouter une periode/i })
      await user.click(addPhaseButton)

      // Remplir les dates
      const dateDebutInput = screen.getByLabelText(/date debut periode 1/i)
      await user.type(dateDebutInput, '2024-03-01')

      const submitButton = screen.getByRole('button', { name: /enregistrer/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(chantiersService.addPhase).toHaveBeenCalledWith(
          1,
          expect.objectContaining({ nom: 'Phase 1' })
        )
      })
    })

    it('affiche un spinner pendant la soumission', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      mockOnSubmit.mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 1000)))

      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const submitButton = screen.getByRole('button', { name: /enregistrer/i })
      await user.click(submitButton)

      expect(submitButton).toBeDisabled()
    })
  })

  describe('Fermeture du modal', () => {
    it('appelle onClose quand on clique sur le bouton fermer', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const closeButton = screen.getByRole('button', { name: /fermer/i })
      await user.click(closeButton)

      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose quand on clique sur le backdrop', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier()
      const { container } = render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const backdrop = container.querySelector('[aria-hidden="true"]')
      await user.click(backdrop!)

      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose quand on clique sur Annuler', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const cancelButton = screen.getByRole('button', { name: /annuler/i })
      await user.click(cancelButton)

      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  describe('Sélection de couleur', () => {
    it('affiche les couleurs disponibles', () => {
      const chantier = createMockChantier({ couleur: '#3498DB' })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const colorGroup = screen.getByRole('radiogroup', { name: /couleur du chantier/i })
      expect(colorGroup).toBeInTheDocument()
    })

    it('permet de changer la couleur', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier({ couleur: '#3498DB' })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      // Trouver un bouton couleur différent
      const colorButtons = screen.getAllByRole('button', { pressed: false })
      const colorButton = colorButtons.find(btn => btn.hasAttribute('title'))
      if (colorButton) {
        await user.click(colorButton)
      }

      const submitButton = screen.getByRole('button', { name: /enregistrer/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })
  })

  describe('Sélection de statut', () => {
    it('affiche tous les statuts disponibles', () => {
      const chantier = createMockChantier({ statut: 'en_cours' })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const select = screen.getByRole('combobox')
      expect(select).toHaveValue('en_cours')
    })

    it('permet de changer le statut', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      const chantier = createMockChantier({ statut: 'en_cours' })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const select = screen.getByRole('combobox')
      await user.selectOptions(select, 'ouvert')

      expect(select).toHaveValue('ouvert')
    })
  })

  describe('Accessibilité', () => {
    it('a un rôle dialog avec aria-modal', () => {
      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-modal', 'true')
    })

    it('a un titre accessible', () => {
      const chantier = createMockChantier()
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-labelledby', 'modal-title')
    })

    it('a des labels accessibles pour les champs de contact', () => {
      const chantier = createMockChantier({
        contacts: [{ nom: 'Test', profession: '', telephone: '' }],
      })
      render(
        <EditChantierModal
          chantier={chantier}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      )

      expect(screen.getByLabelText(/nom du contact 1/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/profession du contact 1/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/telephone du contact 1/i)).toBeInTheDocument()
    })
  })
})
