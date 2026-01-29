/**
 * Tests unitaires pour PointageFormFields
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { PointageFormFields } from './PointageFormFields'
import type { Chantier } from '../../types'

vi.mock('../MobileTimePicker', () => ({
  default: ({ value, onChange, label, disabled }: any) => (
    <div data-testid={`time-picker-${label}`}>
      <label>{label}</label>
      <input value={value} onChange={(e: any) => onChange(e.target.value)} disabled={disabled} />
    </div>
  ),
}))

const mockChantiers: Chantier[] = [
  { id: 1, nom: 'Chantier Alpha', code: 'CHA', statut: 'en_cours', adresse: '1 rue A', conducteurs: [], chefs: [], created_at: '2024-01-01' } as any,
  { id: 2, nom: 'Chantier Beta', code: 'CHB', statut: 'en_cours', adresse: '2 rue B', conducteurs: [], chefs: [], created_at: '2024-01-01' } as any,
]

describe('PointageFormFields', () => {
  const defaultProps = {
    chantierId: '' as number | '',
    setChantierId: vi.fn(),
    heuresNormales: '08:00',
    setHeuresNormales: vi.fn(),
    heuresSupplementaires: '00:00',
    setHeuresSupplementaires: vi.fn(),
    commentaire: '',
    setCommentaire: vi.fn(),
    chantiers: mockChantiers,
    isEditing: false,
    isEditable: true,
  }

  it('affiche le select de chantier', () => {
    // Arrange & Act
    render(<PointageFormFields {...defaultProps} />)

    // Assert
    expect(screen.getByText('Chantier *')).toBeInTheDocument()
    expect(screen.getByText('Selectionner un chantier')).toBeInTheDocument()
  })

  it('affiche les options de chantiers', () => {
    // Arrange & Act
    render(<PointageFormFields {...defaultProps} />)

    // Assert
    expect(screen.getByText('Chantier Alpha')).toBeInTheDocument()
    expect(screen.getByText('Chantier Beta')).toBeInTheDocument()
  })

  it('affiche les champs d\'heures', () => {
    // Arrange & Act
    render(<PointageFormFields {...defaultProps} />)

    // Assert
    expect(screen.getByText('Heures normales *')).toBeInTheDocument()
    expect(screen.getByText('Heures sup.')).toBeInTheDocument()
  })

  it('affiche le champ commentaire', () => {
    // Arrange & Act
    render(<PointageFormFields {...defaultProps} />)

    // Assert
    expect(screen.getByText('Commentaire')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Optionnel...')).toBeInTheDocument()
  })

  it('le select chantier est desactive en mode editing', () => {
    // Arrange & Act
    render(<PointageFormFields {...defaultProps} isEditing={true} />)

    // Assert
    const select = screen.getByRole('combobox')
    expect(select).toBeDisabled()
  })

  it('les champs sont desactives quand isEditable est false', () => {
    // Arrange & Act
    render(<PointageFormFields {...defaultProps} isEditable={false} />)

    // Assert
    const select = screen.getByRole('combobox')
    expect(select).toBeDisabled()
    const textarea = screen.getByPlaceholderText('Optionnel...')
    expect(textarea).toBeDisabled()
  })

  it('appelle setChantierId au changement de chantier', () => {
    // Arrange
    const setChantierId = vi.fn()
    render(<PointageFormFields {...defaultProps} setChantierId={setChantierId} />)

    // Act
    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: '1' } })

    // Assert
    expect(setChantierId).toHaveBeenCalledWith(1)
  })

  it('appelle setCommentaire au changement de commentaire', () => {
    // Arrange
    const setCommentaire = vi.fn()
    render(<PointageFormFields {...defaultProps} setCommentaire={setCommentaire} />)

    // Act
    const textarea = screen.getByPlaceholderText('Optionnel...')
    fireEvent.change(textarea, { target: { value: 'Mon commentaire' } })

    // Assert
    expect(setCommentaire).toHaveBeenCalled()
  })
})
