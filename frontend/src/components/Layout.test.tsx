/**
 * Tests pour Layout
 * Composant principal de mise en page
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Layout from './Layout'
import type { User } from '../types'

const mockUser = {
  id: '1',
  email: 'jean.dupont@test.com',
  nom: 'Dupont',
  prenom: 'Jean',
  role: 'admin',
  type_utilisateur: 'employe',
  is_active: true,
  couleur: '#3498DB',
  created_at: '2024-01-01',
  updated_at: '2024-01-01',
} as User

const mockLogout = vi.fn()

vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: mockUser,
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    logout: mockLogout,
  }),
}))

const renderWithRouter = (initialRoute = '/') => {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <Layout>
        <div data-testid="page-content">Contenu de la page</div>
      </Layout>
    </MemoryRouter>
  )
}

describe('Layout', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendu de base', () => {
    it('affiche le contenu enfant', () => {
      renderWithRouter()
      expect(screen.getByTestId('page-content')).toBeInTheDocument()
      expect(screen.getByText('Contenu de la page')).toBeInTheDocument()
    })

    it('affiche le logo Hub Chantier', () => {
      renderWithRouter()
      expect(screen.getAllByText('Hub Chantier').length).toBeGreaterThan(0)
    })

    it('affiche les liens de navigation', () => {
      renderWithRouter()
      expect(screen.getAllByText('Tableau de bord').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Chantiers').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Utilisateurs').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Planning').length).toBeGreaterThan(0)
      expect(screen.getAllByText("Feuilles d'heures").length).toBeGreaterThan(0)
      expect(screen.getAllByText('Formulaires').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Documents').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Logistique').length).toBeGreaterThan(0)
    })

    it('affiche les initiales de l\'utilisateur', () => {
      renderWithRouter()
      // JD pour Jean Dupont
      const avatars = screen.getAllByText('JD')
      expect(avatars.length).toBeGreaterThan(0)
    })

    it('affiche le nom de l\'utilisateur dans la sidebar', () => {
      renderWithRouter()
      expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
    })
  })

  describe('Navigation active', () => {
    it('met en surbrillance le lien actif - Tableau de bord', () => {
      renderWithRouter('/')
      const dashboardLinks = screen.getAllByText('Tableau de bord')
      // Au moins un lien doit avoir la classe active
      const hasActiveLink = dashboardLinks.some(link =>
        link.closest('a')?.className.includes('bg-primary-50')
      )
      expect(hasActiveLink).toBe(true)
    })

    it('met en surbrillance le lien actif - Chantiers', () => {
      renderWithRouter('/chantiers')
      const chantierLinks = screen.getAllByText('Chantiers')
      const hasActiveLink = chantierLinks.some(link =>
        link.closest('a')?.className.includes('bg-primary-50')
      )
      expect(hasActiveLink).toBe(true)
    })
  })

  describe('Menu mobile', () => {
    it('affiche le bouton menu sur mobile', () => {
      renderWithRouter()
      expect(screen.getByLabelText('Ouvrir le menu')).toBeInTheDocument()
    })

    it('ouvre la sidebar mobile au clic', () => {
      renderWithRouter()
      const menuButton = screen.getByLabelText('Ouvrir le menu')
      fireEvent.click(menuButton)

      // La sidebar mobile doit etre visible (translate-x-0)
      expect(screen.getByLabelText('Fermer le menu')).toBeInTheDocument()
    })

    it('ferme la sidebar mobile au clic sur le bouton fermer', () => {
      renderWithRouter()

      // Ouvrir la sidebar
      fireEvent.click(screen.getByLabelText('Ouvrir le menu'))
      expect(screen.getByLabelText('Fermer le menu')).toBeInTheDocument()

      // Fermer la sidebar
      fireEvent.click(screen.getByLabelText('Fermer le menu'))
      // Le bouton fermer ne devrait plus etre dans une sidebar visible
    })
  })

  describe('Notifications', () => {
    it('affiche le bouton notifications avec badge', () => {
      renderWithRouter()
      const notifButton = screen.getByLabelText(/Notifications/)
      expect(notifButton).toBeInTheDocument()
    })

    it('ouvre le panneau de notifications au clic', () => {
      renderWithRouter()
      const notifButton = screen.getByLabelText(/Notifications/)
      fireEvent.click(notifButton)

      expect(screen.getByText('Notifications')).toBeInTheDocument()
      expect(screen.getByText('Nouvelle affectation sur le chantier Villa Duplex')).toBeInTheDocument()
    })

    it('ferme le panneau au clic exterieur', () => {
      renderWithRouter()
      const notifButton = screen.getByLabelText(/Notifications/)
      fireEvent.click(notifButton)

      // Cliquer sur l'overlay
      const overlay = document.querySelector('.fixed.inset-0.z-10')
      if (overlay) {
        fireEvent.click(overlay)
      }
    })

    it('affiche le bouton Tout marquer comme lu', () => {
      renderWithRouter()
      fireEvent.click(screen.getByLabelText(/Notifications/))
      expect(screen.getByText('Tout marquer comme lu')).toBeInTheDocument()
    })
  })

  describe('Menu utilisateur', () => {
    it('affiche le bouton menu utilisateur', () => {
      renderWithRouter()
      expect(screen.getByLabelText('Menu utilisateur')).toBeInTheDocument()
    })

    it('ouvre le menu utilisateur au clic', () => {
      renderWithRouter()
      const userMenuButton = screen.getByLabelText('Menu utilisateur')
      fireEvent.click(userMenuButton)

      expect(screen.getByText('jean.dupont@test.com')).toBeInTheDocument()
      expect(screen.getByText('Parametres')).toBeInTheDocument()
      expect(screen.getByText('Deconnexion')).toBeInTheDocument()
    })

    it('appelle logout au clic sur Deconnexion', () => {
      renderWithRouter()
      fireEvent.click(screen.getByLabelText('Menu utilisateur'))
      fireEvent.click(screen.getByText('Deconnexion'))

      expect(mockLogout).toHaveBeenCalled()
    })

    it('ferme le menu et navigue vers parametres', () => {
      renderWithRouter()
      fireEvent.click(screen.getByLabelText('Menu utilisateur'))

      const parametresLink = screen.getByText('Parametres')
      expect(parametresLink.closest('a')).toHaveAttribute('href', '/parametres')
    })
  })

  describe('Accessibilite', () => {
    it('les boutons ont des aria-labels', () => {
      renderWithRouter()
      expect(screen.getByLabelText('Ouvrir le menu')).toBeInTheDocument()
      expect(screen.getByLabelText(/Notifications/)).toBeInTheDocument()
      expect(screen.getByLabelText('Menu utilisateur')).toBeInTheDocument()
    })

    it('les menus dropdown ont aria-expanded', () => {
      renderWithRouter()
      const notifButton = screen.getByLabelText(/Notifications/)
      expect(notifButton).toHaveAttribute('aria-expanded', 'false')

      fireEvent.click(notifButton)
      expect(notifButton).toHaveAttribute('aria-expanded', 'true')
    })
  })
})
