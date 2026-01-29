/**
 * Tests unitaires pour PlanningToolbar
 * Barre d'outils du planning
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { PlanningToolbar } from './PlanningToolbar'

const mockChantier: any = {
  id: 1,
  nom: 'Chantier Alpha',
  code: 'CH-001',
}

describe('PlanningToolbar', () => {
  const defaultProps = {
    canEdit: true,
    viewTab: 'utilisateurs' as const,
    onViewTabChange: vi.fn(),
    nonPlanifiesCount: 0,
    showNonPlanifiesOnly: false,
    onToggleNonPlanifies: vi.fn(),
    filterChantier: '',
    onFilterChantierChange: vi.fn(),
    chantiers: [mockChantier],
    showFilters: false,
    onToggleFilters: vi.fn(),
    filterMetiers: [],
    showWeekend: false,
    onToggleWeekend: vi.fn(),
    onCreateClick: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('affiche la barre d\'outils', () => {
    // Act
    render(<PlanningToolbar {...defaultProps} />)

    // Assert
    expect(screen.getByText('Planning')).toBeInTheDocument()
  })

  it('affiche le bouton Nouvelle affectation', () => {
    // Act
    render(<PlanningToolbar {...defaultProps} />)

    // Assert
    expect(screen.getByText(/er une affectation/)).toBeInTheDocument()
  })

  it('appelle onCreateClick au clic sur le bouton', () => {
    // Arrange
    const onCreateClick = vi.fn()

    // Act
    render(<PlanningToolbar {...defaultProps} onCreateClick={onCreateClick} />)
    // Le bouton contient "Creer une affectation" (desktop) ou "Creer" (mobile)
    const button = screen.getByText(/er une affectation/)
    fireEvent.click(button.closest('button')!)

    // Assert
    expect(onCreateClick).toHaveBeenCalled()
  })

  it('affiche les filtres de chantiers', () => {
    // Act
    render(<PlanningToolbar {...defaultProps} />)

    // Assert
    expect(screen.getByText('Tous les chantiers')).toBeInTheDocument()
    expect(screen.getByText('Chantier Alpha')).toBeInTheDocument()
  })

  it('affiche le toggle d\'affichage', () => {
    // Act
    render(<PlanningToolbar {...defaultProps} />)

    // Assert
    expect(screen.getByText('Utilisateurs')).toBeInTheDocument()
    expect(screen.getByText('Chantiers')).toBeInTheDocument()
  })
})
