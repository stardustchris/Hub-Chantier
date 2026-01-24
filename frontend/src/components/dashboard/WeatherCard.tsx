/**
 * WeatherCard - Carte meteo
 * CDC Section 2.3.1 - Carte Meteo (bleue)
 */

import { Sun, Cloud, CloudRain } from 'lucide-react'

interface WeatherData {
  location: string
  temperature: number
  condition: 'sunny' | 'cloudy' | 'rainy'
  wind: number
  rainProbability: number
  minTemp: number
  maxTemp: number
}

interface WeatherCardProps {
  weather?: WeatherData
}

const defaultWeather: WeatherData = {
  location: 'Lyon',
  temperature: 12,
  condition: 'sunny',
  wind: 12,
  rainProbability: 0,
  minTemp: 8,
  maxTemp: 15,
}

const conditionIcons = {
  sunny: Sun,
  cloudy: Cloud,
  rainy: CloudRain,
}

const conditionLabels = {
  sunny: 'Ensoleille',
  cloudy: 'Nuageux',
  rainy: 'Pluvieux',
}

export default function WeatherCard({ weather = defaultWeather }: WeatherCardProps) {
  const WeatherIcon = conditionIcons[weather.condition]

  return (
    <div className="bg-gradient-to-br from-amber-400 to-yellow-500 rounded-2xl p-5 text-white relative overflow-hidden shadow-lg">
      <div className="absolute top-2 right-2 opacity-50">
        <WeatherIcon className="w-20 h-20" />
      </div>
      <p className="text-sm font-medium text-white/80">{weather.location}</p>
      <p className="text-5xl font-bold">{weather.temperature}°C</p>
      <p className="text-sm mt-1 flex items-center gap-1">
        <WeatherIcon className="w-4 h-4" /> {conditionLabels[weather.condition]}
      </p>
      <div className="mt-3 text-xs text-white/80 space-y-0.5">
        <p>Vent {weather.wind} km/h - Pluie {weather.rainProbability}%</p>
        <p>Min {weather.minTemp}°C - Max {weather.maxTemp}°C</p>
      </div>
    </div>
  )
}
