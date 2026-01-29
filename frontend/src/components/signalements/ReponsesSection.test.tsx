/**
 * Tests unitaires pour ReponsesSection
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ReponsesSection from './ReponsesSection'
import type { Reponse } from '../../types/signalements'

vi.mock('../../utils/dates', () => ({
  formatDateDayMonthYearTime: vi.fn().mockReturnValue('24 janv. 2026 14:30'),
}))

const createMockReponse = (overrides: Partial<Reponse> = {}): Reponse => ({
  id: 1,
  signalement_id: 1,
  contenu: 'Ceci est une reponse de test',
  auteur_id: 1,
  auteur_nom: 'Jean Dupont',
  photo_url: null,
  created_at: '2026-01-24T14:30:00Z',
  updated_at: '2026-01-24T14:30:00Z',
  est_resolution: false,
  ...overrides,
})

describe('ReponsesSection', () => {
  const defaultProps = {
    reponses: [] as Reponse[],
    canReply: true,
    onAddReponse: vi.fn().mockResolvedValue(undefined),
  }

  it('affiche le compteur de reponses', () => {
    // Arrange
    const reponses = [createMockReponse(), createMockReponse({ id: 2 })]

    // Act
    render(<ReponsesSection {...defaultProps} reponses={reponses} />)

    // Assert
    expect(screen.getByText('Réponses (2)')).toBeInTheDocument()
  })

  it('affiche "Aucune reponse" quand la liste est vide', () => {
    // Arrange & Act
    render(<ReponsesSection {...defaultProps} reponses={[]} />)

    // Assert
    expect(screen.getByText('Aucune réponse pour le moment.')).toBeInTheDocument()
  })

  it('affiche les reponses avec auteur et contenu', () => {
    // Arrange
    const reponses = [
      createMockReponse({ auteur_nom: 'Marc Martin', contenu: 'Premiere reponse' }),
    ]

    // Act
    render(<ReponsesSection {...defaultProps} reponses={reponses} />)

    // Assert
    expect(screen.getByText('Marc Martin')).toBeInTheDocument()
    expect(screen.getByText('Premiere reponse')).toBeInTheDocument()
  })

  it('affiche le badge Resolution pour les reponses de resolution', () => {
    // Arrange
    const reponses = [createMockReponse({ est_resolution: true })]

    // Act
    render(<ReponsesSection {...defaultProps} reponses={reponses} />)

    // Assert
    expect(screen.getByText('Résolution')).toBeInTheDocument()
  })

  it('affiche la photo quand photo_url est present', () => {
    // Arrange
    const reponses = [createMockReponse({ photo_url: 'https://example.com/photo.jpg' })]

    // Act
    render(<ReponsesSection {...defaultProps} reponses={reponses} />)

    // Assert
    const img = screen.getByAltText('Photo de la réponse')
    expect(img).toBeInTheDocument()
    expect(img).toHaveAttribute('src', 'https://example.com/photo.jpg')
  })

  it('affiche le formulaire de reponse quand canReply est true', () => {
    // Arrange & Act
    render(<ReponsesSection {...defaultProps} canReply={true} />)

    // Assert
    expect(screen.getByPlaceholderText('Ajouter une réponse...')).toBeInTheDocument()
    expect(screen.getByText('Envoyer')).toBeInTheDocument()
  })

  it('n\'affiche pas le formulaire quand canReply est false', () => {
    // Arrange & Act
    render(<ReponsesSection {...defaultProps} canReply={false} />)

    // Assert
    expect(screen.queryByPlaceholderText('Ajouter une réponse...')).not.toBeInTheDocument()
    expect(screen.queryByText('Envoyer')).not.toBeInTheDocument()
  })

  it('le bouton Envoyer est desactive quand le texte est vide', () => {
    // Arrange & Act
    render(<ReponsesSection {...defaultProps} canReply={true} />)

    // Assert
    expect(screen.getByText('Envoyer')).toBeDisabled()
  })

  it('appelle onAddReponse avec le contenu', async () => {
    // Arrange
    const onAddReponse = vi.fn().mockResolvedValue(undefined)
    render(<ReponsesSection {...defaultProps} onAddReponse={onAddReponse} canReply={true} />)
    const user = userEvent.setup()

    // Act
    const textarea = screen.getByPlaceholderText('Ajouter une réponse...')
    await user.type(textarea, 'Ma nouvelle reponse')
    await user.click(screen.getByText('Envoyer'))

    // Assert
    expect(onAddReponse).toHaveBeenCalledWith('Ma nouvelle reponse')
  })
})
