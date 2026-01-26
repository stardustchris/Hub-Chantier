/**
 * WeatherCard - Carte meteo
 * CDC Section 2.3.1 - Carte Meteo (bleue)
 */

import { useCallback } from 'react'
import { Sun, Cloud, CloudRain } from 'lucide-react'

/**
 * Ouvre l'application météo native ou une alternative web
 * - iOS: Ouvre l'app Météo Apple via URL scheme
 * - Android: Ouvre Google Weather (recherche météo Google)
 * - Fallback: Ouvre Météo-France ou Google Weather dans le navigateur
 */
function openWeatherApp(location: string): void {
  const userAgent = navigator.userAgent.toLowerCase()
  const isIOS = /iphone|ipad|ipod/.test(userAgent)
  const isAndroid = /android/.test(userAgent)

  // Encoder la localisation pour les URLs
  const encodedLocation = encodeURIComponent(location)

  if (isIOS) {
    // iOS: Tenter d'ouvrir l'app Météo Apple via URL scheme
    // On utilise un iframe caché pour éviter de quitter la page si l'app n'existe pas
    const iframe = document.createElement('iframe')
    iframe.style.display = 'none'
    iframe.src = 'weather://'
    document.body.appendChild(iframe)

    // Fallback après 1s vers Météo-France si l'app ne s'ouvre pas
    setTimeout(() => {
      document.body.removeChild(iframe)
      window.open(`https://meteofrance.com/previsions-meteo-france/${encodedLocation}`, '_blank')
    }, 1000)
  } else if (isAndroid) {
    // Android: Ouvrir directement Google Weather (fonctionne comme PWA/site)
    // C'est plus fiable que les intents qui varient selon les appareils
    window.open(`https://www.google.com/search?q=météo+${encodedLocation}`, '_blank')
  } else {
    // Desktop ou autre: Ouvrir Météo-France
    window.open(`https://meteofrance.com/previsions-meteo-france/${encodedLocation}`, '_blank')
  }
}

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

  const handleClick = useCallback(() => {
    openWeatherApp(weather.location)
  }, [weather.location])

  return (
    <div
      onClick={handleClick}
      className="bg-gradient-to-br from-amber-400 to-yellow-500 rounded-2xl p-5 text-white relative overflow-hidden shadow-lg cursor-pointer hover:shadow-xl transition-shadow active:scale-[0.98]"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      title="Ouvrir l'application météo"
    >
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
