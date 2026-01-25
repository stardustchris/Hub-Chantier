/**
 * Tests unitaires pour Feed
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Feed from './Feed'
import type { Post, Author } from '../../types/dashboard'

// Mock child components
vi.mock('./PostCard', () => ({
  default: ({ post, onLike, onUnlike, onComment, onDelete, isLiked }: {
    post: Post
    onLike: (id: number) => void
    onUnlike: (id: number) => void
    onComment: (id: number) => void
    onDelete: (id: number) => void
    isLiked: boolean
  }) => (
    <div data-testid={`post-${post.id}`} data-pinned={post.is_pinned}>
      <span data-testid="post-content">{post.content}</span>
      <button onClick={() => isLiked ? onUnlike(post.id) : onLike(post.id)} data-testid={`like-${post.id}`}>
        {isLiked ? 'Unlike' : 'Like'}
      </button>
      <button onClick={() => onComment(post.id)} data-testid={`comment-${post.id}`}>Comment</button>
      <button onClick={() => onDelete(post.id)} data-testid={`delete-${post.id}`}>Delete</button>
    </div>
  ),
}))

vi.mock('./PostComposer', () => ({
  default: ({ onSubmit }: { onSubmit: (data: { content: string; target_type: string }) => void }) => (
    <div data-testid="post-composer">
      <button
        onClick={() => onSubmit({ content: 'New post content', target_type: 'everyone' })}
        data-testid="submit-post"
      >
        Publier
      </button>
    </div>
  ),
}))

vi.mock('./CommentModal', () => ({
  default: ({ isOpen, onClose, postId }: { isOpen: boolean; onClose: () => void; postId: number }) => (
    isOpen ? (
      <div data-testid="comment-modal">
        <span>Comment modal for post {postId}</span>
        <button onClick={onClose} data-testid="close-modal">Close</button>
      </div>
    ) : null
  ),
}))

const mockPosts: Post[] = [
  {
    id: 1,
    author_id: 1,
    content: 'Post pinned content',
    status: 'pinned',
    is_urgent: true,
    is_pinned: true,
    target_type: 'everyone',
    target_display: 'Tout le monde',
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    likes_count: 5,
    comments_count: 2,
    medias_count: 0,
  },
  {
    id: 2,
    author_id: 2,
    content: 'Regular post content',
    status: 'published',
    is_urgent: false,
    is_pinned: false,
    target_type: 'everyone',
    target_display: 'Tout le monde',
    created_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    likes_count: 3,
    comments_count: 1,
    medias_count: 0,
  },
]

const mockAuthors: Record<number, Author> = {
  1: { id: 1, prenom: 'Jean', nom: 'Dupont', role: 'admin', couleur: '#3498DB' },
  2: { id: 2, prenom: 'Marie', nom: 'Martin', role: 'conducteur', couleur: '#E74C3C' },
}

describe('Feed', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.stubGlobal('confirm', vi.fn(() => true))
  })

  describe('rendering', () => {
    it('affiche le composer de post', () => {
      render(<Feed currentUserId={1} currentUserRole="admin" mockPosts={mockPosts} mockAuthors={mockAuthors} />)

      expect(screen.getByTestId('post-composer')).toBeInTheDocument()
    })

    it('affiche tous les posts', () => {
      render(<Feed currentUserId={1} currentUserRole="admin" mockPosts={mockPosts} mockAuthors={mockAuthors} />)

      expect(screen.getByTestId('post-1')).toBeInTheDocument()
      expect(screen.getByTestId('post-2')).toBeInTheDocument()
    })

    it('affiche les posts pinned en premier', () => {
      render(<Feed currentUserId={1} currentUserRole="admin" mockPosts={mockPosts} mockAuthors={mockAuthors} />)

      const posts = screen.getAllByTestId(/^post-\d+$/)
      expect(posts[0]).toHaveAttribute('data-pinned', 'true')
    })
  })

  describe('create post', () => {
    it('ajoute un nouveau post', async () => {
      const user = userEvent.setup()
      render(<Feed currentUserId={1} currentUserRole="admin" mockPosts={mockPosts} mockAuthors={mockAuthors} />)

      await user.click(screen.getByTestId('submit-post'))

      await waitFor(() => {
        expect(screen.getAllByTestId(/^post-\d+$/).length).toBe(3)
      })
    })
  })

  describe('like/unlike', () => {
    it('like un post', async () => {
      const user = userEvent.setup()
      render(<Feed currentUserId={1} currentUserRole="admin" mockPosts={mockPosts} mockAuthors={mockAuthors} />)

      // Post 2 is not liked by default
      await user.click(screen.getByTestId('like-2'))

      // After clicking, the button should change to Unlike
      await waitFor(() => {
        expect(screen.getByTestId('like-2')).toHaveTextContent('Unlike')
      })
    })
  })

  describe('comment', () => {
    it('ouvre le modal de commentaire', async () => {
      const user = userEvent.setup()
      render(<Feed currentUserId={1} currentUserRole="admin" mockPosts={mockPosts} mockAuthors={mockAuthors} />)

      await user.click(screen.getByTestId('comment-1'))

      expect(screen.getByTestId('comment-modal')).toBeInTheDocument()
    })

    it('ferme le modal de commentaire', async () => {
      const user = userEvent.setup()
      render(<Feed currentUserId={1} currentUserRole="admin" mockPosts={mockPosts} mockAuthors={mockAuthors} />)

      await user.click(screen.getByTestId('comment-1'))
      await user.click(screen.getByTestId('close-modal'))

      expect(screen.queryByTestId('comment-modal')).not.toBeInTheDocument()
    })
  })

  describe('delete', () => {
    it('supprime un post apres confirmation', async () => {
      const user = userEvent.setup()
      render(<Feed currentUserId={1} currentUserRole="admin" mockPosts={mockPosts} mockAuthors={mockAuthors} />)

      await user.click(screen.getByTestId('delete-1'))

      await waitFor(() => {
        expect(screen.queryByTestId('post-1')).not.toBeInTheDocument()
      })
    })

    it('ne supprime pas si annule', async () => {
      vi.mocked(confirm).mockReturnValueOnce(false)
      const user = userEvent.setup()
      render(<Feed currentUserId={1} currentUserRole="admin" mockPosts={mockPosts} mockAuthors={mockAuthors} />)

      await user.click(screen.getByTestId('delete-1'))

      expect(screen.getByTestId('post-1')).toBeInTheDocument()
    })
  })

  describe('sorting', () => {
    it('trie les posts: pinned puis par date', () => {
      const postsUnsorted: Post[] = [
        {
          id: 3,
          author_id: 1,
          content: 'Oldest regular',
          status: 'published',
          is_urgent: false,
          is_pinned: false,
          target_type: 'everyone',
          target_display: 'Tout le monde',
          created_at: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString(),
          likes_count: 0,
          comments_count: 0,
          medias_count: 0,
        },
        {
          id: 1,
          author_id: 1,
          content: 'Pinned',
          status: 'pinned',
          is_urgent: true,
          is_pinned: true,
          target_type: 'everyone',
          target_display: 'Tout le monde',
          created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          likes_count: 0,
          comments_count: 0,
          medias_count: 0,
        },
        {
          id: 2,
          author_id: 1,
          content: 'Newest regular',
          status: 'published',
          is_urgent: false,
          is_pinned: false,
          target_type: 'everyone',
          target_display: 'Tout le monde',
          created_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
          likes_count: 0,
          comments_count: 0,
          medias_count: 0,
        },
      ]

      render(<Feed currentUserId={1} currentUserRole="admin" mockPosts={postsUnsorted} mockAuthors={mockAuthors} />)

      const posts = screen.getAllByTestId(/^post-\d+$/)
      // First should be pinned (id=1), then newest (id=2), then oldest (id=3)
      expect(posts[0]).toHaveAttribute('data-testid', 'post-1')
      expect(posts[1]).toHaveAttribute('data-testid', 'post-2')
      expect(posts[2]).toHaveAttribute('data-testid', 'post-3')
    })
  })

  describe('empty state', () => {
    it('affiche aucun post si liste vide', () => {
      render(<Feed currentUserId={1} currentUserRole="admin" mockPosts={[]} mockAuthors={{}} />)

      expect(screen.queryByTestId(/^post-\d+$/)).not.toBeInTheDocument()
    })
  })
})
