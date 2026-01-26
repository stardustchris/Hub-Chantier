/**
 * Tests pour ChantierEquipeTab
 *
 * Couvre:
 * - Affichage des différentes catégories d'équipe
 * - Séparation des ouvriers par type (compagnons, intérimaires, sous-traitants)
 * - Actions d'ajout et suppression
 * - Messages quand les listes sont vides
 * - Affichage conditionnel selon les permissions
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ChantierEquipeTab from './ChantierEquipeTab'
import type { User } from '../../types'

// Mock UserRow
vi.mock('./UserRow', () => ({
  default: vi.fn(({ user, canRemove, onRemove, badge }) => (
    <div data-testid={`user-row-${user.id}`}>
      <span>{user.prenom} {user.nom}</span>
      {badge && <span data-testid="badge">{badge.label}</span>}
      {canRemove && (
        <button data-testid={`remove-${user.id}`} onClick={onRemove}>
          Supprimer
        </button>
      )}
    </div>
  )),
}))

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

describe('ChantierEquipeTab', () => {
  const mockOnAddUser = vi.fn()
  const mockOnRemoveUser = vi.fn()

  const defaultProps = {
    conducteurs: [],
    chefs: [],
    ouvriers: [],
    canEdit: true,
    onAddUser: mockOnAddUser,
    onRemoveUser: mockOnRemoveUser,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Structure de base', () => {
    it('affiche le titre "Equipe"', () => {
      render(<ChantierEquipeTab {...defaultProps} />)
      expect(screen.getByText('Equipe')).toBeInTheDocument()
    })

    it('affiche les sections pour chaque catégorie', () => {
      render(<ChantierEquipeTab {...defaultProps} />)

      expect(screen.getByText('Conducteurs de travaux')).toBeInTheDocument()
      expect(screen.getByText('Chefs de chantier')).toBeInTheDocument()
      expect(screen.getByText('Compagnons')).toBeInTheDocument()
      expect(screen.getByText(/Interimaires/)).toBeInTheDocument()
      expect(screen.getByText(/Sous-traitants/)).toBeInTheDocument()
    })
  })

  describe('Messages quand listes vides', () => {
    it('affiche le message pour conducteurs vides', () => {
      render(<ChantierEquipeTab {...defaultProps} />)
      expect(screen.getByText('Aucun conducteur assigne')).toBeInTheDocument()
    })

    it('affiche le message pour chefs vides', () => {
      render(<ChantierEquipeTab {...defaultProps} />)
      expect(screen.getByText('Aucun chef assigne')).toBeInTheDocument()
    })

    it('affiche le message pour compagnons vides', () => {
      render(<ChantierEquipeTab {...defaultProps} />)
      expect(screen.getByText('Aucun compagnon assigne')).toBeInTheDocument()
    })

    it('affiche le message pour intérimaires vides', () => {
      render(<ChantierEquipeTab {...defaultProps} />)
      expect(screen.getByText('Aucun interimaire assigne')).toBeInTheDocument()
    })

    it('affiche le message pour sous-traitants vides', () => {
      render(<ChantierEquipeTab {...defaultProps} />)
      expect(screen.getByText('Aucun sous-traitant assigne')).toBeInTheDocument()
    })
  })

  describe('Affichage des conducteurs', () => {
    it('affiche les conducteurs', () => {
      const conducteurs = [
        createMockUser({ id: 'c1', prenom: 'Marc', nom: 'Conducteur' }),
      ]
      render(<ChantierEquipeTab {...defaultProps} conducteurs={conducteurs} />)

      expect(screen.getByText('Marc Conducteur')).toBeInTheDocument()
    })

    it('affiche plusieurs conducteurs', () => {
      const conducteurs = [
        createMockUser({ id: 'c1', prenom: 'Marc', nom: 'Un' }),
        createMockUser({ id: 'c2', prenom: 'Paul', nom: 'Deux' }),
      ]
      render(<ChantierEquipeTab {...defaultProps} conducteurs={conducteurs} />)

      expect(screen.getByText('Marc Un')).toBeInTheDocument()
      expect(screen.getByText('Paul Deux')).toBeInTheDocument()
    })
  })

  describe('Affichage des chefs de chantier', () => {
    it('affiche les chefs de chantier', () => {
      const chefs = [
        createMockUser({ id: 'ch1', prenom: 'Sophie', nom: 'Chef' }),
      ]
      render(<ChantierEquipeTab {...defaultProps} chefs={chefs} />)

      expect(screen.getByText('Sophie Chef')).toBeInTheDocument()
    })
  })

  describe('Séparation des ouvriers par type', () => {
    it('affiche les compagnons (employés)', () => {
      const ouvriers = [
        createMockUser({ id: 'o1', prenom: 'Jean', nom: 'Compagnon', type_utilisateur: 'employe' }),
      ]
      render(<ChantierEquipeTab {...defaultProps} ouvriers={ouvriers} />)

      expect(screen.getByText('Jean Compagnon')).toBeInTheDocument()
    })

    it('affiche les ouvriers sans type comme compagnons', () => {
      const ouvriers = [
        createMockUser({ id: 'o1', prenom: 'Pierre', nom: 'SansType', type_utilisateur: undefined }),
      ]
      render(<ChantierEquipeTab {...defaultProps} ouvriers={ouvriers} />)

      expect(screen.getByText('Pierre SansType')).toBeInTheDocument()
    })

    it('affiche les intérimaires séparément', () => {
      const ouvriers = [
        createMockUser({ id: 'i1', prenom: 'Lucas', nom: 'Interim', type_utilisateur: 'interimaire' }),
      ]
      render(<ChantierEquipeTab {...defaultProps} ouvriers={ouvriers} />)

      expect(screen.getByText('Lucas Interim')).toBeInTheDocument()
      expect(screen.getByTestId('badge')).toHaveTextContent('Interimaire')
    })

    it('affiche les sous-traitants séparément', () => {
      const ouvriers = [
        createMockUser({ id: 's1', prenom: 'Marie', nom: 'SousT', type_utilisateur: 'sous_traitant' }),
      ]
      render(<ChantierEquipeTab {...defaultProps} ouvriers={ouvriers} />)

      expect(screen.getByText('Marie SousT')).toBeInTheDocument()
      expect(screen.getByTestId('badge')).toHaveTextContent('Sous-traitant')
    })

    it('affiche le compteur d\'intérimaires', () => {
      const ouvriers = [
        createMockUser({ id: 'i1', type_utilisateur: 'interimaire' }),
        createMockUser({ id: 'i2', type_utilisateur: 'interimaire' }),
      ]
      render(<ChantierEquipeTab {...defaultProps} ouvriers={ouvriers} />)

      expect(screen.getByText('2')).toBeInTheDocument()
    })

    it('affiche le compteur de sous-traitants', () => {
      const ouvriers = [
        createMockUser({ id: 's1', type_utilisateur: 'sous_traitant' }),
        createMockUser({ id: 's2', type_utilisateur: 'sous_traitant' }),
        createMockUser({ id: 's3', type_utilisateur: 'sous_traitant' }),
      ]
      render(<ChantierEquipeTab {...defaultProps} ouvriers={ouvriers} />)

      expect(screen.getByText('3')).toBeInTheDocument()
    })
  })

  describe('Boutons d\'ajout', () => {
    it('affiche les boutons d\'ajout quand canEdit=true', () => {
      render(<ChantierEquipeTab {...defaultProps} canEdit={true} />)

      expect(screen.getByLabelText('Ajouter un conducteur')).toBeInTheDocument()
      expect(screen.getByLabelText('Ajouter un chef de chantier')).toBeInTheDocument()
      expect(screen.getByLabelText('Ajouter un compagnon')).toBeInTheDocument()
    })

    it('n\'affiche pas les boutons d\'ajout quand canEdit=false', () => {
      render(<ChantierEquipeTab {...defaultProps} canEdit={false} />)

      expect(screen.queryByLabelText('Ajouter un conducteur')).not.toBeInTheDocument()
      expect(screen.queryByLabelText('Ajouter un chef de chantier')).not.toBeInTheDocument()
      expect(screen.queryByLabelText('Ajouter un compagnon')).not.toBeInTheDocument()
    })

    it('appelle onAddUser("conducteur") au clic sur ajouter conducteur', async () => {
      const user = userEvent.setup()
      render(<ChantierEquipeTab {...defaultProps} />)

      await user.click(screen.getByLabelText('Ajouter un conducteur'))

      expect(mockOnAddUser).toHaveBeenCalledWith('conducteur')
    })

    it('appelle onAddUser("chef") au clic sur ajouter chef', async () => {
      const user = userEvent.setup()
      render(<ChantierEquipeTab {...defaultProps} />)

      await user.click(screen.getByLabelText('Ajouter un chef de chantier'))

      expect(mockOnAddUser).toHaveBeenCalledWith('chef')
    })

    it('appelle onAddUser("ouvrier") au clic sur ajouter compagnon', async () => {
      const user = userEvent.setup()
      render(<ChantierEquipeTab {...defaultProps} />)

      await user.click(screen.getByLabelText('Ajouter un compagnon'))

      expect(mockOnAddUser).toHaveBeenCalledWith('ouvrier')
    })
  })

  describe('Suppression d\'utilisateurs', () => {
    it('affiche le bouton supprimer quand canEdit=true', () => {
      const conducteurs = [createMockUser({ id: 'c1' })]
      render(<ChantierEquipeTab {...defaultProps} conducteurs={conducteurs} canEdit={true} />)

      expect(screen.getByTestId('remove-c1')).toBeInTheDocument()
    })

    it('n\'affiche pas le bouton supprimer quand canEdit=false', () => {
      const conducteurs = [createMockUser({ id: 'c1' })]
      render(<ChantierEquipeTab {...defaultProps} conducteurs={conducteurs} canEdit={false} />)

      expect(screen.queryByTestId('remove-c1')).not.toBeInTheDocument()
    })

    it('appelle onRemoveUser avec les bons arguments pour un conducteur', async () => {
      const user = userEvent.setup()
      const conducteurs = [createMockUser({ id: 'c1' })]
      render(<ChantierEquipeTab {...defaultProps} conducteurs={conducteurs} />)

      await user.click(screen.getByTestId('remove-c1'))

      expect(mockOnRemoveUser).toHaveBeenCalledWith('c1', 'conducteur')
    })

    it('appelle onRemoveUser avec les bons arguments pour un chef', async () => {
      const user = userEvent.setup()
      const chefs = [createMockUser({ id: 'ch1' })]
      render(<ChantierEquipeTab {...defaultProps} chefs={chefs} />)

      await user.click(screen.getByTestId('remove-ch1'))

      expect(mockOnRemoveUser).toHaveBeenCalledWith('ch1', 'chef')
    })

    it('appelle onRemoveUser avec "ouvrier" pour un compagnon', async () => {
      const user = userEvent.setup()
      const ouvriers = [createMockUser({ id: 'o1', type_utilisateur: 'employe' })]
      render(<ChantierEquipeTab {...defaultProps} ouvriers={ouvriers} />)

      await user.click(screen.getByTestId('remove-o1'))

      expect(mockOnRemoveUser).toHaveBeenCalledWith('o1', 'ouvrier')
    })

    it('appelle onRemoveUser avec "ouvrier" pour un intérimaire', async () => {
      const user = userEvent.setup()
      const ouvriers = [createMockUser({ id: 'i1', type_utilisateur: 'interimaire' })]
      render(<ChantierEquipeTab {...defaultProps} ouvriers={ouvriers} />)

      await user.click(screen.getByTestId('remove-i1'))

      expect(mockOnRemoveUser).toHaveBeenCalledWith('i1', 'ouvrier')
    })

    it('appelle onRemoveUser avec "ouvrier" pour un sous-traitant', async () => {
      const user = userEvent.setup()
      const ouvriers = [createMockUser({ id: 's1', type_utilisateur: 'sous_traitant' })]
      render(<ChantierEquipeTab {...defaultProps} ouvriers={ouvriers} />)

      await user.click(screen.getByTestId('remove-s1'))

      expect(mockOnRemoveUser).toHaveBeenCalledWith('s1', 'ouvrier')
    })
  })

  describe('Équipe complète', () => {
    it('affiche une équipe complète avec toutes les catégories', () => {
      const conducteurs = [createMockUser({ id: 'c1', prenom: 'Marc', nom: 'C' })]
      const chefs = [createMockUser({ id: 'ch1', prenom: 'Sophie', nom: 'Ch' })]
      const ouvriers = [
        createMockUser({ id: 'o1', prenom: 'Jean', nom: 'E', type_utilisateur: 'employe' }),
        createMockUser({ id: 'i1', prenom: 'Lucas', nom: 'I', type_utilisateur: 'interimaire' }),
        createMockUser({ id: 's1', prenom: 'Marie', nom: 'S', type_utilisateur: 'sous_traitant' }),
      ]

      render(
        <ChantierEquipeTab
          {...defaultProps}
          conducteurs={conducteurs}
          chefs={chefs}
          ouvriers={ouvriers}
        />
      )

      expect(screen.getByText('Marc C')).toBeInTheDocument()
      expect(screen.getByText('Sophie Ch')).toBeInTheDocument()
      expect(screen.getByText('Jean E')).toBeInTheDocument()
      expect(screen.getByText('Lucas I')).toBeInTheDocument()
      expect(screen.getByText('Marie S')).toBeInTheDocument()
    })
  })
})
