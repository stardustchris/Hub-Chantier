import { useEffect, useRef } from 'react'
import { MapPin } from 'lucide-react'

interface MiniMapProps {
  /** Latitude du point */
  latitude: number
  /** Longitude du point */
  longitude: number
  /** Hauteur de la carte (classe CSS) */
  height?: string
  /** Zoom de la carte (1-20) */
  zoom?: number
  /** Nom du lieu (pour l'alt) */
  locationName?: string
}

/**
 * Composant de mini carte pour afficher une localisation (CHT-09).
 * Utilise une image statique OpenStreetMap pour éviter une dépendance lourde.
 */
export default function MiniMap({
  latitude,
  longitude,
  height = 'h-40',
  zoom = 15,
  locationName = 'Localisation',
}: MiniMapProps) {
  // URL pour une carte statique OpenStreetMap via un service comme staticmap.io ou similaire
  // Alternative: utiliser une iframe OSM ou Leaflet
  const mapUrl = `https://www.openstreetmap.org/export/embed.html?bbox=${longitude - 0.005}%2C${latitude - 0.003}%2C${longitude + 0.005}%2C${latitude + 0.003}&layer=mapnik&marker=${latitude}%2C${longitude}`

  return (
    <div className={`${height} rounded-lg overflow-hidden relative bg-gray-100`}>
      <iframe
        src={mapUrl}
        className="w-full h-full border-0"
        title={locationName}
        loading="lazy"
        referrerPolicy="no-referrer"
      />
      {/* Overlay pour empêcher scroll accidentel */}
      <div className="absolute inset-0 pointer-events-none" />
    </div>
  )
}

/**
 * Version statique avec image de placeholder si pas d'iframe souhaité.
 */
export function MiniMapStatic({
  latitude,
  longitude,
  height = 'h-40',
  locationName = 'Localisation',
}: MiniMapProps) {
  // Image statique via OpenStreetMap Static Maps API
  const staticUrl = `https://staticmap.openstreetmap.de/staticmap.php?center=${latitude},${longitude}&zoom=15&size=400x200&maptype=mapnik&markers=${latitude},${longitude},ol-marker`

  return (
    <div className={`${height} rounded-lg overflow-hidden relative bg-gray-100`}>
      <img
        src={staticUrl}
        alt={locationName}
        className="w-full h-full object-cover"
        loading="lazy"
        onError={(e) => {
          // Fallback: afficher placeholder
          const target = e.target as HTMLImageElement
          target.style.display = 'none'
          target.parentElement?.classList.add('flex', 'items-center', 'justify-center')
        }}
      />
      <noscript>
        <div className="w-full h-full flex items-center justify-center">
          <MapPin className="w-8 h-8 text-gray-400" />
        </div>
      </noscript>
    </div>
  )
}

/**
 * Placeholder simple quand pas de coordonnées.
 */
export function MapPlaceholder({ height = 'h-40' }: { height?: string }) {
  return (
    <div className={`${height} rounded-lg bg-gray-100 flex items-center justify-center`}>
      <MapPin className="w-8 h-8 text-gray-400" />
    </div>
  )
}
