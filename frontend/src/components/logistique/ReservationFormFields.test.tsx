/**
 * Tests unitaires pour ReservationFormFields
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ReservationFormFields from './ReservationFormFields'
import type { Chantier } from '../../types'

const mockChantiers: Chantier[] = [
  { id: 1, nom: 'Chantier Nord', code: 'CHN', statut: 'en_cours', adresse: '1 rue N', conducteurs: [], chefs: [], created_at: '2024-01-01' } as any,
  { id: 2, nom: 'Chantier Sud', code: 'CHS', statut: 'en_cours', adresse: '2 rue S', conducteurs: [], chefs: [], created_at: '2024-01-01' } as any,
]

const mockReservation: any = {
  id: 1,
  ressource_id: 1,
  chantier_id: 1,
  chantier_nom: 'Chantier Test',
  demandeur_id: 1,
  demandeur_nom: 'Jean Dupont',
  date_reservation: '2024-03-15',
  heure_debut: '08:00:00',
  heure_fin: '17:00:00',
  statut: 'en_attente',
  statut_label: 'En attente',
  statut_couleur: '#FFA500',
  commentaire: 'Test',
}

const mockFormData = {
  chantier_id: 0,
  date_reservation: '2024-03-15',
  heure_debut: '08:00',
  heure_fin: '17:00',
  commentaire: '',
}

describe('ReservationFormFields', () => {
  const defaultCreationProps = {
    isViewMode: false,
    formData: mockFormData,
    chantiers: mockChantiers,
    onFormDataChange: vi.fn(),
  }

  const defaultViewProps = {
    isViewMode: true,
    reservation: mockReservation,
    formData: mockFormData,
    chantiers: mockChantiers,
    onFormDataChange: vi.fn(),
  }

  it('affiche les champs en mode creation (selects et inputs)', () => {
    // Arrange & Act
    render(<ReservationFormFields {...defaultCreationProps} />)

    // Assert
    expect(screen.getByText('Chantier *')).toBeInTheDocument()
    expect(screen.getByText('Date *')).toBeInTheDocument()
    expect(screen.getByText('Commentaire')).toBeInTheDocument()
  })

  it('affiche les donnees en lecture seule en mode vue', () => {
    // Arrange & Act
    render(<ReservationFormFields {...defaultViewProps} />)

    // Assert
    expect(screen.getByText('Chantier Test')).toBeInTheDocument()
    expect(screen.getByText('Test')).toBeInTheDocument()
  })

  it('affiche le select de chantier en mode creation', () => {
    // Arrange & Act
    render(<ReservationFormFields {...defaultCreationProps} />)

    // Assert
    expect(screen.getByText('Sélectionner un chantier')).toBeInTheDocument()
    expect(screen.getByText(/\[CHN\] Chantier Nord/)).toBeInTheDocument()
  })

  it('affiche le champ date', () => {
    // Arrange & Act
    render(<ReservationFormFields {...defaultCreationProps} />)

    // Assert
    expect(screen.getByText(/Date/)).toBeInTheDocument()
  })

  it('affiche les champs horaires debut et fin', () => {
    // Arrange & Act
    render(<ReservationFormFields {...defaultCreationProps} />)

    // Assert
    expect(screen.getByText(/Début/)).toBeInTheDocument()
    expect(screen.getByText(/Fin/)).toBeInTheDocument()
  })

  it('affiche le champ commentaire', () => {
    // Arrange & Act
    render(<ReservationFormFields {...defaultCreationProps} />)

    // Assert
    expect(screen.getByPlaceholderText('Commentaire optionnel...')).toBeInTheDocument()
  })

  it('appelle onFormDataChange au changement de chantier', () => {
    // Arrange
    const onFormDataChange = vi.fn()
    render(<ReservationFormFields {...defaultCreationProps} onFormDataChange={onFormDataChange} />)

    // Act
    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: '1' } })

    // Assert
    expect(onFormDataChange).toHaveBeenCalledWith(
      expect.objectContaining({ chantier_id: 1 })
    )
  })

  it('affiche le demandeur en mode vue', () => {
    // Arrange & Act
    render(<ReservationFormFields {...defaultViewProps} />)

    // Assert
    expect(screen.getByText(/Demandé par: Jean Dupont/)).toBeInTheDocument()
  })
})
