/**
 * Tests pour DashboardPage
 * CDC Section 2 - Tableau de Bord & Feed d'Actualites
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import DashboardPage from './DashboardPage'
import { ToastProvider } from '../contexts/ToastContext'
import type { User } from '../types'

// Mock user pour les tests
const mockUser = {
  id: '1',
  email: 'test@test.com',
  nom: 'Dupont',
  prenom: 'Jean',
  role: 'admin',
  type_utilisateur: 'employe',
  is_active: true,
  couleur: '#3498DB',
  created_at: '2024-01-01',
  updated_at: '2024-01-01',
} as User

let currentMockUser: User | null = mockUser

// Mock useAuth
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: currentMockUser,
    isAuthenticated: !!currentMockUser,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
  }),
}))

// Mock des services
vi.mock('../services/dashboard', () => ({
  dashboardService: {
    getFeed: vi.fn(),
    createPost: vi.fn(),
    getPost: vi.fn(),
    deletePost: vi.fn(),
    likePost: vi.fn(),
    unlikePost: vi.fn(),
    pinPost: vi.fn(),
    unpinPost: vi.fn(),
  },
}))

vi.mock('../services/chantiers', () => ({
  chantiersService: {
    list: vi.fn(),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

// Mock hooks used by DashboardPage that call unmocked services
vi.mock('../hooks/useClockCard', () => ({
  useClockCard: () => ({
    isClocked: false,
    clockTime: null,
    elapsedTime: '00:00:00',
    isLoading: false,
    handleClockToggle: vi.fn(),
  }),
}))

vi.mock('../hooks/useTodayPlanning', () => ({
  useTodayPlanning: () => ({
    slots: [],
    isLoading: false,
  }),
}))

vi.mock('../hooks/useWeeklyStats', () => ({
  useWeeklyStats: () => ({
    hoursWorked: '0:00',
    hoursProgress: 0,
    joursTravailesMois: 0,
    joursTotalMois: 22,
    congesPris: 0,
    congesTotal: 25,
    tasksCompleted: 0,
    tasksTotal: 0,
    isLoading: false,
  }),
}))

vi.mock('../hooks/useTodayTeam', () => ({
  useTodayTeam: () => ({
    members: [],
    isLoading: false,
    getTeamForChantier: () => [],
  }),
}))

vi.mock('../hooks/useWeather', () => ({
  useWeather: () => ({
    weather: null,
    alert: null,
    isLoading: false,
    error: null,
    locationSource: 'fallback',
    refresh: vi.fn(),
    setManualLocation: vi.fn(),
  }),
}))

vi.mock('../services/weatherNotifications', () => ({
  weatherNotificationService: {
    areNotificationsSupported: () => false,
    requestNotificationPermission: vi.fn(),
    sendWeatherAlertNotification: vi.fn(),
  },
}))

vi.mock('../components/common/MentionInput', () => ({
  default: ({ value, onChange, placeholder }: any) => (
    <textarea
      value={value}
      onChange={(e: any) => onChange(e.target.value)}
      placeholder={placeholder}
      data-testid="mention-input"
    />
  ),
}))

vi.mock('../hooks/useRecentDocuments', () => ({
  useRecentDocuments: () => ({
    documents: [],
    isLoading: false,
  }),
}))

// Mock des composants enfants pour isoler les tests
vi.mock('../components/Layout', () => ({
  default: ({ children }: { children: React.ReactNode }) => <div data-testid="layout">{children}</div>,
}))

vi.mock('../components/dashboard', () => ({
  ClockCard: () => <div data-testid="clock-card">ClockCard</div>,
  WeatherCard: () => <div data-testid="weather-card">WeatherCard</div>,
  StatsCard: () => <div data-testid="stats-card">StatsCard</div>,
  QuickActions: () => <div data-testid="quick-actions">QuickActions</div>,
  TodayPlanningCard: () => <div data-testid="today-planning">TodayPlanning</div>,
  TeamCard: () => <div data-testid="team-card">TeamCard</div>,
  DocumentsCard: () => <div data-testid="documents-card">DocumentsCard</div>,
  DashboardPostCard: ({ post, onLike, onDelete }: any) => (
    <div data-testid={`post-${post.id}`}>
      <span>{post.contenu}</span>
      <button onClick={() => onLike(post.id, post.is_liked)}>Like</button>
      <button onClick={() => onDelete(post.id)}>Delete</button>
    </div>
  ),
  WeatherBulletinPost: () => null,
}))

import { dashboardService } from '../services/dashboard'
import { chantiersService } from '../services/chantiers'

// Les mocks utilisent des types simplifies car le composant DashboardPostCard est mocke
const mockPosts: any[] = [
  {
    id: '1',
    contenu: 'Premier post',
    auteur_id: '1',
    auteur_nom: 'Jean Dupont',
    target_type: 'tous',
    is_urgent: false,
    is_pinned: false,
    is_liked: false,
    likes_count: 0,
    comments_count: 0,
    created_at: '2024-01-15T10:00:00Z',
  },
  {
    id: '2',
    contenu: 'Post urgent',
    auteur_id: '1',
    auteur_nom: 'Jean Dupont',
    target_type: 'tous',
    is_urgent: true,
    is_pinned: true,
    is_liked: true,
    likes_count: 5,
    comments_count: 2,
    created_at: '2024-01-14T10:00:00Z',
  },
]

const mockChantiers: any[] = [
  { id: '1', code: 'CH001', nom: 'Chantier A', statut: 'en_cours' },
  { id: '2', code: 'CH002', nom: 'Chantier B', statut: 'en_cours' },
]

const renderWithProviders = (user: any = mockUser) => {
  currentMockUser = user
  return render(
    <MemoryRouter>
      <ToastProvider>
        <DashboardPage />
      </ToastProvider>
    </MemoryRouter>
  )
}

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(dashboardService.getFeed).mockResolvedValue({
      items: mockPosts,
      total: 2,
      page: 1,
      size: 20,
      pages: 1,
    })
    vi.mocked(chantiersService.list).mockResolvedValue({
      items: mockChantiers,
      total: 2,
      page: 1,
      size: 100,
      pages: 1,
    })
    // Mock window.confirm
    vi.spyOn(window, 'confirm').mockReturnValue(true)
  })

  describe('Rendu initial', () => {
    it('affiche le layout avec les composants dashboard', async () => {
      renderWithProviders()

      await waitFor(() => {
        expect(screen.getByTestId('layout')).toBeInTheDocument()
        expect(screen.getByTestId('clock-card')).toBeInTheDocument()
        expect(screen.getByTestId('weather-card')).toBeInTheDocument()
        expect(screen.getByTestId('stats-card')).toBeInTheDocument()
        expect(screen.getByTestId('quick-actions')).toBeInTheDocument()
        expect(screen.getByTestId('today-planning')).toBeInTheDocument()
        expect(screen.getByTestId('team-card')).toBeInTheDocument()
        expect(screen.getByTestId('documents-card')).toBeInTheDocument()
      })
    })

    it('charge le feed au montage', async () => {
      renderWithProviders()

      await waitFor(() => {
        expect(dashboardService.getFeed).toHaveBeenCalledWith({ page: 1, size: 20 })
      })
    })

    it('charge les chantiers au montage', async () => {
      renderWithProviders()

      await waitFor(() => {
        expect(chantiersService.list).toHaveBeenCalledWith({ size: 100, statut: 'en_cours' })
      })
    })

    it('affiche les posts charges', async () => {
      renderWithProviders()

      await waitFor(() => {
        expect(screen.getByTestId('post-1')).toBeInTheDocument()
        expect(screen.getByTestId('post-2')).toBeInTheDocument()
      })
    })

    it('affiche les posts mock quand API retourne vide', async () => {
      vi.mocked(dashboardService.getFeed).mockResolvedValue({
        items: [],
        total: 0,
        page: 1,
        size: 20,
        pages: 0,
      })

      renderWithProviders()

      // Quand l'API retourne vide, on affiche les mocks de démonstration
      await waitFor(() => {
        expect(screen.getByText(/Dalle coulée avec succès/i)).toBeInTheDocument()
      })
    })
  })

  describe('Composer de post', () => {
    it('affiche le champ de saisie', async () => {
      renderWithProviders()

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Partager une photo/i)).toBeInTheDocument()
      })
    })

    it('affiche les initiales de l\'utilisateur', async () => {
      renderWithProviders()

      await waitFor(() => {
        expect(screen.getByText('JD')).toBeInTheDocument()
      })
    })

    it('permet de saisir du contenu', async () => {
      renderWithProviders()

      await waitFor(() => {
        const input = screen.getByPlaceholderText(/Partager une photo/i)
        fireEvent.change(input, { target: { value: 'Mon nouveau post' } })
        expect(input).toHaveValue('Mon nouveau post')
      })
    })

    it('affiche les options de ciblage pour admin', async () => {
      renderWithProviders(mockUser)

      await waitFor(() => {
        const input = screen.getByPlaceholderText(/Partager une photo/i)
        fireEvent.change(input, { target: { value: 'Test post' } })
      })

      await waitFor(() => {
        expect(screen.getByText('Tout le monde')).toBeInTheDocument()
      })
    })

    it('n\'affiche pas les options de ciblage pour compagnon', async () => {
      const compagnon = { ...mockUser, role: 'compagnon' as const }
      renderWithProviders(compagnon)

      await waitFor(() => {
        const input = screen.getByPlaceholderText(/Partager une photo/i)
        fireEvent.change(input, { target: { value: 'Test post' } })
      })

      // Le select de ciblage ne devrait pas apparaitre
      expect(screen.queryByText('Chantiers specifiques')).not.toBeInTheDocument()
    })

    it('cree un post quand on clique sur Publier', async () => {
      vi.mocked(dashboardService.createPost).mockResolvedValue({
        id: '3',
        contenu: 'Nouveau post',
        auteur_id: '1',
        auteur_nom: 'Jean Dupont',
        target_type: 'tous',
        is_urgent: false,
        is_pinned: false,
        is_liked: false,
        likes_count: 0,
        comments_count: 0,
        created_at: '2024-01-16T10:00:00Z',
      } as any)

      renderWithProviders()

      await waitFor(() => {
        const input = screen.getByPlaceholderText(/Partager une photo/i)
        fireEvent.change(input, { target: { value: 'Nouveau post' } })
      })

      const publishButton = screen.getByText('Publier')
      fireEvent.click(publishButton)

      await waitFor(() => {
        expect(dashboardService.createPost).toHaveBeenCalledWith({
          contenu: 'Nouveau post',
          target_type: 'tous',
          target_chantier_ids: undefined,
          is_urgent: false,
        })
      })
    })

    it('desactive le bouton Publier si contenu vide', async () => {
      renderWithProviders()

      await waitFor(() => {
        const publishButton = screen.getByText('Publier')
        expect(publishButton).toBeDisabled()
      })
    })
  })

  describe('Interactions avec les posts', () => {
    it('gere le like d\'un post', async () => {
      vi.mocked(dashboardService.likePost).mockResolvedValue(undefined as any)
      vi.mocked(dashboardService.getPost).mockResolvedValue({
        ...mockPosts[0],
        is_liked: true,
        likes_count: 1,
      } as any)

      renderWithProviders()

      await waitFor(() => {
        expect(screen.getByTestId('post-1')).toBeInTheDocument()
      })

      // post-2 est pinned donc apparait en premier (index 0), post-1 est en second (index 1)
      // post-1 n'est pas like (is_liked: false) donc on appelle likePost
      const likeButtons = screen.getAllByText('Like')
      fireEvent.click(likeButtons[1]) // post-1 est le deuxieme

      await waitFor(() => {
        expect(dashboardService.likePost).toHaveBeenCalledWith('1')
      })
    })

    it('gere le unlike d\'un post deja like', async () => {
      vi.mocked(dashboardService.unlikePost).mockResolvedValue(undefined as any)
      vi.mocked(dashboardService.getPost).mockResolvedValue({
        ...mockPosts[1],
        is_liked: false,
        likes_count: 4,
      } as any)

      renderWithProviders()

      await waitFor(() => {
        expect(screen.getByTestId('post-2')).toBeInTheDocument()
      })

      // Le post-2 est pinned donc apparait en premier (index 0)
      // et il est deja like (is_liked: true)
      const likeButtons = screen.getAllByText('Like')
      fireEvent.click(likeButtons[0]) // post-2 est premier car pinned

      await waitFor(() => {
        expect(dashboardService.unlikePost).toHaveBeenCalledWith('2')
      })
    })

    it('gere la suppression d\'un post', async () => {
      vi.mocked(dashboardService.deletePost).mockResolvedValue(undefined)

      renderWithProviders()

      await waitFor(() => {
        expect(screen.getByTestId('post-1')).toBeInTheDocument()
      })

      // post-2 est pinned donc apparait en premier, post-1 est en second
      const deleteButtons = screen.getAllByText('Delete')
      fireEvent.click(deleteButtons[1]) // post-1 est le deuxieme

      await waitFor(() => {
        expect(dashboardService.deletePost).toHaveBeenCalledWith('1')
      })
    })
  })

  describe('Pagination', () => {
    it('affiche le bouton Charger plus si hasMore', async () => {
      vi.mocked(dashboardService.getFeed).mockResolvedValue({
        items: mockPosts,
        total: 40,
        page: 1,
        size: 20,
        pages: 2,
      })

      renderWithProviders()

      await waitFor(() => {
        expect(screen.getByText('Charger plus')).toBeInTheDocument()
      })
    })

    it('n\'affiche pas le bouton Charger plus si derniere page', async () => {
      vi.mocked(dashboardService.getFeed).mockResolvedValue({
        items: mockPosts,
        total: 2,
        page: 1,
        size: 20,
        pages: 1,
      })

      renderWithProviders()

      await waitFor(() => {
        expect(screen.queryByText('Charger plus')).not.toBeInTheDocument()
      })
    })

    it('charge la page suivante au clic sur Charger plus', async () => {
      vi.mocked(dashboardService.getFeed)
        .mockResolvedValueOnce({
          items: mockPosts,
          total: 40,
          page: 1,
          size: 20,
          pages: 2,
        })
        .mockResolvedValueOnce({
          items: [{ ...mockPosts[0], id: '3', contenu: 'Nouveau post page 2' }],
          total: 40,
          page: 2,
          size: 20,
          pages: 2,
        })

      renderWithProviders()

      await waitFor(() => {
        expect(screen.getByText('Charger plus')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('Charger plus'))

      await waitFor(() => {
        expect(dashboardService.getFeed).toHaveBeenCalledWith({ page: 2, size: 20 })
      })
    })
  })

  describe('Gestion des erreurs', () => {
    it('gere l\'erreur de chargement du feed', async () => {
      const { logger } = await import('../services/logger')
      vi.mocked(dashboardService.getFeed).mockRejectedValue(new Error('Network error'))

      renderWithProviders()

      await waitFor(() => {
        expect(logger.error).toHaveBeenCalledWith(
          'Error loading feed',
          expect.any(Error),
          { context: 'DashboardFeed' }
        )
      })
    })

    it('gere l\'erreur de creation de post', async () => {
      const { logger } = await import('../services/logger')
      vi.mocked(dashboardService.createPost).mockRejectedValue(new Error('Create error'))

      renderWithProviders()

      await waitFor(() => {
        const input = screen.getByPlaceholderText(/Partager une photo/i)
        fireEvent.change(input, { target: { value: 'Test error' } })
      })

      fireEvent.click(screen.getByText('Publier'))

      await waitFor(() => {
        expect(logger.error).toHaveBeenCalledWith(
          'Erreur lors de la publication',
          expect.any(Error),
          { context: 'DashboardFeed', showToast: true }
        )
      })
    })
  })
})
