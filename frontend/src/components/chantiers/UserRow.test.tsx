/**
 * Tests unitaires pour UserRow
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import UserRow from './UserRow'
import type { User } from '../../types'

const mockUser: User = {
  id: '1',
  email: 'john.doe@example.com',
  nom: 'Doe',
  prenom: 'John',
  role: 'chef_chantier',
  type_utilisateur: 'employe',
  couleur: '#3498DB',
  telephone: '0612345678',
  is_active: true,
  created_at: '2026-01-01T00:00:00',
}

describe('UserRow', () => {
  it('affiche les initiales de l\'utilisateur', () => {
    render(<UserRow user={mockUser} canRemove={false} onRemove={() => {}} />)

    expect(screen.getByText('JD')).toBeInTheDocument()
  })

  it('affiche le nom complet de l\'utilisateur', () => {
    render(<UserRow user={mockUser} canRemove={false} onRemove={() => {}} />)

    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })

  it('affiche le role de l\'utilisateur', () => {
    render(<UserRow user={mockUser} canRemove={false} onRemove={() => {}} />)

    expect(screen.getByText('Chef de chantier')).toBeInTheDocument()
  })

  it('n\'affiche pas le bouton supprimer si canRemove est false', () => {
    render(<UserRow user={mockUser} canRemove={false} onRemove={() => {}} />)

    expect(
      screen.queryByRole('button', { name: /retirer/i })
    ).not.toBeInTheDocument()
  })

  it('affiche le bouton supprimer si canRemove est true', () => {
    render(<UserRow user={mockUser} canRemove={true} onRemove={() => {}} />)

    expect(
      screen.getByRole('button', { name: /retirer john doe/i })
    ).toBeInTheDocument()
  })

  it('appelle onRemove quand on clique sur le bouton', () => {
    const handleRemove = vi.fn()
    render(<UserRow user={mockUser} canRemove={true} onRemove={handleRemove} />)

    fireEvent.click(screen.getByRole('button', { name: /retirer/i }))

    expect(handleRemove).toHaveBeenCalledTimes(1)
  })

  it('utilise la couleur personnalisee de l\'utilisateur', () => {
    const userWithColor = { ...mockUser, couleur: '#FF5733' }
    render(<UserRow user={userWithColor} canRemove={false} onRemove={() => {}} />)

    const avatar = screen.getByText('JD')
    expect(avatar).toHaveStyle({ backgroundColor: '#FF5733' })
  })

  it('utilise une couleur par defaut si pas de couleur', () => {
    const userWithoutColor = { ...mockUser, couleur: undefined }
    render(<UserRow user={userWithoutColor} canRemove={false} onRemove={() => {}} />)

    const avatar = screen.getByText('JD')
    expect(avatar).toHaveStyle({ backgroundColor: '#3498DB' })
  })

  it('gere les utilisateurs avec role inconnu', () => {
    const userUnknownRole = { ...mockUser, role: 'unknown_role' as User['role'] }
    render(<UserRow user={userUnknownRole} canRemove={false} onRemove={() => {}} />)

    // L'utilisateur s'affiche toujours
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })

  it('a un aria-label accessible sur le bouton supprimer', () => {
    render(<UserRow user={mockUser} canRemove={true} onRemove={() => {}} />)

    const button = screen.getByRole('button')
    expect(button).toHaveAttribute('aria-label', 'Retirer John Doe')
  })
})
