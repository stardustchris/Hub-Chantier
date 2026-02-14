/**
 * Tests pour RessourceList
 *
 * Couvre:
 * - Chargement et affichage des ressources
 * - Recherche textuelle
 * - Filtre par catégorie
 * - Toggle ressources inactives (admin)
 * - Sélection d'une ressource
 * - Création et édition (admin)
 * - États de chargement et erreur
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { createMockRessource } from '../../fixtures'
import userEvent from '@testing-library/user-event'
import RessourceList from './RessourceList'
import type { Ressource } from '../../types/logistique'

// Mock API
vi.mock('../../services/logistique', () => ({
  listRessources: vi.fn(),
}))

// Mock RessourceCard
vi.mock('./RessourceCard', () => ({
  default: ({
    ressource,
    onSelect,
    onEdit,
    selected,
  }: {
    ressource: Ressource
    onSelect?: (r: Ressource) => void
    onEdit?: (r: Ressource) => void
    selected: boolean
  }) => (
    <div
      data-testid={`ressource-card-${ressource.id}`}
      data-selected={selected}
      onClick={() => onSelect?.(ressource)}
    >
      <span>{ressource.nom}</span>
      <span>{ressource.code}</span>
      {onEdit && (
        <button onClick={() => onEdit(ressource)} data-testid={`edit-${ressource.id}`}>
          Edit
        </button>
      )}
    </div>
  ),
}))

// Mock logger
vi.mock('../../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

import { listRessources } from '../../services/logistique'
const mockListRessources = listRessources as ReturnType<typeof vi.fn>


describe('RessourceList', () => {
  const mockOnSelectRessource = vi.fn()
  const mockOnCreateRessource = vi.fn()
  const mockOnEditRessource = vi.fn()

  const defaultProps = {
    onSelectRessource: mockOnSelectRessource,
    onCreateRessource: mockOnCreateRessource,
    onEditRessource: mockOnEditRessource,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockListRessources.mockResolvedValue({
      items: [
        createMockRessource({ id: 1, nom: 'Camion benne', code: 'CAM01' }),
        createMockRessource({ id: 2, nom: 'Grue mobile', code: 'GRU01', categorie: 'engin_levage' }),
        createMockRessource({ id: 3, nom: 'Perceuse', code: 'OUT01', categorie: 'gros_outillage' }),
      ],
    })
  })

  describe('Chargement', () => {
    it('affiche un spinner pendant le chargement', async () => {
      let resolvePromise: (value: unknown) => void
      mockListRessources.mockReturnValue(
        new Promise((resolve) => {
          resolvePromise = resolve
        })
      )

      render(<RessourceList {...defaultProps} />)

      expect(document.querySelector('.animate-spin')).toBeInTheDocument()

      resolvePromise!({ items: [] })
      await waitFor(() => {
        expect(document.querySelector('.animate-spin')).not.toBeInTheDocument()
      })
    })

    it('charge les ressources au montage', async () => {
      render(<RessourceList {...defaultProps} />)

      await waitFor(() => {
        expect(mockListRessources).toHaveBeenCalledWith({
          categorie: undefined,
          actif_seulement: true,
          limit: 100,
        })
      })
    })
  })

  describe('Affichage des ressources', () => {
    it('affiche toutes les ressources', async () => {
      render(<RessourceList {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Camion benne')).toBeInTheDocument()
        expect(screen.getByText('Grue mobile')).toBeInTheDocument()
        expect(screen.getByText('Perceuse')).toBeInTheDocument()
      })
    })

    it('affiche un message si aucune ressource', async () => {
      mockListRessources.mockResolvedValue({ items: [] })

      render(<RessourceList {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Aucune ressource disponible')).toBeInTheDocument()
      })
    })
  })

  describe('Recherche', () => {
    it('affiche le champ de recherche', async () => {
      render(<RessourceList {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Rechercher une ressource...')).toBeInTheDocument()
      })
    })

    it('filtre les ressources par nom', async () => {
      const user = userEvent.setup()
      render(<RessourceList {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Camion benne')).toBeInTheDocument()
      })

      await user.type(screen.getByPlaceholderText('Rechercher une ressource...'), 'Grue')

      await waitFor(() => {
        expect(screen.queryByText('Camion benne')).not.toBeInTheDocument()
        expect(screen.getByText('Grue mobile')).toBeInTheDocument()
      })
    })

    it('filtre les ressources par code', async () => {
      const user = userEvent.setup()
      render(<RessourceList {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Camion benne')).toBeInTheDocument()
      })

      await user.type(screen.getByPlaceholderText('Rechercher une ressource...'), 'OUT01')

      await waitFor(() => {
        expect(screen.getByText('Perceuse')).toBeInTheDocument()
        expect(screen.queryByText('Camion benne')).not.toBeInTheDocument()
      })
    })

    it('affiche un message si aucun résultat', async () => {
      const user = userEvent.setup()
      render(<RessourceList {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Camion benne')).toBeInTheDocument()
      })

      await user.type(screen.getByPlaceholderText('Rechercher une ressource...'), 'xyz123')

      await waitFor(() => {
        expect(screen.getByText('Aucune ressource ne correspond aux critères')).toBeInTheDocument()
      })
    })
  })

  describe('Filtre catégorie', () => {
    it('affiche le sélecteur de catégorie', async () => {
      render(<RessourceList {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Toutes categories')).toBeInTheDocument()
      })
    })

    it('filtre par catégorie', async () => {
      const user = userEvent.setup()
      render(<RessourceList {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Camion benne')).toBeInTheDocument()
      })

      await user.selectOptions(screen.getByRole('combobox'), 'vehicule')

      await waitFor(() => {
        expect(mockListRessources).toHaveBeenCalledWith(
          expect.objectContaining({ categorie: 'vehicule' })
        )
      })
    })
  })

  describe('Toggle inactifs (admin)', () => {
    it('n\'affiche pas le toggle si pas admin', async () => {
      render(<RessourceList {...defaultProps} isAdmin={false} />)

      await waitFor(() => {
        expect(screen.queryByText('Afficher inactifs')).not.toBeInTheDocument()
      })
    })

    it('affiche le toggle si admin', async () => {
      render(<RessourceList {...defaultProps} isAdmin={true} />)

      await waitFor(() => {
        expect(screen.getByText('Afficher inactifs')).toBeInTheDocument()
      })
    })

    it('charge les ressources inactives au toggle', async () => {
      const user = userEvent.setup()
      render(<RessourceList {...defaultProps} isAdmin={true} />)

      await waitFor(() => {
        expect(screen.getByText('Afficher inactifs')).toBeInTheDocument()
      })

      await user.click(screen.getByRole('checkbox'))

      await waitFor(() => {
        expect(mockListRessources).toHaveBeenCalledWith(
          expect.objectContaining({ actif_seulement: false })
        )
      })
    })
  })

  describe('Bouton créer (admin)', () => {
    it('n\'affiche pas le bouton si pas admin', async () => {
      render(<RessourceList {...defaultProps} isAdmin={false} />)

      await waitFor(() => {
        expect(screen.queryByText('Nouvelle ressource')).not.toBeInTheDocument()
      })
    })

    it('affiche le bouton si admin', async () => {
      render(<RessourceList {...defaultProps} isAdmin={true} />)

      await waitFor(() => {
        expect(screen.getByText('Nouvelle ressource')).toBeInTheDocument()
      })
    })

    it('appelle onCreateRessource au clic', async () => {
      const user = userEvent.setup()
      render(<RessourceList {...defaultProps} isAdmin={true} />)

      await waitFor(() => {
        expect(screen.getByText('Nouvelle ressource')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Nouvelle ressource'))
      expect(mockOnCreateRessource).toHaveBeenCalled()
    })
  })

  describe('Sélection ressource', () => {
    it('appelle onSelectRessource au clic sur une carte', async () => {
      const user = userEvent.setup()
      render(<RessourceList {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByTestId('ressource-card-1')).toBeInTheDocument()
      })

      await user.click(screen.getByTestId('ressource-card-1'))
      expect(mockOnSelectRessource).toHaveBeenCalledWith(
        expect.objectContaining({ id: 1 })
      )
    })

    it('marque la ressource sélectionnée', async () => {
      render(<RessourceList {...defaultProps} selectedRessourceId={2} />)

      await waitFor(() => {
        const card2 = screen.getByTestId('ressource-card-2')
        expect(card2).toHaveAttribute('data-selected', 'true')
      })
    })
  })

  describe('Édition ressource (admin)', () => {
    it('affiche le bouton éditer si admin', async () => {
      render(<RessourceList {...defaultProps} isAdmin={true} />)

      await waitFor(() => {
        expect(screen.getByTestId('edit-1')).toBeInTheDocument()
      })
    })

    it('n\'affiche pas le bouton éditer si pas admin', async () => {
      render(<RessourceList {...defaultProps} isAdmin={false} />)

      await waitFor(() => {
        expect(screen.queryByTestId('edit-1')).not.toBeInTheDocument()
      })
    })

    it('appelle onEditRessource au clic', async () => {
      const user = userEvent.setup()
      render(<RessourceList {...defaultProps} isAdmin={true} />)

      await waitFor(() => {
        expect(screen.getByTestId('edit-1')).toBeInTheDocument()
      })

      await user.click(screen.getByTestId('edit-1'))
      expect(mockOnEditRessource).toHaveBeenCalledWith(
        expect.objectContaining({ id: 1 })
      )
    })
  })

  describe('Erreur', () => {
    it('affiche un message d\'erreur', async () => {
      mockListRessources.mockRejectedValue(new Error('Network error'))

      render(<RessourceList {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Erreur lors du chargement des ressources')).toBeInTheDocument()
      })
    })
  })
})
