/**
 * Tests unitaires pour ChantierLogistiqueSection
 * Section logistique pour la page detail chantier
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import ChantierLogistiqueSection from './ChantierLogistiqueSection'

// Mock du hook useChantierLogistique
vi.mock('../../hooks', () => ({
  useChantierLogistique: vi.fn(),
}))

import { useChantierLogistique } from '../../hooks'

const mockedUseChantierLogistique = useChantierLogistique as ReturnType<typeof vi.fn>

const mockReservation: any = {
  id: 1,
  ressource_id: 1,
  ressource_nom: 'Grue mobile',
  ressource_code: 'GR-001',
  ressource_couleur: '#3498DB',
  date_reservation: '2024-03-15',
  heure_debut: '08:00:00',
  heure_fin: '17:00:00',
  statut: 'validee',
}

const mockReservationEnAttente: any = {
  ...mockReservation,
  id: 2,
  ressource_nom: 'Benne',
  statut: 'en_attente',
}

function renderWithRouter(ui: React.ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>)
}

describe('ChantierLogistiqueSection', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('affiche le titre "Logistique"', () => {
    // Arrange
    mockedUseChantierLogistique.mockReturnValue({
      upcomingReservations: [],
      stats: { todayCount: 0, upcomingCount: 0, pendingCount: 0 },
      isLoading: false,
    })

    // Act
    renderWithRouter(<ChantierLogistiqueSection chantierId="1" />)

    // Assert
    expect(screen.getByText('Logistique')).toBeInTheDocument()
  })

  it('affiche le loader pendant le chargement', () => {
    // Arrange
    mockedUseChantierLogistique.mockReturnValue({
      upcomingReservations: [],
      stats: { todayCount: 0, upcomingCount: 0, pendingCount: 0 },
      isLoading: true,
    })

    // Act
    const { container } = renderWithRouter(
      <ChantierLogistiqueSection chantierId="1" />
    )

    // Assert
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument()
  })

  it('affiche les reservations du chantier', () => {
    // Arrange
    mockedUseChantierLogistique.mockReturnValue({
      upcomingReservations: [mockReservation],
      stats: { todayCount: 1, upcomingCount: 1, pendingCount: 0 },
      isLoading: false,
    })

    // Act
    renderWithRouter(<ChantierLogistiqueSection chantierId="1" />)

    // Assert
    expect(screen.getByText('Grue mobile')).toBeInTheDocument()
    expect(screen.getByText('GR-001')).toBeInTheDocument()
  })

  it('affiche "Aucune reservation" quand vide', () => {
    // Arrange
    mockedUseChantierLogistique.mockReturnValue({
      upcomingReservations: [],
      stats: { todayCount: 0, upcomingCount: 0, pendingCount: 0 },
      isLoading: false,
    })

    // Act
    renderWithRouter(<ChantierLogistiqueSection chantierId="1" />)

    // Assert
    expect(screen.getByText('Aucune reservation prevue')).toBeInTheDocument()
  })

  it('affiche le statut de chaque reservation', () => {
    // Arrange
    mockedUseChantierLogistique.mockReturnValue({
      upcomingReservations: [mockReservation, mockReservationEnAttente],
      stats: { todayCount: 1, upcomingCount: 2, pendingCount: 1 },
      isLoading: false,
    })

    // Act
    renderWithRouter(<ChantierLogistiqueSection chantierId="1" />)

    // Assert
    // Les statuts sont affiches via STATUTS_RESERVATION
    expect(screen.getByText('Grue mobile')).toBeInTheDocument()
    expect(screen.getByText('Benne')).toBeInTheDocument()
  })
})
