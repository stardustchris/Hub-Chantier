/**
 * Service de geocoding utilisant Nominatim (OpenStreetMap)
 * Convertit une adresse en coordonnées GPS (latitude, longitude)
 */

interface GeocodingResult {
  latitude: number
  longitude: number
  displayName: string
}

interface NominatimResponse {
  lat: string
  lon: string
  display_name: string
}

/**
 * Geocode une adresse en coordonnées GPS via Nominatim
 * @param address L'adresse à geocoder
 * @returns Les coordonnées GPS ou null si non trouvées
 */
export async function geocodeAddress(address: string): Promise<GeocodingResult | null> {
  if (!address.trim()) {
    return null
  }

  try {
    const encodedAddress = encodeURIComponent(address)
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodedAddress}&limit=1`,
      {
        headers: {
          'User-Agent': 'HubChantier/1.0',
        },
      }
    )

    if (!response.ok) {
      console.error('Erreur geocoding:', response.status)
      return null
    }

    const results: NominatimResponse[] = await response.json()

    if (results.length === 0) {
      return null
    }

    const result = results[0]
    return {
      latitude: parseFloat(result.lat),
      longitude: parseFloat(result.lon),
      displayName: result.display_name,
    }
  } catch (error) {
    console.error('Erreur geocoding:', error)
    return null
  }
}
