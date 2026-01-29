/**
 * Tests unitaires pour WeatherBulletinPost
 * Post automatique du bulletin meteo dans le feed
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import WeatherBulletinPost from './WeatherBulletinPost'

vi.mock('../../services/weather', () => ({
  weatherService: {
    fetchWeather: vi.fn(),
  },
}))

vi.mock('../../services/logger', () => ({
  logger: {
    warn: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}))

const mockWeather: any = {
  location: 'Paris',
  temperature: 18,
  condition: 'sunny',
  conditionCode: 0,
  wind: 15,
  windDirection: 'NO',
  rainProbability: 10,
  humidity: 60,
  minTemp: 12,
  maxTemp: 22,
  uvIndex: 5,
  sunrise: '07:15',
  sunset: '19:45',
  bulletin: 'Temps ensoleille prevu pour la journee',
}

describe('WeatherBulletinPost', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('affiche le bulletin meteo', () => {
    // Act
    render(<WeatherBulletinPost weather={mockWeather} />)

    // Assert
    expect(screen.getByText('Bulletin Meteo')).toBeInTheDocument()
  })

  it('affiche la temperature', () => {
    // Act
    render(<WeatherBulletinPost weather={mockWeather} />)

    // Assert
    expect(screen.getByText(/18°C/)).toBeInTheDocument()
  })

  it('affiche la description du temps', () => {
    // Act
    render(<WeatherBulletinPost weather={mockWeather} />)

    // Assert
    expect(screen.getByText(/Ensoleille/)).toBeInTheDocument()
  })

  it('affiche les alertes meteo si presentes', () => {
    // Arrange
    const mockAlert: any = {
      type: 'vigilance_orange',
      title: 'Alerte vent violent',
      description: 'Rafales attendues jusqu\'a 100km/h',
      phenomena: ['Vent'],
    }

    // Act
    render(<WeatherBulletinPost weather={mockWeather} alert={mockAlert} />)

    // Assert
    expect(screen.getByText('Alerte vent violent')).toBeInTheDocument()
    expect(screen.getByText(/Rafales attendues/)).toBeInTheDocument()
    expect(screen.getByText('Vent')).toBeInTheDocument()
  })

  it('affiche les previsions', () => {
    // Act
    render(<WeatherBulletinPost weather={mockWeather} />)

    // Assert
    expect(screen.getByText(/12° \/ 22°/)).toBeInTheDocument()
    expect(screen.getByText(/15 km\/h NO/)).toBeInTheDocument()
    expect(screen.getByText(/Pluie 10%/)).toBeInTheDocument()
    expect(screen.getByText(/UV 5/)).toBeInTheDocument()
  })

  it('gere l\'absence de donnees meteo avec chantier', () => {
    // Act
    render(
      <WeatherBulletinPost
        weather={mockWeather}
        chantierName="Chantier Delta"
      />
    )

    // Assert
    expect(screen.getByText(/Bulletin Meteo - Chantier Delta/)).toBeInTheDocument()
  })
})
