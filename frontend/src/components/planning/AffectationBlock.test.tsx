/**
 * Tests unitaires pour AffectationBlock
 * Bloc d'affectation dans le planning
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import AffectationBlock from './AffectationBlock'

const mockAffectation: any = {
  id: 1,
  date: '2024-03-15',
  chantier_id: 1,
  chantier_nom: 'Chantier Alpha',
  chantier_couleur: '#E74C3C',
  utilisateur_couleur: '#E74C3C',
  heure_debut: '08:00',
  heure_fin: '17:00',
  utilisateur_id: 1,
  note: 'Note de test',
}

describe('AffectationBlock', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('affiche le nom du chantier', () => {
    // Act
    render(<AffectationBlock affectation={mockAffectation} />)

    // Assert
    expect(screen.getByText('Chantier Alpha')).toBeInTheDocument()
  })

  it('affiche les heures de l\'affectation', () => {
    // Act
    render(<AffectationBlock affectation={mockAffectation} />)

    // Assert
    expect(screen.getByText('08:00 - 17:00')).toBeInTheDocument()
  })

  it('affiche la couleur du chantier', () => {
    // Act
    const { container } = render(<AffectationBlock affectation={mockAffectation} />)

    // Assert
    const block = container.firstChild as HTMLElement
    expect(block.style.backgroundColor).toBe('rgb(231, 76, 60)')
  })

  it('appelle onClick au clic sur le block', () => {
    // Arrange
    const onClick = vi.fn()

    // Act
    render(<AffectationBlock affectation={mockAffectation} onClick={onClick} />)
    fireEvent.click(screen.getByText('Chantier Alpha'))

    // Assert
    expect(onClick).toHaveBeenCalled()
  })

  it('gere le mode compact', () => {
    // Act
    const { container } = render(
      <AffectationBlock affectation={mockAffectation} compact={true} />
    )

    // Assert
    const block = container.firstChild as HTMLElement
    expect(block.className).toContain('text-xs')
    expect(screen.getByText('Chantier Alpha')).toBeInTheDocument()
  })
})
