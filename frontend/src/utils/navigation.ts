/**
 * Utilitaires de navigation GPS
 *
 * Gère l'ouverture d'applications de navigation (Waze, Apple Maps, Google Maps)
 * selon la plateforme détectée (iOS, Android, Desktop).
 */

/**
 * Détecte si l'appareil est sous iOS
 */
function isIOSDevice(): boolean {
  return /iPad|iPhone|iPod/.test(navigator.userAgent)
}

/**
 * Détecte si l'appareil est sous Android
 */
function isAndroidDevice(): boolean {
  return /Android/.test(navigator.userAgent)
}

/**
 * Ouvre l'application de navigation appropriée avec l'adresse donnée
 *
 * Priorité des applications :
 * - iOS: Waze > Apple Maps > Google Maps (web)
 * - Android: Waze > Google Maps (app) > Google Maps (web)
 * - Desktop: Google Maps (web)
 *
 * @param address - Adresse de destination
 *
 * @example
 * ```typescript
 * openNavigationApp('123 Rue de la Paix, Paris')
 * ```
 */
export function openNavigationApp(address: string): void {
  const encodedAddress = encodeURIComponent(address)

  if (isIOSDevice()) {
    // iOS: Tenter Waze, puis Apple Maps, puis Google Maps web
    const wazeUrl = `waze://?q=${encodedAddress}&navigate=yes`
    const appleMapsUrl = `maps://maps.apple.com/?q=${encodedAddress}`
    const googleMapsWeb = `https://maps.google.com/?q=${encodedAddress}`

    // Tentative Waze
    window.location.href = wazeUrl

    // Fallback Apple Maps après 500ms
    setTimeout(() => {
      window.location.href = appleMapsUrl

      // Fallback Google Maps web après 500ms supplémentaires
      setTimeout(() => {
        window.open(googleMapsWeb, '_blank')
      }, 500)
    }, 500)
  } else if (isAndroidDevice()) {
    // Android: Tenter Waze, puis Google Maps app, puis Google Maps web
    const wazeUrl = `waze://?q=${encodedAddress}&navigate=yes`
    const googleMapsUrl = `google.navigation:q=${encodedAddress}`
    const googleMapsWeb = `https://maps.google.com/?q=${encodedAddress}`

    // Tentative Waze
    window.location.href = wazeUrl

    // Fallback Google Maps app après 500ms
    setTimeout(() => {
      window.location.href = googleMapsUrl

      // Fallback Google Maps web après 500ms supplémentaires
      setTimeout(() => {
        window.open(googleMapsWeb, '_blank')
      }, 500)
    }, 500)
  } else {
    // Desktop: Google Maps web directement
    window.open(`https://maps.google.com/?q=${encodedAddress}`, '_blank')
  }
}
