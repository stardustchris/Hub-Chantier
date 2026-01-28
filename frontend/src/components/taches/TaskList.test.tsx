/**
 * Tests unitaires pour TaskList
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TaskList from './TaskList'
import { tachesService } from '../../services/taches'
import type { Tache, TacheStats } from '../../types'

// Mocks
vi.mock('../../services/taches', () => ({
  tachesService: {
    listByChantier: vi.fn(),
    getStats: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    complete: vi.fn(),
    importTemplate: vi.fn(),
    exportPDF: vi.fn(),
    downloadPDF: vi.fn(),
  },
}))

vi.mock('../../services/logger', () => ({
  logger: {
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
  },
}))

vi.mock('./TaskItem', () => ({
  default: ({ tache }: { tache: Tache }) => (
    <div data-testid={`task-${tache.id}`}>{tache.titre}</div>
  ),
}))

vi.mock('./TaskModal', () => ({
  default: ({ onClose, onSave }: { onClose: () => void; onSave: (data: unknown) => void }) => (
    <div data-testid="task-modal">
      <button onClick={onClose} data-testid="close-modal">Close</button>
      <button onClick={() => onSave({ titre: 'New Task' })} data-testid="save-task">Save</button>
    </div>
  ),
}))

vi.mock('./TemplateImportModal', () => ({
  default: ({ onClose, onImport }: { onClose: () => void; onImport: (id: number) => void }) => (
    <div data-testid="template-modal">
      <button onClick={onClose} data-testid="close-template">Close</button>
      <button onClick={() => onImport(1)} data-testid="import-template">Import</button>
    </div>
  ),
}))

const mockTaches: Tache[] = [
  {
    id: 1,
    chantier_id: 1,
    titre: 'Tache 1',
    description: 'Description 1',
    ordre: 1,
    statut: 'a_faire',
    statut_display: 'À faire',
    statut_icon: '⏳',
    quantite_realisee: 0,
    heures_realisees: 0,
    progression_heures: 0,
    progression_quantite: 0,
    couleur_progression: 'rouge',
    couleur_hex: '#EF4444',
    est_terminee: false,
    est_en_retard: false,
    a_sous_taches: false,
    nombre_sous_taches: 0,
    nombre_sous_taches_terminees: 0,
    sous_taches: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 2,
    chantier_id: 1,
    titre: 'Tache 2',
    description: 'Description 2',
    ordre: 2,
    statut: 'termine',
    statut_display: 'Terminé',
    statut_icon: '✅',
    quantite_realisee: 100,
    heures_realisees: 10,
    progression_heures: 100,
    progression_quantite: 100,
    couleur_progression: 'vert',
    couleur_hex: '#10B981',
    est_terminee: true,
    est_en_retard: false,
    a_sous_taches: false,
    nombre_sous_taches: 0,
    nombre_sous_taches_terminees: 0,
    sous_taches: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

const mockStats: TacheStats = {
  chantier_id: 1,
  total_taches: 10,
  taches_terminees: 5,
  taches_en_cours: 3,
  taches_en_retard: 2,
  heures_estimees_total: 100,
  heures_realisees_total: 50,
  progression_globale: 50,
}

describe('TaskList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(tachesService.listByChantier).mockResolvedValue({ items: mockTaches, total: mockTaches.length, page: 1, size: 20, pages: 1 })
    vi.mocked(tachesService.getStats).mockResolvedValue(mockStats)
    vi.stubGlobal('confirm', vi.fn(() => true))
  })

  describe('loading', () => {
    it('affiche le loader pendant le chargement', () => {
      vi.mocked(tachesService.listByChantier).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      )

      const { container } = render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      // Check for the spinning loader
      const spinner = container.querySelector('.animate-spin')
      expect(spinner).toBeTruthy()
    })

    it('charge les taches au demarrage', async () => {
      render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      await waitFor(() => {
        expect(tachesService.listByChantier).toHaveBeenCalledWith(1, expect.any(Object))
      })
    })

    it('charge les stats au demarrage', async () => {
      render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      await waitFor(() => {
        expect(tachesService.getStats).toHaveBeenCalledWith(1)
      })
    })
  })

  describe('stats display', () => {
    it('affiche les statistiques', async () => {
      render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      await waitFor(() => {
        expect(screen.getByText('10')).toBeInTheDocument() // total
        expect(screen.getByText('5')).toBeInTheDocument() // terminees
        expect(screen.getByText('2')).toBeInTheDocument() // en retard
        expect(screen.getByText('50%')).toBeInTheDocument() // progression
      })
    })
  })

  describe('task list', () => {
    it('affiche les taches', async () => {
      render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      await waitFor(() => {
        expect(screen.getByTestId('task-1')).toBeInTheDocument()
        expect(screen.getByTestId('task-2')).toBeInTheDocument()
      })
    })

    it('affiche message si aucune tache', async () => {
      vi.mocked(tachesService.listByChantier).mockResolvedValue({ items: [], total: 0, page: 1, size: 20, pages: 0 })

      render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      await waitFor(() => {
        expect(screen.getByText('Aucune tache pour ce chantier')).toBeInTheDocument()
      })
    })
  })

  describe('search', () => {
    it('filtre les taches par recherche', async () => {
      const user = userEvent.setup()
      render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      await waitFor(() => {
        expect(screen.getByTestId('task-1')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText('Rechercher une tache...')
      await user.type(searchInput, 'test')

      await waitFor(() => {
        expect(tachesService.listByChantier).toHaveBeenCalledWith(
          1,
          expect.objectContaining({ query: 'test' })
        )
      })
    })
  })

  describe('filters', () => {
    it('ouvre le panneau de filtres', async () => {
      const user = userEvent.setup()
      render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      await waitFor(() => {
        expect(screen.getByTestId('task-1')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Filtrer'))

      expect(screen.getByText('Toutes')).toBeInTheDocument()
      expect(screen.getByText('A faire')).toBeInTheDocument()
      // Use getAllByText because "Terminees" appears in stats and filters
      expect(screen.getAllByText('Terminees').length).toBeGreaterThanOrEqual(1)
    })

    it('filtre par statut', async () => {
      const user = userEvent.setup()
      render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      await waitFor(() => {
        expect(screen.getByTestId('task-1')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Filtrer'))
      // Click on "A faire" button in filter panel
      const aFaireButtons = screen.getAllByText('A faire')
      await user.click(aFaireButtons[aFaireButtons.length - 1]) // Click the filter button

      await waitFor(() => {
        expect(tachesService.listByChantier).toHaveBeenCalledWith(
          1,
          expect.objectContaining({ statut: 'a_faire' })
        )
      })
    })
  })

  describe('create task', () => {
    it('ouvre le modal de creation', async () => {
      const user = userEvent.setup()
      render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      await waitFor(() => {
        expect(screen.getByTestId('task-1')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Ajouter'))

      expect(screen.getByTestId('task-modal')).toBeInTheDocument()
    })

    it('cree une nouvelle tache', async () => {
      const user = userEvent.setup()
      render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      await waitFor(() => {
        expect(screen.getByTestId('task-1')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Ajouter'))
      await user.click(screen.getByTestId('save-task'))

      await waitFor(() => {
        expect(tachesService.create).toHaveBeenCalledWith(
          expect.objectContaining({ chantier_id: 1 })
        )
      })
    })
  })

  describe('template import', () => {
    it('ouvre le modal template', async () => {
      const user = userEvent.setup()
      render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      await waitFor(() => {
        expect(screen.getByTestId('task-1')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Modele'))

      expect(screen.getByTestId('template-modal')).toBeInTheDocument()
    })

    it('importe un template', async () => {
      const user = userEvent.setup()
      render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      await waitFor(() => {
        expect(screen.getByTestId('task-1')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Modele'))
      await user.click(screen.getByTestId('import-template'))

      await waitFor(() => {
        expect(tachesService.importTemplate).toHaveBeenCalledWith(1, 1)
      })
    })
  })

  describe('export PDF', () => {
    it('exporte en PDF', async () => {
      const mockBlob = new Blob(['pdf content'])
      vi.mocked(tachesService.exportPDF).mockResolvedValue(mockBlob)

      const user = userEvent.setup()
      render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      await waitFor(() => {
        expect(screen.getByTestId('task-1')).toBeInTheDocument()
      })

      await user.click(screen.getByText('PDF'))

      await waitFor(() => {
        expect(tachesService.exportPDF).toHaveBeenCalledWith(1)
      })
    })
  })

  describe('error handling', () => {
    it('affiche une erreur si chargement echoue', async () => {
      vi.mocked(tachesService.listByChantier).mockRejectedValue(new Error('Network error'))

      render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      await waitFor(() => {
        expect(screen.getByText(/Impossible de charger les taches/)).toBeInTheDocument()
      })
    })

    it('permet de fermer le message d erreur', async () => {
      vi.mocked(tachesService.listByChantier).mockRejectedValue(new Error('Network error'))
      const user = userEvent.setup()

      render(<TaskList chantierId={1} chantierNom="Test Chantier" />)

      await waitFor(() => {
        expect(screen.getByText(/Impossible de charger les taches/)).toBeInTheDocument()
      })

      await user.click(screen.getByText('Fermer'))

      expect(screen.queryByText(/Impossible de charger les taches/)).not.toBeInTheDocument()
    })
  })
})
