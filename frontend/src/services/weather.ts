/**
 * Service Météo avec géolocalisation
 * Utilise Open-Meteo API (gratuite, sans clé API)
 * Et l'API de géolocalisation du navigateur
 */

import { logger } from './logger'

export interface WeatherData {
  location: string
  temperature: number
  condition: 'sunny' | 'cloudy' | 'rainy' | 'stormy' | 'snowy' | 'foggy'
  conditionCode: number
  wind: number
  windDirection: string
  rainProbability: number
  humidity: number
  minTemp: number
  maxTemp: number
  uvIndex: number
  sunrise: string
  sunset: string
  /** Alerte météo si présente */
  alert?: WeatherAlert
  /** Bulletin du jour */
  bulletin?: string
  /** Coordonnées de la position */
  coordinates?: {
    latitude: number
    longitude: number
  }
}

export interface WeatherAlert {
  type: 'vigilance_jaune' | 'vigilance_orange' | 'vigilance_rouge'
  title: string
  description: string
  startTime: string
  endTime?: string
  phenomena: string[] // ex: ['vent', 'pluie-inondation', 'orages']
}

export interface HourlyForecast {
  time: string
  temperature: number
  condition: WeatherData['condition']
  rainProbability: number
}

export interface DailyForecast {
  date: string
  dayName: string
  minTemp: number
  maxTemp: number
  condition: WeatherData['condition']
  rainProbability: number
}

interface GeoPosition {
  latitude: number
  longitude: number
  city?: string
}

// Codes météo Open-Meteo -> condition
const weatherCodeToCondition = (code: number): WeatherData['condition'] => {
  if (code === 0 || code === 1) return 'sunny'
  if (code >= 2 && code <= 3) return 'cloudy'
  if (code >= 45 && code <= 48) return 'foggy'
  if (code >= 51 && code <= 67) return 'rainy'
  if (code >= 71 && code <= 77) return 'snowy'
  if (code >= 80 && code <= 82) return 'rainy'
  if (code >= 85 && code <= 86) return 'snowy'
  if (code >= 95 && code <= 99) return 'stormy'
  return 'cloudy'
}

// Direction du vent en français
const getWindDirection = (degrees: number): string => {
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']
  const index = Math.round(degrees / 45) % 8
  return directions[index]
}

// Génère un bulletin météo basé sur les données
const generateBulletin = (data: WeatherData): string => {
  const tempDescription =
    data.temperature < 5 ? 'froid' :
    data.temperature < 15 ? 'frais' :
    data.temperature < 25 ? 'doux' : 'chaud'

  const conditionText = {
    sunny: 'ensoleillé',
    cloudy: 'nuageux',
    rainy: 'pluvieux',
    stormy: 'orageux',
    snowy: 'neigeux',
    foggy: 'brumeux',
  }[data.condition]

  let bulletin = `Temps ${conditionText} et ${tempDescription} aujourd'hui sur ${data.location}.`

  if (data.rainProbability > 50) {
    bulletin += ` Risque de pluie à ${data.rainProbability}%.`
  }

  if (data.wind > 30) {
    bulletin += ` Vent soutenu de ${data.wind} km/h.`
  }

  if (data.uvIndex >= 6) {
    bulletin += ` Indice UV élevé (${data.uvIndex}), protection solaire recommandée.`
  }

  return bulletin
}

/**
 * Obtient la position géographique de l'utilisateur
 */
