/**
 * Tests pour ChantierCard
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import ChantierCard from './ChantierCard'
import type { Chantier, User } from '../../types'

vi.mock('../../utils/dates', () => ({
  formatDateDayMonth: vi.fn((date: string) => {
    const d = new Date(date)
    return `${d.getDate()}/${d.getMonth() + 1}`
  }),
}))

const createMockUser = (overrides: Partial<User> = {}): User => ({
  id: 'user-1',
  email: 'test@example.com',
  nom: 'Dupont',
  prenom: 'Jean',
  role: 'chef_chantier',
  type_utilisateur: 'employe',
  is_active: true,
  created_at: '2024-01-01',
  couleur: '#3498DB',
  ...overrides,
})

const createMockChantier = (overrides: Partial<Chantier> = {}): Chantier => ({
  id: 'chantier-1',
  code: 'CH001',
  nom: 'Chantier Test',
  adresse: '123 Rue de Test, 75001 Paris',
  statut: 'en_cours',
  conducteurs: [],
  chefs: [],
  created_at: '2024-01-01',
  ...overrides,
})

const renderWithRouter = (chantier: Chantier) => {
  return render(
    <MemoryRouter>
      <ChantierCard chantier={chantier} />
    </MemoryRouter>
  )
}

describe('ChantierCard', () => {
  it('affiche le code et le nom du chantier', () => {
    const chantier = createMockChantier({ code: 'CH123', nom: 'Mon Chantier' })
    renderWithRouter(chantier)

    expect(screen.getByText('CH123')).toBeInTheDocument()
    expect(screen.getByText('Mon Chantier')).toBeInTheDocument()
  })

  it('affiche l\'adresse du chantier', () => {
    const chantier = createMockChantier({ adresse: '456 Avenue des Champs, Paris' })
    renderWithRouter(chantier)

    expect(screen.getByText('456 Avenue des Champs, Paris')).toBeInTheDocument()
  })

  it('affiche le statut en cours', () => {
    const chantier = createMockChantier({ statut: 'en_cours' })
    renderWithRouter(chantier)

    expect(screen.getByText('En cours')).toBeInTheDocument()
  })

  it('affiche le statut ouvert', () => {
    const chantier = createMockChantier({ statut: 'ouvert' })
    renderWithRouter(chantier)

    expect(screen.getByText('Ouvert')).toBeInTheDocument()
  })

  it('affiche le statut receptionne', () => {
    const chantier = createMockChantier({ statut: 'receptionne' })
    renderWithRouter(chantier)

    expect(screen.getByText('Receptionne')).toBeInTheDocument()
  })

  it('affiche le statut ferme', () => {
    const chantier = createMockChantier({ statut: 'ferme' })
    renderWithRouter(chantier)

    expect(screen.getByText('Ferme')).toBeInTheDocument()
  })

  it('affiche les heures estimees si definies', () => {
    const chantier = createMockChantier({ heures_estimees: 120 })
    renderWithRouter(chantier)

    expect(screen.getByText('120h')).toBeInTheDocument()
  })

  it('n\'affiche pas les heures si non definies', () => {
    const chantier = createMockChantier({ heures_estimees: undefined })
    renderWithRouter(chantier)

    expect(screen.queryByText(/h$/)).not.toBeInTheDocument()
  })

  it('affiche la date de debut prevue si definie', () => {
    const chantier = createMockChantier({ date_debut_prevue: '2024-03-15' })
    renderWithRouter(chantier)

    expect(screen.getByText('15/3')).toBeInTheDocument()
  })

  it('affiche les initiales des conducteurs', () => {
    const conducteur = createMockUser({ id: 'c1', prenom: 'Marc', nom: 'Durand' })
    const chantier = createMockChantier({ conducteurs: [conducteur] })
    renderWithRouter(chantier)

    expect(screen.getByTitle('Marc Durand')).toBeInTheDocument()
    expect(screen.getByText('MD')).toBeInTheDocument()
  })

  it('affiche les initiales des chefs de chantier', () => {
    const chef = createMockUser({ id: 'chef1', prenom: 'Paul', nom: 'Martin' })
    const chantier = createMockChantier({ chefs: [chef] })
    renderWithRouter(chantier)

    expect(screen.getByTitle('Paul Martin')).toBeInTheDocument()
    expect(screen.getByText('PM')).toBeInTheDocument()
  })

  it('affiche un maximum de 3 membres de l\'equipe', () => {
    const users = [
      createMockUser({ id: 'u1', prenom: 'User', nom: 'One' }),
      createMockUser({ id: 'u2', prenom: 'User', nom: 'Two' }),
      createMockUser({ id: 'u3', prenom: 'User', nom: 'Three' }),
      createMockUser({ id: 'u4', prenom: 'User', nom: 'Four' }),
    ]
    const chantier = createMockChantier({ conducteurs: users })
    renderWithRouter(chantier)

    expect(screen.getByText('+1')).toBeInTheDocument()
  })

  it('affiche +2 pour 5 membres', () => {
    const users = [
      createMockUser({ id: 'u1', prenom: 'A', nom: 'B' }),
      createMockUser({ id: 'u2', prenom: 'C', nom: 'D' }),
      createMockUser({ id: 'u3', prenom: 'E', nom: 'F' }),
      createMockUser({ id: 'u4', prenom: 'G', nom: 'H' }),
      createMockUser({ id: 'u5', prenom: 'I', nom: 'J' }),
    ]
    const chantier = createMockChantier({ chefs: users })
    renderWithRouter(chantier)

    expect(screen.getByText('+2')).toBeInTheDocument()
  })

  it('n\'affiche pas la section equipe si pas de membres', () => {
    const chantier = createMockChantier({ conducteurs: [], chefs: [] })
    const { container } = renderWithRouter(chantier)

    // La section equipe a une bordure en haut, donc si pas de membres, pas de bordure
    expect(container.querySelector('.border-t')).not.toBeInTheDocument()
  })

  it('applique la couleur du chantier', () => {
    const chantier = createMockChantier({ couleur: '#FF5500' })
    const { container } = renderWithRouter(chantier)

    const colorBar = container.querySelector('[style*="background-color: rgb(255, 85, 0)"]')
    expect(colorBar).toBeInTheDocument()
  })

  it('utilise la couleur par defaut si non definie', () => {
    const chantier = createMockChantier({ couleur: undefined })
    const { container } = renderWithRouter(chantier)

    // Couleur par defaut est #3498DB -> rgb(52, 152, 219)
    const colorBar = container.querySelector('[style*="background-color: rgb(52, 152, 219)"]')
    expect(colorBar).toBeInTheDocument()
  })

  it('cree un lien vers la page du chantier', () => {
    const chantier = createMockChantier({ id: 'abc123' })
    const { container } = renderWithRouter(chantier)

    const link = container.querySelector('a[href="/chantiers/abc123"]')
    expect(link).toBeInTheDocument()
  })

  it('gere les conducteurs et chefs combines', () => {
    const conducteur = createMockUser({ id: 'c1', prenom: 'Cond', nom: 'Ucteur' })
    const chef = createMockUser({ id: 'ch1', prenom: 'Chef', nom: 'Equipe' })
    const chantier = createMockChantier({ conducteurs: [conducteur], chefs: [chef] })
    renderWithRouter(chantier)

    expect(screen.getByText('CU')).toBeInTheDocument()
    expect(screen.getByText('CE')).toBeInTheDocument()
  })

  it('applique la couleur de l\'utilisateur pour l\'avatar', () => {
    const user = createMockUser({ id: 'u1', prenom: 'Test', nom: 'User', couleur: '#E74C3C' })
    const chantier = createMockChantier({ conducteurs: [user] })
    const { container } = renderWithRouter(chantier)

    // Couleur #E74C3C -> rgb(231, 76, 60)
    const avatar = container.querySelector('[style*="background-color: rgb(231, 76, 60)"]')
    expect(avatar).toBeInTheDocument()
  })
})
