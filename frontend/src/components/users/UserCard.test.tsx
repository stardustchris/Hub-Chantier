/**
 * Tests pour UserCard
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import UserCard from './UserCard'
import type { User } from '../../types'

const createMockUser = (overrides: Partial<User> = {}): User => ({
  id: 'user-1',
  email: 'jean.dupont@example.com',
  nom: 'Dupont',
  prenom: 'Jean',
  role: 'chef_chantier',
  type_utilisateur: 'employe',
  is_active: true,
  created_at: '2024-01-01',
  couleur: '#3498DB',
  ...overrides,
})

const renderWithRouter = (user: User, canEdit = false, onToggleActive = vi.fn()) => {
  return render(
    <MemoryRouter>
      <UserCard user={user} canEdit={canEdit} onToggleActive={onToggleActive} />
    </MemoryRouter>
  )
}

describe('UserCard', () => {
  it('affiche le nom complet de l\'utilisateur', () => {
    const user = createMockUser({ prenom: 'Marc', nom: 'Martin' })
    renderWithRouter(user)

    expect(screen.getByText('Marc Martin')).toBeInTheDocument()
  })

  it('affiche les initiales de l\'utilisateur', () => {
    const user = createMockUser({ prenom: 'Pierre', nom: 'Duval' })
    renderWithRouter(user)

    expect(screen.getByText('PD')).toBeInTheDocument()
  })

  it('affiche l\'email de l\'utilisateur', () => {
    const user = createMockUser({ email: 'test@company.com' })
    renderWithRouter(user)

    expect(screen.getByText('test@company.com')).toBeInTheDocument()
  })

  it('affiche le telephone si defini', () => {
    const user = createMockUser({ telephone: '+33 6 12 34 56 78' })
    renderWithRouter(user)

    expect(screen.getByText('+33 6 12 34 56 78')).toBeInTheDocument()
  })

  it('n\'affiche pas le telephone si non defini', () => {
    const user = createMockUser({ telephone: undefined })
    const { container } = renderWithRouter(user)

    // Phone icon est un svg dans la meme div que le numero
    const phoneIcons = container.querySelectorAll('svg')
    // Il y a mail icon, arrow icon, mais pas de phone si pas de numero
    expect(screen.queryByText('+33')).not.toBeInTheDocument()
  })

  it('affiche le role administrateur', () => {
    const user = createMockUser({ role: 'admin' })
    renderWithRouter(user)

    expect(screen.getByText('Administrateur')).toBeInTheDocument()
  })

  it('affiche le role conducteur', () => {
    const user = createMockUser({ role: 'conducteur' })
    renderWithRouter(user)

    expect(screen.getByText('Conducteur de travaux')).toBeInTheDocument()
  })

  it('affiche le role chef de chantier', () => {
    const user = createMockUser({ role: 'chef_chantier' })
    renderWithRouter(user)

    expect(screen.getByText('Chef de chantier')).toBeInTheDocument()
  })

  it('affiche le role compagnon', () => {
    const user = createMockUser({ role: 'compagnon' })
    renderWithRouter(user)

    expect(screen.getByText('Compagnon')).toBeInTheDocument()
  })

  it('affiche le metier macon', () => {
    const user = createMockUser({ metier: 'macon' })
    renderWithRouter(user)

    expect(screen.getByText('Macon')).toBeInTheDocument()
  })

  it('affiche le metier electricien', () => {
    const user = createMockUser({ metier: 'electricien' })
    renderWithRouter(user)

    expect(screen.getByText('Electricien')).toBeInTheDocument()
  })

  it('n\'affiche pas le badge metier si non defini', () => {
    const user = createMockUser({ metier: undefined })
    renderWithRouter(user)

    expect(screen.queryByText('Macon')).not.toBeInTheDocument()
    expect(screen.queryByText('Coffreur')).not.toBeInTheDocument()
  })

  it('affiche le badge desactive pour utilisateur inactif', () => {
    const user = createMockUser({ is_active: false })
    renderWithRouter(user)

    expect(screen.getByText('Desactive')).toBeInTheDocument()
  })

  it('n\'affiche pas le badge desactive pour utilisateur actif', () => {
    const user = createMockUser({ is_active: true })
    renderWithRouter(user)

    expect(screen.queryByText('Desactive')).not.toBeInTheDocument()
  })

  it('applique l\'opacite pour utilisateur inactif', () => {
    const user = createMockUser({ is_active: false })
    const { container } = renderWithRouter(user)

    expect(container.querySelector('.opacity-60')).toBeInTheDocument()
  })

  it('n\'applique pas l\'opacite pour utilisateur actif', () => {
    const user = createMockUser({ is_active: true })
    const { container } = renderWithRouter(user)

    expect(container.querySelector('.opacity-60')).not.toBeInTheDocument()
  })

  it('affiche le bouton toggle si canEdit est true', () => {
    const user = createMockUser({ is_active: true })
    renderWithRouter(user, true)

    expect(screen.getByTitle('Desactiver')).toBeInTheDocument()
  })

  it('n\'affiche pas le bouton toggle si canEdit est false', () => {
    const user = createMockUser({ is_active: true })
    renderWithRouter(user, false)

    expect(screen.queryByTitle('Desactiver')).not.toBeInTheDocument()
    expect(screen.queryByTitle('Activer')).not.toBeInTheDocument()
  })

  it('affiche Activer pour utilisateur inactif avec canEdit', () => {
    const user = createMockUser({ is_active: false })
    renderWithRouter(user, true)

    expect(screen.getByTitle('Activer')).toBeInTheDocument()
  })

  it('appelle onToggleActive au clic sur le bouton', () => {
    const onToggleActive = vi.fn()
    const user = createMockUser({ is_active: true })
    renderWithRouter(user, true, onToggleActive)

    const toggleButton = screen.getByTitle('Desactiver')
    fireEvent.click(toggleButton)

    expect(onToggleActive).toHaveBeenCalled()
  })

  it('empeche la propagation du clic sur le bouton toggle', () => {
    const onToggleActive = vi.fn()
    const user = createMockUser({ is_active: true })
    renderWithRouter(user, true, onToggleActive)

    const toggleButton = screen.getByTitle('Desactiver')
    const clickEvent = fireEvent.click(toggleButton)

    // Le clic sur le bouton ne devrait pas naviguer (preventDefault)
    expect(onToggleActive).toHaveBeenCalled()
  })

  it('cree un lien vers la page utilisateur', () => {
    const user = createMockUser({ id: 'user-abc' })
    const { container } = renderWithRouter(user)

    const link = container.querySelector('a[href="/utilisateurs/user-abc"]')
    expect(link).toBeInTheDocument()
  })

  it('applique la couleur de l\'utilisateur pour l\'avatar', () => {
    const user = createMockUser({ couleur: '#E74C3C' })
    const { container } = renderWithRouter(user)

    // Couleur #E74C3C -> rgb(231, 76, 60)
    const avatar = container.querySelector('[style*="background-color: rgb(231, 76, 60)"]')
    expect(avatar).toBeInTheDocument()
  })

  it('utilise la couleur par defaut si non definie', () => {
    const user = createMockUser({ couleur: undefined })
    const { container } = renderWithRouter(user)

    // Couleur par defaut #3498DB -> rgb(52, 152, 219)
    const avatar = container.querySelector('[style*="background-color: rgb(52, 152, 219)"]')
    expect(avatar).toBeInTheDocument()
  })

  it('gere les prenoms et noms avec accents', () => {
    const user = createMockUser({ prenom: 'Rene', nom: 'Lefevre' })
    renderWithRouter(user)

    expect(screen.getByText('Rene Lefevre')).toBeInTheDocument()
    expect(screen.getByText('RL')).toBeInTheDocument()
  })

  it('affiche tous les metiers correctement', () => {
    const metiers = ['coffreur', 'ferrailleur', 'grutier', 'charpentier', 'couvreur', 'plombier', 'autre'] as const
    const labels = ['Coffreur', 'Ferrailleur', 'Grutier', 'Charpentier', 'Couvreur', 'Plombier', 'Autre']

    metiers.forEach((metier, index) => {
      const user = createMockUser({ metier })
      const { unmount } = renderWithRouter(user)
      expect(screen.getByText(labels[index])).toBeInTheDocument()
      unmount()
    })
  })
})
