/**
 * WeatherBulletinPost - Post automatique du bulletin météo dans le feed
 * Affiche le bulletin météo du jour avec alertes éventuelles
 */

import { Sun, Cloud, CloudRain, CloudLightning, Snowflake, CloudFog, AlertTriangle, Wind, Droplets, Thermometer } from 'lucide-react'
import type { WeatherData, WeatherAlert } from '../../hooks/useWeather'

interface WeatherBulletinPostProps {
  weather: WeatherData
  alert?: WeatherAlert | null
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

const alertStyles = {
  vigilance_jaune: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-400',
    text: 'text-yellow-800',
    icon: 'text-yellow-500',
  },
  vigilance_orange: {
    bg: 'bg-orange-50',
    border: 'border-orange-400',
    text: 'text-orange-800',
    icon: 'text-orange-500',
  },
  vigilance_rouge: {
    bg: 'bg-red-50',
    border: 'border-red-500',
    text: 'text-red-800',
    icon: 'text-red-600',
  },
}

export default function WeatherBulletinPost({ weather, alert }: WeatherBulletinPostProps) {
  const WeatherIcon = conditionIcons[weather.condition]
  const today = new Date().toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  })

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* En-tête */}
      <div className="bg-gradient-to-r from-blue-500 to-cyan-500 px-4 py-3 text-white">
        <div className="flex items-center gap-2">
          <Sun className="w-5 h-5" />
          <span className="font-semibold">Bulletin Meteo</span>
          <span className="text-sm text-white/80 ml-auto">{today}</span>
        </div>
      </div>

      {/* Alerte météo si présente */}
      {alert && (
        <div className={`${alertStyles[alert.type].bg} ${alertStyles[alert.type].border} border-l-4 p-3 mx-4 mt-4 rounded-r-lg`}>
          <div className="flex items-start gap-2">
            <AlertTriangle className={`w-5 h-5 ${alertStyles[alert.type].icon} shrink-0 mt-0.5`} />
            <div>
              <p className={`font-semibold ${alertStyles[alert.type].text}`}>{alert.title}</p>
              <p className={`text-sm ${alertStyles[alert.type].text} mt-1`}>{alert.description}</p>
              {alert.phenomena.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {alert.phenomena.map((p) => (
                    <span
                      key={p}
                      className={`text-xs px-2 py-0.5 rounded-full ${alertStyles[alert.type].bg} ${alertStyles[alert.type].text} border ${alertStyles[alert.type].border}`}
                    >
                      {p}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Contenu principal */}
      <div className="p-4">
        {/* Résumé météo */}
        <div className="flex items-center gap-4 mb-4">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-100 to-cyan-100 flex items-center justify-center">
            <WeatherIcon className="w-10 h-10 text-blue-600" />
          </div>
          <div>
            <p className="text-3xl font-bold text-gray-900">{weather.temperature}°C</p>
            <p className="text-gray-600">{conditionLabels[weather.condition]} a {weather.location}</p>
          </div>
        </div>

        {/* Bulletin texte */}
        {weather.bulletin && (
          <p className="text-gray-700 mb-4 leading-relaxed">{weather.bulletin}</p>
        )}

        {/* Détails en grille */}
        <div className="grid grid-cols-2 gap-3">
          <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
            <Thermometer className="w-4 h-4 text-red-500" />
            <span className="text-sm text-gray-600">
              {weather.minTemp}° / {weather.maxTemp}°
            </span>
          </div>
          <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
            <Wind className="w-4 h-4 text-blue-500" />
            <span className="text-sm text-gray-600">
              {weather.wind} km/h {weather.windDirection}
            </span>
          </div>
          <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
            <Droplets className="w-4 h-4 text-cyan-500" />
            <span className="text-sm text-gray-600">
              Pluie {weather.rainProbability}%
            </span>
          </div>
          <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
            <Sun className="w-4 h-4 text-yellow-500" />
            <span className="text-sm text-gray-600">
              UV {weather.uvIndex}
            </span>
          </div>
        </div>

        {/* Lever/coucher soleil */}
        <div className="flex items-center justify-center gap-6 mt-4 pt-3 border-t border-gray-100 text-sm text-gray-500">
          <span>Lever {weather.sunrise}</span>
          <span className="w-1 h-1 bg-gray-300 rounded-full" />
          <span>Coucher {weather.sunset}</span>
        </div>
      </div>
    </div>
  )
}
