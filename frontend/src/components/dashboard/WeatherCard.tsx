/**
 * WeatherCard - Carte meteo avec données réelles
 * CDC Section 2.3.1 - Carte Meteo (bleue)
 * Utilise la géolocalisation et l'API Open-Meteo
 */

import { useCallback } from 'react'
import { Sun, Cloud, CloudRain, CloudLightning, Snowflake, CloudFog, Loader2, AlertTriangle, MapPin } from 'lucide-react'
import { useWeather, type WeatherData } from '../../hooks/useWeather'

/**
 * Ouvre l'application météo native ou une alternative web
 */
function openWeatherApp(location: string, coordinates?: { latitude: number; longitude: number }): void {
  const userAgent = navigator.userAgent.toLowerCase()
  const isIOS = /iphone|ipad|ipod/.test(userAgent)
  const isAndroid = /android/.test(userAgent)

  const encodedLocation = encodeURIComponent(location)

  if (isIOS) {
    const iframe = document.createElement('iframe')
    iframe.style.display = 'none'
    iframe.src = 'weather://'
    document.body.appendChild(iframe)

    setTimeout(() => {
      document.body.removeChild(iframe)
      window.open(`https://meteofrance.com/previsions-meteo-france/${encodedLocation}`, '_blank')
    }, 1000)
  } else if (isAndroid) {
    window.open(`https://www.google.com/search?q=météo+${encodedLocation}`, '_blank')
  } else {
    // Desktop: Météo France avec coordonnées si disponibles
    if (coordinates) {
      window.open(`https://meteofrance.com/previsions-meteo-france/${encodedLocation}`, '_blank')
    } else {
      window.open(`https://meteofrance.com/previsions-meteo-france/${encodedLocation}`, '_blank')
    }
  }
}

const conditionIcons = {
  sunny: Sun,
  cloudy: Cloud,
  rainy: CloudRain,
  stormy: CloudLightning,
  snowy: Snowflake,
  foggy: CloudFog,
}

const conditionLabels = {
  sunny: 'Ensoleille',
  cloudy: 'Nuageux',
  rainy: 'Pluvieux',
  stormy: 'Orageux',
  snowy: 'Neigeux',
  foggy: 'Brumeux',
}

const conditionGradients = {
  sunny: 'from-amber-400 to-yellow-500',
  cloudy: 'from-slate-400 to-slate-500',
  rainy: 'from-blue-400 to-blue-600',
  stormy: 'from-purple-500 to-indigo-700',
  snowy: 'from-cyan-200 to-blue-300',
  foggy: 'from-gray-300 to-gray-500',
}

const alertColors = {
  vigilance_jaune: 'bg-yellow-500',
  vigilance_orange: 'bg-orange-500',
  vigilance_rouge: 'bg-red-600',
}

interface WeatherCardProps {
  /** Pour override les données (tests/preview) */
  weatherOverride?: WeatherData
}

export default function WeatherCard({ weatherOverride }: WeatherCardProps) {
  const { weather: liveWeather, alert, isLoading, locationSource } = useWeather()

  const weather = weatherOverride || liveWeather

  const handleClick = useCallback(() => {
    if (weather) {
      openWeatherApp(weather.location, weather.coordinates)
    }
  }, [weather])

  // État de chargement
  if (isLoading && !weather) {
    return (
      <div className="bg-gradient-to-br from-slate-400 to-slate-500 rounded-2xl p-5 text-white relative overflow-hidden shadow-lg min-h-[140px] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    )
  }

  // Pas de données
  if (!weather) {
    return (
      <div className="bg-gradient-to-br from-slate-400 to-slate-500 rounded-2xl p-5 text-white relative overflow-hidden shadow-lg">
        <p className="text-sm">Météo indisponible</p>
      </div>
    )
  }

  const WeatherIcon = conditionIcons[weather.condition]
  const gradient = conditionGradients[weather.condition]

  return (
    <div
      onClick={handleClick}
      className={`bg-gradient-to-br ${gradient} rounded-2xl p-5 text-white relative overflow-hidden shadow-lg cursor-pointer hover:shadow-xl transition-shadow active:scale-[0.98]`}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      title="Ouvrir l'application météo"
    >
      {/* Icône de fond */}
      <div className="absolute top-2 right-2 opacity-30">
        <WeatherIcon className="w-20 h-20" />
      </div>

      {/* Alerte météo */}
      {alert && (
        <div className={`absolute top-2 left-2 ${alertColors[alert.type]} px-2 py-1 rounded-md text-xs font-medium flex items-center gap-1 animate-pulse`}>
          <AlertTriangle className="w-3 h-3" />
          {alert.type.replace('vigilance_', '').toUpperCase()}
        </div>
      )}

      {/* Localisation */}
      <p className="text-sm font-medium text-white/80 flex items-center gap-1 mt-6">
        <MapPin className="w-3 h-3" />
        {weather.location}
        {locationSource === 'fallback' && (
          <span className="text-xs opacity-60">(par défaut)</span>
        )}
      </p>

      {/* Température */}
      <p className="text-5xl font-bold">{weather.temperature}°C</p>

      {/* Condition */}
      <p className="text-sm mt-1 flex items-center gap-1">
        <WeatherIcon className="w-4 h-4" /> {conditionLabels[weather.condition]}
      </p>

      {/* Détails */}
      <div className="mt-3 text-xs text-white/80 space-y-0.5">
        <p>
          Vent {weather.wind} km/h {weather.windDirection} - Pluie {weather.rainProbability}%
        </p>
        <p>
          Min {weather.minTemp}°C - Max {weather.maxTemp}°C
          {weather.uvIndex > 0 && ` - UV ${weather.uvIndex}`}
        </p>
      </div>

      {/* Indicateur de rafraîchissement */}
      {isLoading && (
        <div className="absolute bottom-2 right-2">
          <Loader2 className="w-4 h-4 animate-spin opacity-50" />
        </div>
      )}
    </div>
  )
}
