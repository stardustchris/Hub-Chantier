/**
 * Tests unitaires pour AddUserModal
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AddUserModal from './AddUserModal'
import type { User } from '../../types'

const mockUsers: User[] = [
  {
    id: '1',
    nom: 'Dupont',
    prenom: 'Jean',
    email: 'jean.dupont@example.com',
    role: 'conducteur',
    couleur: '#3498DB',
  },
  {
    id: '2',
    nom: 'Martin',
    prenom: 'Marie',
    email: 'marie.martin@example.com',
    role: 'conducteur',
    couleur: '#E74C3C',
  },
]

const mockOnClose = vi.fn()
const mockOnSelect = vi.fn()

const defaultProps = {
  type: 'conducteur' as const,
  users: mockUsers,
  onClose: mockOnClose,
  onSelect: mockOnSelect,
}

describe('AddUserModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('rendering', () => {
    it('affiche le titre pour conducteur', () => {
      render(<AddUserModal {...defaultProps} />)
      expect(screen.getByText('Ajouter un conducteur')).toBeInTheDocument()
    })

    it('affiche le titre pour chef de chantier', () => {
      render(<AddUserModal {...defaultProps} type="chef" />)
      expect(screen.getByText('Ajouter un chef de chantier')).toBeInTheDocument()
    })

    it('affiche la liste des utilisateurs', () => {
      render(<AddUserModal {...defaultProps} />)

      expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
      expect(screen.getByText('Marie Martin')).toBeInTheDocument()
      expect(screen.getByText('jean.dupont@example.com')).toBeInTheDocument()
      expect(screen.getByText('marie.martin@example.com')).toBeInTheDocument()
    })

    it('affiche les initiales dans l avatar', () => {
      render(<AddUserModal {...defaultProps} />)

      // Jean Dupont = JD
      expect(screen.getByText('JD')).toBeInTheDocument()
      // Marie Martin = MM
      expect(screen.getByText('MM')).toBeInTheDocument()
    })

    it('affiche message si aucun utilisateur', () => {
      render(<AddUserModal {...defaultProps} users={[]} />)
      expect(screen.getByText('Aucun utilisateur disponible')).toBeInTheDocument()
    })

    it('a les bons attributs aria', () => {
      render(<AddUserModal {...defaultProps} />)

      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-modal', 'true')
      expect(dialog).toHaveAttribute('aria-labelledby', 'add-user-title')

      const listbox = screen.getByRole('listbox')
      expect(listbox).toHaveAttribute('aria-label', 'Liste des utilisateurs')
    })
  })

  describe('interactions', () => {
    it('appelle onClose quand on clique sur le bouton fermer', async () => {
      const user = userEvent.setup()
      render(<AddUserModal {...defaultProps} />)

      await user.click(screen.getByLabelText('Fermer'))

      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose quand on clique sur le backdrop', async () => {
      const user = userEvent.setup()
      render(<AddUserModal {...defaultProps} />)

      // Click on the backdrop (the first div with bg-black/50)
      const backdrop = document.querySelector('.bg-black\\/50')
      await user.click(backdrop!)

      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onSelect avec userId quand on clique sur un utilisateur', async () => {
      const user = userEvent.setup()
      render(<AddUserModal {...defaultProps} />)

      await user.click(screen.getByText('Jean Dupont'))

      expect(mockOnSelect).toHaveBeenCalledWith('1')
    })

    it('appelle onSelect pour le second utilisateur', async () => {
      const user = userEvent.setup()
      render(<AddUserModal {...defaultProps} />)

      await user.click(screen.getByText('Marie Martin'))

      expect(mockOnSelect).toHaveBeenCalledWith('2')
    })
  })

  describe('styling', () => {
    it('applique la couleur de l utilisateur a l avatar', () => {
      render(<AddUserModal {...defaultProps} />)

      const jdAvatar = screen.getByText('JD')
      expect(jdAvatar).toHaveStyle({ backgroundColor: '#3498DB' })

      const mmAvatar = screen.getByText('MM')
      expect(mmAvatar).toHaveStyle({ backgroundColor: '#E74C3C' })
    })

    it('utilise couleur par defaut si pas de couleur', () => {
      const usersWithoutColor: User[] = [
        {
          id: '3',
          nom: 'Sans',
          prenom: 'Couleur',
          email: 'sans.couleur@example.com',
          role: 'conducteur',
        },
      ]

      render(<AddUserModal {...defaultProps} users={usersWithoutColor} />)

      const avatar = screen.getByText('CS')
      expect(avatar).toHaveStyle({ backgroundColor: '#3498DB' })
    })
  })

  describe('accessibility', () => {
    it('bouton fermer a un aria-label', () => {
      render(<AddUserModal {...defaultProps} />)
      expect(screen.getByLabelText('Fermer')).toBeInTheDocument()
    })

    it('options utilisateurs ont role="option"', () => {
      render(<AddUserModal {...defaultProps} />)

      const options = screen.getAllByRole('option')
      expect(options).toHaveLength(2)
    })
  })
})