export async function getCurrentPosition(): Promise<GeoPosition> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Géolocalisation non supportée'))
      return
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords

        // Reverse geocoding pour obtenir le nom de la ville
        try {
          const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json&accept-language=fr`
          )
          const data = await response.json()
          const city = data.address?.city || data.address?.town || data.address?.village || data.address?.municipality || 'Position actuelle'

          resolve({ latitude, longitude, city })
        } catch {
          // Si le reverse geocoding échoue, on renvoie juste les coordonnées
          resolve({ latitude, longitude, city: 'Position actuelle' })
        }
      },
      (error) => {
        logger.warn('Erreur géolocalisation', { error: error.message })
        // Fallback sur Chambéry si géolocalisation refusée
        resolve({ latitude: 45.5646, longitude: 5.9178, city: 'Chambéry' })
      },
      {
        enableHighAccuracy: false,
        timeout: 10000,
        maximumAge: 300000, // Cache 5 minutes
      }
    )
  })
}

/**
 * Récupère les données météo depuis Open-Meteo
 */
export async function fetchWeather(position?: GeoPosition): Promise<WeatherData> {
  const pos = position || await getCurrentPosition()

  const url = new URL('https://api.open-meteo.com/v1/forecast')
  url.searchParams.set('latitude', pos.latitude.toString())
  url.searchParams.set('longitude', pos.longitude.toString())
  url.searchParams.set('current', 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m')
  url.searchParams.set('daily', 'temperature_2m_max,temperature_2m_min,precipitation_probability_max,uv_index_max,sunrise,sunset,weather_code')
  url.searchParams.set('timezone', 'Europe/Paris')

  const response = await fetch(url.toString())

  if (!response.ok) {
    throw new Error(`Erreur API météo: ${response.status}`)
  }

  const data = await response.json()

  const current = data.current
  const daily = data.daily

  const weatherData: WeatherData = {
    location: pos.city || 'Position actuelle',
    temperature: Math.round(current.temperature_2m),
    condition: weatherCodeToCondition(current.weather_code),
    conditionCode: current.weather_code,
    wind: Math.round(current.wind_speed_10m),
    windDirection: getWindDirection(current.wind_direction_10m),
    rainProbability: daily.precipitation_probability_max[0] || 0,
    humidity: current.relative_humidity_2m,
    minTemp: Math.round(daily.temperature_2m_min[0]),
    maxTemp: Math.round(daily.temperature_2m_max[0]),
    uvIndex: Math.round(daily.uv_index_max[0] || 0),
    sunrise: daily.sunrise[0]?.split('T')[1] || '07:00',
    sunset: daily.sunset[0]?.split('T')[1] || '19:00',
    coordinates: {
      latitude: pos.latitude,
      longitude: pos.longitude,
    },
  }

  // Générer le bulletin
  weatherData.bulletin = generateBulletin(weatherData)

  // Vérifier les alertes Météo France (simulation basée sur les conditions)
  const alert = checkWeatherAlert(weatherData)
  if (alert) {
    weatherData.alert = alert
  }

  return weatherData
}

/**
 * Vérifie si une alerte météo doit être émise
 * En production, cela devrait appeler l'API Météo France Vigilance
 */
function checkWeatherAlert(weather: WeatherData): WeatherAlert | undefined {
  // Alerte vent fort
  if (weather.wind > 80) {
    return {
      type: 'vigilance_orange',
      title: 'Vigilance orange - Vent violent',
      description: `Rafales de vent attendues jusqu'à ${weather.wind} km/h. Évitez les déplacements.`,
      startTime: new Date().toISOString(),
      phenomena: ['vent'],
    }
  }

  if (weather.wind > 60) {
    return {
      type: 'vigilance_jaune',
      title: 'Vigilance jaune - Vent',
      description: `Vent soutenu prévu (${weather.wind} km/h). Prudence sur les chantiers.`,
      startTime: new Date().toISOString(),
      phenomena: ['vent'],
    }
  }

  // Alerte orages
  if (weather.condition === 'stormy') {
    return {
      type: 'vigilance_orange',
      title: 'Vigilance orange - Orages',
      description: 'Orages violents prévus. Mettez à l\'abri le matériel sensible.',
      startTime: new Date().toISOString(),
      phenomena: ['orages'],
    }
  }

  // Alerte pluie forte
  if (weather.condition === 'rainy' && weather.rainProbability > 80) {
    return {
      type: 'vigilance_jaune',
      title: 'Vigilance jaune - Pluie-inondation',
      description: 'Fortes précipitations attendues. Risque d\'inondation localisée.',
      startTime: new Date().toISOString(),
      phenomena: ['pluie-inondation'],
    }
  }

  // Alerte neige/verglas
  if (weather.condition === 'snowy' && weather.temperature < 2) {
    return {
      type: 'vigilance_jaune',
      title: 'Vigilance jaune - Neige-verglas',
      description: 'Chutes de neige et risque de verglas. Adaptez vos déplacements.',
      startTime: new Date().toISOString(),
      phenomena: ['neige-verglas'],
    }
  }

  // Alerte canicule
  if (weather.maxTemp > 35) {
    return {
      type: 'vigilance_orange',
      title: 'Vigilance orange - Canicule',
      description: `Températures élevées (max ${weather.maxTemp}°C). Hydratez-vous régulièrement.`,
      startTime: new Date().toISOString(),
      phenomena: ['canicule'],
    }
  }

  // Alerte grand froid
  if (weather.minTemp < -10) {
    return {
      type: 'vigilance_orange',
      title: 'Vigilance orange - Grand froid',
      description: `Températures très basses (min ${weather.minTemp}°C). Protégez-vous du froid.`,
      startTime: new Date().toISOString(),
      phenomena: ['grand-froid'],
    }
  }

  return undefined
}

