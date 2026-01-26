/**
 * Tests pour WeatherCard
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import WeatherCard from './WeatherCard'
import type { WeatherData } from '../../hooks/useWeather'

// Mock du hook useWeather
vi.mock('../../hooks/useWeather', () => ({
  useWeather: () => ({
    weather: {
      location: 'Lyon',
      temperature: 12,
      condition: 'sunny',
      conditionCode: 0,
      wind: 12,
      windDirection: 'N',
      rainProbability: 0,
      humidity: 50,
      minTemp: 8,
      maxTemp: 15,
      uvIndex: 3,
      sunrise: '07:30',
      sunset: '19:00',
    } as WeatherData,
    alert: null,
    isLoading: false,
    error: null,
    locationSource: 'geolocation' as const,
    refresh: vi.fn(),
    setManualLocation: vi.fn(),
  }),
}))

describe('WeatherCard', () => {
  it('affiche les données météo', () => {
    render(<WeatherCard />)

    expect(screen.getByText('Lyon')).toBeInTheDocument()
    expect(screen.getByText('12°C')).toBeInTheDocument()
    expect(screen.getByText('Ensoleille')).toBeInTheDocument()
    expect(screen.getByText(/Vent 12 km\/h N - Pluie 0%/)).toBeInTheDocument()
    expect(screen.getByText(/Min 8°C - Max 15°C/)).toBeInTheDocument()
  })

  it('affiche la meteo personnalisee avec weatherOverride', () => {
    const customWeather: WeatherData = {
      location: 'Paris',
      temperature: 20,
      condition: 'cloudy',
      conditionCode: 3,
      wind: 25,
      windDirection: 'SO',
      rainProbability: 40,
      humidity: 60,
      minTemp: 15,
      maxTemp: 25,
      uvIndex: 5,
      sunrise: '07:00',
      sunset: '20:00',
    }

    render(<WeatherCard weatherOverride={customWeather} />)

    expect(screen.getByText('Paris')).toBeInTheDocument()
    expect(screen.getByText('20°C')).toBeInTheDocument()
    expect(screen.getByText('Nuageux')).toBeInTheDocument()
    expect(screen.getByText(/Vent 25 km\/h SO - Pluie 40%/)).toBeInTheDocument()
    expect(screen.getByText(/Min 15°C - Max 25°C/)).toBeInTheDocument()
  })

  it('affiche le temps pluvieux', () => {
    const rainyWeather: WeatherData = {
      location: 'Bordeaux',
      temperature: 8,
      condition: 'rainy',
      conditionCode: 61,
      wind: 30,
      windDirection: 'O',
      rainProbability: 80,
      humidity: 90,
      minTemp: 5,
      maxTemp: 10,
      uvIndex: 1,
      sunrise: '08:00',
      sunset: '18:00',
    }

    render(<WeatherCard weatherOverride={rainyWeather} />)

    expect(screen.getByText('Bordeaux')).toBeInTheDocument()
    expect(screen.getByText('8°C')).toBeInTheDocument()
    expect(screen.getByText('Pluvieux')).toBeInTheDocument()
  })

  it('affiche le temps orageux', () => {
    const stormyWeather: WeatherData = {
      location: 'Toulouse',
      temperature: 18,
      condition: 'stormy',
      conditionCode: 95,
      wind: 50,
      windDirection: 'S',
      rainProbability: 90,
      humidity: 85,
      minTemp: 15,
      maxTemp: 22,
      uvIndex: 2,
      sunrise: '07:15',
      sunset: '19:30',
    }

    render(<WeatherCard weatherOverride={stormyWeather} />)

    expect(screen.getByText('Toulouse')).toBeInTheDocument()
    expect(screen.getByText('18°C')).toBeInTheDocument()
    expect(screen.getByText('Orageux')).toBeInTheDocument()
  })

  it('affiche le temps neigeux', () => {
    const snowyWeather: WeatherData = {
      location: 'Chamonix',
      temperature: -5,
      condition: 'snowy',
      conditionCode: 71,
      wind: 10,
      windDirection: 'NE',
      rainProbability: 60,
      humidity: 70,
      minTemp: -10,
      maxTemp: 0,
      uvIndex: 4,
      sunrise: '08:15',
      sunset: '17:00',
    }

    render(<WeatherCard weatherOverride={snowyWeather} />)

    expect(screen.getByText('Chamonix')).toBeInTheDocument()
    expect(screen.getByText('-5°C')).toBeInTheDocument()
    expect(screen.getByText('Neigeux')).toBeInTheDocument()
    expect(screen.getByText(/Min -10°C - Max 0°C/)).toBeInTheDocument()
  })

  it('affiche une alerte météo si présente', () => {
    const weatherWithAlert: WeatherData = {
      location: 'Nice',
      temperature: 28,
      condition: 'sunny',
      conditionCode: 0,
      wind: 70,
      windDirection: 'SE',
      rainProbability: 0,
      humidity: 40,
      minTemp: 22,
      maxTemp: 35,
      uvIndex: 8,
      sunrise: '06:30',
      sunset: '20:30',
      alert: {
        type: 'vigilance_orange',
        title: 'Vigilance orange - Canicule',
        description: 'Températures élevées',
        startTime: new Date().toISOString(),
        phenomena: ['canicule'],
      },
    }

    render(<WeatherCard weatherOverride={weatherWithAlert} />)

    expect(screen.getByText('Nice')).toBeInTheDocument()
    expect(screen.getByText('ORANGE')).toBeInTheDocument()
  })
})
