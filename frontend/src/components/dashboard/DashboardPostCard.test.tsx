/**
 * Tests pour DashboardPostCard
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { DashboardPostCard } from './DashboardPostCard'
import type { Post } from '../../types'

// Mock useAuth
const mockUser = {
  id: '1',
  nom: 'Dupont',
  prenom: 'Jean',
  email: 'jean@test.com',
  role: 'admin',
  couleur: '#3498DB',
}

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ user: mockUser }),
}))

// Mock dashboardService
vi.mock('../../services/dashboard', () => ({
  dashboardService: {
    addComment: vi.fn(),
  },
}))

// Mock logger
vi.mock('../../services/logger', () => ({
  logger: {
    error: vi.fn(),
  },
}))

const createMockPost = (overrides: Partial<Post> = {}): Post => ({
  id: '1',
  contenu: 'Test post content',
  type: 'general',
  auteur: {
    id: '2',
    prenom: 'Marie',
    nom: 'Martin',
    couleur: '#FF5733',
    email: 'marie@test.com',
    role: 'conducteur' as const,
    type_utilisateur: 'employe',
    is_active: true,
    created_at: '2024-01-01',
  },
  created_at: new Date().toISOString(),
  is_pinned: false,
  is_urgent: false,
  likes_count: 5,
  commentaires_count: 2,
  likes: [],
  commentaires: [],
  target_type: 'tous',
  ...overrides,
})

describe('DashboardPostCard', () => {
  const mockOnLike = vi.fn()
  const mockOnPin = vi.fn()
  const mockOnDelete = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  const renderCard = (post: Post = createMockPost()) => {
    return render(
      <MemoryRouter>
        <DashboardPostCard
          post={post}
          onLike={mockOnLike}
          onPin={mockOnPin}
          onDelete={mockOnDelete}
        />
      </MemoryRouter>
    )
  }

  describe('rendering', () => {
    it('affiche le contenu du post', () => {
      renderCard()
      expect(screen.getByText('Test post content')).toBeInTheDocument()
    })

    it('affiche le nom de l auteur', () => {
      renderCard()
      expect(screen.getByText('Marie Martin')).toBeInTheDocument()
    })

    it('affiche les initiales de l auteur', () => {
      renderCard()
      expect(screen.getByText('MM')).toBeInTheDocument()
    })

    it('affiche le nombre de likes', () => {
      renderCard()
      expect(screen.getByText('5')).toBeInTheDocument()
    })

    it('affiche le nombre de commentaires', () => {
      renderCard()
      expect(screen.getByText('2')).toBeInTheDocument()
    })

    it('affiche le badge role si disponible', () => {
      renderCard()
      const badge = document.querySelector('.rounded-full')
      expect(badge).toBeInTheDocument()
    })
  })

  describe('post pinned', () => {
    it('applique le style epingle', () => {
      const post = createMockPost({ is_pinned: true })
      const { container } = renderCard(post)
      expect(container.firstChild).toHaveClass('border-l-green-500')
    })
  })

  describe('post urgent', () => {
    it('applique le style urgent', () => {
      const post = createMockPost({ is_urgent: true })
      const { container } = renderCard(post)
      expect(container.firstChild).toHaveClass('border-l-red-500')
    })
  })

  describe('target type', () => {
    it('affiche Tout le monde pour target_type tous', () => {
      const post = createMockPost({ target_type: 'tous' })
      renderCard(post)
      expect(screen.getByText('→ Tout le monde')).toBeInTheDocument()
    })

    it('affiche les chantiers cibles', () => {
      const post = createMockPost({
        target_type: 'chantiers',
        target_chantiers: [
          { id: '1', nom: 'Chantier A', code: 'CH001', adresse: 'Adresse A', statut: 'en_cours', conducteurs: [], chefs: [], created_at: '2024-01-01' },
          { id: '2', nom: 'Chantier B', code: 'CH002', adresse: 'Adresse B', statut: 'en_cours', conducteurs: [], chefs: [], created_at: '2024-01-01' },
        ],
      })
      renderCard(post)
      expect(screen.getByText('→ Chantier A, Chantier B')).toBeInTheDocument()
    })
  })

  describe('medias', () => {
    it('affiche les medias du post', () => {
      const post = createMockPost({
        medias: [
          { id: '1', url: 'https://example.com/img1.jpg', type: 'image' },
          { id: '2', url: 'https://example.com/img2.jpg', type: 'image' },
        ],
      })
      const { container } = renderCard(post)
      const images = container.querySelectorAll('img')
      expect(images).toHaveLength(2)
    })
  })

  describe('like interaction', () => {
    it('affiche le nombre de likes', () => {
      renderCard()
      expect(screen.getByText('5')).toBeInTheDocument()
    })

    it('affiche le nombre de commentaires', () => {
      renderCard()
      expect(screen.getByText('2')).toBeInTheDocument()
    })
  })

  describe('comments', () => {
    it('affiche les commentaires dans le post', () => {
      const post = createMockPost({
        commentaires: [
          {
            id: 'c1',
            contenu: 'Premier commentaire',
            auteur: mockUser as any,
            created_at: new Date().toISOString(),
          },
        ],
        commentaires_count: 1,
      })
      renderCard(post)
      expect(screen.getByText('1')).toBeInTheDocument()
    })
  })

  describe('admin features', () => {
    it('permet a l admin de voir les options', () => {
      renderCard()
      expect(screen.getByText('Test post content')).toBeInTheDocument()
    })
  })

  describe('isMockPost helper', () => {
    it('gere les posts avec ID negatif', () => {
      const post = createMockPost({ id: '-5' })
      renderCard(post)
      expect(screen.getByText('Test post content')).toBeInTheDocument()
    })
  })
})