/**
 * Récupère les prévisions horaires
 */
export async function fetchHourlyForecast(position?: GeoPosition): Promise<HourlyForecast[]> {
  const pos = position || await getCurrentPosition()

  const url = new URL('https://api.open-meteo.com/v1/forecast')
  url.searchParams.set('latitude', pos.latitude.toString())
  url.searchParams.set('longitude', pos.longitude.toString())
  url.searchParams.set('hourly', 'temperature_2m,weather_code,precipitation_probability')
  url.searchParams.set('timezone', 'Europe/Paris')
  url.searchParams.set('forecast_days', '1')

  const response = await fetch(url.toString())
  const data = await response.json()

  const hourly = data.hourly
  const forecasts: HourlyForecast[] = []

  const now = new Date()
  const currentHour = now.getHours()

  // Prendre les 12 prochaines heures
  for (let i = currentHour; i < Math.min(currentHour + 12, hourly.time.length); i++) {
    forecasts.push({
      time: hourly.time[i].split('T')[1].substring(0, 5),
      temperature: Math.round(hourly.temperature_2m[i]),
      condition: weatherCodeToCondition(hourly.weather_code[i]),
      rainProbability: hourly.precipitation_probability[i] || 0,
    })
  }

  return forecasts
}

/**
 * Récupère les prévisions sur 7 jours
 */
export async function fetchDailyForecast(position?: GeoPosition): Promise<DailyForecast[]> {
  const pos = position || await getCurrentPosition()

  const url = new URL('https://api.open-meteo.com/v1/forecast')
  url.searchParams.set('latitude', pos.latitude.toString())
  url.searchParams.set('longitude', pos.longitude.toString())
  url.searchParams.set('daily', 'temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max')
  url.searchParams.set('timezone', 'Europe/Paris')
  url.searchParams.set('forecast_days', '7')

  const response = await fetch(url.toString())
  const data = await response.json()

  const daily = data.daily
  const dayNames = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam']

  return daily.time.map((date: string, i: number) => {
    const d = new Date(date)
    return {
      date,
      dayName: i === 0 ? "Aujourd'hui" : dayNames[d.getDay()],
      minTemp: Math.round(daily.temperature_2m_min[i]),
      maxTemp: Math.round(daily.temperature_2m_max[i]),
      condition: weatherCodeToCondition(daily.weather_code[i]),
      rainProbability: daily.precipitation_probability_max[i] || 0,
    }
  })
}

// Export du service
export const weatherService = {
  getCurrentPosition,
  fetchWeather,
  fetchHourlyForecast,
  fetchDailyForecast,
}
