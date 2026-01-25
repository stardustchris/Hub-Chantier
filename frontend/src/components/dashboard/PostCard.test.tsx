/**
 * Tests pour PostCard
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import PostCard from './PostCard'
import type { Post, Author } from '../../types/dashboard'

// Mock de formatRelativeShort
vi.mock('../../utils/dates', () => ({
  formatRelativeShort: vi.fn(() => 'il y a 2h'),
}))

const createMockPost = (overrides: Partial<Post> = {}): Post => ({
  id: 1,
  author_id: 100,
  content: 'Contenu du post',
  target_type: 'everyone',
  target_display: 'Tout le monde',
  likes_count: 5,
  comments_count: 3,
  medias_count: 0,
  is_pinned: false,
  created_at: '2024-01-15T10:00:00Z',
  updated_at: '2024-01-15T10:00:00Z',
  ...overrides,
})

const createMockAuthor = (overrides: Partial<Author> = {}): Author => ({
  id: 100,
  prenom: 'Jean',
  nom: 'Dupont',
  role: 'chef_chantier',
  couleur: '#3498DB',
  ...overrides,
})

describe('PostCard', () => {
  const defaultProps = {
    post: createMockPost(),
    author: createMockAuthor(),
    currentUserId: 200,
    onLike: vi.fn(),
    onUnlike: vi.fn(),
    onComment: vi.fn(),
  }

  it('affiche le contenu du post', () => {
    render(<PostCard {...defaultProps} />)

    expect(screen.getByText('Contenu du post')).toBeInTheDocument()
  })

  it('affiche le nom de l\'auteur', () => {
    render(<PostCard {...defaultProps} />)

    expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
  })

  it('affiche les initiales de l\'auteur', () => {
    render(<PostCard {...defaultProps} />)

    expect(screen.getByText('JD')).toBeInTheDocument()
  })

  it('affiche Utilisateur si pas d\'auteur', () => {
    render(<PostCard {...defaultProps} author={undefined} />)

    expect(screen.getByText('Utilisateur')).toBeInTheDocument()
    expect(screen.getByText('??')).toBeInTheDocument()
  })

  it('affiche le badge Direction pour admin', () => {
    const author = createMockAuthor({ role: 'admin' })
    render(<PostCard {...defaultProps} author={author} />)

    expect(screen.getByText('Direction')).toBeInTheDocument()
  })

  it('affiche le badge Conducteur de travaux', () => {
    const author = createMockAuthor({ role: 'conducteur' })
    render(<PostCard {...defaultProps} author={author} />)

    expect(screen.getByText('Conducteur de travaux')).toBeInTheDocument()
  })

  it('affiche le badge Chef de chantier', () => {
    const author = createMockAuthor({ role: 'chef_chantier' })
    render(<PostCard {...defaultProps} author={author} />)

    expect(screen.getByText('Chef de chantier')).toBeInTheDocument()
  })

  it('affiche le badge Compagnon', () => {
    const author = createMockAuthor({ role: 'compagnon' })
    render(<PostCard {...defaultProps} author={author} />)

    expect(screen.getByText('Compagnon')).toBeInTheDocument()
  })

  it('affiche la date relative', () => {
    render(<PostCard {...defaultProps} />)

    expect(screen.getByText('il y a 2h')).toBeInTheDocument()
  })

  it('affiche le ciblage everyone', () => {
    const post = createMockPost({ target_type: 'everyone', target_display: 'Tout le monde' })
    render(<PostCard {...defaultProps} post={post} />)

    expect(screen.getByText(/Tout le monde/)).toBeInTheDocument()
  })

  it('affiche le ciblage specific_chantiers', () => {
    const post = createMockPost({ target_type: 'specific_chantiers', target_display: 'Villa Moderne' })
    render(<PostCard {...defaultProps} post={post} />)

    expect(screen.getByText(/Villa Moderne/)).toBeInTheDocument()
  })

  it('affiche le ciblage specific_people', () => {
    const post = createMockPost({ target_type: 'specific_people', target_display: '3 personnes' })
    render(<PostCard {...defaultProps} post={post} />)

    expect(screen.getByText(/3 personnes/)).toBeInTheDocument()
  })

  it('affiche le nombre de likes', () => {
    const post = createMockPost({ likes_count: 10 })
    render(<PostCard {...defaultProps} post={post} />)

    expect(screen.getByText("10 j'aime")).toBeInTheDocument()
  })

  it('affiche le nombre de commentaires', () => {
    const post = createMockPost({ comments_count: 5 })
    render(<PostCard {...defaultProps} post={post} />)

    expect(screen.getByText('5 commentaires')).toBeInTheDocument()
  })

  it('affiche commentaire au singulier', () => {
    const post = createMockPost({ comments_count: 1 })
    render(<PostCard {...defaultProps} post={post} />)

    expect(screen.getByText('1 commentaire')).toBeInTheDocument()
  })

  it('n\'affiche pas les compteurs si zero', () => {
    const post = createMockPost({ likes_count: 0, comments_count: 0 })
    render(<PostCard {...defaultProps} post={post} />)

    expect(screen.queryByText("j'aime")).not.toBeInTheDocument()
    expect(screen.queryByText('commentaire')).not.toBeInTheDocument()
  })

  it('affiche Post epingle si is_pinned', () => {
    const post = createMockPost({ is_pinned: true })
    render(<PostCard {...defaultProps} post={post} />)

    expect(screen.getByText('Post épinglé')).toBeInTheDocument()
  })

  it('n\'affiche pas Post epingle si non epingle', () => {
    const post = createMockPost({ is_pinned: false })
    render(<PostCard {...defaultProps} post={post} />)

    expect(screen.queryByText('Post épinglé')).not.toBeInTheDocument()
  })

  it('affiche le nombre de photos', () => {
    const post = createMockPost({ medias_count: 3 })
    render(<PostCard {...defaultProps} post={post} />)

    expect(screen.getByText('📷 3 photos')).toBeInTheDocument()
  })

  it('affiche photo au singulier', () => {
    const post = createMockPost({ medias_count: 1 })
    render(<PostCard {...defaultProps} post={post} />)

    expect(screen.getByText('📷 1 photo')).toBeInTheDocument()
  })

  it('appelle onLike au clic sur J\'aime', () => {
    const onLike = vi.fn()
    render(<PostCard {...defaultProps} onLike={onLike} isLiked={false} />)

    fireEvent.click(screen.getByText("J'aime"))

    expect(onLike).toHaveBeenCalledWith(1)
  })

  it('appelle onUnlike si deja like', () => {
    const onUnlike = vi.fn()
    render(<PostCard {...defaultProps} onUnlike={onUnlike} isLiked={true} />)

    fireEvent.click(screen.getByText("J'aime"))

    expect(onUnlike).toHaveBeenCalledWith(1)
  })

  it('incremente le compteur apres like', () => {
    const post = createMockPost({ likes_count: 5 })
    render(<PostCard {...defaultProps} post={post} isLiked={false} />)

    fireEvent.click(screen.getByText("J'aime"))

    expect(screen.getByText("6 j'aime")).toBeInTheDocument()
  })

  it('decremente le compteur apres unlike', () => {
    const post = createMockPost({ likes_count: 5 })
    render(<PostCard {...defaultProps} post={post} isLiked={true} />)

    fireEvent.click(screen.getByText("J'aime"))

    expect(screen.getByText("4 j'aime")).toBeInTheDocument()
  })

  it('appelle onComment au clic sur Commenter', () => {
    const onComment = vi.fn()
    render(<PostCard {...defaultProps} onComment={onComment} />)

    fireEvent.click(screen.getByText('Commenter'))

    expect(onComment).toHaveBeenCalledWith(1)
  })

  it('affiche le bouton supprimer si auteur', () => {
    const post = createMockPost({ author_id: 200 })
    const onDelete = vi.fn()
    render(<PostCard {...defaultProps} post={post} currentUserId={200} onDelete={onDelete} />)

    expect(screen.getByTitle('Supprimer')).toBeInTheDocument()
  })

  it('affiche le bouton supprimer si admin', () => {
    const author = createMockAuthor({ role: 'admin' })
    const onDelete = vi.fn()
    render(<PostCard {...defaultProps} author={author} onDelete={onDelete} />)

    expect(screen.getByTitle('Supprimer')).toBeInTheDocument()
  })

  it('n\'affiche pas le bouton supprimer si pas auteur et pas admin', () => {
    const author = createMockAuthor({ role: 'compagnon' })
    const post = createMockPost({ author_id: 100 })
    const onDelete = vi.fn()
    render(<PostCard {...defaultProps} post={post} author={author} currentUserId={200} onDelete={onDelete} />)

    expect(screen.queryByTitle('Supprimer')).not.toBeInTheDocument()
  })

  it('appelle onDelete au clic sur supprimer', () => {
    const post = createMockPost({ author_id: 200 })
    const onDelete = vi.fn()
    render(<PostCard {...defaultProps} post={post} currentUserId={200} onDelete={onDelete} />)

    fireEvent.click(screen.getByTitle('Supprimer'))

    expect(onDelete).toHaveBeenCalledWith(1)
  })

  it('a l\'aria-label correct pour le bouton like', () => {
    render(<PostCard {...defaultProps} isLiked={false} />)

    expect(screen.getByLabelText("J'aime")).toBeInTheDocument()
  })

  it('a l\'aria-label correct pour le bouton unlike', () => {
    render(<PostCard {...defaultProps} isLiked={true} />)

    expect(screen.getByLabelText("Retirer j'aime")).toBeInTheDocument()
  })

  it('a l\'aria-pressed correct pour le bouton like', () => {
    render(<PostCard {...defaultProps} isLiked={true} />)

    const likeButton = screen.getByLabelText("Retirer j'aime")
    expect(likeButton).toHaveAttribute('aria-pressed', 'true')
  })

  it('applique la bordure orange pour post epingle', () => {
    const post = createMockPost({ is_pinned: true })
    const { container } = render(<PostCard {...defaultProps} post={post} />)

    expect(container.querySelector('.border-orange-500')).toBeInTheDocument()
  })

  it('applique la couleur de l\'auteur pour l\'avatar', () => {
    const author = createMockAuthor({ couleur: '#E74C3C' })
    const { container } = render(<PostCard {...defaultProps} author={author} />)

    const avatar = container.querySelector('[style*="background-color"]')
    expect(avatar).toHaveStyle({ backgroundColor: '#E74C3C' })
  })
})
