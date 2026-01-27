/**
 * WeatherBulletinPost - Post automatique du bulletin météo dans le feed
 * Affiche le bulletin météo du jour lié au premier chantier du planning
 */

import { useState, useEffect } from 'react'
import { Sun, Cloud, CloudRain, CloudLightning, Snowflake, CloudFog, AlertTriangle, Wind, Droplets, Thermometer, MapPin } from 'lucide-react'
import type { WeatherData, WeatherAlert } from '../../hooks/useWeather'
import { weatherService } from '../../services/weather'
import { logger } from '../../services/logger'

interface WeatherBulletinPostProps {
  weather: WeatherData
  alert?: WeatherAlert | null
  /** Nom du chantier du planning */
  chantierName?: string
  /** Adresse du chantier */
  chantierAddress?: string
  /** Coordonnées GPS du chantier pour météo locale */
  chantierLatitude?: number
  chantierLongitude?: number
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

export default function WeatherBulletinPost({ weather, alert, chantierName, chantierAddress, chantierLatitude, chantierLongitude }: WeatherBulletinPostProps) {
  const [siteWeather, setSiteWeather] = useState<WeatherData | null>(null)
  const [siteAlert, setSiteAlert] = useState<WeatherAlert | null | undefined>(undefined)

  // Si le chantier a des coordonnées GPS, fetcher la météo sur site
  useEffect(() => {
    if (!chantierLatitude || !chantierLongitude) {
      setSiteWeather(null)
      setSiteAlert(undefined)
      return
    }

    let cancelled = false

    async function fetchSiteWeather() {
      try {
        const data = await weatherService.fetchWeather({
          latitude: chantierLatitude!,
          longitude: chantierLongitude!,
          city: chantierName || 'Chantier',
        })
        if (!cancelled) {
          setSiteWeather(data)
          setSiteAlert(data.alert || null)
        }
      } catch (err) {
        logger.warn('Impossible de charger la météo du chantier', { chantierName, err })
        if (!cancelled) {
          setSiteWeather(null)
          setSiteAlert(undefined)
        }
      }
    }

    fetchSiteWeather()
    return () => { cancelled = true }
  }, [chantierLatitude, chantierLongitude, chantierName])

  // Utiliser la météo du chantier si disponible, sinon la météo générale
  const displayWeather = siteWeather || weather
  const displayAlert = siteAlert !== undefined ? siteAlert : alert

  const WeatherIcon = conditionIcons[displayWeather.condition]
  const today = new Date().toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  })

  // Titre du bulletin
  const bulletinTitle = chantierName
    ? `Bulletin Meteo - ${chantierName}`
    : 'Bulletin Meteo'

  // Localisation affichée
  const displayLocation = siteWeather
    ? chantierName || displayWeather.location
    : displayWeather.location

  // Texte du bulletin
  const bulletinText = chantierName
    ? `Temps ${conditionLabels[displayWeather.condition].toLowerCase()} aujourd'hui sur le chantier ${chantierName}. Risque de pluie à ${displayWeather.rainProbability}%.`
    : displayWeather.bulletin

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* En-tête */}
      <div className="bg-gradient-to-r from-blue-500 to-cyan-500 px-4 py-3 text-white">
        <div className="flex items-center gap-2">
          <Sun className="w-5 h-5" />
          <span className="font-semibold">{bulletinTitle}</span>
          <span className="text-sm text-white/80 ml-auto">{today}</span>
        </div>
        {chantierAddress && (
          <div className="flex items-center gap-1 mt-1 text-sm text-white/70">
            <MapPin className="w-3.5 h-3.5" />
            <span>{chantierAddress}</span>
          </div>
        )}
      </div>

      {/* Alerte météo si présente */}
      {displayAlert && (
        <div className={`${alertStyles[displayAlert.type].bg} ${alertStyles[displayAlert.type].border} border-l-4 p-3 mx-4 mt-4 rounded-r-lg`}>
          <div className="flex items-start gap-2">
            <AlertTriangle className={`w-5 h-5 ${alertStyles[displayAlert.type].icon} shrink-0 mt-0.5`} />
            <div>
              <p className={`font-semibold ${alertStyles[displayAlert.type].text}`}>{displayAlert.title}</p>
              <p className={`text-sm ${alertStyles[displayAlert.type].text} mt-1`}>{displayAlert.description}</p>
              {displayAlert.phenomena.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {displayAlert.phenomena.map((p) => (
                    <span
                      key={p}
                      className={`text-xs px-2 py-0.5 rounded-full ${alertStyles[displayAlert.type].bg} ${alertStyles[displayAlert.type].text} border ${alertStyles[displayAlert.type].border}`}
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
            <p className="text-3xl font-bold text-gray-900">{displayWeather.temperature}°C</p>
            <p className="text-gray-600">{conditionLabels[displayWeather.condition]} a {displayLocation}</p>
          </div>
        </div>

        {/* Bulletin texte */}
        {bulletinText && (
          <p className="text-gray-700 mb-4 leading-relaxed">{bulletinText}</p>
        )}

        {/* Détails en grille */}
        <div className="grid grid-cols-2 gap-3">
          <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
            <Thermometer className="w-4 h-4 text-red-500" />
            <span className="text-sm text-gray-600">
              {displayWeather.minTemp}° / {displayWeather.maxTemp}°
            </span>
          </div>
          <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
            <Wind className="w-4 h-4 text-blue-500" />
            <span className="text-sm text-gray-600">
              {displayWeather.wind} km/h {displayWeather.windDirection}
            </span>
          </div>
          <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
            <Droplets className="w-4 h-4 text-cyan-500" />
            <span className="text-sm text-gray-600">
              Pluie {displayWeather.rainProbability}%
            </span>
          </div>
          <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
            <Sun className="w-4 h-4 text-yellow-500" />
            <span className="text-sm text-gray-600">
              UV {displayWeather.uvIndex}
            </span>
          </div>
        </div>

        {/* Lever/coucher soleil */}
        <div className="flex items-center justify-center gap-6 mt-4 pt-3 border-t border-gray-100 text-sm text-gray-500">
          <span>Lever {displayWeather.sunrise}</span>
          <span className="w-1 h-1 bg-gray-300 rounded-full" />
          <span>Coucher {displayWeather.sunset}</span>
        </div>
      </div>
    </div>
  )
}
