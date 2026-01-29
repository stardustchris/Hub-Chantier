/**
 * Tests unitaires pour MesInterventions
 * Affiche les interventions planifiees de l'utilisateur courant
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import MesInterventions from './MesInterventions'

// Mock des services
vi.mock('../../services/planning', () => ({
  planningService: {
    getAffectations: vi.fn(),
  },
}))

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}))

vi.mock('../../utils/dates', () => ({
  formatDateFull: vi.fn().mockReturnValue('15 mars 2024'),
}))

vi.mock('../../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

import { planningService } from '../../services/planning'
import { useAuth } from '../../contexts/AuthContext'

const mockedPlanningService = planningService as { getAffectations: ReturnType<typeof vi.fn> }
const mockedUseAuth = useAuth as ReturnType<typeof vi.fn>

describe('MesInterventions', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockedUseAuth.mockReturnValue({
      user: { id: 1, nom: 'Jean Dupont' },
    })
  })

  it('affiche le titre "Mes interventions"', async () => {
    // Arrange
    mockedPlanningService.getAffectations.mockResolvedValue([])

    // Act
    render(<MesInterventions chantierId={1} />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/Mes interventions sur ce chantier/)).toBeInTheDocument()
    })
  })

  it('affiche le loader pendant le chargement', () => {
    // Arrange
    mockedPlanningService.getAffectations.mockReturnValue(new Promise(() => {})) // never resolves

    // Act
    render(<MesInterventions chantierId={1} />)

    // Assert
    expect(screen.getByText('Chargement...')).toBeInTheDocument()
  })

  it('affiche "Aucune intervention" quand pas de donnees', async () => {
    // Arrange
    mockedPlanningService.getAffectations.mockResolvedValue([])

    // Act
    render(<MesInterventions chantierId={1} />)

    // Assert
    await waitFor(() => {
      expect(
        screen.getByText(/Vous n'avez pas d'interventions planifiees/)
      ).toBeInTheDocument()
    })
  })

  it('affiche les interventions avec chantier et date', async () => {
    // Arrange
    const futureDate = new Date()
    futureDate.setDate(futureDate.getDate() + 7)
    const futureDateStr = futureDate.toISOString().split('T')[0]

    mockedPlanningService.getAffectations.mockResolvedValue([
      {
        id: 1,
        date: futureDateStr,
        heure_debut: '08:00',
        heure_fin: '17:00',
        chantier_nom: 'Chantier A',
        note: '',
      },
    ])

    // Act
    render(<MesInterventions chantierId={1} />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('15 mars 2024')).toBeInTheDocument()
      expect(screen.getByText('08:00 - 17:00')).toBeInTheDocument()
    })
  })

  it('affiche le message d\'erreur en cas d\'echec', async () => {
    // Arrange
    mockedPlanningService.getAffectations.mockRejectedValue(new Error('Erreur reseau'))

    // Act
    render(<MesInterventions chantierId={1} />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Impossible de charger vos interventions')).toBeInTheDocument()
    })
  })

  it('filtre par utilisateur courant', async () => {
    // Arrange
    mockedPlanningService.getAffectations.mockResolvedValue([])

    // Act
    render(<MesInterventions chantierId={5} />)

    // Assert
    await waitFor(() => {
      expect(mockedPlanningService.getAffectations).toHaveBeenCalledWith(
        expect.objectContaining({
          utilisateur_ids: ['1'],
          chantier_ids: ['5'],
        })
      )
    })
  })
})
