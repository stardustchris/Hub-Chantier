/**
 * Tests pour WeatherCard
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import WeatherCard from './WeatherCard'

describe('WeatherCard', () => {
  it('affiche les valeurs par defaut', () => {
    render(<WeatherCard />)

    expect(screen.getByText('Lyon')).toBeInTheDocument()
    expect(screen.getByText('12°C')).toBeInTheDocument()
    expect(screen.getByText('Ensoleille')).toBeInTheDocument()
    expect(screen.getByText(/Vent 12 km\/h/)).toBeInTheDocument()
    expect(screen.getByText(/Min 8°C - Max 15°C/)).toBeInTheDocument()
  })

  it('affiche la meteo personnalisee', () => {
    render(
      <WeatherCard
        weather={{
          location: 'Paris',
          temperature: 20,
          condition: 'cloudy',
          wind: 25,
          rainProbability: 40,
          minTemp: 15,
          maxTemp: 25,
        }}
      />
    )

    expect(screen.getByText('Paris')).toBeInTheDocument()
    expect(screen.getByText('20°C')).toBeInTheDocument()
    expect(screen.getByText('Nuageux')).toBeInTheDocument()
    expect(screen.getByText(/Vent 25 km\/h - Pluie 40%/)).toBeInTheDocument()
    expect(screen.getByText(/Min 15°C - Max 25°C/)).toBeInTheDocument()
  })

  it('affiche le temps pluvieux', () => {
    render(
      <WeatherCard
        weather={{
          location: 'Bordeaux',
          temperature: 8,
          condition: 'rainy',
          wind: 30,
          rainProbability: 80,
          minTemp: 5,
          maxTemp: 10,
        }}
      />
    )

    expect(screen.getByText('Bordeaux')).toBeInTheDocument()
    expect(screen.getByText('8°C')).toBeInTheDocument()
    expect(screen.getByText('Pluvieux')).toBeInTheDocument()
  })

  it('affiche le temps ensoleille', () => {
    render(
      <WeatherCard
        weather={{
          location: 'Nice',
          temperature: 28,
          condition: 'sunny',
          wind: 5,
          rainProbability: 0,
          minTemp: 22,
          maxTemp: 30,
        }}
      />
    )

    expect(screen.getByText('Nice')).toBeInTheDocument()
    expect(screen.getByText('28°C')).toBeInTheDocument()
    expect(screen.getByText('Ensoleille')).toBeInTheDocument()
  })

  it('gere les temperatures negatives', () => {
    render(
      <WeatherCard
        weather={{
          location: 'Chamonix',
          temperature: -5,
          condition: 'cloudy',
          wind: 10,
          rainProbability: 20,
          minTemp: -10,
          maxTemp: 0,
        }}
      />
    )

    expect(screen.getByText('Chamonix')).toBeInTheDocument()
    expect(screen.getByText('-5°C')).toBeInTheDocument()
    expect(screen.getByText(/Min -10°C - Max 0°C/)).toBeInTheDocument()
  })
})
